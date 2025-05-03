from __future__ import annotations
from functools import cached_property
import numpy as np
from typing import Tuple, Union

from .enums import AztecType
from .exceptions import (
    BullseyeDetectionError,
    InvalidParameterError,
)

__all__ = ["BullseyeDetector"]


class BullseyeDetector:
    """Locate the *bull’s-eye* and derive layer count & symbol type.

    The bull’s-eye is the central square of alternating black/white rings
    that uniquely identifies an Aztec Code.  Starting from the centre module,
    the detector expands outward ring-by-ring until the pattern breaks.

    Parameters
    ----------
    matrix : numpy.ndarray
        Square binary matrix (0/1) representing the entire Aztec symbol.

    Attributes
    ----------
    bounds : Tuple[int, int, int, int]
        Coordinates ``(top, left, bottom, right)`` of the outer edge of the
        bull’s-eye (lazy - computed on first access).
    layers : Union[int, None]
        Number of data layers (computed during :pyattr:`bounds` evaluation).
    aztec_type : AztecType
        ``AztecType.COMPACT`` when exactly **two** data layers, otherwise
        ``AztecType.FULL`` (lazy - depends on :pyattr:`layers`).

    Raises
    ------
    InvalidParameterError
        *matrix* is not a square 2-D array of **odd** side length.
    BullseyeDetectionError
        The alternating ring pattern cannot be found (symbol damaged or
        crop/threshold error).

    Examples
    --------
    >>> det = BullseyeDetector(my_matrix)
    >>> det.bounds
    (29, 29, 71, 71)
    >>> det.layers
    6
    >>> det.aztec_type
    <AztecType.FULL: 1>
    """

    def __init__(self, matrix: np.ndarray) -> None:
        if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
            raise InvalidParameterError("matrix must be a square 2-D array")
        if matrix.shape[0] % 2 == 0:
            raise InvalidParameterError("Aztec symbol side length must be odd")

        self.matrix = matrix
        self.layers: Union[int, None] = None

    def _detect_bounds(self) -> Tuple[int, int, int, int]:
        h, w = self.matrix.shape
        cx, cy = w // 2, h // 2

        layer = 1
        try:
            while True:
                color = (layer + 1) % 2
                for y in range(cy - layer, cy + layer + 1):
                    if (
                        self.matrix[y, cx - layer] != color
                        or self.matrix[y, cx + layer] != color
                    ):
                        raise StopIteration
                for x in range(cx - layer, cx + layer + 1):
                    if (
                        self.matrix[cy - layer, x] != color
                        or self.matrix[cy + layer, x] != color
                    ):
                        raise StopIteration
                layer += 1
        except StopIteration:
            layer -= 1

        if layer < 1:
            raise BullseyeDetectionError("failed to locate a valid bull’s-eye")

        top_left = (cy - layer, cx - layer)
        bottom_right = (cy + layer, cx + layer)

        self.layers = layer - 2
        return top_left + bottom_right

    @cached_property
    def bounds(self) -> Tuple[int, int, int, int]:
        return self._detect_bounds()

    def _get_aztec_type(self) -> AztecType:
        if self.layers == 2:
            return AztecType.COMPACT
        return AztecType.FULL

    @cached_property
    def aztec_type(self) -> AztecType:
        if self.layers is None:
            self._detect_bounds()  # Ensure bounds are detected before getting aztec type because bounds are used to determine aztec type
        return self._get_aztec_type()
