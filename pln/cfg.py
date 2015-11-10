from   . import py
from   .itr import chain


NO_DEFAULT = object()

def idem(obj):
    return obj


class Var:

    def __init__(self, ctor=idem, default=NO_DEFAULT, help=None):
        self.__ctor = ctor
        self.__default = default
        self.__help = help


    def __repr__(self):
        kw_args = dict(ctor=self.__ctor, help=self.__help)
        try:
            kw_args["default"] = self.__default
        except AttributeError:
            pass
        return py.format_ctor(self, **kw_args)


    def __str__(self):
        result = getattr(self.__ctor, "__name__", str(self.__ctor))
        if self.__default is not NO_DEFAULT:
            result += " default={!r}".format(self.__default)
        if self.__help is not None:
            result += " : " + help
        return result


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



def _check_name(name):
    if name.isidentifier():
        return name
    else:
        raise ValueError("invalid name '{}'".format(name))


class Group:

    def __init__(self, args={}, **kw_args):
        self.vars = {}
        self.update(args, **kw_args)


    def __repr__(self):
        return py.format_ctor(self, self.vars)


    def __setitem__(self, name, value):
        name = _check_name(name)

        if isinstance(value, (Group, Var)):
            self.vars[name] = value
        elif callable(value):
            self.vars[name] = Var(ctor=value)
        else:
            self.vars[name] = Var(ctor=type(value), default=value)


    def __getitem__(self, name):
        name = _check_name(name)
        try:
            return self.vars[name]
        except KeyError:
            raise KeyError(name) from None


    def update(self, args={}, **kw_args):
        for name, var in args.items():
            self.__setitem__(name, var)
        for name, var in kw_args.items():
            self.__setitem__(name, var)



class Cfg:

    def __init__(self, group, args={}):
        vals = {}
        for name, var in group.vars.items():
            if isinstance(var, Group):
                vals[name] = Cfg(var, args.pop(name, {}))
            else:
                try:
                    val = args.pop(name)
                except KeyError:
                    pass
                else:
                    vals[name] = val

        if len(args) > 0:
            raise LookupError("no vars " + ", ".join(args.keys()))

        object.__setattr__(self, "_Cfg__group", group)
        object.__setattr__(self, "_Cfg__vals", vals)


    def __repr__(self):
        return py.format_ctor(self, self.__group, self.__vals)


    def __str__(self):
        return "\n".join(self.__format()) + "\n"


    def __format(self, indent="  "):
        for name, var in sorted(self.__group.vars.items()):
            if isinstance(var, Group):
                cfg = getattr(self, name)
                yield "{}.".format(name)
                for line in cfg.__format(indent):
                    yield indent + line
            else:
                try:
                    val = self.__vals[name]
                except KeyError:
                    val = ""
                else:
                    val = "={!r}".format(val)
                yield "{}{} {}".format(name, val, var)


    def __setattr__(self, name, value):
        try:
            var = self.__group[name]
        except KeyError:
            raise AttributeError(name) from None

        if isinstance(var, Group):
            try:
                cfg = self.__vals[name]
            except KeyError:
                cfg = self.__vals[name] = Cfg(var)
            cfg(value)

        else:  
            self.__vals[name] = var.convert(value)


    def __getattr__(self, name):
        try:
            return self.__vals[name]
        except KeyError:
            try:
                var = self.__group[name]
            except KeyError:
                raise AttributeError("no config " + name) from None
            else:
                raise AttributeError("no value for config " + name) from None


    def __call__(self, args={}, **kw_args):
        for name, value in args.items():
            self.__setattr__(name, value)
        for name, value in kw_args.items():
            self.__setattr__(name, value)
        



DEFAULT_CFG = Group(
    bottom=Group(
        line                    ="-",
        separator=Group(
            between             =" ",
            end                 ="",
            index               ="  ",
            start               ="",
        ),
        show                    =False
    ),
    float=Group(
        inf                     ="\u221e",
        max_precision           =8,
        min_precision           =1,
        nan                     ="NaN",
    ),
)


print(DEFAULT_CFG)
print()
print(Cfg(DEFAULT_CFG))
print()


c = Cfg(DEFAULT_CFG)
c.bottom(
    line                        = "\u2500",
    separator = dict(
        between                 = "\u2500\u2534\u2500",
        end                     = "\u2500\u2518",
        index                   = "\u2500\u2534\u2500",
        start                   = "\u2514\u2500",
    )
)
print(c)
print()

print(repr(c.bottom.separator))
print(repr(c.bottom.separator.index))

