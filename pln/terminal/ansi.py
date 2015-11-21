"""
ANSI escape codes.

See https://en.wikipedia.org/wiki/ANSI_escape_code.
"""

#-------------------------------------------------------------------------------

from   math import floor

#-------------------------------------------------------------------------------

ESC = "\x1b"
CSI = ESC + "["

def SGR(*codes):
    assert all( isinstance(c, int) for c in codes )
    return CSI + ";".join( str(c) for c in codes ) + "m"


RESET               = SGR(  )  # Same as NORMAL.
NORMAL              = SGR( 0)
BOLD                = SGR( 1)
LIGHT               = SGR( 2)
ITALIC              = SGR( 3)
UNDERLINE           = SGR( 4)
SLOW_BLINK          = SGR( 5)
RAPID_BLINK         = SGR( 6)
NEGATIVE            = SGR( 7)
CONCEAL             = SGR( 8)
CROSS_OUT           = SGR( 9)
PRIMARY_FONT        = SGR(10)
ALTERNATE_FONT_1    = SGR(11)
ALTERNATE_FONT_2    = SGR(12)
ALTERNATE_FONT_3    = SGR(13)
ALTERNATE_FONT_4    = SGR(14)
ALTERNATE_FONT_5    = SGR(15)
ALTERNATE_FONT_6    = SGR(16)
ALTERNATE_FONT_7    = SGR(17)
ALTERNATE_FONT_8    = SGR(18)
ALTERNATE_FONT_9    = SGR(19)
BOLD_OFF            = SGR(21)
NORMAL_INTENSITY    = SGR(22)
ITALIC_OFF          = SGR(23)
UNDERLINE_OFF       = SGR(24)
BLINK_OFF           = SGR(25)
POSITIVE            = SGR(27)
REVEAL              = SGR(28)
CROSS_OUT_OFF       = SGR(29)
BLACK_TEXT          = SGR(30)
RED_TEXT            = SGR(31)
GREEN_TEXT          = SGR(32)
YELLOW_TEXT         = SGR(33)
BLUE_TEXT           = SGR(34)
MAGENTA_TEXT        = SGR(35)
CYAN_TEXT           = SGR(36)
WHITE_TEXT          = SGR(37)
DEFAULT_TEXT        = SGR(39)
BLACK_BACKGROUND    = SGR(40)
RED_BACKGROUND      = SGR(41)
GREEN_BACKGROUND    = SGR(42)
YELLOW_BACKGROUND   = SGR(43)
BLUE_BACKGROUND     = SGR(44)
MAGENTA_BACKGROUND  = SGR(45)
CYAN_BACKGROUND     = SGR(46)
WHITE_BACKGROUND    = SGR(47)
DEFAULT_BACKGROUND  = SGR(49)

def COLORMAP_TEXT(i):
    assert 0 <= i < 256
    return SGR(38, 5, i)


def COLORMAP_BACKGROUND(i):
    assert 0 <= i < 256
    return SGR(48, 5, i)


BLACK   =   0
RED     =   1
GREEN   =   2
YELLOW  =   3
BLUE    =   4
MAGENTA =   5
CYAN    =   6
GRAY    =   7
WHITE   = 231


def GRAY_LEVEL(fraction):
    """
    Returns the closest color map code for a gray level between 0 and 1.
    """
    assert 0 <= fraction <= 1
    index = int(floor(fraction * 24.999999999999))
    return WHITE if index == 24 else 232 + index


def sgr(*, color=None, background=None, light=False, bold=False, 
        underline=False, blink=False, reverse=False, conceal=False):
    """
    Returns an SGR sequence.
    """
    codes = []
    if color is not None:
        codes.extend([38, 5, int(color)])
    if background is not None:
        try:
            codes.append(40 + _COLOR_NAMES[background])
        except KeyError:
            codes.extend([48, 5, int(background)])
    if bold:
        codes.append(1)
    if light:
        codes.append(2)
    if underline:
        codes.append(4)
    if blink:
        codes.append(5)
    if reverse:
        codes.append(7)
    if conceal:
        codes.append(8)
    return SGR(*codes)


def inverse_sgr(*, color=None, background=None, light=False, bold=False,
                underline=False, blink=False, reverse=False, conceal=False):
    """
    Returns the inverse SGR sequence to `sgr()`.
    """
    codes = []
    if color is not None:
        codes.append(39)
    if background is not None:
        codes.append(49)
    if bold or light:
        codes.append(22)
    if underline:
        codes.append(24)
    if blink:
        codes.append(25)
    if reverse:
        codes.append(27)
    if conceal:
        codes.append(28)
    return SGR(*codes)


def style(**kw_args):
    """
    Returns a function that applies graphics style to text.

    The styling function accepts a single string argument, and returns that
    string styled and followed by a graphics reset.
    """
    escape = sgr(**kw_args)
    unescape = inverse_sgr(**kw_args)
    return lambda text: escape + str(text) + unescape


