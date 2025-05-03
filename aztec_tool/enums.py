from enum import Enum

__all__ = ["ReadingDirection", "AztecType", "AztecTableType"]


class ReadingDirection(Enum):
    BOTTOM = 0
    RIGHT = 1
    TOP = 2
    LEFT = 3


class AztecType(Enum):
    COMPACT = 0
    FULL = 1


class AztecTableType(Enum):
    UPPER = 0
    LOWER = 1
    MIXED = 2
    PUNCT = 3
    DIGIT = 4
