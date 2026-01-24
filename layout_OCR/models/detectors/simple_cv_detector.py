from __future__ import annotations

from dataclasses import dataclass
from typing import List

import cv2
import numpy as np
from PIL import Image

from .base import Box, LayoutDetector


@dataclass
class SimpleCvConfig:
    min_area: int = 50
    kernel_width: int = 10
    kernel_height: int = 3
    adaptive_block_size: int = 25
    adaptive_c: int = 15
    remove_lines: bool = True
    line_length_ratio: float = 0.15
    line_thickness: int = 1
    border_margin: int = 2
    max_area_ratio: float = 0.85
    merge_linefree: bool = False
    merge_iou_threshold: float = 0.7
    merge_area_ratio: float = 0.25


class SimpleCvDetector(LayoutDetector):
    name = "simple_cv"

    def __init__(self, config: SimpleCvConfig | None = None) -> None:
        self.config = config or SimpleCvConfig()

    def detect(self, image: Image.Image) -> List[Box]:
        rgb = np.array(image.convert("RGB"))
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        block_size = max(3, int(self.config.adaptive_block_size))
        if block_size % 2 == 0:
            block_size += 1
        thresh = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY_INV,
            block_size,
            self.config.adaptive_c,
        )
        if self.config.border_margin > 0:
            margin = int(self.config.border_margin)
            thresh[:margin, :] = 0
            thresh[-margin:, :] = 0
            thresh[:, :margin] = 0
            thresh[:, -margin:] = 0
        thresh_raw = thresh.copy()

        if self.config.remove_lines:
            max_dim = max(image.width, image.height)
            line_length = max(10, int(max_dim * self.config.line_length_ratio))
            thickness = max(1, int(self.config.line_thickness))
            horiz_kernel = cv2.getStructuringElement(
                cv2.MORPH_RECT, (line_length, thickness)
            )
            vert_kernel = cv2.getStructuringElement(
                cv2.MORPH_RECT, (thickness, line_length)
            )
            horiz = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horiz_kernel, iterations=1)
            vert = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vert_kernel, iterations=1)
            lines = cv2.bitwise_or(horiz, vert)
            thresh = cv2.bitwise_and(thresh, cv2.bitwise_not(lines))

        kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT,
            (self.config.kernel_width, self.config.kernel_height),
        )
        merged = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=1)
        max_area = int(self.config.max_area_ratio * image.width * image.height)
        boxes = self._extract_boxes(merged, max_area)
        if self.config.merge_linefree:
            merged_raw = cv2.morphologyEx(
                thresh_raw, cv2.MORPH_CLOSE, kernel, iterations=1
            )
            extra_boxes = self._extract_boxes(merged_raw, max_area)
            boxes = self._merge_boxes(
                boxes,
                extra_boxes,
                iou_threshold=self.config.merge_iou_threshold,
                area_ratio=self.config.merge_area_ratio,
            )
        if not boxes:
            boxes = self._extract_boxes(thresh, max_area)
        return self.clip_boxes(boxes, image.width, image.height)

    def _extract_boxes(self, mask: np.ndarray, max_area: int) -> List[Box]:
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        boxes: List[Box] = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            if area < self.config.min_area:
                continue
            if max_area > 0 and area > max_area:
                continue
            boxes.append(Box(x, y, x + w, y + h))
        return boxes

    def _merge_boxes(
        self,
        primary: List[Box],
        secondary: List[Box],
        iou_threshold: float,
        area_ratio: float,
    ) -> List[Box]:
        combined = list(primary) + list(secondary)
        combined.sort(key=lambda b: b.width * b.height, reverse=True)
        kept: List[Box] = []
        for box in combined:
            should_keep = True
            for existing in kept:
                iou = _iou(box, existing)
                if iou >= iou_threshold:
                    ratio = min(box.width * box.height, existing.width * existing.height) / max(
                        1, max(box.width * box.height, existing.width * existing.height)
                    )
                    if ratio >= area_ratio:
                        should_keep = False
                        break
            if should_keep:
                kept.append(box)
        return kept


def _iou(box_a: Box, box_b: Box) -> float:
    left = max(box_a.left, box_b.left)
    top = max(box_a.top, box_b.top)
    right = min(box_a.right, box_b.right)
    bottom = min(box_a.bottom, box_b.bottom)
    inter_w = max(0, right - left)
    inter_h = max(0, bottom - top)
    inter_area = inter_w * inter_h
    area_a = box_a.width * box_a.height
    area_b = box_b.width * box_b.height
    union = area_a + area_b - inter_area
    if union <= 0:
        return 0.0
    return inter_area / union
