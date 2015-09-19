from   functools import partial
import random

import numpy as np
import pandas as pd

#-------------------------------------------------------------------------------

def normal(mu=0, sigma=1):
    return partial(np.random.normal, mu, sigma)


def uniform(lo=0, hi=1):
    return partial(np.random.uniform, lo, hi)


def uniform_int(lo, hi):
    return partial(np.random.randint, lo, hi)


def word(length, upper=False):
    dtype = "U{}".format(length)
    if upper:
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    else:
        letters = "abcdefghijklmnopqrstuvwxyz"

    # FIXME: Accept random function for length.
    def gen(shape):
        result = np.empty(shape, dtype=dtype)
        flat = result.ravel()
        for i in range(len(flat)):
            flat[i] = "".join( random.choice(letters) for _ in range(length) )
        return result

    return gen


def choice(choices):
    return partial(np.random.choice, choices)


def dataframe(**kw_args):
    def gen(length):
        columns = [ (n, g(length)) for n, g in kw_args.items() ]
        return pd.DataFrame.from_items(sorted(columns))

    return gen


