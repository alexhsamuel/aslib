import html.parser
import io
import logging
import re
import shutil

from   . import ansi
from   .printer import Printer
from   ..text import get_common_indent
import pln.log

log = pln.log.get()
# FIXME: Remove log_calls.
# log.setLevel(logging.INFO)
log_call = pln.log.log_call(log.info)

#-------------------------------------------------------------------------------

# FIXME: 
# - Add UPPERCASE feature
# - Elide / truncate words longer than width?
# - French spacing.

class Converter(html.parser.HTMLParser):

    # (indent, prefix, prenl, postnl, style, )
    ELEMENTS = {
        # Block elements
        "h1"    : ("", "\u272a ", 3, 2, {"bold": True, "underline": True}),
        "h2"    : ("", "\u2605 ", 2, 2, {"bold": True}),
        "h3"    : ("", "\u2734 ", 2, 2, {}),
        "p"     : ("", "", 2, 2, {}),
        "pre"   : ("\u2503 ", "", 2, 2, {"fg": "gray20"}),

        # Inline elements
        "b"     : ("", "", 0, 0, {"bold": True}),
        "code"  : ("", "", 0, 0, {"fg": "#243"}),
        "em"    : ("", "", 0, 0, {"underline": True}),
        "i"     : ("", "", 0, 0, {"fg": "#600"}),
        "u"     : ("", "", 0, 0, {"underline": True}),
    }


    # FIXME: Suffix?  Or remove prefix?
    def __init__(self, printer, *, normalize_pre=True):
        super().__init__()

        self.__printer = printer
        self.__normalize_pre = bool(normalize_pre)

        # True if horizontal space is required before the next word.
        self.__hspace = False
        # Number of lines of vertical space present.
        self.__vspace = 0
        # Are we in a <pre> element?
        self.__pre = False
        # Stack of ANSI terminal styles.
        self.__style = ansi.StyleStack()


    # FIXME: Expose StyleStack instead of taking a style argument?
    # FIXME: Or move the StyleStack into the Printer?
    def convert(self, html, style={}):
        self.__printer << self.__style.push(**style)
        self.feed(html)
        self.__printer << self.__style.pop()


    @log_call
    def handle_starttag(self, tag, attrs):
        pr = self.__printer

        # If needed, emit a word separator before emitting the word.
        if self.__hspace and not pr.at_start:
            pr << " "
            self.__hspace = False

        try:
            indent, prefix, prenl, postnl, style = self.ELEMENTS[tag]
        except KeyError:
            log.warning("unknown tag: {}".format(tag))
        else:
            if indent:
                pr.push_indent(indent)
            if style:
                pr << self.__style.push(**style)

            num_lines = prenl - (self.__vspace + (1 if pr.at_start else 0))
            log.warning("start {} vspace={} adding {}".format(tag, self.__vspace, num_lines))
            if num_lines > 0:
                pr.newline(num_lines)
                self.__vspace = prenl

            pr.write(prefix)

        if tag == "pre":
            # Enable special handling for preformatted elements.
            self.__pre = True


    @log_call
    def handle_endtag(self, tag):
        pr = self.__printer

        try:
            indent, prefix, prenl, postnl, style = self.ELEMENTS[tag]
        except KeyError:
            pass
        else:
            if indent:
                pr.pop_indent()
            if style:
                pr << self.__style.pop()

            num_lines = postnl - (self.__vspace + (1 if pr.at_start else 0))
            log.warning("end {} vspace={} adding {}".format(tag, self.__vspace, num_lines))
            if num_lines > 0:
                pr.newline(num_lines)
                self.__vspace = postnl

        if tag == "pre":
            self.__pre = False


    @log_call
    def handle_data(self, data):
        assert isinstance(data, str)
        if self.__pre:
            self.__handle_pre_text(data)
        else:
            self.__handle_text(data)


    def __handle_text(self, text):
        pr = self.__printer

        # Break into words at whitespace boundaries, keeping whitespace.
        words = [ w for w in re.split(r"(\s+)", text) if len(w) > 0 ]

        for word in words:
            length = len(word)
            if re.match(r"\s+$", word):  # FIXME
                # This is whitespace.  Don't emit it, but flag that we've 
                # seen it and require a separation for the next word.
                self.__hspace = True

            else:
                # Check if this word would take us past the terminal width.
                if (not pr.at_start
                    and (pr.column + (1 if self.__hspace else 0) + length) 
                        > pr.width):
                    # On to the next line.
                    pr.newline()
                    self.__hspace = False

                # Don't need a separator at the start of a line.
                if pr.at_start:
                    self.__hspace = False

                # If needed, emit a word separator before emitting the word.
                if self.__hspace:
                    pr << " "
                    self.__hspace = False

                pr << word
                self.__vspace = 0


    def __handle_pre_text(self, text):
        if self.__normalize_pre:
            # We assume (?) that the entire pre text is delivered together.
            lines = text.split("\n")
            # Remove the first and/or last lines, if they're blank.
            if lines[0].strip() == "":
                lines = lines[1 :]
            if lines[-1].strip() == "":
                lines = lines[: -1]
            # Remove common indentation.
            _, lines = get_common_indent(lines)
            text = "\n".join(lines)

        self.__printer.write(text)


    @log_call
    def handle_entityref(self, name):
        pass



def convert(html, **kw_args):
    """
    Converts HTML to text with ANSI escape sequences.

    @keywords
      See `Converter.__init__()`.
    """
    buffer = io.StringIO()
    converter = Converter(Printer(buffer.write), **kw_args)
    converter.feed(html)
    return buffer.getvalue()


#-------------------------------------------------------------------------------

# FIXME: For testing.

if __name__ == "__main__":
    with open("tmp/test0.html") as file:
        html = file.read()
    print(convert(html))


