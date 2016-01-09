import os
import shutil
import sys

#-------------------------------------------------------------------------------

def get_width():
    """
    Returns the width in columns.
    """
    if sys.platform == "darwin":
        from . import tty
        tty_path = tty.get_path(tty.get_name())
        with open(tty_path) as file:
            return os.get_terminal_size(file.fileno()).columns
    else:
        # FIXME: Linux
        return shutil.get_terminal_size().columns



