from .py import format_ctor

#-------------------------------------------------------------------------------

class Token:

    def __init__(self, name):
        self.__name = name


    def __str__(self):
        return self.__name


    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, self.__name)


    def __hash__(self):
        return hash(self.__name)


    def __eq__(self, other):
        return other is self


    def __ne__(self, other):
        return other is not self


    def __lt__(self, other):
        return NotImplemented


    __gt__ = __le__ = __ge__ = __lt__


        
UNDEFINED = Token("UNDEFINED")

#-------------------------------------------------------------------------------

class BaseStruct:

    def __init__(self, **kw_args):
        for name in self.__slots__:
            super(BaseStruct, self).__setattr__(name, kw_args.pop(name, None))
        if len(kw_args) > 0:
            raise AttributeError("no attributes {}".format(", ".join(kw_args)))
        

    def __repr__(self):
        return format_ctor(
            self, **{ n: getattr(self, n) for n in self.__slots__ })


    def __setattr__(self, name, value):
        raise RuntimeError("read-only struct")


    def copy(self, **kw_args):
        for name in self.__slots__:
            kw_args.setdefault(name, getattr(self, name))
        return self.__class__(**kw_args)



def Struct(*names, name="Struct"):
    names = tuple( str(n) for n in names )
    return type(name, (BaseStruct, ), {"__slots__": names})


