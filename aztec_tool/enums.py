"""aztec_tool.enums
==================

Enum helpers used across *aztec-tool*.

The module defines three small enumerations:

* **ReadingDirection** - internal state-machine for the data spiral walk
* **AztecType** - compact vs full symbols
* **AztecTableType** - character tables used by the high-level decoder
"""

from enum import Enum

__all__ = ["ReadingDirection", "AztecType", "AztecTableType"]


class ReadingDirection(Enum):
    """Direction in which the spiral is currently read.

    Values
    ------
    BOTTOM : 0
        We are reading vertically from the top to the bottom.
    RIGHT : 1
        We are reading a horizontal strip from the left to the right on the **right** side.
    TOP : 2
        We are reading vertically from the bottom to the top.
    LEFT : 3
        We are reading a horizontal strip from the right to the left on the **left** side.

    Notes
    -----
    The spiral starts at the upper left corner and starts reading in the BOTTOM direction.
    """

    BOTTOM = 0
    RIGHT = 1
    TOP = 2
    LEFT = 3


class AztecType(Enum):
    """Physical Aztec symbol variant.

    COMPACT
        Up to 2 data layers, no reference grid, smaller bull’s-eye.
    FULL
        3-32 data layers, reference grid every 16 cells.
    """

    COMPACT = 0
    FULL = 1


class AztecTableType(Enum):
    """Character tables, available at https://en.wikipedia.org/wiki/Aztec_Code.

    The decoder switches between these tables using shift/latch
    instructions embedded in the bit-stream.

    UPPER
        Upper-case letters **A-Z** plus space.
    LOWER
        Lower-case letters **a-z** plus space.
    MIXED
        Control codes and miscellaneous chars.
    PUNCT
        Punctuation set.
    DIGIT
        Numerals **0-9**, space, and shift/latch tokens.
    """

    UPPER = 0
    LOWER = 1
    MIXED = 2
    PUNCT = 3
    DIGIT = 4
