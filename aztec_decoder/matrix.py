import cv2
import numpy as np

def estimate_N_from_image(binary: np.ndarray) -> int:
    h, w = binary.shape
    row = (binary[h//2, :] < 128).astype(int)

    runs = []
    current = row[0]
    length = 1
    for pix in row[1:]:
        if pix == current:
            length += 1
        else:
            runs.append(length)
            length = 1
            current = pix
    runs.append(length)

    cell_size = int(np.median(runs))
    N = int(round(w / cell_size))
    return N

def extract_matrix(image_path: str) -> np.ndarray:
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    N = estimate_N_from_image(binary)
    h, w = binary.shape
    cell_size = h // N 

    module_matrix = np.zeros((N, N), dtype=int)

    for y in range(N):
        for x in range(N):
            cx = int((x + 0.5) * cell_size)
            cy = int((y + 0.5) * cell_size)
            if cx < w and cy < h:
                module_matrix[y, x] = 1 if binary[cy, cx] < 128 else 0
    
    return module_matrix
    