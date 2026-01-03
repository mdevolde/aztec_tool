import pytest

from aztec_tool.detection import BullseyeDetector
from aztec_tool.enums import AztecType
from aztec_tool.exceptions import InvalidParameterError
from aztec_tool.matrix import AztecMatrix


def test_bullseye_detector(compact_img):
    matrix = AztecMatrix(str(compact_img)).matrix
    detector = BullseyeDetector(matrix)
    assert detector.bounds == (7, 7, 15, 15)
    assert detector.aztec_type == AztecType.COMPACT


def test_exception_non_square_matrix(compact_img):
    matrix = AztecMatrix(str(compact_img)).matrix
    # remove a row to make it non-square
    matrix = matrix[:-1, :]

    with pytest.raises(InvalidParameterError):
        BullseyeDetector(matrix)


def test_exception_non_odd_matrix(compact_img):
    matrix = AztecMatrix(str(compact_img)).matrix
    # make it even size
    matrix = matrix[:-1, :-1]

    with pytest.raises(InvalidParameterError):
        BullseyeDetector(matrix)
