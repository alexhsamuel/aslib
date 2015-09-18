import sys

# FIXME: __all__

#-------------------------------------------------------------------------------

def tupleize(obj):
    if isinstance(obj, str):
        return (obj, )
    else:
        try:
            return tuple(obj)
        except:
            return (obj, )


def format_call(name, *args, **kw_args):
    try:
        name = name.__name__
    except AttributeError:
        name = str(name)
    args = [ repr(a) for a in args ]
    args.extend( n + "=" + repr(v) for n, v in kw_args.items() )
    return "{}({})".format(name, ", ".join(args))


def format_ctor(obj, *args, **kw_args):
    return format_call(obj.__class__, *args, **kw_args)


def look_up(name, obj):
    """
    Looks up a qualified name.
    """
    result = obj
    for part in name.split("."):
        result = getattr(result, part)
    return result


def import_(name):
    """
    Imports a module.

    @param name
      The fully-qualified module name.
    @rtype
      module
    @raise ImportError
      The name could not be imported.
    """
    __import__(name)
    return sys.modules[name]


def import_look_up(name):
    """
    Looks up a fully qualified name, importing modules as needed.

    @param name
      A fully-qualified name.
    @raise NameError
      The name could not be found.
    """
    # Split the name into parts.
    parts = name.split(".")
    # Try to import as much of the name as possible.
    # FIXME: Import left to right as much as possible.
    for i in range(len(parts) + 1, 0, -1):
        module_name = ".".join(parts[: i])
        try:
            obj = import_(module_name)
        except ImportError:
            pass
        else:
            # Imported some.  Resolve the rest with getattr.
            for j in range(i, len(parts)):
                try:
                    obj = getattr(obj, parts[j])
                except AttributeError:
                    raise NameError(name) from None
            else:
                # Found all parts.
                return obj
    else:
        raise NameError(name)
    

