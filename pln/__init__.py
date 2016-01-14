"""
Standard library-style code for Python.
"""

#-------------------------------------------------------------------------------

def if_none(value, none_value):
    """
    Returns `value`, or `none_value` if it is `None`.
    """
    return none_value if value is None else value


def or_none(fn):
    """
    Decorates `fn` to pass through `None` in its first positional argument.

      >>> def fn(x, y):
      ...     return 2 * x + y
      ...
      >>> fn(3, 4)
      10
      >>> or_none(fn)(None, 4)
      None


    @return
      A wrapper for `fn` that returns `None` without calling `fn` if the first
      positional argument is `None`; otherwise, calls `fn`.
    """
    import functools

    @functools.wraps(fn)
    def wrapped(*args, **kw_args):
        if len(args) > 0 and args[0] is None:
            return None
        else:
            return fn(*args, **kw_args)

    return wrapped


