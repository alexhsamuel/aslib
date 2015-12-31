import sys

from   . import get_width
from   .ansi import length

#-------------------------------------------------------------------------------

class Printer:
    """
    Does some bookkeeping for printing to a fixed-width device.
    """

    def __init__(self, write=None, *, width=None, indent=""):
        if write is None:
            write = sys.stdout.write
        if width is None:
            width = get_width()
        self.__width = width
        self.__indent = [indent]
        self.__col = None
        self._write = write


    @property
    def width(self):
        """
        The effective width, i.e. the total width minus current indent.
        """
        return self.__width - length(self.__indent[-1])


    @property
    def at_start(self):
        """
        Trye if printing is at the start of a new line.
        """
        return self.__col is None


    @property
    def column(self):
        """
        The current column number.

        The width of the current indentation is not included.
        """
        return self.__col or 0


    @property
    def indent(self):
        return self.__indent[-1]


    def push_indent(self, indent):
        self.__indent.append(self.__indent[-1] + indent)


    def pop_indent(self):
        self.__indent.pop()


    def write_string(self, string):
        """
        Prints a string on the current line.

        `string` may not contain newlines.  Does not end the current line.
        """
        if len(string) == 0:
            return
        assert "\n" not in string, repr(string)

        if self.__col is None:
            if length(string) > 0:
                self._write(self.__indent[-1] + string)
                self.__col = length(string)
            else:
                self._write(string)
        else:
            self._write(string)
            self.__col += length(string)


    def write(self, string):
        if "\n" in string:
            lines = string.split("\n")
            for line in lines[: -1]:
                self.write_string(line)
                self.newline()
            self.write_string(lines[-1])
        else:
            self.write_string(string)


    def newline(self, count=1):
        if count < 1:
            return
        if self.at_start:
            self._write(self.__indent[-1])
        self._write("\n")
        if count > 1:
            self._write((self.__indent[-1] + "\n") * (count - 1))
        self.__col = None


    def print(self, *args, **kw_args):
        print(*args, file=self, **kw_args)


    def __lshift__(self, string):
        self.write_string(string)
        return self


    def __le__(self, line):
        self.write_string(line)
        self.newline()
        return self



