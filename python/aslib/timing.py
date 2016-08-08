"""
Timing and measurement functionality.
"""

#-------------------------------------------------------------------------------

from   time import perf_counter
import sys

#-------------------------------------------------------------------------------

print_err = lambda *a, **k: print(*a, file=sys.stderr, **k)

def progress(iterable, *, file=sys.stderr, in_place=True, interval=0.2, 
             prefix=""):
    """
    Shows a progress bar while iterating over `iterable`.

    @param in_place
      If true, overwrite each line using a LF ('\r').
    @param interval
      Approximate time in seconds between updates.
    """
    count = 0
    start = perf_counter()
    update = 1

    def get_msg():
        elapsed = perf_counter() - start
        rate = int(count / elapsed)
        msg = "{}{}{} items in {:.1f} sec, {} items/sec  ".format(
            "\r" if in_place else "", prefix, count, elapsed, rate)
        return rate, msg

    end = "" if in_place else "\n"
    for item in iterable:
        yield item
        count += 1
        if count % update == 0:
            rate, msg = get_msg()
            print(msg, end=end, file=file)
            update = max(1, int(rate * interval))

    _, msg = get_msg()
    print(msg, file=file)


#-------------------------------------------------------------------------------

class timing:
    """
    Context manager that measures wall clock time between entry and exit.
    """

    def __init__(self):
        self.__start = self.__end = self.__elapsed = None


    def __enter__(self):
        self.__start = perf_counter()
        return self
        

    def __exit__(self, *exc):
        self.__end = perf_counter()
        self.__elapsed = self.__end - self.__start


    @property
    def start(self):
        return self.__start


    @property
    def end(self):
        return self.__end


    @property
    def elapsed(self):
        return self.__elapsed



def _format_elapsed(elapsed):
    if elapsed < 1e-4:
        return "{:.1f} µs".format(elapsed * 1e+6)
    elif elapsed < 1e-3:
        return "{:.0f} µs".format(elapsed * 1e+6)
    elif elapsed < 1e-1:
        return "{:.1f} ms".format(elapsed * 1e+3)
    elif elapsed < 1:
        return "{:.0f} ms".format(elapsed * 1e+3)
    elif elapsed < 10:
        return "{:.2f} s".format(elapsed)
    elif elapsed < 100:
        return "{:.1f} s".format(elapsed)
    else:
        return "{:.0f} s".format(elapsed)


class timing_log(timing):
    """
    Context manager that logs elapsed wall clock time on exit.
    """

    def __init__(self, name="timer", print=print_err, start=False):
        super().__init__()
        self.__name = name
        self.__print = print
        self.__start = bool(start)


    def __enter__(self):
        if self.__start:
            self.__print("{} starting".format(self.__name))
        super().__enter__()


    def __exit__(self, *exc):
        super().__exit__(*exc)
        self.__print(
            "{} {} in {}".format(
                self.__name, "done" if exc[0] is None else "exception",
                _format_elapsed(self.elapsed)))



#-------------------------------------------------------------------------------

MSEC = 1e-3
USEC = 1e-6
NSEC = 1e-6

def _time(fn, count):
    start = perf_counter()
    for _ in range(count):
        fn()
    return (perf_counter() - start) / count


def _estimate_time(fn, *, min_time=USEC):
    """
    Estimates the time to invoke `fn()`.
    """
    # Number of iterations to time.  
    count = 1
    while True:
        # Time 'count' iterations.
        elapsed = _time(fn, count)
        # Is the total time significant?
        if elapsed > min_time:
            return elapsed / count
        else:
            # No.  Try again with more iterations.
            count *= 10


def _time_it(fn, *, samples=10, count=1):
    """
    Times callable `fn`.

    @param samples
      Number of samples.
    @param count
      Number of invocations per trial, or `None` to choose automatically
      based on `target`.
    @param target
      Approximate total time in seconds for all samples, used to choose `count` 
      automatically.
    @param warm_up
      Number of times to invoke `fn` as a warm-up before timing.
    @return
      Generator of trial times.  Each time is the total time for the trial
      divided by the number of invocations per trial.
    """
    return ( _time(fn, count) for _ in range(samples) )

    
def timer(samples=100, warm_up=1, min_sample_time=10 * USEC):
    """
    Creates a timer.
    """
    def time(fn, *args, **kw_args):
        call = lambda: fn(*args, **kw_args)

        # Do some un-timed warm up calls.
        for _ in range(warm_up):
            call()

        time_estimate = _estimate_time(call)
        count = max(1, round(min_sample_time / time_estimate))

        times = sorted(_time_it(call, samples=samples, count=count))
        time = times[len(times) // 10]

        return {
            "name"      : fn.__name__,
            "time"      : time,
            "samples"   : samples,
            "count"     : count,
        }

    return time


