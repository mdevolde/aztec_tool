import cv2
import numpy as np

def extract_matrix():
    img = cv2.imread("barcode.jpg", cv2.IMREAD_GRAYSCALE)

    _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    N = 23 #TODO: deduce N from the image
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
    