from pathlib import Path
from typing import Optional

from pdf2image import convert_from_path
from PIL import Image
import pytesseract


class OcrModel:
    def __init__(
        self, lang: str = "eng+ara", dpi: int = 300, image_dpi: Optional[int] = None
    ) -> None:
        self.lang = lang
        self.dpi = dpi
        self.image_dpi = image_dpi

    def extract_text(self, input_path: Path) -> str:
        suffix = input_path.suffix.lower()
        if suffix == ".pdf":
            return self._extract_text_from_pdf(input_path)
        return self._extract_text_from_image(input_path)

    def _extract_text_from_pdf(self, pdf_path: Path) -> str:
        pages = convert_from_path(str(pdf_path), dpi=self.dpi)
        chunks = []
        for page in pages:
            chunks.append(pytesseract.image_to_string(page, lang=self.lang))
        return "\n".join(chunks).strip()

    def _extract_text_from_image(self, image_path: Path) -> str:
        with Image.open(image_path) as image:
            if self.image_dpi is None:
                return pytesseract.image_to_string(image, lang=self.lang).strip()
            config = f"--dpi {self.image_dpi}"
            return (
                pytesseract.image_to_string(image, lang=self.lang, config=config)
                .strip()
            )
