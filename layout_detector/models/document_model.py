from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

from PIL import Image

from utils.pdf_utils import pdf_to_images


@dataclass
class DocumentPage:
    index: int
    image: Image.Image
    source_name: str


class Document:
    def __init__(self, path: Path) -> None:
        self.path = path

    @property
    def is_pdf(self) -> bool:
        return self.path.suffix.lower() == ".pdf"

    def load_pages(self, dpi: int) -> List[DocumentPage]:
        if self.is_pdf:
            images = pdf_to_images(self.path, dpi=dpi)
            return [
                DocumentPage(index=i, image=image, source_name=self.path.stem)
                for i, image in enumerate(images)
            ]

        image = Image.open(self.path)
        return [DocumentPage(index=0, image=image, source_name=self.path.stem)]
