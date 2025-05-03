from __future__ import annotations
from functools import cached_property
import numpy as np

from .enums import AztecType
from .exceptions import (
    BullseyeDetectionError,
    InvalidParameterError,
)

__all__ = ["BullseyeDetector"]


class BullseyeDetector:
    def __init__(self, matrix: np.ndarray):
        if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
            raise InvalidParameterError("matrix must be a square 2-D array")
        if matrix.shape[0] % 2 == 0:
            raise InvalidParameterError("Aztec symbol side length must be odd")

        self.matrix = matrix
        self.layers = None

    def _detect_bounds(self) -> tuple:
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
    def bounds(self) -> tuple:
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
