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
    2: AztecTableEntry("A", "a", "^A", "\n\r", "0"),
    3: AztecTableEntry("B", "b", "^B", ". ", "1"),
    4: AztecTableEntry("C", "c", "^C", ", ", "2"),
    5: AztecTableEntry("D", "d", "^D", ": ", "3"),
    6: AztecTableEntry("E", "e", "^E", "!", "4"),
    7: AztecTableEntry("F", "f", "^F", '"', "5"),
    8: AztecTableEntry("G", "g", "^G", "#", "6"),
    9: AztecTableEntry("H", "h", "^H", "$", "7"),
    10: AztecTableEntry("I", "i", "^I", "%", "8"),
    11: AztecTableEntry("J", "j", "^J", "&", "9"),
    12: AztecTableEntry("K", "k", "^K", "'", ","),
    13: AztecTableEntry("L", "l", "^L", "(", "."),
    14: AztecTableEntry("M", "m", "^M", ")", "U/L"),
    15: AztecTableEntry("N", "n", "^[", "*", "U/S"),
    16: AztecTableEntry("O", "o", "^\\", "+"),
    17: AztecTableEntry("P", "p", "^]", ","),
    18: AztecTableEntry("Q", "q", "^^", "-"),
    19: AztecTableEntry("R", "r", "^_", "."),
    20: AztecTableEntry("S", "s", "@", "/"),
    21: AztecTableEntry("T", "t", "\\", ":"),
    22: AztecTableEntry("U", "u", "^", ";"),
    23: AztecTableEntry("V", "v", "_", "<"),
    24: AztecTableEntry("W", "w", "`", "="),
    25: AztecTableEntry("X", "x", "|", ">"),
    26: AztecTableEntry("Y", "y", "~", "?"),
    27: AztecTableEntry("Z", "z", "^?", "["),
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
                print(line, i, start_point[0], end_point[0]+1, start_point[1] - i + apply_to_borns, matrix[start_point[0]:end_point[0]+1, start_point[1] - i + apply_to_borns])
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
    print(bitmap)
    decode_codewords(bitmap, data_words, layers)


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
