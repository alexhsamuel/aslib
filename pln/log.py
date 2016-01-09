import functools
import inspect
import logging

from   . import itr
from   . import py

#-------------------------------------------------------------------------------

# FIXME: Do better.
logging.basicConfig(
    format="%(asctime)s.%(msecs)03d [%(levelname)-7s] %(message)s",
    datefmt="%H:%M:%S")

#-------------------------------------------------------------------------------

def get(name=None):
    """
    Returns the logger for `name`.

    @param name
      The logger name.  If `None`, uses the caller's global `__name__`.
    """
    if name is None:
        frame = inspect.stack()[1][0]
        try:
            name = frame.f_globals["__name__"]
        except KeyError:
            logging.warning("caller has no __name__; using root logger")
            name = None
    return logging.getLogger(name)


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



