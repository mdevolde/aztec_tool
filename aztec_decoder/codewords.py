from functools import cached_property
import numpy as np
import reedsolo

from .tables import TableManager
from .enums import ReadingDirection, AztecTableType, AztecType

__all__ = ["CodewordReader"]


class CodewordReader:

    PRIM_POLY = {
        6:  0x43,   # x^6 + x^5 + 1
        8:  0x12d,  # x^8 + x^5 + x^3 + x^2 + 1
        10: 0x409,  # x^10 + x^3 + 1
        12: 0x1069  # x^12 + x^6 + x^5 + x^3 + 1
    }
    
    def __init__(self, matrix: np.ndarray, layers: int, data_words: int, aztec_type: AztecType, auto_correct: bool = True):
        self.matrix = matrix
        self.layers = layers
        self.data_words = data_words
        self.aztec_type = aztec_type
        self.auto_correct = auto_correct

    def is_reference(self, r, c):
        centre = self.matrix.shape[0] // 2
        return (r - centre) % 16 == 0 or (c - centre) % 16 == 0

    def _read_bits(self) -> np.ndarray:
        bitmap = []
        square_size = self.matrix.shape[0]
        reading_direction = ReadingDirection.BOTTOM
        start_point = (0, 0)
        end_point = (square_size - 1 - 2, 1) # - 2 because the two last lines are readed in a different direction
        apply_to_borns = 0
        
        for _ in range(1, self.layers*4 + 1):
            for i in range(apply_to_borns, square_size - 2 + apply_to_borns):
                if reading_direction == ReadingDirection.BOTTOM:
                    if not self.is_reference(i, start_point[1]) or self.aztec_type == AztecType.COMPACT:
                        bitmap.append(self.matrix[i, start_point[1]:end_point[1]+1])
                elif reading_direction == ReadingDirection.RIGHT:
                    if not self.is_reference(start_point[0], i) or self.aztec_type == AztecType.COMPACT:
                        bitmap.append(self.matrix[start_point[0]:end_point[0]-1:-1, i])
                elif reading_direction == ReadingDirection.TOP:
                    if not self.is_reference(start_point[0]-i + apply_to_borns, start_point[1])  or self.aztec_type == AztecType.COMPACT:
                        bitmap.append(self.matrix[start_point[0]-i + apply_to_borns, start_point[1]:end_point[1]-1:-1])
                elif reading_direction == ReadingDirection.LEFT:
                    if not self.is_reference(start_point[0], start_point[1] - i + apply_to_borns) or self.aztec_type == AztecType.COMPACT:
                        bitmap.append(self.matrix[start_point[0]:end_point[0]+1, start_point[1] - i + apply_to_borns])

            if reading_direction == ReadingDirection.BOTTOM:
                start_point = (start_point[0] + square_size - 1, start_point[1])
                end_point = start_point
                end_point = (end_point[0] - 1, end_point[1] + square_size - 1 - 2)
                reading_direction = ReadingDirection.RIGHT
            elif reading_direction == ReadingDirection.RIGHT:
                start_point = (start_point[0], start_point[1] + square_size - 1)
                end_point = start_point
                end_point = (end_point[0] - square_size + 1 + 2, end_point[1] - 1)
                reading_direction = ReadingDirection.TOP
            elif reading_direction == ReadingDirection.TOP:
                start_point = (start_point[0] - square_size + 1, start_point[1])
                end_point = start_point
                end_point = (end_point[0] + 1, end_point[1] - square_size + 1 + 2)
                reading_direction = ReadingDirection.LEFT
            elif reading_direction == ReadingDirection.LEFT:
                square_size -= 4
                apply_to_borns += 2
                start_point = end_point
                start_point = (start_point[0] + 1, start_point[1])
                if self.is_reference(start_point[0], start_point[1]):
                    start_point = (start_point[0] + 1, start_point[1] + 1)
                    square_size -= 2
                    apply_to_borns += 1
                end_point = start_point
                end_point = (end_point[0] + square_size - 1 - 2, end_point[1] + 1)
                reading_direction = ReadingDirection.BOTTOM

        bitmap = np.concatenate(bitmap).astype(int)
        return bitmap

    @cached_property
    def bitmap(self) -> np.ndarray:
        return self._read_bits()

    def _correct(self) -> list:
        if   self.layers <=  2: cw_size = 6
        elif self.layers <=  8: cw_size = 8
        elif self.layers <= 22: cw_size = 10
        else:               cw_size = 12

        prim = self.PRIM_POLY[cw_size]
        nsize = (1 << cw_size) - 1 

        total_words = len(self.bitmap) // cw_size

        symbols = [
            int(''.join(str(b) for b in self.bitmap[i*cw_size:(i+1)*cw_size]), 2)
            for i in range(total_words)
        ]

        ecc_words = total_words - self.data_words

        rs = reedsolo.RSCodec(
            nsym=ecc_words,
            nsize=nsize,
            fcr=1,
            generator=2,
            c_exp=cw_size,
            prim=prim,
        )

        decoded = rs.decode(symbols)
        full_codeword = decoded[1]

        corrected_bits = []
        for sym in full_codeword:
            for shift in range(cw_size-1, -1, -1):
                corrected_bits.append((sym >> shift) & 1)

        return corrected_bits
    
    @cached_property
    def corrected_bits(self) -> list[int]:
        return self._correct()
    
    @classmethod
    def _bits_to_int(cls, bits) -> int:
        return int("".join(str(b) for b in bits), 2)

    @classmethod
    def _bits_to_bytes(cls, bits) -> bytes:
        return bytes(
            cls._bits_to_int(bits[i : i + 8]) for i in range(0, len(bits), 8)
        )

    def _remove_stuff_bits(self, bits, cw_size, data_words):
        cleaned = []
        i = 0
        words_seen = 0
        while words_seen < data_words and i < len(bits):
            run = bits[i:i + cw_size]
            if all(b == run[0] for b in run[:-1]):
                cleaned.extend(run[:-1])
                i += cw_size
            else:
                cleaned.extend(run)
                i += cw_size
            words_seen += 1
        start_padding = len(bits) % cw_size
        return cleaned[start_padding:data_words * cw_size]

    def _decode(self) -> str:
        if   self.layers <=  2: codeword_size = 6
        elif self.layers <=  8: codeword_size = 8
        elif self.layers <= 22: codeword_size = 10
        else:               codeword_size = 12

        if self.auto_correct:
            bits = self._remove_stuff_bits(self.corrected_bits, codeword_size, self.data_words)
        else:
            bits = self._remove_stuff_bits(self.bitmap, codeword_size, self.data_words)

        i = 0
        chars = []
        current_mode = AztecTableType.UPPER
        previous_mode = AztecTableType.UPPER
        single_shift    = False
        single_consumed = 0
        while (i // codeword_size) < self.data_words:
            if single_shift and single_consumed == 1:
                current_mode    = previous_mode
                single_shift    = False
                single_consumed = 0

            if current_mode == AztecTableType.DIGIT:
                symbol_bits = bits[i : i + 4]
                i += 4
            else:
                symbol_bits = bits[i : i + 5]
                i += 5

            val  = self._bits_to_int(symbol_bits)
            char = TableManager.get_char(val, current_mode)

            if char == "B/S":
                if len(bits[i : i + 5]) == 0:
                    break
                length = self._bits_to_int(bits[i : i + 5])
                i += 5
                if length == 0:
                    length = self._bits_to_int(bits[i : i + 11]) + 31
                    i += 11

                byte_bits  = bits[i : i + 8 * length]
                i += 8 * length
                chars.append(self._bits_to_bytes(byte_bits).decode("latin-1"))
                continue

            elif char.endswith("/S"):
                previous_mode = current_mode
                current_mode  = TableManager.letter_to_mode(char[0])
                single_shift  = True
                single_consumed = 0
                continue

            elif char.endswith("/L"):
                current_mode = TableManager.letter_to_mode(char[0])
                previous_mode = current_mode
                continue

            if char.startswith("FLG"):
                n = self._bits_to_int(bits[i : i + 3])
                i += 3
                if n == 0:
                    chars.append("\x1D")
                elif 1 <= n <= 6:
                    digits = ""
                    for _ in range(n):
                        d = self._bits_to_int(bits[i : i + 4]); i += 4
                        digits += TableManager.get_char(d, AztecTableType.DIGIT)
                    eci_id = digits.zfill(6)
                    chars.append(f"[ECI:{eci_id}]")
                else:
                    raise ValueError("FLG(7) reserved/illegal")
                continue

            if char in ("U/S", "L/S", "M/S", "P/S", "D/S"):
                continue
            chars.append(char)

            if single_shift:
                single_consumed += 1

        return "".join(chars)
    
    @cached_property
    def decoded_string(self) -> str:
        return self._decode()
