from __future__ import annotations
from functools import cached_property
from pathlib import Path
from typing import Union, Optional, Tuple, List, Dict
import numpy as np

from .matrix import AztecMatrix
from .detection import BullseyeDetector
from .orientation import OrientationManager
from .mode import ModeReader
from .codewords import CodewordReader
from .enums import AztecType
from .exceptions import InvalidParameterError

__all__ = ["AztecDecoder"]


class AztecDecoder:
    """High-level façade that decodes an Aztec symbol from an image in **one line**.

        This class orchestrates all lower-level components:
        :class:`AztecMatrix`, :class:`BullseyeDetector`,
        :class:`OrientationManager`, :class:`ModeReader` and
        :class:`CodewordReader`.

        Parameters
        ----------
        image_path : Union[str, Path]
            Path to the image file **already cropped** to the Aztec symbol.
        auto_orient : Optional[bool], default ``True``
            If *True*, the matrix is rotated automatically so that orientation
            patterns match the canonical position (black-white corner pattern).
        auto_correct :  Optional[bool], default ``True``
            Apply Reed-Solomon correction on the *data* code-words before
            high-level decoding.  Disable it for debugging corrupted symbols.
        mode_auto_correct :  Optional[bool], default ``True``
            Apply Reed-Solomon correction on the *mode message* (layers, data
            words, ecc bits).

        Attributes
        ----------
        matrix : numpy.ndarray
            Final, possibly rotated, binary matrix (0/1) of the symbol.
        aztec_type : AztecType
            ``COMPACT`` or ``FULL`` deduced from the bull's-eye.
        bullseye_bounds : Tuple[int, int, int, int]
            Coordinates of the bull's-eye corners.
        mode_info : Dict[str, Union[int, List[int]]]
            Parsed mode fields - keys ``layers``, ``data_words``, ``ecc_bits``.
        bitmap : numpy.ndarray
            Raw bit-stream extracted from the data spiral (before ECC).
        corrected_bits : List[int]
            Bit-stream after Reed-Solomon correction and bit-stuff removal.
        message : str
            Decoded user message (lazy property, evaluated once).

        Raises
        ------
        InvalidParameterError
            *image_path* does not point to an existing file.
        BullseyeDetectionError, OrientationError, BitReadError, etc.
            Any lower-level exception is propagated so the caller can catch
            precisely the failing phase.

        Examples
        --------
        >>> from aztec_tool import AztecDecoder
        >>> dec = AztecDecoder("ticket.png")
        >>> dec.message  # same as dec.decode()
        'EVENT: Concert
    ROW 12 SEAT 34'

        A one-liner helper is also available:

        >>> from aztec_tool import decode
        >>> decode("hello.png")
        'Hello, world!'
    """

    def __init__(
        self,
        image_path: Union[str, Path],
        *,
        auto_orient: Optional[bool] = True,
        auto_correct: Optional[bool] = True,
        mode_auto_correct: Optional[bool] = True,
    ) -> None:
        self.image_path = Path(image_path)
        if not self.image_path.exists():
            raise InvalidParameterError("image file not found")
        if not self.image_path.is_file():
            raise InvalidParameterError("image_path is not a file")
        self._auto_orient = auto_orient
        self._auto_correct = auto_correct
        self._mode_auto_correct = mode_auto_correct

    @cached_property
    def _raw_matrix(self) -> np.ndarray:
        return AztecMatrix(str(self.image_path)).matrix

    @cached_property
    def _bullseye(self) -> BullseyeDetector:
        return BullseyeDetector(self._raw_matrix)

    @cached_property
    def bullseye_bounds(self) -> Tuple[int, int, int, int]:
        return self._bullseye.bounds

    @cached_property
    def aztec_type(self) -> AztecType:
        return self._bullseye.aztec_type

    @cached_property
    def matrix(self) -> np.ndarray:
        if not self._auto_orient:
            return self._raw_matrix
        return OrientationManager(
            self._raw_matrix, self.bullseye_bounds
        ).rotate_if_needed()

    @cached_property
    def _mode(self) -> ModeReader:
        bullseye = BullseyeDetector(self.matrix)
        return ModeReader(
            self.matrix, bullseye.bounds, bullseye.aztec_type, self._mode_auto_correct
        )

    @cached_property
    def mode_info(self) -> Dict[str, Union[int, List[int]]]:
        return self._mode.mode_fields

    @cached_property
    def _codewords(self) -> CodewordReader:
        return CodewordReader(
            self.matrix,
            self.mode_info["layers"],
            self.mode_info["data_words"],
            self.aztec_type,
            self._auto_correct,
        )

    @cached_property
    def bitmap(self) -> np.ndarray:
        return self._codewords.bitmap

    @cached_property
    def corrected_bits(self) -> List[int]:
        return self._codewords.corrected_bits

    @cached_property
    def message(self) -> str:
        return self._codewords.decoded_string

    def decode(self) -> str:
        """Return the decoded user message (alias of :pyattr:`message`)."""
        return self.message
