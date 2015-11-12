"""
Tools for working with iterators.
"""

#-------------------------------------------------------------------------------

from   collections import deque

from   .recipes import *  # also imports * from itertools

#-------------------------------------------------------------------------------

def ntimes(value, times):
    """
    Generates `times` copies of `value`.
    """
    for _ in range(times):
        yield value


def first(iterable):
    """
    Generates `(first, item)` for each item in `iterable`, where `first` is 
    true for the first time and false for subsequent items.
    """
    i = iter(iterable)
    yield True, next(i)
    while True:
        yield False, next(i)


#-------------------------------------------------------------------------------

class PeekIter:
    """
    Iterator wrapper that supports arbitrary push back and peek ahead.
    """

    def __init__(self, iterable):
        self.__iter = iter(iterable)
        self.__items = deque()


    def __iter__(self):
        # FIXME: Sloppy.
        return self


    def __next__(self):
        try:
            return self.__items.popleft()
        except IndexError:
            return next(self.__iter)


    @property
    def is_done(self):
        """
        True if the iterator is exhausted.
        """
        if len(self.__items) > 0:
            return False
        else:
            try:
                self.__items.append(next(self._iter))
            except StopIteration:
                return True
            else:
                return False


    def push(self, item):
        """
        Pushes an `item` to the front of the iterator so that it is next.
        """
        self.__items.appendleft(item)


    def peek(self, ahead=0):
        """
        Returns a future item from the iterator, without advancing.

        @param ahead
          The number of items to peek ahead; 0 for the next item.
        """
        while len(self.__items) <= ahead:
            self.__items.append(next(self.__iter))
        return self.__items[ahead]



