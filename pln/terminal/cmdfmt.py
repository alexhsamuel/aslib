# FIXME: Handle stdin.
# FIXME: Trim or wrap long lines.
# FIXME: Handle KeyboardInterrupt correctly.
# FIXME: Handle BrokenPipeError correctly.

import asyncio
from   contextlib import closing, suppress
from   datetime import datetime
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
    

def show(text, fg):
    global col
    global last_timestamp

    time = datetime.now()

    # Set the color, and turn off bold.
    write(ansi.sgr(fg=fg, bold=False))

    for line in re.split("(\n)", text):
        if line == "":
            pass
        elif line == "\n":
            col = 0
            write("\n".format(col))
        else:
            assert "\n" not in line
            write(line)
            col += len(text) 
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
        # Read whatever's available in the buffer.
        output += await stream.read(len(stream._buffer))
        show(output.decode(), fg)


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
    run(sys.argv[1 :])


if __name__ == "__main__":
    main()


