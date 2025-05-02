from __future__ import annotations
from functools import cached_property
from pathlib import Path

from .matrix      import AztecMatrix
from .detection   import BullseyeDetector
from .orientation import OrientationManager
from .mode        import ModeReader
from .codewords   import CodewordReader
from .enums       import AztecType

__all__ = ["AztecDecoder"]


class AztecDecoder:
    def __init__(self, image_path: str | Path, *, auto_orient: bool = True, auto_correct: bool = True, mode_auto_correct: bool = True) -> None:
        self.image_path  = Path(image_path)
        self._auto_orient = auto_orient
        self._auto_correct = auto_correct
        self._mode_auto_correct = mode_auto_correct

    @cached_property
    def _raw_matrix(self):
        return AztecMatrix(str(self.image_path)).matrix

    @cached_property
    def _bullseye(self) -> BullseyeDetector:
        return BullseyeDetector(self._raw_matrix)

    @cached_property
    def bullseye_bounds(self):
        return self._bullseye.bounds

    @cached_property
    def aztec_type(self) -> AztecType:
        return self._bullseye.aztec_type

    @cached_property
    def matrix(self):
        if not self._auto_orient:
            return self._raw_matrix
        return OrientationManager(
            self._raw_matrix,
            self.bullseye_bounds
        ).rotate_if_needed()

    @cached_property
    def _mode(self):
        bullseye = BullseyeDetector(self.matrix)
        return ModeReader(
            self.matrix,
            bullseye.bounds,
            bullseye.aztec_type,
            self._mode_auto_correct
        )

    @cached_property
    def mode_info(self):
        return self._mode.mode_fields

    @cached_property
    def _codewords(self):
        return CodewordReader(
            self.matrix,
            self.mode_info["layers"],
            self.mode_info["data_words"],
            self.aztec_type,
            self._auto_correct
        )

    @cached_property
    def bitmap(self):
        return self._codewords.bitmap

    @cached_property
    def corrected_bits(self):
        return self._codewords.corrected_bits


    @cached_property
    def message(self) -> str:
        return self._codewords.decoded_string

    def decode(self) -> str:
        return self.message
