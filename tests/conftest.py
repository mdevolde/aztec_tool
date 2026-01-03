import pathlib
from pathlib import Path

import pytest

from aztec_tool import AztecDecoder

HERE = pathlib.Path(__file__).parent


@pytest.fixture(scope="session")
def compact_img() -> Path:
    return HERE / "data" / "compact_ok.jpg"


@pytest.fixture(scope="session")
def full_img() -> Path:
    return HERE / "data" / "full_ok.png"


@pytest.fixture(scope="session")
def decoder(compact_img: Path) -> AztecDecoder:
    return AztecDecoder(compact_img)


@pytest.fixture(scope="session")
def full_decoder(full_img: Path) -> AztecDecoder:
    return AztecDecoder(full_img)
