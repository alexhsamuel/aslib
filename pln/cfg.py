

SEPARATOR = "."

NO_DEFAULT = object()


class Group:

    def __init__(self, **kw_args):
        self.__cfg = {}
        self.update(kw_args)


    def resolve(self, key):
        *parts, key = key.split(self.SEPARATOR)
        cfg = self
        for part in parts:
            cfg = cfg / part


    def update(self, args={}, **kw_args):
        args = dict(args)
        args.update(kw_args)
        for key, value in args.items():
            cfg, key = self.resolve(key)



class Item:

    @classmethod
    def ensure(class_, obj):
        if isinstance(obj, class_):
            return obj
        elif callable(obj):
            return class_(ctor=obj)
        else:
            return class_(ctor=type(obj), default=obj)


    def __init__(self, ctor=None, default=NO_DEFAULT, help=None):
        self.__ctor = ctor
        if default is not NO_DEFAULT:
            self.__default = default
        self.__help = help


    @property
    def ctor(self):
        return self.__ctor


    @property
    def default(self):
        try:
            return self.__default
        except AttributeError:
            raise LookupError("no default")


    @property
    def help(self):
        return self.__help


    def convert(self, value):
        return value if self.__ctor is None else self.__ctor(value)



DEFAULT_CFG = Cfg(
    bottom=Cfg(
        line                    ="-",
        separator=Cfg(
            between             =" ",
            end                 ="",
            index               ="  ",
            start               ="",
        ),
        show                    =False
    ),
    float=Cfg(
        inf                     ="\u221e",
        max_precision           =8,
        min_precision           =1,
        nan                     ="NaN",
    ),
)
