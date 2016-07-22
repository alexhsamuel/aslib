import pickle

#-------------------------------------------------------------------------------

def is_file(obj):
    # FIXME: This isn't quite right.
    return (
        hasattr(obj, "close") 
        and (hasattr(obj, "read") or hasattr(obj, "write"))
    )


# FIXME: Hacky hacky.
def _maybe_open(obj, write=False, binary=False):
    if is_file(obj):
        return obj
    else:
        mode = ("w" if write else "r") + ("b" if binary else "")
        return open(obj, mode)


def load_pickle(filename):
    with _maybe_open(filename, binary=True) as file:
        return pickle.load(file)


def dump_pickle(obj, filename):
    with _maybe_open(filename, write=True, binary=True) as file:
        pickle.dump(obj, file)


