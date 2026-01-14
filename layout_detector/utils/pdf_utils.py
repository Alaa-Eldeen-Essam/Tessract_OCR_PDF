from __future__ import annotations

from pathlib import Path
from typing import List

from pdf2image import convert_from_path
from PIL import Image


def pdf_to_images(path: Path, dpi: int = 200) -> List[Image.Image]:
    return convert_from_path(str(path), dpi=dpi)
