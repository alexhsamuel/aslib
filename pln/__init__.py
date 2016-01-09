"""
Standard library-style code for Python.
"""

#-------------------------------------------------------------------------------

def if_none(value, none_value):
    """
    Returns `value`, or `none_value` if it is `None`.
    """
    return none_value if value is None else value


