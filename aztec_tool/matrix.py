from __future__ import annotations
from functools import cached_property
import cv2
import numpy as np
from pathlib import Path
from typing import Union

from .exceptions import InvalidParameterError, UnsupportedSymbolError

__all__ = ["AztecMatrix"]


class AztecMatrix:
    """Convert a *cropped* Aztec-code image into a binary module matrix.

    The extractor assumes the image already contains **only** the Aztec
    symbol (no perspective skew, no surrounding background).

    Parameters
    ----------
    image_path : Union[str, Path]
        Path to the file with the Aztec code.

    Attributes
    ----------
    matrix : numpy.ndarray, shape (N, N)
        Lazy property - the binary module matrix (0 = white, 1 = black).

    Raises
    ------
    InvalidParameterError
        * The image file does not exist or cannot be read
        * Estimated cell size is zero (image too small or blurred)
        * Sampling point falls outside the image (wrong crop or resolution)
    UnsupportedSymbolError
        Computed side length *N* is even or outside the range 15 - 151.
    """

    def __init__(self, image_path: Union[str, Path]) -> None:
        self.image_path = Path(image_path)
        if not self.image_path.exists():
            raise InvalidParameterError(f"file not found: {self.image_path}")
        if not self.image_path.is_file():
            raise InvalidParameterError(f"path is not a file: {self.image_path}")

    def _estimate_N(self, binary: np.ndarray) -> int:
        h, w = binary.shape
        row = (binary[h // 2, :] < 128).astype(int)

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
        if cell_size == 0:
            raise InvalidParameterError(
                "estimated cell size is zero - image too small / blurred"
            )
        N = int(round(w / cell_size))
        if N % 2 == 0 or not (15 <= N <= 151):
            raise UnsupportedSymbolError(f"unsupported Aztec side length: {N}")
        return N

    def _extract_matrix(self) -> np.ndarray:
        img = cv2.imread(self.image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise InvalidParameterError(f"cannot read image: {self.image_path}")

        _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        N = self._estimate_N(binary)
        h, w = binary.shape
        cell_size = h // N
        if cell_size == 0:
            raise InvalidParameterError(
                "cell size computed as zero - check image resolution"
            )

        module_matrix = np.zeros((N, N), dtype=int)

        for y in range(N):
            for x in range(N):
                cx = int((x + 0.5) * cell_size)
                cy = int((y + 0.5) * cell_size)
                if cy >= h or cx >= binary.shape[1]:
                    raise InvalidParameterError(
                        "sampling point outside image - wrong N or skewed image"
                    )
                module_matrix[y, x] = 1 if binary[cy, cx] < 128 else 0

        return module_matrix

    @cached_property
    def matrix(self) -> np.ndarray:
        return self._extract_matrix()
