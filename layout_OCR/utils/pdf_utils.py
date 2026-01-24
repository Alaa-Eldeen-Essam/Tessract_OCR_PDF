from __future__ import annotations

from pathlib import Path
from typing import List

from pdf2image import convert_from_path
from pdf2image.exceptions import PDFInfoNotInstalledError
from PIL import Image


def pdf_to_images(path: Path, dpi: int = 200, poppler_path: str | None = None) -> List[Image.Image]:
    try:
        return convert_from_path(str(path), dpi=dpi, poppler_path=poppler_path)
    except PDFInfoNotInstalledError as err:
        raise RuntimeError(
            "Poppler is required for PDF rendering. Install it and ensure `pdftoppm` is on PATH, "
            "or provide --poppler-path pointing to the Poppler bin directory."
        ) from err
