from __future__ import annotations

from dataclasses import dataclass
from typing import List

from models.detectors.base import Box


@dataclass
class Column:
    left: int
    right: int
    boxes: List[Box]

    def add(self, box: Box) -> None:
        self.boxes.append(box)
        self.left = min(self.left, box.left)
        self.right = max(self.right, box.right)


def order_boxes_column_aware(
    boxes: List[Box],
    page_width: int,
    rtl: bool = False,
    overlap_ratio: float = 0.3,
) -> List[Box]:
    if not boxes:
        return []

    columns: List[Column] = []
    if rtl:
        sorted_boxes = sorted(boxes, key=lambda b: b.center_x, reverse=True)
    else:
        sorted_boxes = sorted(boxes, key=lambda b: b.center_x)
    for box in sorted_boxes:
        placed = False
        for column in columns:
            overlap = min(box.right, column.right) - max(box.left, column.left)
            min_width = min(box.width, column.right - column.left)
            if overlap > 0 and overlap / max(1, min_width) >= overlap_ratio:
                column.add(box)
                placed = True
                break
        if not placed:
            columns.append(Column(left=box.left, right=box.right, boxes=[box]))

    if rtl:
        columns.sort(key=lambda c: c.right, reverse=True)
    else:
        columns.sort(key=lambda c: c.left)
    ordered: List[Box] = []
    for column in columns:
        if rtl:
            ordered.extend(sorted(column.boxes, key=lambda b: (b.top, -b.right)))
        else:
            ordered.extend(sorted(column.boxes, key=lambda b: (b.top, b.left)))
    return ordered
