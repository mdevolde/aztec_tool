"""Aztec Code orientation manager to align the symbol."""

from __future__ import annotations

from functools import cached_property
from typing import List, Tuple

import numpy as np
import numpy.typing as npt

from .exceptions import InvalidParameterError, OrientationError

__all__ = ["OrientationManager"]


class OrientationManager:
    """Rotate the module matrix until the four orientation markers are aligned.

    Aztec codes embed a distinctive 3 bits *orientation pattern* at each
    corner of the bull's-eye. In the canonical (upright) position, those
    four mini-matrices must match the reference layout stored in
    :attr:`_TARGET`::

        TL         TR         BR         BL
        1 1        0 1          1        0
        1            1        0 0        0 0

    A clockwise 90° rotation is performed until the patterns fit. After
    four unsuccessful attempts the symbol is considered corrupt.

    :param matrix: 0/1 matrix of the Aztec symbol (must be square and of odd size).
    :type matrix: npt.NDArray[np.int_]
    :param bounds: Bull's-eye bounding box returned by :class:`~aztec_tool.detection.BullseyeDetector` -
        ``(top, left, bottom, right)``.
    :type bounds: tuple[int, int, int, int]

    :raises InvalidParameterError: *matrix* not square/odd, or *bounds* malformed/outside matrix.
    :raises OrientationError: Index error while reading patterns or alignment failed after
        four rotations.
    """

    def __init__(
        self, matrix: npt.NDArray[np.int_], bounds: Tuple[int, int, int, int]
    ) -> None:
        if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
            raise InvalidParameterError("matrix must be a square 2-D ndarray")
        if matrix.shape[0] % 2 == 0:
            raise InvalidParameterError("Aztec symbol side length must be odd")
        if len(bounds) != 4:
            raise InvalidParameterError("bounds must be a 4-tuple")
        self.matrix = matrix
        self.bounds = bounds

    def _read_patterns(self) -> List[List[int]]:
        """Read the four orientation patterns from the matrix.

        Orientation patterns are 3x3 matrices located at the corners of
        the bull's-eye.

        :return: The four orientation patterns read TL→TR→BR→BL.
        :rtype: List[List[int]]
        """
        tl_y, tl_x, br_y, br_x = self.bounds
        tr_y, tr_x, bl_y, bl_x = tl_y, br_x, br_y, tl_x

        try:
            tl_orientation = [
                int(self.matrix[tl_y, tl_x - 1]),
                int(self.matrix[tl_y - 1, tl_x - 1]),
                int(self.matrix[tl_y - 1, tl_x]),
            ]
            tr_orientation = [
                int(self.matrix[tr_y - 1, tr_x]),
                int(self.matrix[tr_y - 1, tr_x + 1]),
                int(self.matrix[tr_y, tr_x + 1]),
            ]
            br_orientation = [
                int(self.matrix[br_y, br_x + 1]),
                int(self.matrix[br_y + 1, br_x + 1]),
                int(self.matrix[br_y + 1, br_x]),
            ]
            bl_orientation = [
                int(self.matrix[bl_y + 1, bl_x]),
                int(self.matrix[bl_y + 1, bl_x - 1]),
                int(self.matrix[bl_y, bl_x - 1]),
            ]
        except IndexError as exc:
            raise OrientationError("orientation pattern indices out of range") from exc

        return [tl_orientation, tr_orientation, br_orientation, bl_orientation]

    @cached_property
    def patterns(self) -> List[List[int]]:
        """The four 3-bit orientation patterns read TL→TR→BR→BL (lazy)."""
        return self._read_patterns()

    def rotate_if_needed(self) -> npt.NDArray[np.int_]:
        """Rotate *matrix* clockwise until orientation markers match.

        :return: The (possibly rotated) matrix now in canonical orientation.
        :rtype: npt.NDArray[np.int_]
        :raises OrientationError: Unable to align orientation markers after 4 rotations.
        """
        for _ in range(4):
            if self._need_rotation():
                self.matrix = np.rot90(self.matrix, k=3)
                if "patterns" in self.__dict__:
                    del self.__dict__["patterns"]
            else:
                return self.matrix
        raise OrientationError("unable to align orientation markers after 4 rotations")

    _TARGET = ([1, 1, 1], [0, 1, 1], [1, 0, 0], [0, 0, 0])

    def _need_rotation(self) -> bool:
        return self.patterns != list(self._TARGET)
