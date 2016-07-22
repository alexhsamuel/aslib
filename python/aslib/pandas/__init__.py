import pandas as pd

#-------------------------------------------------------------------------------

def get_data_size(df):
    """
    Returns the size in bytes of the data in a dataframe.
    """
    # FIXME: Does this handle category columns correctly?
    # FIXME: Does this handle multiindex correctly?
    return (
          sum( b.values.nbytes for b in df.blocks.values() )
        + index.values.nbytes
    )


