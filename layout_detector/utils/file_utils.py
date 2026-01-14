from __future__ import annotations

from pathlib import Path
from typing import List

SUPPORTED_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}


def is_supported_file(path: Path) -> bool:
    suffix = path.suffix.lower()
    return suffix == ".pdf" or suffix in SUPPORTED_IMAGE_EXTS


def collect_inputs(input_path: Path) -> List[Path]:
    if input_path.is_file():
        return [input_path]

    files: List[Path] = []
    for path in input_path.rglob("*"):
        if path.is_file() and is_supported_file(path):
            files.append(path)
    return sorted(files)


def ensure_output_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def build_output_name(base_name: str, page_index: int | None) -> str:
    if page_index is None:
        return f"{base_name}_boxes.png"
    return f"{base_name}_page_{page_index + 1}_boxes.png"
