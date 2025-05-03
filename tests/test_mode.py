import pytest
from aztec_tool.detection import BullseyeDetector
from aztec_tool.mode import ModeReader
from aztec_tool.matrix import AztecMatrix
from aztec_tool.enums import AztecType
from aztec_tool.exceptions import InvalidParameterError


def test_mode_fields(compact_img):
    matrix = AztecMatrix(str(compact_img)).matrix
    bounds = BullseyeDetector(matrix).bounds
    dec = ModeReader(
        matrix=matrix,
        bounds=bounds,
        aztec_type=AztecType.COMPACT,
    )
    fields = dec.mode_fields
    assert (
        fields["layers"] == 3
        and fields["data_words"] == 22
        and len(fields["ecc_bits"]) == 20
    )


def test_mode_without_auto_correct(compact_img):
    matrix = AztecMatrix(str(compact_img)).matrix
    bounds = BullseyeDetector(matrix).bounds
    dec = ModeReader(
        matrix=matrix,
        bounds=bounds,
        aztec_type=AztecType.COMPACT,
        auto_correct=False,
    )
    fields = dec.mode_fields
    assert (
        fields["layers"] == 3
        and fields["data_words"] == 22
        and len(fields["ecc_bits"]) == 20
    )


def test_exception_non_square_matrix(compact_img):
    matrix = AztecMatrix(str(compact_img)).matrix
    bounds = BullseyeDetector(matrix).bounds

    # remove a row to make it non-square
    matrix = matrix[:-1, :]

    with pytest.raises(InvalidParameterError):
        ModeReader(
            matrix=matrix,
            bounds=bounds,
            aztec_type=AztecType.COMPACT,
        )


def test_exception_non_odd_matrix(compact_img):
    matrix = AztecMatrix(str(compact_img)).matrix
    bounds = BullseyeDetector(matrix).bounds

    # make it even size
    matrix = matrix[:-1, :-1]

    with pytest.raises(InvalidParameterError):
        ModeReader(
            matrix=matrix,
            bounds=bounds,
            aztec_type=AztecType.COMPACT,
        )


def test_exception_non_complete_bounds(compact_img):
    matrix = AztecMatrix(str(compact_img)).matrix
    bounds = BullseyeDetector(matrix).bounds

    # remove a row to make it non-square
    bounds = bounds[:-1]

    with pytest.raises(InvalidParameterError):
        ModeReader(
            matrix=matrix,
            bounds=bounds,
            aztec_type=AztecType.COMPACT,
        )


def test_exception_out_of_bounds(compact_img):
    matrix = AztecMatrix(str(compact_img)).matrix
    bounds = BullseyeDetector(matrix).bounds

    # make it even size
    bounds = (-1, bounds[1], bounds[2], bounds[3])

    with pytest.raises(InvalidParameterError):
        ModeReader(
            matrix=matrix,
            bounds=bounds,
            aztec_type=AztecType.COMPACT,
        )
