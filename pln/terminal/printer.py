import sys

from   . import get_width
from   .ansi import length, StyleStack

#-------------------------------------------------------------------------------

# FIXME: Docstrings.

# FIXME: API is terrible.  Fix it.  Maybe something like this?
#
#   >>> printer(fg="green") << "text"
#   >>> printer(style_dict) <= "line"
#   >>> printer(indent="... ") <= "line"
#   >>> printer(style=...).html("<p>Blah blah.</p>")
#   >>> printer.nl()
#   >>> printer.start()  # nl if not at_start
#   >>> printer.indent(...)
#   >>> printer.unindent(...)

class Printer:
    """
    Does some bookkeeping for printing to a fixed-width device.
    """

    def __init__(self, write=None, *, width=None, indent="", 
                 style=StyleStack.DEFAULT_STYLE):
        if write is None:
            write = sys.stdout.write
        if width is None:
            width = get_width()
        self.__width = width
        self.__indent = [indent]
        self.__col = None
        self.__style = StyleStack(style)
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


    def push_style(self, **style):
        self.write_string(self.__style.push(**style))


    def pop_style(self):
        self.write_string(self.__style.pop())


    def write_string(self, string, *, style={}):
        """
        Prints a string on the current line.

        `string` may not contain newlines.  Does not end the current line.
        """
        if len(string) == 0:
            return
        assert "\n" not in string, repr(string)

        if style:
            self.push_style(**style)
        if self.__col is None:
            if length(string) > 0:
                # FIXME: Hacky.  What's the style policy for indentation?
                self.push_style(**StyleStack.DEFAULT_STYLE)
                self._write(self.__indent[-1])
                self.pop_style()
                self._write(string)
                self.__col = length(string)
            else:
                self._write(string)
        else:
            self._write(string)
            self.__col += length(string)
        if style:
            self.pop_style()


    def write_line(self, string, *, style={}):
        self.write_string(string, style=style)
        self.newline()


    def write(self, string, *, style={}):
        if style:
            self.push_style(**style)
        if "\n" in string:
            lines = string.split("\n")
            for line in lines[: -1]:
                self.write_string(line)
                self.newline()
            self.write_string(lines[-1])
        else:
            self.write_string(string)
        if style:
            self.pop_style()


    def fits(self, string):
        """
        Returns true if `string` fits on the current line.
        """
        return self.column + length(string) <= self.width


    def elide(self, string, *, style={}, ellipsis="\u2026"):
        """
        Prints `string`, elided at the end if it doesn't fit the current line.
        """
        space = self.width - self.column
        if length(string) > space:
            string = string[: space - length(ellipsis)] + ellipsis
        self.write_line(string, style=style)


    def right_justify(self, string, style={}):
        """
        Prints right-justified.

        Prints `string` right justified on the current line, if it fits,
        on the next line otherwise, followed in either case by a newline.
        """
        l = length(string)
        if self.column + l > self.width:
            self.newline()
        self.write_string(
            (self.width - (self.column + l)) * " " + string,
            style=style)
        self.newline()


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



