from pathlib import Path

import aztec_tool as az
from aztec_tool import AztecDecoder


def test_decode_func(compact_img: Path) -> None:
    assert az.decode(compact_img) == "You are reading me for Testing !"


def test_decode_message(decoder: AztecDecoder) -> None:
    assert decoder.decode() == "You are reading me for Testing !"


def test_bitmap_size(decoder: AztecDecoder) -> None:
    assert decoder.bitmap.size == 408


def test_matrix_without_auto_orient(compact_img: Path) -> None:
    decoder = az.AztecDecoder(compact_img, auto_orient=False)
    assert decoder.matrix.size == 529 and len(decoder.corrected_bits) == 408


def test_exception_on_bad_path() -> None:
    import pytest

    with pytest.raises(az.InvalidParameterError):
        az.AztecDecoder("no/file/here.png").decode()


def test_exception_non_file_path() -> None:
    import pytest

    with pytest.raises(az.InvalidParameterError):
        az.AztecDecoder("tests").decode()


def test_decode_message_full(full_decoder: AztecDecoder) -> None:
    assert (
        full_decoder.decode()
        == "Data Matrix is a high density 2 dimensional matrix style barcode symbology that can encode up to 3116 characters from the entire 256 byte ASCII character set"
    )
