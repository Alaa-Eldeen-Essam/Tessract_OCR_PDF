from pathlib import Path

from pdf2image import convert_from_path
import pytesseract


class OcrModel:
    def __init__(self, lang: str = "eng+ara", dpi: int = 300) -> None:
        self.lang = lang
        self.dpi = dpi

    def extract_text(self, pdf_path: Path) -> str:
        pages = convert_from_path(str(pdf_path), dpi=self.dpi)
        chunks = []
        for page in pages:
            chunks.append(pytesseract.image_to_string(page, lang=self.lang))
        return "\n".join(chunks).strip()