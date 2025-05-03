from __future__ import annotations
import toml
from importlib.metadata import version, PackageNotFoundError
from pathlib import Path
from typing import Any

from .decoder    import AztecDecoder
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
except PackageNotFoundError: # pragma: no cover
    with open("pyproject.toml", "rb") as f: # If the package is not installed in the environment, read the version from pyproject.toml
        __version__ = toml.loads(f.read().decode('utf-8'))["project"]["version"]

def decode(
    image_path: str | Path,
    *,
    auto_orient: bool = True,
    auto_correct: bool = True,
    mode_auto_correct: bool = True,
    **kwargs: Any,
) -> str:
    return AztecDecoder(
        image_path,
        auto_orient=auto_orient,
        auto_correct=auto_correct,
        mode_auto_correct=mode_auto_correct,
    ).decode()
