from functools import cached_property
import numpy as np

__all__ = ["OrientationManager"]


class OrientationManager:
    def __init__(self, matrix: np.ndarray, bounds: tuple):
        self.matrix = matrix
        self.bounds = bounds

    def _read_patterns(self) -> list:
        tl_y, tl_x, br_y, br_x = self.bounds
        tr_y, tr_x, bl_y, bl_x = tl_y, br_x, br_y, tl_x
        
        tl_orientation = []
        tl_orientation.append(int(self.matrix[tl_y, tl_x-1]))
        tl_orientation.append(int(self.matrix[tl_y-1, tl_x-1]))
        tl_orientation.append(int(self.matrix[tl_y-1, tl_x]))

        tr_orientation = []
        tr_orientation.append(int(self.matrix[tr_y-1, tr_x]))
        tr_orientation.append(int(self.matrix[tr_y-1, tr_x+1]))
        tr_orientation.append(int(self.matrix[tr_y, tr_x+1]))
        
        br_orientation = []
        br_orientation.append(int(self.matrix[br_y, br_x+1]))
        br_orientation.append(int(self.matrix[br_y+1, br_x+1]))
        br_orientation.append(int(self.matrix[br_y+1, br_x]))
        
        bl_orientation = []
        bl_orientation.append(int(self.matrix[bl_y+1, bl_x]))
        bl_orientation.append(int(self.matrix[bl_y+1, bl_x-1]))
        bl_orientation.append(int(self.matrix[bl_y, bl_x-1]))
        
        return [tl_orientation, tr_orientation, br_orientation, bl_orientation]
    
    @cached_property
    def patterns(self) -> list:
        return self._read_patterns()

    def rotate_if_needed(self) -> np.ndarray:
        for _ in range(4):
            if self._need_rotation():
                self.matrix = np.rot90(self.matrix, k=3)
            else:
                break
        return self.matrix

    def _need_rotation(self) -> bool:
        orientation_patterns = self._read_patterns()
        if orientation_patterns[0] == [1, 1, 1] and orientation_patterns[1] == [0, 1, 1] and orientation_patterns[2] == [1, 0, 0] and orientation_patterns[3] == [0, 0, 0]:
            return False
        return True
