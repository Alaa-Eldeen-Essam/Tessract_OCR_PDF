from __future__ import annotations

from typing import Iterable

from PIL import Image, ImageDraw, ImageFont

from models.detectors.base import Box


def draw_boxes_with_order(
    image: Image.Image,
    boxes: Iterable[Box],
    color: str = "red",
    width: int = 2,
) -> Image.Image:
    overlay = image.convert("RGB").copy()
    draw = ImageDraw.Draw(overlay)
    font = _load_default_font()
    for idx, box in enumerate(boxes, start=1):
        draw.rectangle([box.left, box.top, box.right, box.bottom], outline=color, width=width)
        draw.text((box.left + 2, box.top + 2), str(idx), fill=color, font=font)
    return overlay


def _load_default_font() -> ImageFont.ImageFont:
    try:
        return ImageFont.load_default()
    except OSError:
        return ImageFont.load_default()
