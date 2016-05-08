import asyncio
from   contextlib import closing
from   datetime import datetime
import re
import resource
from   subprocess import PIPE
import sys

from   pln.terminal import ansi, get_size

#-------------------------------------------------------------------------------

# FIXME
def go_to_column(col):
    return ansi.CSI + str(col + 1) + "G"


write = sys.stdout.write

width, _ = get_size()  # FIXME: Should be dynamic.
col = 0
last_timestamp = None

TIME_STYLE = ansi.style(fg="light_gray")

def show(text, style=None):
    global col
    global last_timestamp

    timestamp = " " + format(datetime.now(), "%H:%M:%S.%f")[: -3]

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

            if timestamp != last_timestamp:
                write(go_to_column(width - len(timestamp)))
                write(TIME_STYLE(timestamp))
                write(go_to_column(col))
                last_timestamp = timestamp

    sys.stdout.flush()
    

async def format_output(stream, style):
    try:
        while True:
            # Wait for some output to be available.
            output = await stream.read(1)
            if len(output) == 0:
                break
            # Read whatever's available in the buffer.
            output += await stream.read(len(stream._buffer))
            show(output.decode(), style)
    except BrokenPipeError:
        # FIXME: What to do?  We need to close the pipes and cancel the other
        # coro.
        raise


async def run_command(loop, argv):
    proc = await asyncio.create_subprocess_exec(
        *argv, loop=loop, stdout=PIPE, stderr=PIPE)

    stdout = format_output(proc.stdout, None)
    stderr = format_output(proc.stderr, ansi.style(fg="#600000"))

    try:
        result, *_ = await asyncio.gather(proc.wait(), stdout, stderr)
    except KeyboardInterrupt:
        show("\n")
        # Because that's what the shell does.  (?)
        return 130
    else:
        return result


def main():
    with closing(asyncio.get_event_loop()) as loop:
        result = loop.run_until_complete(run_command(loop, sys.argv[1 :]))
        raise SystemExit(result)


if __name__ == "__main__":
    main()


