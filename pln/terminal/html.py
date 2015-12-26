import html.parser
import logging
import re
import shutil

from   . import ansi
import pln.log

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
log_call = pln.log.log_call(log.info)

#-------------------------------------------------------------------------------

# FIXME: 
# - Add UPPERCASE feature

class Converter(html.parser.HTMLParser):

    # (prefix, suffix, style, newline)
    ELEMENTS = {
        "b"     : ("", "", {"bold": True}, False),
        "code"  : ("", "", {"fg": "#254"}, False),
        "em"    : ("", "", {"underline": True}, False),
        "h2"    : ("\n", "\n", {"underline": True}, True),
        "p"     : ("\n\n", "", {}, True),
        "u"     : ("", "", {"underline": True}, False),
    }


    # FIXME: Suffix?  Or remove prefix?
    def __init__(self, width=None, indent=""):
        super().__init__()

        if width is None:
            width = shutil.get_terminal_size().columns

        self.__width = width

        # The current column, or `None` if just starting a new line.
        self.__col = None
        # Needs a space.
        self.__sep = False
        # Stack of indentation prefixes; last element is the top.
        self.__indent = [indent]
        # Stack of ANSI terminal styles.
        self.__style = ansi.StyleStack()
        # Lines of converted output.
        self.__lines = []


    @property
    def indent(self):
        return self.__indent(-1)


    def push_indent(self, prefix):
        self.__indent.add(self.__indent[-1] + prefix)


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
        try:
            prefix, _, style, newline = self.ELEMENTS[tag.lower()]
        except KeyError:
            log.warning("unknown tag: {}".format(tag))
        else:
            self << prefix
            if style:
                self << self.__style.push(**style)
            if newline:
                self.__col = None


    @log_call
    def handle_endtag(self, tag):
        try:
            _, suffix, style, _ = self.ELEMENTS[tag.lower()]
        except KeyError:
            pass
        else:
            if style:
                self << self.__style.pop()
            self << suffix


    @log_call
    def handle_data(self, data):
        assert isinstance(data, str)
        words = re.split(r"(\s+)", data)
        for word in words:
            length = len(word)
            if self.__col is None or self.__col + 1 + length > self.__width:
                self << self.__style.push(**self.__style.DEFAULT_STYLE)
                if self.__col is not None:
                    self << "\n"
                indent = self.__indent[-1]
                self << indent
                self.__col = len(indent)
                self.__sep = False
                self << self.__style.pop()
            if re.match(r"\s+$", word):  # FIXME
                if self.__sep:
                    self << " "
                    self.__sep = False
            elif length > 0:
                self << word
                self.__col += length + 1
                self.__sep = True


    @log_call
    def handle_entityref(self, name):
        pass



#-------------------------------------------------------------------------------

# FIXME: For testing.

if __name__ == "__main__":
    with open("tmp/test0.html") as file:
        html = file.read()

    converter = Converter(indent="-- ")
    converter.feed(html)
    print(converter.result)


