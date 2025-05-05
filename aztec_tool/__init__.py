from __future__ import annotations
import toml
from importlib.metadata import PackageNotFoundError
from pathlib import Path
from typing import Any, Union, Optional

from .decoder import AztecDecoder, MultiAztecDecoder
from .exceptions import (
    AztecDecoderError,
    InvalidParameterError,
    UnsupportedSymbolError,
    BullseyeDetectionError,
    OrientationError,
    ModeFieldError,
    BitReadError,
    BitStuffingError,
    ReedSolomonError,
    SymbolDecodeError,
    StreamTerminationError,
)


__all__: list[str] = [
    # version & helper
    "__version__",
    "decode",
    # Main class
    "AztecDecoder",
    "MultiAztecDecoder",
    # Exceptions
    "AztecDecoderError",
    "InvalidParameterError",
    "UnsupportedSymbolError",
    "BullseyeDetectionError",
    "OrientationError",
    "ModeFieldError",
    "BitReadError",
    "BitStuffingError",
    "ReedSolomonError",
    "SymbolDecodeError",
    "StreamTerminationError",
]

try:
    from importlib.metadata import version as _pkg_version

    __version__: str = _pkg_version(__name__)
except PackageNotFoundError:  # pragma: no cover
    with open(
        "pyproject.toml", "rb"
    ) as f:  # If the package is not installed in the environment, read the version from pyproject.toml
        __version__ = toml.loads(f.read().decode("utf-8"))["project"]["version"]


def decode(
    image_path: Union[str, Path],
    *,
    auto_orient: Optional[bool] = True,
    auto_correct: Optional[bool] = True,
    mode_auto_correct: Optional[bool] = True,
    **kwargs: Any,
) -> str:
    """Decode an Aztec Code image in **one line**.

    This convenience wrapper instantiates :class:`~aztec_tool.decoder.AztecDecoder`
    and returns its :pyattr:`~aztec_tool.decoder.AztecDecoder.message`
    property.  All keyword arguments are forwarded unchanged.

    Parameters
    ----------
    image_path : Union[str, pathlib.Path]
        Path to the cropped image containing the Aztec symbol.
    auto_orient : Optional[bool], default ``True``
        Auto-rotate the matrix to the canonical orientation.
    auto_correct : Optional[bool], default ``True``
        Apply Reed-Solomon correction on the *data* code-words.
    mode_auto_correct : Optional[bool], default ``True``
        Apply Reed-Solomon correction on the *mode* message.
    **kwargs
        Reserved for future options, currently ignored.

    Returns
    -------
    str
        The decoded user message.

    Raises
    ------
    InvalidParameterError
        The image path is invalid or the file cannot be opened.
    BullseyeDetectionError, OrientationError, ReedSolomonError, …
        Any exception propagated by the underlying decoder phases.

    Examples
    --------
    >>> from aztec_tool import decode
    >>> decode("ticket.png")
    'EVENT: Concert\\nROW 12 SEAT 34'
    """
    return AztecDecoder(
        image_path,
        auto_orient=auto_orient,
        auto_correct=auto_correct,
        mode_auto_correct=mode_auto_correct,
    ).decode()
