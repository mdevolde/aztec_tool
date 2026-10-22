"""A fast, pure-Python Aztec Code reader with auto-orientation and Reed-Solomon correction."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from pathlib import Path
from typing import Any, Optional, Union

import toml

from .decoder import AztecDecoder, MultiAztecDecoder
from .exceptions import (
    AztecDecoderError,
    BitReadError,
    BitStuffingError,
    BullseyeDetectionError,
    InvalidParameterError,
    ModeFieldError,
    OrientationError,
    ReedSolomonError,
    StreamTerminationError,
    SymbolDecodeError,
    UnsupportedSymbolError,
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
except PackageNotFoundError:  # If the package is not installed in the environment, read the version from pyproject.toml
    project_root = Path(__file__).resolve().parent.parent
    pyproject = project_root / "pyproject.toml"
    with open(pyproject, "rb") as f:
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
    and returns its :attr:`~aztec_tool.decoder.AztecDecoder.message`
    property. All keyword arguments are forwarded unchanged.

    :param image_path: Path to the cropped image containing the Aztec symbol.
    :type image_path: Union[str, pathlib.Path]
    :param auto_orient: Auto-rotate the matrix to the canonical orientation, defaults to ``True``
    :type auto_orient: Optional[bool]
    :param auto_correct: Apply Reed-Solomon correction on the *data* code-words, defaults to ``True``
    :type auto_correct: Optional[bool]
    :param mode_auto_correct: Apply Reed-Solomon correction on the *mode* message, defaults to ``True``
    :type mode_auto_correct: Optional[bool]
    :param kwargs: Reserved for future options, currently ignored.
    :type kwargs: Any

    :return: The decoded user message.
    :rtype: str

    :raises InvalidParameterError: The image path is invalid or the file cannot be opened.
    :raises BullseyeDetectionError: Error during bullseye detection.
    :raises OrientationError: Error during orientation detection.
    :raises ReedSolomonError: Error during Reed-Solomon correction.

    **Example:**

    .. code-block:: python

        >>> from aztec_tool import decode
        >>> decode("ticket.png")
        'EVENT: Concert\\\\nROW 12 SEAT 34'
    """
    return AztecDecoder(
        image_path,
        auto_orient=auto_orient,
        auto_correct=auto_correct,
        mode_auto_correct=mode_auto_correct,
    ).decode()
