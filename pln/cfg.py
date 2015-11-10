from   . import py
from   .itr import chain


NO_DEFAULT = object()

def idem(obj):
    return obj


class Item:

    def __init__(self, ctor=None, default=None, help=None):
        self.__ctor = ctor
        self.__help = help


    def __repr__(self):
        return py.format_ctor(self, self.__ctor, self.__help)


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



def _check_key(key):
    if key.isidentifier():
        return key
    else:
        raise ValueError("invalid key '{}'".format(key))


class Group:

    def __init__(self, items):
        self.__items = items


    def __repr__(self):
        return py.format_ctor(self, self.__items)


    def __setitem__(self, key, item):
        assert isinstance(item, (Item, Group))
        self.__items[__check_key(key)] = item


    def __getitem__(self, key):
        key = _check_key(key)
        try:
            return self.__items[key]
        except KeyError:
            raise KeyError(key) from None


    def update(self, args={}, **kw_args):
        for key, item in args.items():
            self.__setitem__(key, item)
        for key, item in kw_args.items():
            self.__setitem__(key, item)



class item:

    def __init__(self, default=NO_DEFAULT, ctor=idem, help=None):
        self.default = default
        self.ctor = ctor
        self.help = help



def group(args={}, **kw_args):
    items = {}
    vals = {}
    for name, var in chain(args.items(), kw_args.items()):
        if isinstance(var, item):
            items[name] = Item(ctor=var.ctor, help=var.help)
            if var.default is not NO_DEFAULT:
                vals[name] = var.default
        elif isinstance(var, Cfg):
            items[name] = Cfg(var._group, dict(var._vals))
        elif callable(var):
            items[name] = Item(ctor=var)
        else:
            items[name] = Item(ctor=type(var))
            vals[name] = var
    return Cfg(Group(items), vals)



class Cfg:

    def __init__(self, group, vals={}):
        object.__setattr__(self, "_Cfg__group", group)
        object.__setattr__(self, "_Cfg__values", vals)


    def __repr__(self):
        return py.format_ctor(self, self.__group, self.__values)


    @property
    def _group(self):
        return self.__group


    @property
    def _vals(self):
        return self.__values


    def __setattr__(self, name, value):
        try:
            item = self.__group[name]
        except KeyError:
            raise AttributeError(name) from None

        if isinstance(item, Group):
            try:
                cfg = self.__values[name]
            except KeyError:
                cfg = self.__values[name] = Cfg(item)
            cfg(value)

        else:  
            self.__values = item.convert(value)


    def __getattr__(self, name):
        try:
            return self.__values[name]
        except KeyError:
            try:
                self.__group[name]
            except KeyError:
                raise AttributeError("no config " + name) from None
            else:
                raise AttributeError("no value for config " + name) from None


    def __call__(self, args={}, **kw_args):
        for name, value in args.item():
            self.__setattr__(name, value)
        for name, value in kw_args.items():
            self.__setattr__(name, value)
        



DEFAULT_CFG = group(
    bottom=group(
        line                    ="-",
        separator=group(
            between             =" ",
            end                 ="",
            index               ="  ",
            start               ="",
        ),
        show                    =False
    ),
    float=group(
        inf                     ="\u221e",
        max_precision           =8,
        min_precision           =1,
        nan                     ="NaN",
    ),
)


print(DEFAULT_CFG)


c = DEFAULT_CFG
c.bottom(
    line                        = "\u2500",
    separator = dict(
        bottom                  = "\u2500\u2534\u2500",
        end                     = "\u2500\u2518",
        index                   = "\u2500\u2534\u2500",
        start                   = "\u2514\u2500",
    )
)

print(repr(c.bottom.separator))
print(repr(c.bottom.separator.index))

