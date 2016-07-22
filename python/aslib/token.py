#-------------------------------------------------------------------------------

class Token:
    """
    A token is an object that exists only to identify something by its presence.

    Each token is a distinct object instance.  Use `is` to check for token
    identity.

    For example::

      END = Token("END")

      def print_word(word):
          if word is END:
              print("All done!")
          else:
              print(word)
      
    """

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


        
UNDEFINED       = Token("UNDEFINED")
NO_DEFAULT      = Token("NO_DEFAULT")
RAISE           = Token("RAISE")

