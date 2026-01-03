"""Aztec Code related enumerations."""

from enum import Enum

__all__ = ["ReadingDirection", "AztecType", "AztecTableType"]


class ReadingDirection(Enum):
    """Direction in which the spiral is currently read.

    The spiral starts at the upper left corner and starts reading in the BOTTOM direction.
    """

    BOTTOM = 0
    """We are reading vertically from the top to the bottom."""

    RIGHT = 1
    """We are reading a horizontal strip from the left to the right on the **right** side."""

    TOP = 2
    """We are reading vertically from the bottom to the top."""

    LEFT = 3
    """We are reading a horizontal strip from the right to the left on the **left** side."""


class AztecType(Enum):
    """Physical Aztec symbol variant."""

    COMPACT = 0
    """Up to 2 data layers, no reference grid, smaller bull's-eye."""

    FULL = 1
    """3-32 data layers, reference grid every 16 cells."""


class AztecTableType(Enum):
    """Character tables, available at https://en.wikipedia.org/wiki/Aztec_Code.

    The decoder switches between these tables using shift/latch
    instructions embedded in the bit-stream.
    """

    UPPER = 0
    """Upper-case letters **A-Z** plus space."""

    LOWER = 1
    """Lower-case letters **a-z** plus space."""

    MIXED = 2
    """Control codes and miscellaneous chars."""

    PUNCT = 3
    """Punctuation set."""

    DIGIT = 4
    """Numerals **0-9**, space, and shift/latch tokens."""
