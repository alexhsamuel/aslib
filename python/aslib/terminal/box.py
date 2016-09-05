"""
Code to draw boxes and frames with Unicode box-drawing characters.

See also https://github.com/Robpol86/terminaltables.
"""

#-------------------------------------------------------------------------------

from   .. import py

#-------------------------------------------------------------------------------

# Directions.  We use the CSS ordering convention.
TOP     = 0
RIGHT   = 1
BOTTOM  = 2
LEFT    = 3

# Box drawing line types.
EMPTY   = 0
SINGLE  = 1
DOUBLE  = 2
HEAVY   = 3

# Unicode version 9 box drawing characters.
#
# Encodes box drawing characters as a flattened four-dimensional array whose
# dimensions are the four directions and indexes are the four line types.  Many
# combinations are missing; the value is then `None`.
#
# The comments encode the four line types in CSS direction order.
#
# See https://en.wikipedia.org/wiki/Box-drawing_character.

_BOX_CHARS = (
    " "       , #     
    "\u2574"  , #    -
    None      , #    =
    "\u2578"  , #    *
    "\u2577"  , #   - 
    "\u2510"  , #   --
    "\u2555"  , #   -=
    "\u2511"  , #   -*
    None      , #   = 
    "\u2556"  , #   =-
    "\u2557"  , #   ==
    None      , #   =*
    "\u257b"  , #   * 
    "\u2512"  , #   *-
    None      , #   *=
    "\u2513"  , #   **
    "\u2576"  , #  -  
    "\u2500"  , #  - -
    None      , #  - =
    "\u257e"  , #  - *
    "\u250c"  , #  -- 
    "\u252c"  , #  ---
    None      , #  --=
    "\u252d"  , #  --*
    "\u2553"  , #  -= 
    "\u2565"  , #  -=-
    None      , #  -==
    None      , #  -=*
    "\u250e"  , #  -* 
    "\u2530"  , #  -*-
    None      , #  -*=
    "\u2531"  , #  -**
    None      , #  =  
    None      , #  = -
    "\u2550"  , #  = =
    None      , #  = *
    "\u2552"  , #  =- 
    None      , #  =--
    "\u2564"  , #  =-=
    None      , #  =-*
    "\u2554"  , #  == 
    None      , #  ==-
    "\u2566"  , #  ===
    None      , #  ==*
    None      , #  =* 
    None      , #  =*-
    None      , #  =*=
    None      , #  =**
    "\u257a"  , #  *  
    "\u257c"  , #  * -
    None      , #  * =
    "\u2501"  , #  * *
    "\u250d"  , #  *- 
    "\u252e"  , #  *--
    None      , #  *-=
    "\u252f"  , #  *-*
    None      , #  *= 
    None      , #  *=-
    None      , #  *==
    None      , #  *=*
    "\u250f"  , #  ** 
    "\u2533"  , #  **-
    None      , #  **=
    "\u2534"  , #  ***
    "\u2575"  , # -   
    "\u2518"  , # -  -
    "\u255b"  , # -  =
    "\u2519"  , # -  *
    "\u2502"  , # - - 
    "\u2524"  , # - --
    "\u2561"  , # - -=
    "\u2525"  , # - -*
    None      , # - = 
    None      , # - =-
    None      , # - ==
    None      , # - =*
    "\u257d"  , # - * 
    "\u2527"  , # - *-
    None      , # - *=
    "\u252a"  , # - **
    "\u2514"  , # --  
    "\u2534"  , # -- -
    None      , # -- =
    "\u2535"  , # -- *
    "\u251c"  , # --- 
    "\u253c"  , # ----
    None      , # ---=
    "\u253d"  , # ---*
    None      , # --= 
    None      , # --=-
    None      , # --==
    None      , # --=*
    "\u251f"  , # --* 
    "\u2541"  , # --*-
    None      , # --*=
    "\u2545"  , # --**
    "\u2558"  , # -=  
    None      , # -= -
    "\u2567"  , # -= =
    None      , # -= *
    "\u255e"  , # -=- 
    None      , # -=--
    "\u256a"  , # -=-=
    None      , # -=-*
    None      , # -== 
    None      , # -==-
    None      , # -===
    None      , # -==*
    None      , # -=* 
    None      , # -=*-
    None      , # -=*=
    None      , # -=**
    "\u2515"  , # -*  
    "\u2536"  , # -* -
    None      , # -* =
    "\u2537"  , # -* *
    "\u251d"  , # -*- 
    "\u253e"  , # -*--
    None      , # -*-=
    "\u253f"  , # -*-*
    None      , # -*= 
    None      , # -*=-
    None      , # -*==
    None      , # -*=*
    "\u2522"  , # -** 
    "\u2546"  , # -**-
    None      , # -**=
    "\u2548"  , # -***
    None      , # =   
    "\u255c"  , # =  -
    "\u255d"  , # =  =
    None      , # =  *
    None      , # = - 
    None      , # = --
    None      , # = -=
    None      , # = -*
    "\u2551"  , # = = 
    "\u2562"  , # = =-
    "\u2563"  , # = ==
    None      , # = =*
    None      , # = * 
    None      , # = *-
    None      , # = *=
    None      , # = **
    "\u2559"  , # =-  
    "\u2568"  , # =- -
    None      , # =- =
    None      , # =- *
    None      , # =-- 
    None      , # =---
    None      , # =--=
    None      , # =--*
    "\u255f"  , # =-= 
    "\u256b"  , # =-=-
    None      , # =-==
    None      , # =-=*
    None      , # =-* 
    None      , # =-*-
    None      , # =-*=
    None      , # =-**
    "\u255a"  , # ==  
    None      , # == -
    "\u2569"  , # == =
    None      , # == *
    None      , # ==- 
    None      , # ==--
    None      , # ==-=
    None      , # ==-*
    "\u2560"  , # === 
    None      , # ===-
    "\u256c"  , # ====
    None      , # ===*
    None      , # ==* 
    None      , # ==*-
    None      , # ==*=
    None      , # ==**
    None      , # =*  
    None      , # =* -
    None      , # =* =
    None      , # =* *
    None      , # =*- 
    None      , # =*--
    None      , # =*-=
    None      , # =*-*
    None      , # =*= 
    None      , # =*=-
    None      , # =*==
    None      , # =*=*
    None      , # =** 
    None      , # =**-
    None      , # =**=
    None      , # =***
    "\u2579"  , # *   
    "\u251a"  , # *  -
    None      , # *  =
    "\u251b"  , # *  *
    "\u257f"  , # * - 
    "\u2526"  , # * --
    None      , # * -=
    "\u2529"  , # * -*
    None      , # * = 
    None      , # * =-
    None      , # * ==
    None      , # * =*
    "\u2503"  , # * * 
    "\u2528"  , # * *-
    None      , # * *=
    "\u252b"  , # * **
    "\u2516"  , # *-  
    "\u2538"  , # *- -
    None      , # *- =
    "\u2539"  , # *- *
    "\u251e"  , # *-- 
    "\u2540"  , # *---
    None      , # *--=
    "\u2543"  , # *--*
    None      , # *-= 
    None      , # *-=-
    None      , # *-==
    None      , # *-=*
    "\u2520"  , # *-* 
    "\u2542"  , # *-*-
    None      , # *-*=
    "\u2549"  , # *-**
    None      , # *=  
    None      , # *= -
    None      , # *= =
    None      , # *= *
    None      , # *=- 
    None      , # *=--
    None      , # *=-=
    None      , # *=-*
    None      , # *== 
    None      , # *==-
    None      , # *===
    None      , # *==*
    None      , # *=* 
    None      , # *=*-
    None      , # *=*=
    None      , # *=**
    "\u2517"  , # **  
    "\u253a"  , # ** -
    None      , # ** =
    "\u253b"  , # ** *
    "\u2521"  , # **- 
    "\u2544"  , # **--
    None      , # **-=
    "\u2547"  , # **-*
    None      , # **= 
    None      , # **=-
    None      , # **==
    None      , # **=*
    "\u2523"  , # *** 
    "\u254a"  , # ***-
    None      , # ***=
    "\u254b"  , # ****
)


def get(t, r, b, l):
    """
    Returns a box drawing character.

    `t`, `r`, `b`, `l` are the line types for the four directions.

    @return
      The box drawing character, or an approximate substitute if none is
      available.
    """
    char = _BOX_CHARS[t << 6 | r << 4 | b << 2 | l]
    if char is None:
        # Missing character.  Degrade heavy to single.
        if t == HEAVY: t = SINGLE
        if r == HEAVY: r = SINGLE
        if b == HEAVY: b = SINGLE
        if l == HEAVY: l = SINGLE
        char = _BOX_CHARS[t << 6 | r << 4 | b << 2 | l]
        if char is None:
            # Still missing.  Degrade double to single.
            if t == DOUBLE: t = SINGLE
            if r == DOUBLE: r = SINGLE
            if b == DOUBLE: b = SINGLE
            if l == DOUBLE: l = SINGLE
            char = _BOX_CHARS[t << 6 | r << 4 | b << 2 | l]
    # All permutations of EMPTY and SINGLE are available.
    assert char is not None

    return char


def expand(dirs):
    """
    Expands four directions per CSS convention.

    `dirs` may be a four-element iterable of (top, right, bottom, left), or
    a two-element iterable of (top-bottom, left-right), or a single-element
    iterable or a plan value for all four directions.

    @return
      A `tuple` of top, right, bottom, left.
    """
    try:
        t, r, b, l = dirs
    except (TypeError, ValueError):
        pass
    else:
        return (t, r, b, l)
    try:
        tb, rl = dirs
    except (TypeError, ValueError):
        pass
    else:
        return (tb, rl, tb, rl)
    try:
        trbl, = dirs
    except (TypeError, ValueError):
        trbl = dirs
    return (trbl, trbl, trbl, trbl)


def box(width, height, sides=SINGLE):
    """
    Returns a box.

    @param sides
      The line types for the sides; see `expand()`.
    """
    t, r, b, l = expand(sides)
    row = (
          get(l, 0, l, 0)
        + get(0, 0, 0, 0) * width
        + get(r, 0, r, 0)
    )
    return "\n".join((
            get(0, t, l, 0)
          + get(0, t, 0, t) * width
          + get(0, 0, r, t)
        , *((row, ) * height)
        ,   get(l, b, 0, 0)
          + get(0, b, 0, b) * width
          + get(r, 0, 0, b)
        , ""
    ))


#-------------------------------------------------------------------------------

# FIXME: Not done yet.
class Frame:

    class Column:

        def __init__(self, width, sep=SINGLE, pad=" "):
            if isinstance(pad, str): 
                pad = (pad, pad)
            assert len(pad) == 2

            self.width = width
            self.sep = sep
            self.pad = pad
            

    def __init__(self, cols, edge=SINGLE):
        cols = py.tupleize(cols)
        if not py.is_seq(edge):
            edge = (edge, ) * 4

        self.cols = cols
        self.edge = edge


    @property
    def top(self):
        edge = self.edge[TOP]
        if edge is None:
            return None

        parts = []

        left = self.edge[LEFT]
        if left is not None:
            pass




            
        
