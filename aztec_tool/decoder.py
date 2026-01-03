from __future__ import annotations

from functools import cached_property
from pathlib import Path
from typing import List, Optional, Tuple, Union

import numpy as np

from .codewords import CodewordReader
from .detection import BullseyeDetector
from .enums import AztecType
from .exceptions import AztecDecoderError, InvalidParameterError
from .matrix import AztecMatrix
from .mode import ModeFields, ModeReader
from .orientation import OrientationManager

__all__ = ["AztecDecoder", "MultiAztecDecoder"]


class AztecDecoder:
    """High-level façade that decodes an Aztec symbol from an image in **one line**.

        This class orchestrates all lower-level components:
        :class:`AztecMatrix`, :class:`BullseyeDetector`,
        :class:`OrientationManager`, :class:`ModeReader` and
        :class:`CodewordReader`.

        Parameters
        ----------
        image_path : Optional[Union[str, Path]]
            Path to the image file **already cropped** to the Aztec symbol.
            If not provided, the *matrix* parameter must be used instead.
        matrix : Optional[np.ndarray]
            Binary matrix (0/1) of the Aztec symbol.  If not provided, the
            *image_path* parameter must be used instead.
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
        image_path: Optional[Union[str, Path]] = None,
        *,
        matrix: Optional[np.ndarray] = None,
        auto_orient: Optional[bool] = True,
        auto_correct: Optional[bool] = True,
        mode_auto_correct: Optional[bool] = True,
    ) -> None:
        if matrix is None and image_path is None:
            raise InvalidParameterError(
                "either 'image_path' or 'matrix' must be provided"
            )

        self._input_matrix: Optional[np.ndarray] = None
        if matrix is not None:
            if not isinstance(matrix, np.ndarray) or matrix.ndim != 2:
                raise InvalidParameterError(
                    "'matrix' must be a 2-D numpy array of 0/1 values"
                )
            self._input_matrix = matrix.astype(int)
            self.image_path = None
        else:
            self.image_path = Path(image_path)  # type: ignore[arg-type]
            if not self.image_path.exists():
                raise InvalidParameterError("image file not found")
            if not self.image_path.is_file():
                raise InvalidParameterError("image_path is not a file")

        self._auto_orient = auto_orient
        self._auto_correct = auto_correct
        self._mode_auto_correct = mode_auto_correct

    @cached_property
    def _raw_matrix(self) -> np.ndarray:
        if self._input_matrix is not None:
            return self._input_matrix
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
    def mode_info(self) -> ModeFields:
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


class MultiAztecDecoder:
    """
    MultiAztecDecoder is a utility class for decoding multiple Aztec codes from an image.

    Parameters
    ----------
        image_path (Union[str, Path]): The path to the image containing Aztec codes.
        _auto_orient (bool): Whether to automatically orient the Aztec codes. Defaults to True.
        _auto_correct (bool): Whether to apply error correction to the decoded data. Defaults to True.
        _mode_auto_correct (bool): Whether to apply mode-specific error correction. Defaults to True.

    Attributes
    ----------
        _matrices (List[np.ndarray]): A list of matrices representing the Aztec codes found in the image.
        decoders (List[AztecDecoder]): A list of AztecDecoder instances for each detected Aztec code.
        messages (List[str]): A list of successfully decoded messages from the Aztec codes.

    Raises
    ------
        InvalidParameterError: If the provided image path does not exist or is not a file.
    """

    def __init__(
        self,
        image_path: Union[str, Path],
        *,
        auto_orient: bool = True,
        auto_correct: bool = True,
        mode_auto_correct: bool = True,
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
    def _matrices(self) -> List[np.ndarray]:
        return AztecMatrix(str(self.image_path), multiple=True).matrices

    @cached_property
    def decoders(self) -> List[AztecDecoder]:
        subs: List[AztecDecoder] = []
        for mat in self._matrices:
            try:
                subs.append(
                    AztecDecoder(
                        matrix=mat,
                        auto_orient=self._auto_orient,
                        auto_correct=self._auto_correct,
                        mode_auto_correct=self._mode_auto_correct,
                    )
                )
            except AztecDecoderError:
                # Ignore errors in the sub-decoders
                continue
        return subs

    @property
    def messages(self) -> List[str]:
        """Decoded messages (only successful ones)."""
        messages = []
        for decoder in self.decoders:
            try:
                messages.append(decoder.decode())
            except AztecDecoderError:
                self.decoders.remove(decoder)
        return messages

    def decode_all(self) -> List[str]:
        """Return the decoded user messages (alias of :pyattr:`messages`)."""
        return self.messages
