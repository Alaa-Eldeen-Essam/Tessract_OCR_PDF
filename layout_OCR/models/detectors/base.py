from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from PIL import Image


@dataclass(frozen=True)
class Box:
    left: int
    top: int
    right: int
    bottom: int

    @property
    def width(self) -> int:
        return max(0, self.right - self.left)

    @property
    def height(self) -> int:
        return max(0, self.bottom - self.top)

    @property
    def center_x(self) -> float:
        return self.left + self.width / 2.0

    @property
    def center_y(self) -> float:
        return self.top + self.height / 2.0


class LayoutDetector:
    name = "base"

    def detect(self, image: Image.Image) -> List[Box]:
        raise NotImplementedError

    @staticmethod
    def clip_boxes(boxes: Iterable[Box], width: int, height: int) -> List[Box]:
        clipped = []
        for box in boxes:
            left = max(0, min(box.left, width - 1))
            top = max(0, min(box.top, height - 1))
            right = max(0, min(box.right, width - 1))
            bottom = max(0, min(box.bottom, height - 1))
            if right > left and bottom > top:
                clipped.append(Box(left, top, right, bottom))
        return clipped
