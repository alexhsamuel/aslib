# FIXME: Handle stdin.
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

STDOUT_STYLE    = None
STDERR_STYLE    = ansi.style(fg="#400000")
TIME_STYLE      = ansi.style(fg="light_gray")
EXIT_STYLE      = ansi.style(fg="light_gray")
USAGE_STYLE     = ansi.style(fg="#80c0ff")

def get_signal_name(signum):
    try:
        return Signals(signum).name
    except ValueError:
        return "SIG???"


# Our own output goes to stdout.
write = sys.stdout.write

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
    

def show(text, style=None):
    global col
    global last_timestamp

    time = datetime.now()

    for line in re.split("(\n)", text):
        if line == "":
            pass
        elif line == "\n":
            col = 0
            write("\n".format(col))
        else:
            assert "\n" not in line
            write(line if style is None else style(line))
            col += len(text) 
            show_time(time)

    sys.stdout.flush()
    

async def format_output(stream, style):
    while True:
        # Wait for some output to be available.
        output = await stream.read(1)
        if len(output) == 0:
            break
        # Read whatever's available in the buffer.
        output += await stream.read(len(stream._buffer))
        show(output.decode(), style)


async def run_command(loop, argv):
    proc = await asyncio.create_subprocess_exec(
        *argv, loop=loop, stdout=PIPE, stderr=PIPE)

    stdout = format_output(proc.stdout, STDOUT_STYLE)
    stderr = format_output(proc.stderr, STDERR_STYLE)

    try:
        result, *_ = await asyncio.gather(proc.wait(), stdout, stderr)
    except KeyboardInterrupt:
        show("\n")
        return KEYBOARD_INTERRUPT_EXIT_STATUS
    else:
        return result


def main():
    with closing(asyncio.get_event_loop()) as loop:
        start = time.monotonic()
        try:
            result = loop.run_until_complete(run_command(loop, sys.argv[1 :]))
        except KeyboardInterrupt:
            result = KEYBOARD_INTERRUPT_EXIT_STATUS
        end = time.monotonic()

    if col != 0:
        write("\n")
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    write(
        EXIT_STYLE("exit: ")
        + (USAGE_STYLE("0") if result == 0
           else STDERR_STYLE(str(result)) if result > 0 
           else STDERR_STYLE(get_signal_name(-result)))
        + " ")
    write(" ".join(
        EXIT_STYLE(l + ": ") + USAGE_STYLE(v)
        for l, v in (
                ("real", format(end - start, ".3f")),
                ("user", format(usage.ru_utime, ".3f")),
                ("sys", format(usage.ru_stime, ".3f")),
                ("RSS", format(usage.ru_maxrss / 1024**2, ".0f") + "M"),
        )
    ) + "\n")

    raise SystemExit(result)


if __name__ == "__main__":
    main()


