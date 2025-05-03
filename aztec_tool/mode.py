from __future__ import annotations
from functools import cached_property
import numpy as np
import reedsolo

from .detection import AztecType
from .exceptions import InvalidParameterError, ModeFieldError, ReedSolomonError

__all__ = ["ModeReader"]


class ModeReader:
    def __init__(
        self,
        matrix: np.ndarray,
        bounds: tuple,
        aztec_type: AztecType,
        auto_correct: bool = True,
    ):
        if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
            raise InvalidParameterError("matrix must be a square 2-D ndarray")
        if matrix.shape[0] % 2 == 0:
            raise InvalidParameterError("Aztec symbol side length must be odd")
        if len(bounds) != 4:
            raise InvalidParameterError(
                "bounds must be a 4-tuple (top, left, bottom, right)"
            )
        tl_y, tl_x, br_y, br_x = bounds
        if tl_y < 0 or tl_x < 0 or br_y >= matrix.shape[0] or br_x >= matrix.shape[1]:
            raise InvalidParameterError("bounds outside matrix dimensions")
        self.matrix = matrix
        self.bounds = bounds
        self.aztec_type = aztec_type
        self.auto_correct = auto_correct

    def _read_mode_bits(self) -> list:
        bits = []
        try:
            tl_y, tl_x, br_y, br_x = self.bounds
            tr_y, tr_x, bl_y, bl_x = tl_y, br_x, br_y, tl_x

            mode_on_top_start = tl_y - 1, tl_x + 1
            mode_on_top_end = tr_y - 1, tr_x - 1

            for x in range(mode_on_top_start[1], mode_on_top_end[1] + 1):  # top row
                if self.aztec_type == AztecType.FULL and x == (
                    mode_on_top_start[1] + 5
                ):
                    continue
                bits.append(self.matrix[mode_on_top_start[0], x])

            mode_on_right_start = tr_y + 1, tr_x + 1
            mode_on_right_end = br_y - 1, br_x + 1

            for y in range(
                mode_on_right_start[0], mode_on_right_end[0] + 1
            ):  # right column
                if self.aztec_type == AztecType.FULL and y == (
                    mode_on_right_start[0] + 5
                ):
                    continue
                bits.append(self.matrix[y, mode_on_right_start[1]])

            mode_on_bottom_start = br_y + 1, br_x - 1
            mode_on_bottom_end = bl_y + 1, bl_x + 1

            for x in range(
                mode_on_bottom_start[1], mode_on_bottom_end[1] - 1, -1
            ):  # bottom row
                if self.aztec_type == AztecType.FULL and x == (
                    mode_on_bottom_start[1] - 5
                ):
                    continue
                bits.append(self.matrix[mode_on_bottom_start[0], x])

            mode_on_left_start = bl_y - 1, bl_x - 1
            mode_on_left_end = tl_y + 1, tl_x - 1

            for y in range(
                mode_on_left_start[0], mode_on_left_end[0] - 1, -1
            ):  # left column
                if self.aztec_type == AztecType.FULL and y == (
                    mode_on_left_start[0] - 5
                ):
                    continue
                bits.append(self.matrix[y, mode_on_left_start[1]])
        except IndexError as exc:
            raise ModeFieldError(
                "mode message indices out of range - check bounds"
            ) from exc

        return [int(b) for b in bits]

    @cached_property
    def mode_bitmap(self) -> np.ndarray:
        return self._read_mode_bits()

    def _correct(self) -> list:
        if self.aztec_type == AztecType.COMPACT:
            nsym = 5
        else:
            nsym = 6
        rs = reedsolo.RSCodec(nsym=nsym, nsize=15, fcr=1, generator=2, c_exp=4)
        if len(self.mode_bitmap) % 4 != 0:
            raise ModeFieldError("mode bitmap length not multiple of 4")
        symbols = [
            int("".join(map(str, self.mode_bitmap[i : i + 4])), 2)
            for i in range(0, len(self.mode_bitmap), 4)
        ]

        try:
            _, full_codeword, _ = rs.decode(bytearray(symbols))
        except reedsolo.ReedSolomonError as exc:
            raise ReedSolomonError("RS decode failed for mode message") from exc

        corrected_bits = []
        for sym in full_codeword:
            for shift in (3, 2, 1, 0):
                corrected_bits.append((sym >> shift) & 1)

        return corrected_bits

    @cached_property
    def mode_corrected_bits(self) -> list[int]:
        return self._correct()

    def _extract_fields(self) -> dict:
        if self.auto_correct:
            bits = self.mode_corrected_bits
        else:
            bits = self.mode_bitmap
        if self.aztec_type == AztecType.COMPACT:
            if len(bits) < 28:
                raise ModeFieldError("compact mode message must be 28 bits")
            layers_bits = bits[:2]
            data_words_bits = bits[2:8]
            ecc_bits = bits[8:]
        else:
            if len(bits) < 40:
                raise ModeFieldError("full mode message must be 40 bits")
            layers_bits = bits[0:5]
            data_words_bits = bits[5:16]
            ecc_bits = bits[16:]

        layers = int("".join(map(str, layers_bits)), 2) + 1
        data_words = int("".join(map(str, data_words_bits)), 2) + 1

        if not (1 <= layers <= 32):
            raise ModeFieldError(f"layers out of range: {layers}")

        return {"layers": layers, "data_words": data_words, "ecc_bits": ecc_bits}

    @cached_property
    def mode_fields(self) -> dict:
        return self._extract_fields()
