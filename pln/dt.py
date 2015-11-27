from   datetime import date, time, datetime, timedelta
from   enum import Enum
import re

from   . import itr

#-------------------------------------------------------------------------------

USEC    = timedelta(   0,    0,    1)
MSEC    = timedelta(   0,    0, 1000)
SEC     = timedelta(   0,    1,    0)
MIN     = timedelta(   0,   60,    0)
HOUR    = timedelta(   0, 3600,    0)
DAY     = timedelta(   1,    0,    0)
WEEK    = timedelta(   7,    0,    0)

class Weekday(Enum):

    MON = 0
    TUE = 1
    WED = 2
    THU = 3
    FRI = 4
    SAT = 5
    SUN = 6



DATE_FMT_ISO        = "%Y%m%d"
DATE_FMT_ISO_EXT    = "%Y-%m-%d"

TIME_FMT_ISO        = "%H%M%S"
TIME_FMT_ISO_EXT    = "%H:%M:%S"
TIME_FMT_SHORT      = "%H:%M"

#-------------------------------------------------------------------------------

def ensure_date(obj):
    if isinstance(obj, date):
        return obj
    elif obj == "local-today":
        return datetime.now().date()
    elif obj == "utc-today":
        return datetime.utcnow().date()

    # Check if it is a YYYYMMDD-encoded date.
    try:
        dt = int(obj)
    except (TypeError, ValueError):
        pass
    else:
        if 10000000 < dt < 99999999:
            return date(dt // 10000, dt % 10000 // 100, dt % 100)

    for format in DATE_FMT_ISO_EXT, DATE_FMT_ISO:
        try:
            dt = datetime.strptime(str(obj), format)
        except ValueError:
            continue
        else:
            return dt.date()

    raise TypeError("can't convert to date: {!r}".format(obj))


def ensure_time(obj):
    if isinstance(obj, time):
        return obj
    elif obj == "local-now":
        return datetime.now().time()
    elif obj == "utc-now":
        return datetime.now().time()

    # Check if it is a HHMMSS-encoded time.
    try:
        tm = float(obj)
    except (TypeError, ValueError):
        pass
    else:
        if 0 <= tm < 240000:
            secs = int(tm)
            usecs = round((tm % 1) * 1e6)
            return time(secs // 10000, secs % 10000 // 100, secs % 100, usecs)

    for format in TIME_FMT_ISO_EXT, TIME_FMT_ISO, TIME_FMT_SHORT:
        try:
            dt = datetime.strptime(str(obj), format)
        except ValueError:
            continue
        else:
            return dt.time()

    raise TypeError("can't convert to time: {!r}".format(obj))


def ensure_timedelta(obj):
    if isinstance(obj, timedelta):
        return obj

    raise TypeError("can't convert to timedelta: {!r}".format(obj))


def time_to_ssm(tm):
    """
    Converts `time` to seconds since midnight.
    """
    return (
          3600 * tm.hour 
        +   60 * tm.minute
        +        tm.second 
        + 1e-6 * tm.microsecond
    )


def ssm_to_time(ssm):
    """
    Converts seconds since midnight to `time`.
    """
    secs = int(ssm)
    usecs = round((ssm % 1) * 1e6)
    return time(secs // 3600, secs % 3600 // 60, secs % 60, usecs)


#-------------------------------------------------------------------------------

def date_range(start, end, *, incl=None):
    """
    Generates a range of dates from `start` to `end`.
    """
    start = ensure_date(start)
    end = ensure_date(end)
    return itr.range(start, end, DAY, incl=None)


def time_range(start, end, step, *, incl=None):
    # FIXME: Support wrap around once?
    start   = ensure_time(start)
    end     = ensure_time(end)
    step    = ensure_timedelta(step).total_seconds()
    incl_start, incl_end = itr.ensure_incl(incl)

    # Perform the computation in terms of seconds since midnight.
    ssm = time_to_ssm(start)
    if not incl_start:
        ssm += step
    end_ssm = time_to_ssm(end)

    while ssm < end_ssm or (incl_end and ssm == end_ssm):
        yield ssm_to_time(ssm)
        ssm += step

        
