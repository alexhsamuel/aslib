from   collections import namedtuple
import math

import numpy as np

#-------------------------------------------------------------------------------

Stats = namedtuple(
    "Stats",
    ("num", "min", "pct_5", "mean", "median", "pct_95", "max", "std_dev"))


class Stats(Stats):

    @property
    def mean_std(self):
        precision = max(0, -math.floor(math.log10(self.mean)) + 2)
        return ("{{:.{0}f}} ± {{:.{0}f}}"
            .format(precision)
            .format(self.mean, self.std_dev)
        )


    def __str__(self):
        values = [ format(getattr(self, f), ".6f") for f in self._fields ]
        values[0] = str(self.num)
        return (
            "\n".join(
                "{:8s} {}".format(f, v) 
                for f, v in zip(self._fields, values) ) 
            + "\n"
        )
    

def get_stats(values, *, ddof=1):
    if hasattr(values, "__len__"):
        values = np.array(values, dtype="double")
    else:
        values = np.fromiter(values, dtype="double")

    values.sort()
    percentile = lambda p: values[int(round((len(values) - 1) * p))]

    return Stats(
        len(values),
        values[0],
        percentile(0.05),
        values.mean(),
        percentile(0.50),
        percentile(0.95),
        values[-1],
        values.std(ddof=ddof),
    )


