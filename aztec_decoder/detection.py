from functools import cached_property
import numpy as np

from .enums import AztecType

__all__ = ["BullseyeDetector"]


class BullseyeDetector:
    def __init__(self, matrix: np.ndarray):
        self.matrix = matrix
        self.layers = None

    def _detect_bounds(self) -> tuple:
        h, w = self.matrix.shape
        cx, cy = w // 2, h // 2

        layer = 1
        while True:
            color = (layer + 1) % 2

            valid = True
            for y in range(cy - layer, cy + layer + 1):
                if self.matrix[y, cx - layer] != color or self.matrix[y, cx + layer] != color:
                    valid = False
                    break
            for x in range(cx - layer, cx + layer + 1):
                if self.matrix[cy - layer, x] != color or self.matrix[cy + layer, x] != color:
                    valid = False
                    break

            if not valid:
                layer -= 1
                break
            layer += 1

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
            self._detect_bounds() # Ensure bounds are detected before getting aztec type because bounds are used to determine aztec type
        return self._get_aztec_type()
