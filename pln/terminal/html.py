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
        "code"  : ("", "", {"fg": "#073"}, False),
        "em"    : ("", "", {"underline": True}, False),
        "h2"    : ("\n\n", "\n", {"underline": True}, True),
        "p"     : ("\n\n", "", {}, True),
        "u"     : ("", "", {"underline": True}, False),
    }


    def __init__(self, width=None, indent=""):
        super().__init__()

        if width is None:
            width = shutil.get_terminal_size().columns

        self.__width = width
        self.__col = None

        # Stack of indentation prefixes; last element is the top.
        self.__indent = [indent]

        # Stack of ANSI terminal style.
        self.__style = ansi.StyleStack()

        self.__result = []


    @property
    def indent(self):
        return self.__indent(-1)


    def push_indent(self, prefix):
        self.__indent.add(self.__indent[-1] + prefix)


    def pop_indent(self):
        self.__indent.pop()


    def __lshift__(self, string):
        if string:
            self.__result.append(string)


    @property
    def result(self):
        return "".join(self.__result)


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
        words = [ w for w in re.split(r"\s+", data) if len(w) > 0 ]
        for word in words:
            length = len(word)
            if self.__col is None or self.__col + 1 + length > self.__width:
                if self.__col is not None:
                    self << "\n"
                indent = self.__indent[-1]
                self << indent
                self.__col = len(indent)
            else:
                self << " "
            self << word
            self.__col += length + 1


    @log_call
    def handle_entityref(self, name):
        pass



#-------------------------------------------------------------------------------

# FIXME: For testing.

if __name__ == "__main__":
    with open("tmp/test0.html") as file:
        html = file.read()

    converter = Converter()
    converter.feed(html)
    print(converter.result)


