from   collections import namedtuple
import math

import numpy as np

#-------------------------------------------------------------------------------

Stats = namedtuple(
    "Stats",
    ("num", "min", "mean", "median", "max", "std_dev"))


class Stats(Stats):

    @property
    def mean_std(self):
        precision = max(0, -math.floor(math.log10(self.mean)) + 2)
        return ("{{:.{0}f}} ± {{:.{0}f}}"
            .format(precision)
            .format(self.mean, self.std_dev)
        )

    

def get_stats(values, *, ddof=1):
    if hasattr(values, "__len__"):
        values = np.array(values, dtype="double")
    else:
        values = np.fromiter(values, dtype="double")
    return Stats(
        len(values),
        values.min(),
        values.mean(),
        np.median(values),
        values.max(),
        values.std(ddof=ddof),
    )


