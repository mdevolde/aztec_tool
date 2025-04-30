import numpy as np
import reedsolo

def read_mode_message(matrix: np.ndarray, bullseye_bounds: tuple) -> list:
    bits = []
    tl_y, tl_x, br_y, br_x = bullseye_bounds
    tr_y, tr_x, bl_y, bl_x = tl_y, br_x, br_y, tl_x

    mode_on_top_start = tl_y - 1, tl_x + 1
    mode_on_top_end = tr_y - 1, tr_x - 1

    for x in range(mode_on_top_start[1], mode_on_top_end[1] + 1):   # top row
        bits.append(matrix[mode_on_top_start[0], x])

    mode_on_right_start = tr_y + 1, tr_x + 1
    mode_on_right_end = br_y - 1, br_x + 1

    for y in range(mode_on_right_start[0], mode_on_right_end[0] + 1):  # right column
        bits.append(matrix[y, mode_on_right_start[1]])

    mode_on_bottom_start = br_y + 1, br_x - 1
    mode_on_bottom_end = bl_y + 1, bl_x + 1

    for x in range(mode_on_bottom_start[1], mode_on_bottom_end[1] - 1, -1):  # bottom row
        bits.append(matrix[mode_on_bottom_start[0], x])

    mode_on_left_start = bl_y - 1, bl_x - 1
    mode_on_left_end = tl_y + 1, tl_x - 1

    for y in range(mode_on_left_start[0], mode_on_left_end[0] - 1, -1):  # left column
        bits.append(matrix[y, mode_on_left_start[1]])

    return [int(b) for b in bits]

def correct_mode(mode_bits: list):
    rs = reedsolo.RSCodec(nsym=5, nsize=15, fcr=1, generator=2, c_exp=4)
    symbols = [int(''.join(map(str, mode_bits[i:i+4])), 2) for i in range(0, 28, 4)]
    
    corrected_data = rs.decode(bytearray(symbols))
    _, full_codeword, _ = corrected_data

    corrected_bits = []
    for sym in full_codeword:
        for shift in (3, 2, 1, 0):
            corrected_bits.append((sym >> shift) & 1)

    return corrected_bits

def extract_mode_fields(mode_bits: list) -> dict:
    if len(mode_bits) != 28:
        raise ValueError("Le mode message doit contenir exactement 28 bits.")

    layers_bits = mode_bits[:2]
    data_words_bits = mode_bits[2:8]
    ecc_bits = mode_bits[8:]

    layers = int(''.join(map(str, layers_bits)), 2) + 1
    data_words = int(''.join(map(str, data_words_bits)), 2) + 1

    return {
        "layers": layers,
        "data_words": data_words,
        "ecc_bits": ecc_bits
    }
