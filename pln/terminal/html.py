import html.parser
import logging
import re
import shutil

from   . import ansi
from   ..text import get_common_indent
import pln.log

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
log_call = pln.log.log_call(log.info)

#-------------------------------------------------------------------------------

# FIXME: 
# - Add UPPERCASE feature
# - Track __col in __lshift__() using fixfmt.string_length().

class Converter(html.parser.HTMLParser):

    # (indent, prefix, suffix, style, newline)
    ELEMENTS = {
        "b"     : (None, "", "", {"bold": True}, False),
        "code"  : (None, "", "", {"fg": "#254"}, False),
        "em"    : (None, "", "", {"underline": True}, False),
        "h1"    : (None, "\n", "\n", {"bold": True, "underline": True}, True),
        "h2"    : (None, "\n", "\n", {"underline": True}, True),
        "i"     : (None, "", "", {"fg": "#600"}, False),
        "p"     : (None, "", "\n", {}, True),
        "pre"   : ("\u2503 ", "", "", {"fg": "gray20"}, False),
        "u"     : (None, "", "", {"underline": True}, False),
    }


    # FIXME: Suffix?  Or remove prefix?
    def __init__(self, *, width=None, indent="", normalize_pre=True):
        super().__init__()

        if width is None:
            width = shutil.get_terminal_size().columns

        self.__width = width
        self.__normalize_pre = bool(normalize_pre)

        # The current column, or `None` if just starting a new line.
        self.__col = None
        # Needs a space.
        self.__sep = False
        # Are we in a <pre> element?
        self.__pre = False
        # Stack of indentation prefixes; last element is the top.
        self.__indent = [indent]
        # Stack of ANSI terminal styles.
        self.__style = ansi.StyleStack()
        # Lines of converted output.
        self.__lines = []


    @property
    def indent(self):
        return self.__indent[-1]


    def push_indent(self, indent):
        self.__indent.append(self.__indent[-1] + indent)


    def pop_indent(self):
        self.__indent.pop()


    def __lshift__(self, string):
        first, *rest = string.split("\n")
        if first:
            self.__lines[-1] += first
        if rest:
            self.__lines.extend(rest)


    @property
    def result(self):
        return "\n".join(self.__lines) + "\n"


    @log_call
    def handle_starttag(self, tag, attrs):
        # If needed, emit a word separator before emitting the word.
        if self.__sep and self.__col is not None:
            self << " "
            self.__col += 1
            self.__sep = False

        try:
            indent, prefix, _, style, newline = self.ELEMENTS[tag]
        except KeyError:
            log.warning("unknown tag: {}".format(tag))
        else:
            if indent:
                self.push_indent(indent)
            self << prefix
            if style:
                self << self.__style.push(**style)
            if newline:
                self << "\n"
                self.__col = None
                self.__sep = False

        if tag == "pre":
            self.__pre = True
            self << "\n"
            self << self.indent
            self.__col = len(self.indent)


    @log_call
    def handle_endtag(self, tag):
        try:
            indent, _, suffix, style, _ = self.ELEMENTS[tag.lower()]
        except KeyError:
            pass
        else:
            if indent:
                self.pop_indent()
            if style:
                self << self.__style.pop()
            self << suffix

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
        # Break into words at whitespace boundaries, keeping whitespace.
        words = [ w for w in re.split(r"(\s+)", text) if len(w) > 0 ]

        for word in words:
            length = len(word)
            if re.match(r"\s+$", word):  # FIXME
                # This is whitespace.  Don't emit it, but flag that we've 
                # seen it and requie a separation for the next word.
                self.__sep = True

            else:
                # Check if this word would take us past the terminal width.
                if (self.__col is not None 
                    and (self.__col 
                         + (1 if self.__sep else 0) 
                         + length) > self.__width):
                    # Emit the newline.
                    self << "\n"
                    self.__col = None
                    self.__sep = False

                if self.__col is None:
                    # Yes.  First, revert to the default style so we don't 
                    # carry underlines, reverse video, etc. over the newline.
                    self << self.__style.push(**self.__style.DEFAULT_STYLE)
                    # Emit the current indentation.
                    self << self.indent
                    self.__col = len(self.indent)
                    # Revert the current style.
                    self << self.__style.pop()
                    # No word separator required immediately after a newline.
                    self.__sep = False

                # If needed, emit a word separator before emitting the word.
                if self.__sep:
                    self << " "
                    self.__col += 1
                    self.__sep = False

                self << word
                self.__col += length 


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

        # Add the current indent to each line of text.
        text = text.replace("\n", "\n" + self.indent)

        self << text


    @log_call
    def handle_entityref(self, name):
        pass



#-------------------------------------------------------------------------------

# FIXME: For testing.

if __name__ == "__main__":
    with open("tmp/test0.html") as file:
        html = file.read()

    converter = Converter(indent=" ")
    converter.feed(html)
    print(converter.result)


