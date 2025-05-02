from functools import cached_property
import numpy as np
import reedsolo

from .detection import AztecType

__all__ = ["ModeReader"]


class ModeReader:
    def __init__(self, matrix: np.ndarray, bounds: tuple, aztec_type: AztecType, auto_correct: bool = True):
        self.matrix = matrix
        self.bounds = bounds
        self.aztec_type = aztec_type
        self.auto_correct = auto_correct

    def _read_mode_bits(self) -> list:
        bits = []
        tl_y, tl_x, br_y, br_x = self.bounds
        tr_y, tr_x, bl_y, bl_x = tl_y, br_x, br_y, tl_x

        mode_on_top_start = tl_y - 1, tl_x + 1
        mode_on_top_end = tr_y - 1, tr_x - 1

        for x in range(mode_on_top_start[1], mode_on_top_end[1] + 1):   # top row
            if self.aztec_type == AztecType.FULL and x == (mode_on_top_start[1] + 5):
                continue
            bits.append(self.matrix[mode_on_top_start[0], x])

        mode_on_right_start = tr_y + 1, tr_x + 1
        mode_on_right_end = br_y - 1, br_x + 1

        for y in range(mode_on_right_start[0], mode_on_right_end[0] + 1):  # right column
            if self.aztec_type == AztecType.FULL and y == (mode_on_right_start[0] + 5):
                continue
            bits.append(self.matrix[y, mode_on_right_start[1]])

        mode_on_bottom_start = br_y + 1, br_x - 1
        mode_on_bottom_end = bl_y + 1, bl_x + 1

        for x in range(mode_on_bottom_start[1], mode_on_bottom_end[1] - 1, -1):  # bottom row
            if self.aztec_type == AztecType.FULL and x == (mode_on_bottom_start[1] - 5):
                continue
            bits.append(self.matrix[mode_on_bottom_start[0], x])

        mode_on_left_start = bl_y - 1, bl_x - 1
        mode_on_left_end = tl_y + 1, tl_x - 1

        for y in range(mode_on_left_start[0], mode_on_left_end[0] - 1, -1):  # left column
            if self.aztec_type == AztecType.FULL and y == (mode_on_left_start[0] - 5):
                continue
            bits.append(self.matrix[y, mode_on_left_start[1]])

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
        symbols = [int(''.join(map(str, self.mode_bitmap[i:i+4])), 2) for i in range(0, len(self.mode_bitmap), 4)]
        
        corrected_data = rs.decode(bytearray(symbols))
        _, full_codeword, _ = corrected_data

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
            layers_bits = bits[:2]
            data_words_bits = bits[2:8]
            ecc_bits = bits[8:]
        else:
            layers_bits = bits[0:5]
            data_words_bits = bits[5:16]
            ecc_bits = bits[16:]

        layers = int(''.join(map(str, layers_bits)), 2) + 1
        data_words = int(''.join(map(str, data_words_bits)), 2) + 1

        return {
            "layers": layers,
            "data_words": data_words,
            "ecc_bits": ecc_bits
        }
    
    @cached_property
    def mode_fields(self) -> dict:
        return self._extract_fields()
