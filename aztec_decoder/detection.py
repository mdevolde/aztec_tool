import numpy as np

def detect_bullseye_bounds(matrix: np.ndarray) -> tuple:
    h, w = matrix.shape
    cx, cy = w // 2, h // 2

    layer = 1
    while True:
        color = (layer + 1) % 2

        valid = True
        for y in range(cy - layer, cy + layer + 1):
            if matrix[y, cx - layer] != color or matrix[y, cx + layer] != color:
                valid = False
                break
        for x in range(cx - layer, cx + layer + 1):
            if matrix[cy - layer, x] != color or matrix[cy + layer, x] != color:
                valid = False
                break

        if not valid:
            layer -= 1
            break
        layer += 1

    top_left = (cy - layer, cx - layer)
    bottom_right = (cy + layer, cx + layer)
    return top_left + bottom_right

def read_orientation_patterns(matrix: np.ndarray, bullseye_bounds: tuple) -> list:
    tl_y, tl_x, br_y, br_x = bullseye_bounds
    tr_y, tr_x, bl_y, bl_x = tl_y, br_x, br_y, tl_x
    
    tl_orientation = []
    tl_orientation.append(int(matrix[tl_y, tl_x-1]))
    tl_orientation.append(int(matrix[tl_y-1, tl_x-1]))
    tl_orientation.append(int(matrix[tl_y-1, tl_x]))

    tr_orientation = []
    tr_orientation.append(int(matrix[tr_y-1, tr_x]))
    tr_orientation.append(int(matrix[tr_y-1, tr_x+1]))
    tr_orientation.append(int(matrix[tr_y, tr_x+1]))
    
    br_orientation = []
    br_orientation.append(int(matrix[br_y, br_x+1]))
    br_orientation.append(int(matrix[br_y+1, br_x+1]))
    br_orientation.append(int(matrix[br_y+1, br_x]))
    
    bl_orientation = []
    bl_orientation.append(int(matrix[bl_y+1, bl_x]))
    bl_orientation.append(int(matrix[bl_y+1, bl_x-1]))
    bl_orientation.append(int(matrix[bl_y, bl_x-1]))
    
    return [tl_orientation, tr_orientation, br_orientation, bl_orientation]

def need_rotation(orientation_patterns: list) -> bool:
    if orientation_patterns[0] == [1, 1, 1] and orientation_patterns[1] == [0, 1, 1] and orientation_patterns[2] == [1, 0, 0] and orientation_patterns[3] == [0, 0, 0]:
        return False
    return True

def rotate_matrix(matrix: np.ndarray, orientation_patterns: list) -> np.ndarray:
    for _ in range(4):
        if need_rotation(orientation_patterns):
            matrix = np.rot90(matrix, k=3)
            orientation_patterns = read_orientation_patterns(matrix, detect_bullseye_bounds(matrix))
        else:
            break
    return matrix
