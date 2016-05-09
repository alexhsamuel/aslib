"""
Usage: {} [ Options ] PROGRAM [ ARG ... ]

Runs PROGRAM with ARGs and enhances the output.

  - Input to stdin is shown in boldface.
  - Output to stderr is shown in red.
  - Timestamps are shown for lines of output, at the right. 
  - The exit status and basic resource usage are shown on termination.

Note that the program will not work correctly if PROGRAM outputs ANSI escape
sequences, or otherwises uses the terminal in nontrivial ways.

Options:
  -h --help     Print usage information and exit.
"""

#-------------------------------------------------------------------------------

# FIXME: Handle stdin.
# FIXME: Trim or wrap long lines.
# FIXME: Handle KeyboardInterrupt correctly.
# FIXME: Handle BrokenPipeError correctly.

import asyncio
from   contextlib import closing, suppress
from   datetime import datetime
import os
import re
import resource
from   signal import Signals
from   subprocess import PIPE
import sys
import time

from   . import ansi, get_size

#-------------------------------------------------------------------------------

KEYBOARD_INTERRUPT_EXIT_STATUS = -Signals.SIGINT

STDERR_COLOR    = "#800000"
TIME_STYLE      = ansi.style(fg="gray50")
EXIT_STYLE      = ansi.style(fg="gray50")
ERROR_STYLE     = ansi.style(fg="#800000")
USAGE_STYLE     = ansi.style(fg="#0055aa")

def get_signal_name(signum):
    try:
        return Signals(signum).name
    except ValueError:
        return "SIG???"


# Our own output goes to stdout.
write = sys.stdout.write
flush = sys.stdout.flush

# The terminal width.
width, _    = get_size()  # FIXME: Should be dynamic.

# The current column.
col         = 0

last_timestamp = None

def show_time(time):
    global last_timestamp

    timestamp = " " + format(time, "%H:%M:%S.%f")[: -3]

    if timestamp != last_timestamp:
        write(ansi.to_column(width - len(timestamp)))
        write(TIME_STYLE(timestamp))
        write(ansi.to_column(col))
        last_timestamp = timestamp
    

def show(text, time, fg):
    global col
    global last_timestamp

    for line in re.split(r"(\n)", text):
        if line == "":
            pass
        elif line == "\n":
            col = 0
            write("\n")
        else:
            assert "\n" not in line
            # Set the color, and turn off bold.
            write(ansi.sgr(fg=fg, bold=False))
            write(line)
            col += len(line) 
            show_time(time)

    # Disable the color, and reenable bold for stdin.
    write(ansi.sgr(fg="default", bold=True))

    flush()


async def format_output(stream, fg):
    while True:
        # Wait for some output to be available.
        output = await stream.read(1)
        if len(output) == 0:
            break
        time = datetime.now()
        # Read whatever's available in the buffer.
        buf_len = len(stream._buffer)
        if buf_len > 0:
            output += await stream.read(buf_len)
        show(output.decode(), time, fg)


async def run_command(loop, argv):
    proc = await asyncio.create_subprocess_exec(
        *argv, loop=loop, stdout=PIPE, stderr=PIPE)

    stdout = format_output(proc.stdout, None)
    stderr = format_output(proc.stderr, STDERR_COLOR)

    try:
        result, *_ = await asyncio.gather(proc.wait(), stdout, stderr)
    except KeyboardInterrupt:
        show("\n")
        return KEYBOARD_INTERRUPT_EXIT_STATUS
    else:
        return result


def run(argv):
    # Reset the terminal, and set it to bold to style stdin.
    write(ansi.NORMAL + ansi.BOLD)
    flush()

    try:
        with closing(asyncio.get_event_loop()) as loop:
            start = time.monotonic()
            try:
                exit = loop.run_until_complete(run_command(loop, argv))
            except KeyboardInterrupt:
                exit = KEYBOARD_INTERRUPT_EXIT_STATUS
            end = time.monotonic()

        usage = resource.getrusage(resource.RUSAGE_CHILDREN)

        write(ansi.NORMAL_INTENSITY)
        if col != 0:
            write("\n")
        # Show the exit status.
        write(
            EXIT_STYLE("exit: ")
            + (USAGE_STYLE("0") if exit == 0
               else ERROR_STYLE(str(exit)) if exit > 0 
               else ERROR_STYLE(get_signal_name(-exit)))
            + " ")
        # Show resource usage.
        write(" ".join(
            EXIT_STYLE(l + ": ") + USAGE_STYLE(v)
            for l, v in (
                    ("real", format(end - start, ".3f")),
                    ("user", format(usage.ru_utime, ".3f")),
                    ("sys", format(usage.ru_stime, ".3f")),
                    ("RSS", format(usage.ru_maxrss / 1024**2, ".0f") + "M"),
            )
        ) + "\n")

        raise SystemExit(exit)

    finally:
        write(ansi.RESET)


def main():
    # We don't use argparse, as we want to accept optional arguments only
    # at the beginning of argv.
    argv = list(sys.argv)
    this_prog = os.path.basename(argv.pop(0))
    while len(argv) > 0 and argv[0].startswith("-"):
        arg = argv.pop(0)
        if arg in ("-h", "--help"):
            print(__doc__.format(this_prog))
            raise SystemExit(0)
        else:
            print("Unknown option: {}\n".format(arg), file=sys.stderr)
            print(__doc__.format(this_prog), file=sys.stderr)
            raise SystemExit(2)

    run(argv)


if __name__ == "__main__":
    main()


