from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from PIL import Image

from models.detectors.base import Box
from models.detectors.simple_cv_detector import SimpleCvConfig, SimpleCvDetector
from models.document_model import Document
from utils.file_utils import build_output_name, collect_inputs, ensure_output_dir
from utils.ocr_utils import ocr_image
from utils.ordering_utils import order_boxes_column_aware
from utils.render_utils import draw_boxes_with_order


class PipelineController:
    def __init__(
        self,
        detector_options: Dict[str, object],
        ocr_options: Dict[str, object],
        order_options: Dict[str, object],
        view_options: Dict[str, object],
        poppler_path: str | None = None,
        tesseract_cmd: str | None = None,
    ) -> None:
        self.detector = SimpleCvDetector(SimpleCvConfig(**detector_options))
        self.ocr_options = ocr_options
        self.order_options = order_options
        self.view_options = view_options
        self.poppler_path = poppler_path
        self.tesseract_cmd = tesseract_cmd

    def run(
        self,
        input_path: Path,
        output_dir: Path,
        dpi: int,
        debug_dir: Path | None = None,
        include_page_breaks: bool = False,
        fallback_full_page: bool = True,
    ) -> List[Path]:
        files = collect_inputs(input_path)
        if not files:
            raise FileNotFoundError(f"No supported files found in {input_path}")

        output_dir = ensure_output_dir(output_dir)
        if debug_dir:
            ensure_output_dir(debug_dir)

        outputs: List[Path] = []
        for file_path in files:
            output_path = self._process_file(
                file_path,
                output_dir,
                dpi,
                debug_dir,
                include_page_breaks,
                fallback_full_page,
            )
            outputs.append(output_path)
        return outputs

    def _process_file(
        self,
        file_path: Path,
        output_dir: Path,
        dpi: int,
        debug_dir: Path | None,
        include_page_breaks: bool,
        fallback_full_page: bool,
    ) -> Path:
        document = Document(file_path)
        text_sections: List[str] = []

        for page in document.load_pages(dpi, poppler_path=self.poppler_path):
            page_text = self._process_page(
                page.image,
                page.index,
                file_path.stem,
                debug_dir,
                fallback_full_page,
            )
            if include_page_breaks and document.is_pdf:
                page_text = f"--- Page {page.index + 1} ---\n{page_text}"
            text_sections.append(page_text.strip())
            page.image.close()

        separator = "\n\n" if include_page_breaks else "\n"
        combined = separator.join(section for section in text_sections if section)
        output_name = build_output_name(file_path.stem)
        output_path = output_dir / output_name
        output_path.write_text(combined, encoding="utf-8")
        return output_path

    def _process_page(
        self,
        image: Image.Image,
        page_index: int,
        base_name: str,
        debug_dir: Path | None,
        fallback_full_page: bool,
    ) -> str:
        boxes = self.detector.detect(image)
        if not boxes and fallback_full_page:
            boxes = [Box(0, 0, image.width, image.height)]

        ordered = order_boxes_column_aware(
            boxes,
            image.width,
            rtl=bool(self.order_options.get("rtl", False)),
            overlap_ratio=float(self.order_options.get("column_overlap_ratio", 0.3)),
        )

        if debug_dir:
            overlay = draw_boxes_with_order(
                image,
                ordered,
                color=self.view_options.get("color", "red"),
                width=int(self.view_options.get("width", 2)),
            )
            debug_name = f"{base_name}_page_{page_index + 1}_order.png"
            overlay.save(debug_dir / debug_name)

        chunks: List[str] = []
        crop_padding = int(self.ocr_options.get("crop_padding", 0))
        for idx, box in enumerate(ordered, start=1):
            if crop_padding > 0:
                left = max(0, box.left - crop_padding)
                top = max(0, box.top - crop_padding)
                right = min(image.width, box.right + crop_padding)
                bottom = min(image.height, box.bottom + crop_padding)
            else:
                left, top, right, bottom = box.left, box.top, box.right, box.bottom
            crop = image.crop((left, top, right, bottom))
            if debug_dir:
                crop_name = f"{base_name}_page_{page_index + 1}_crop_{idx}.png"
                crop.save(debug_dir / crop_name)
            height_ratio = box.height / max(1, image.height)
            default_psm = self.ocr_options.get("psm")
            line_psm = self.ocr_options.get("line_psm")
            line_psm_ratio = float(self.ocr_options.get("line_psm_height_ratio", 0.07))
            psm = default_psm
            if line_psm is not None and height_ratio <= line_psm_ratio:
                psm = line_psm

            text = ocr_image(
                crop,
                lang=str(self.ocr_options.get("lang", "eng+ara")),
                tesseract_cmd=self.tesseract_cmd,
                psm=psm,
                oem=self.ocr_options.get("oem"),
                whitelist=self.ocr_options.get("whitelist"),
                extra_config=self.ocr_options.get("extra_config"),
                scale=float(self.ocr_options.get("scale", 2.0)),
                binarize=bool(self.ocr_options.get("binarize", True)),
                denoise=bool(self.ocr_options.get("denoise", True)),
                sharpen=bool(self.ocr_options.get("sharpen", True)),
            )

            if self._digits_pass_enabled(height_ratio):
                digits_text = ocr_image(
                    crop,
                    lang=str(self.ocr_options.get("lang", "eng+ara")),
                    tesseract_cmd=self.tesseract_cmd,
                    psm=self.ocr_options.get("digits_psm", 7),
                    oem=self.ocr_options.get("oem"),
                    whitelist=self.ocr_options.get(
                        "digits_whitelist", "0123456789-/:.,"
                    ),
                    extra_config=self.ocr_options.get("digits_extra_config"),
                    scale=float(self.ocr_options.get("scale", 2.0)),
                    binarize=bool(self.ocr_options.get("binarize", True)),
                    denoise=bool(self.ocr_options.get("denoise", True)),
                    sharpen=bool(self.ocr_options.get("sharpen", True)),
                )
                text = self._prefer_digits(text, digits_text)
            text = text.strip()
            if text:
                chunks.append(text)
        return "\n".join(chunks)

    def _digits_pass_enabled(self, height_ratio: float) -> bool:
        if not bool(self.ocr_options.get("digits_pass", False)):
            return False
        scope = str(self.ocr_options.get("digits_pass_scope", "short")).lower()
        if scope == "none":
            return False
        if scope == "all":
            return True
        max_ratio = float(self.ocr_options.get("digits_height_ratio", 0.08))
        return height_ratio <= max_ratio

    def _prefer_digits(self, text: str, digits_text: str) -> str:
        digits_text = digits_text.strip()
        if not digits_text:
            return text

        if bool(self.ocr_options.get("digits_replace", False)):
            replaced = _replace_digit_groups(text, digits_text)
            return replaced

        min_chars = int(self.ocr_options.get("digits_min_chars", 2))
        digits_count = _count_digits(digits_text)
        if digits_count < min_chars:
            return text

        base_digits = _count_digits(text)
        base_letters = _count_letters(text)
        if digits_count > base_digits and digits_count >= base_letters:
            return digits_text
        return text


def _count_digits(text: str) -> int:
    return sum(1 for ch in text if ch.isdigit())


def _count_letters(text: str) -> int:
    return sum(1 for ch in text if ch.isalpha())


def _replace_digit_groups(text: str, digits_text: str) -> str:
    groups = _extract_digit_groups(digits_text)
    if not groups:
        return text

    result: list[str] = []
    index = 0
    i = 0
    while i < len(text):
        ch = text[i]
        if _is_digit_or_sep(ch):
            start = i
            has_digit = ch.isdigit()
            i += 1
            while i < len(text) and _is_digit_or_sep(text[i]):
                if text[i].isdigit():
                    has_digit = True
                i += 1
            segment = text[start:i]
            if has_digit and index < len(groups):
                result.append(groups[index])
                index += 1
            else:
                result.append(segment)
        else:
            result.append(ch)
            i += 1
    return "".join(result)


def _extract_digit_groups(text: str) -> list[str]:
    groups: list[str] = []
    current: list[str] = []
    has_digit = False
    for ch in text:
        if _is_digit_or_sep(ch):
            current.append(ch)
            if ch.isdigit():
                has_digit = True
        else:
            if current and has_digit:
                groups.append("".join(current).strip())
            current = []
            has_digit = False
    if current and has_digit:
        groups.append("".join(current).strip())
    return groups


def _is_digit_or_sep(ch: str) -> bool:
    return ch.isdigit() or ch in {".", ",", "-", "/", ":"}
