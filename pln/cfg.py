
class Item:

    def __init__(self, ctor=None, help=None):
        self.__ctor = ctor
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



class Group:

    def __init__(self, **kw_args):
        self.__items = {}
        self.__defaults = {}
        self.update(**kw_args)


    def __check_key(self, key):
        if key.isidentifier():
            return key
        else:
            raise ValueError("key '{}' not a valid identifier".format(key))


    def __setattr__(self, key, item):
        key = self.__check_key(key)
        if isinstance(item, (Item, Group)):
            self.__items[key] = item
        elif callable(item):
            self.__items[key] = Item(ctor=item)
        else:
            self.__items[key] = Item(ctor=type(item))
            self.__defaults[key] = item


    def update(self, args={}, **kw_args):
        for key, item in args.items():
            self.set(key, item)
        for key, item in kw_args.items():
            self.set(key, item)



class Cfg:

    def __init__(self, group):
        self.__group = group
        self.__values = dict( 
        




DEFAULT_GROUP = Group(
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


UNICODE_BOX_CFG = DEFAULT_GROUP.cfg()
UNICODE_BOX_CFG.bottom.line = "\u2500"
UNICODE_BOX_CFG.separator.between = "\u2500\u2534\u2500"

