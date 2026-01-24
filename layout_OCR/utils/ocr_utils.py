from __future__ import annotations

import cv2
import numpy as np
import pytesseract
from PIL import Image


def ocr_image(
    image: Image.Image,
    lang: str,
    tesseract_cmd: str | None = None,
    psm: int | None = None,
    oem: int | None = None,
    whitelist: str | None = None,
    extra_config: str | None = None,
    scale: float = 2.0,
    binarize: bool = True,
    denoise: bool = True,
    sharpen: bool = True,
) -> str:
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    processed = preprocess_for_ocr(
        image, scale=scale, binarize=binarize, denoise=denoise, sharpen=sharpen
    )
    config_parts = []
    if psm is not None:
        config_parts.append(f"--psm {psm}")
    if oem is not None:
        config_parts.append(f"--oem {oem}")
    whitelist = _expand_whitelist(whitelist)
    if whitelist:
        config_parts.append(f"-c tessedit_char_whitelist={whitelist}")
    if extra_config:
        config_parts.append(extra_config)
    config = " ".join(config_parts)
    return pytesseract.image_to_string(processed, lang=lang, config=config)


def _expand_whitelist(whitelist: str | None) -> str | None:
    if not whitelist:
        return whitelist
    arabic_indic = "".join(chr(code) for code in range(0x0660, 0x066A))
    eastern_arabic_indic = "".join(chr(code) for code in range(0x06F0, 0x06FA))
    return (
        whitelist.replace("{ARABIC_INDIC}", arabic_indic).replace(
            "{EASTERN_ARABIC_INDIC}", eastern_arabic_indic
        )
    )


def preprocess_for_ocr(
    image: Image.Image,
    scale: float = 2.0,
    binarize: bool = True,
    denoise: bool = True,
    sharpen: bool = True,
) -> Image.Image:
    gray = cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2GRAY)
    if scale and scale != 1.0:
        new_width = max(1, int(round(gray.shape[1] * scale)))
        new_height = max(1, int(round(gray.shape[0] * scale)))
        gray = cv2.resize(gray, (new_width, new_height), interpolation=cv2.INTER_CUBIC)

    if denoise:
        gray = cv2.medianBlur(gray, 3)

    if sharpen:
        blurred = cv2.GaussianBlur(gray, (0, 0), 1.0)
        gray = cv2.addWeighted(gray, 1.5, blurred, -0.5, 0)

    if binarize:
        _, gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return Image.fromarray(gray)
