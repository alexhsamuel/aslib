import shutil

#-------------------------------------------------------------------------------

def get_width():
    """
    Returns the width in columns.
    """
    # FIXME: This doesn't handle redirected stdout; use /proc/self/tty or 
    # something.
    return shutil.get_terminal_size().columns


