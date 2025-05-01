import numpy as np
import reedsolo
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict


class AztecTableType(Enum):
    UPPER = "upper"
    LOWER = "lower"
    MIXED = "mixed"
    PUNCT = "punct"
    DIGIT = "digit"

@dataclass
class AztecTableEntry:
    upper: str
    lower: str
    mixed: str
    punct: str
    digit: Optional[str] = None

mapping: Dict[int, AztecTableEntry] = {
    0: AztecTableEntry("P/S", "P/S", "P/S", "FLG(n)", "P/S"),
    1: AztecTableEntry(" ", " ", " ", "\n", " "),
    2: AztecTableEntry("A", "a", chr(1), "\n\r", "0"),
    3: AztecTableEntry("B", "b", chr(2), ". ", "1"),
    4: AztecTableEntry("C", "c", chr(3), ", ", "2"),
    5: AztecTableEntry("D", "d", chr(4), ": ", "3"),
    6: AztecTableEntry("E", "e", chr(5), "!", "4"),
    7: AztecTableEntry("F", "f", chr(6), '"', "5"),
    8: AztecTableEntry("G", "g", chr(7), "#", "6"),
    9: AztecTableEntry("H", "h", chr(8), "$", "7"),
    10: AztecTableEntry("I", "i", chr(9), "%", "8"),
    11: AztecTableEntry("J", "j", chr(10), "&", "9"),
    12: AztecTableEntry("K", "k", chr(11), "'", ","),
    13: AztecTableEntry("L", "l", chr(12), "(", "."),
    14: AztecTableEntry("M", "m", chr(13), ")", "U/L"),
    15: AztecTableEntry("N", "n", chr(27), "*", "U/S"),
    16: AztecTableEntry("O", "o", chr(28), "+"),
    17: AztecTableEntry("P", "p", chr(29), ","),
    18: AztecTableEntry("Q", "q", chr(30), "-"),
    19: AztecTableEntry("R", "r", chr(31), "."),
    20: AztecTableEntry("S", "s", "@", "/"),
    21: AztecTableEntry("T", "t", "\\", ":"),
    22: AztecTableEntry("U", "u", "^", ";"),
    23: AztecTableEntry("V", "v", "_", "<"),
    24: AztecTableEntry("W", "w", "`", "="),
    25: AztecTableEntry("X", "x", "|", ">"),
    26: AztecTableEntry("Y", "y", "~", "?"),
    27: AztecTableEntry("Z", "z", chr(127), "["),
    28: AztecTableEntry("L/L", "U/S", "L/L", "]"),
    29: AztecTableEntry("M/L", "M/L", "U/L", "{"),
    30: AztecTableEntry("D/L", "D/L", "P/L", "}"),
    31: AztecTableEntry("B/S", "B/S", "B/S", "U/L"),
}


class ReadingDirection(Enum):
    BOTTOM = 0
    RIGHT = 1
    TOP = 2
    LEFT = 3


def read_codewords(matrix: np.ndarray, layers: int, data_words: int) -> np.ndarray:
    bitmap = []
    square_size = matrix.shape[0]
    reading_direction = ReadingDirection.BOTTOM
    start_point = (0, 0)
    end_point = (square_size - 1 - 2, 1) # - 2 because the two last lines are readed in a different direction
    apply_to_borns = 0
    
    for line in range(1, layers*4 + 1):
        for i in range(apply_to_borns, square_size - 2 + apply_to_borns):
            if reading_direction == ReadingDirection.BOTTOM:
                bitmap.append(matrix[i, start_point[1]:end_point[1]+1])
            elif reading_direction == ReadingDirection.RIGHT:
                bitmap.append(matrix[start_point[0]:end_point[0]-1:-1, i])
            elif reading_direction == ReadingDirection.TOP:
                bitmap.append(matrix[start_point[0]-i + apply_to_borns, start_point[1]:end_point[1]-1:-1])
            elif reading_direction == ReadingDirection.LEFT:
                bitmap.append(matrix[start_point[0]:end_point[0]+1, start_point[1] - i + apply_to_borns])
        
        if line % 4 == 0:
            square_size -= 4
            apply_to_borns += 2

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
            start_point = end_point
            start_point = (start_point[0] + 1, start_point[1])
            end_point = start_point
            end_point = (end_point[0] + square_size - 1 - 2, end_point[1] + 1)
            reading_direction = ReadingDirection.BOTTOM

    bitmap = np.concatenate(bitmap).astype(int)
    corrected_bitmap = correct_data_bits(bitmap, layers, data_words)
    decode_codewords(corrected_bitmap, data_words, layers)
    return bitmap

PRIM_POLY = {
    6:  0x43,   # x^6 + x^5 + 1
    8:  0x12d,  # x^8 + x^5 + x^3 + x^2 + 1
    10: 0x409,  # x^10 + x^3 + 1
    12: 0x1069  # x^12 + x^6 + x^5 + x^3 + 1
}

def correct_data_bits(bit_stream: np.ndarray,
                      layers: int,
                      data_words: int) -> np.ndarray:

    if   layers <=  2: cw_size = 6
    elif layers <=  8: cw_size = 8
    elif layers <= 22: cw_size = 10
    else:               cw_size = 12

    prim = PRIM_POLY[cw_size]
    nsize = (1 << cw_size) - 1 

    total_words = len(bit_stream) // cw_size

    symbols = [
        int(''.join(str(b) for b in bit_stream[i*cw_size:(i+1)*cw_size]), 2)
        for i in range(total_words)
    ]

    ecc_words = total_words - data_words

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


def decode_codewords(bitmap, data_words, layers):
    if layers <= 2:
       codewords_size = 6
    elif layers <= 8:
       codewords_size = 8
    elif layers <= 22:
       codewords_size = 10
    elif layers <= 32:
       codewords_size = 12

    i = 0
    punct_count = 0
    chars = ""
    current_mode = AztecTableType.UPPER
    previous_mode = AztecTableType.UPPER
    while (i//codewords_size) < data_words:
        if current_mode == AztecTableType.PUNCT and punct_count == 0:
            punct_count = 1
        elif current_mode == AztecTableType.PUNCT and punct_count == 1:
            punct_count = 0
            current_mode = previous_mode
        binary_as_a_slice = bitmap[i:i+5]
        decimal = int("".join(str(x) for x in binary_as_a_slice), 2)
        char = getattr(mapping[decimal], current_mode.name.lower())
        if char == "P/S":
            previous_mode = current_mode
            current_mode = AztecTableType.PUNCT
        elif char == "U/L" or char == "U/S":
            previous_mode = current_mode
            current_mode = AztecTableType.UPPER
        elif char == "D/L":
            previous_mode = current_mode
            current_mode = AztecTableType.DIGIT
        elif char == "M/L":
            previous_mode = current_mode
            current_mode = AztecTableType.MIXED
        elif char == "L/L":
            previous_mode = current_mode
            current_mode = AztecTableType.LOWER
        else:
            chars += char
        i += 5 if current_mode != AztecTableType.DIGIT else 4
    print(chars)
    return chars
