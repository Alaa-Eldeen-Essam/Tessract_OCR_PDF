from __future__ import annotations

from dataclasses import dataclass
from typing import List

import pytesseract
from PIL import Image

from .base import Box, LayoutDetector


@dataclass
class TesseractConfig:
    langs: str = "eng+ara"
    min_confidence: int = 50


class TesseractDetector(LayoutDetector):
    name = "tesseract"

    def __init__(self, config: TesseractConfig | None = None) -> None:
        self.config = config or TesseractConfig()

    def detect(self, image: Image.Image) -> List[Box]:
        data = pytesseract.image_to_data(
            image,
            lang=self.config.langs,
            output_type=pytesseract.Output.DICT,
        )
        boxes: List[Box] = []
        for i, text in enumerate(data.get("text", [])):
            if not text or not text.strip():
                continue
            conf = int(float(data["conf"][i])) if data["conf"][i] != "-1" else -1
            if conf < self.config.min_confidence:
                continue
            left = int(data["left"][i])
            top = int(data["top"][i])
            width = int(data["width"][i])
            height = int(data["height"][i])
            boxes.append(Box(left, top, left + width, top + height))
        return self.clip_boxes(boxes, image.width, image.height)
