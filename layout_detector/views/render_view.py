from __future__ import annotations

from typing import Iterable

from PIL import Image, ImageDraw

from models.detectors.base import Box


def draw_boxes(
    image: Image.Image,
    boxes: Iterable[Box],
    color: str = "red",
    width: int = 2,
) -> Image.Image:
    overlay = image.convert("RGB").copy()
    draw = ImageDraw.Draw(overlay)
    for box in boxes:
        draw.rectangle([box.left, box.top, box.right, box.bottom], outline=color, width=width)
    return overlay
