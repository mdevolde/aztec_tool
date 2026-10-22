"""Aztec Code matrix extractor from cropped images."""

from __future__ import annotations

from functools import cached_property
from pathlib import Path
from typing import List, Optional, Tuple, Union

import cv2
import numpy as np
import numpy.typing as npt
from cv2.typing import MatLike

from .exceptions import InvalidParameterError, UnsupportedSymbolError

__all__ = ["AztecMatrix"]


class AztecMatrix:
    """Convert a *cropped* Aztec-code image into a binary module matrix.

    The extractor assumes the image already contains **only** the Aztec
    symbol (no perspective skew, no surrounding background).

    :param image_path: Path to the file with the Aztec code.
    :type image_path: Union[str, Path]
    :param multiple: If ``True``, detect multiple Aztec codes in the image, defaults to ``False``
    :type multiple: Optional[bool]

    :raises InvalidParameterError: The image file does not exist or cannot be read, or
        estimated cell size is zero (image too small or blurred), or
        sampling point falls outside the image (wrong crop or resolution).
    :raises UnsupportedSymbolError: Computed side length *N* is even or outside the range 15 - 151.
    """

    def __init__(
        self, image_path: Union[str, Path], *, multiple: Optional[bool] = False
    ) -> None:
        self.image_path = Path(image_path)
        self._multiple = multiple
        if not self.image_path.exists():
            raise InvalidParameterError(f"file not found: {self.image_path}")
        if not self.image_path.is_file():
            raise InvalidParameterError(f"path is not a file: {self.image_path}")

    def _detect_rois(
        self,
        min_area_ratio: float = 0.005,
        ar_tol: float = 0.15,
        density_tol: float = 0.15,
    ) -> List[Tuple[MatLike, Tuple[int, int, int, int]]]:
        """Detect all candidate Aztec codes in the image and return the crops.

        :param min_area_ratio: Minimum area of the detected region as a fraction of the image area, defaults to 0.005
        :type min_area_ratio: float
        :param ar_tol: Allowed aspect ratio tolerance (width/height) for the detected region, defaults to 0.15
        :type ar_tol: float
        :param density_tol: Allowed density tolerance for the detected region (black/white ratio), defaults to 0.15
        :type density_tol: float

        :return: One entry per code candidate.
        :rtype: List[Tuple[crop_BGR, (x, y, w, h)]]
        """

        img = cv2.imread(str(self.image_path))
        h, w = img.shape[:2]

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        # White background, black foreground
        _, bin_bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # 8-neighbors on "black code" => invert to make the code white (255) for detection
        inv = cv2.bitwise_not(bin_bw)
        n_labels, _, stats, _ = cv2.connectedComponentsWithStats(inv, connectivity=8)

        img_area = h * w
        rois: List[Tuple[MatLike, Tuple[int, int, int, int]]] = []  # results

        for i in range(1, n_labels):  # 0 = background, we start from 1
            x, y, ww, hh, area = stats[i]

            if area < img_area * min_area_ratio:
                continue

            ar = ww / float(hh)
            if not (1 - ar_tol <= ar <= 1 + ar_tol):
                continue

            # density : 50% black / 50% white
            roi_bin = bin_bw[y : y + hh, x : x + ww]
            black_ratio = 1 - cv2.countNonZero(roi_bin) / float(ww * hh)
            if abs(black_ratio - 0.5) > density_tol:
                continue

            crop = img[y : y + hh, x : x + ww].copy()
            rois.append((crop, (x, y, ww, hh)))

        for i, roi in enumerate(rois):
            cv2.imwrite(f"{i}.png", roi[0])

        print(len(rois))
        return rois

    def _estimate_n(self, binary: MatLike) -> int:
        h, w = binary.shape
        row = (binary[h // 2, :] < 128).astype(int)

        runs: List[int] = []
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
        n = int(round(w / cell_size))
        if n % 2 == 0 or not (15 <= n <= 151):
            raise UnsupportedSymbolError(f"unsupported Aztec side length: {n}")
        return n

    def _matrix_from_crop(self, crop: MatLike) -> npt.NDArray[np.int_]:
        """Convert a *single* square crop to a binary module matrix."""
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        n = self._estimate_n(binary)
        h = binary.shape[0]
        cell_size = h // n
        if cell_size == 0:
            raise InvalidParameterError(
                "cell size computed as zero – check image resolution"
            )

        matrix = np.zeros((n, n), dtype=int)
        for y in range(n):
            for x in range(n):
                cx = int((x + 0.5) * cell_size)
                cy = int((y + 0.5) * cell_size)
                if cy >= h or cx >= binary.shape[1]:
                    raise InvalidParameterError(
                        "sampling point outside image – wrong crop or skewed image"
                    )
                matrix[y, x] = 1 if binary[cy, cx] < 128 else 0
        return matrix

    def _extract_matrix(self) -> List[npt.NDArray[np.int_]]:
        rois = self._detect_rois() if self._multiple else []
        if not rois:  # No Aztec code croped, try to read the whole image
            img = cv2.imread(str(self.image_path))
            try:
                return [self._matrix_from_crop(img)]
            except (InvalidParameterError, UnsupportedSymbolError):
                return []  # no Aztec code found

        matrices: List[npt.NDArray[np.int_]] = []
        for crop, _ in rois:
            try:
                matrices.append(self._matrix_from_crop(crop))
            except (InvalidParameterError, UnsupportedSymbolError) as e:
                # If exception is raised, pass to the next crop
                print(e)
                continue
        return matrices

    @cached_property
    def matrices(self) -> List[npt.NDArray[np.int_]]:
        """List of module matrices detected in the image."""
        matrices = self._extract_matrix()
        if not matrices:
            raise InvalidParameterError("no Aztec matrix detected in the image")
        return matrices

    @cached_property
    def matrix(self) -> npt.NDArray[np.int_]:
        """The binary module matrix (0 = white, 1 = black), shape (N, N). Lazy property."""
        if not self.matrices:
            raise InvalidParameterError("no Aztec matrix detected in the image")
        return self.matrices[0]
