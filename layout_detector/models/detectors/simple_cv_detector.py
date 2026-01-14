from __future__ import annotations

from dataclasses import dataclass
from typing import List

import cv2
import numpy as np
from PIL import Image

from .base import Box, LayoutDetector


@dataclass
class SimpleCvConfig:
    min_area: int = 200
    kernel_width: int = 25
    kernel_height: int = 7


class SimpleCvDetector(LayoutDetector):
    name = "simple_cv"

    def __init__(self, config: SimpleCvConfig | None = None) -> None:
        self.config = config or SimpleCvConfig()

    def detect(self, image: Image.Image) -> List[Box]:
        rgb = np.array(image.convert("RGB"))
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        thresh = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY_INV,
            25,
            15,
        )
        kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT,
            (self.config.kernel_width, self.config.kernel_height),
        )
        merged = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=1)
        contours, _ = cv2.findContours(merged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        boxes: List[Box] = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w * h < self.config.min_area:
                continue
            boxes.append(Box(x, y, x + w, y + h))
        return self.clip_boxes(boxes, image.width, image.height)
