import functools
import inspect
import logging

from   . import itr
from   . import py

#-------------------------------------------------------------------------------

# FIXME: Do better.
logging.basicConfig(format="[%(levelname)-7s] %(message)s")

#-------------------------------------------------------------------------------

def log_call(log=logging.debug, *, show_self=False):
    """
    Returns a decorator that logs calls to a method.

    Example::

      @log_call(logger.info)
      def my_function(x, y):
          return 2 * x + y

      >>> my_function(3, 4)
      [INFO] my_function(3, 4)
      10

    @param log
      The logging method to use for logging calls.
    @param show_self
      If false and the decorated function's first argument is named "self",
      the first argument is not included in the log.
    """
    def log_call(fn):
        name = fn.__name__
        remove_self = (
            not show_self 
            and itr.nth(inspect.signature(fn).parameters, 0) == "self"
        )

        @functools.wraps(fn)
        def wrapped(*args, **kw_args):
            log(py.format_call(
                name, *(args[1 :] if remove_self else args), **kw_args))
            return fn(*args, **kw_args)

        return wrapped

    return log_call



