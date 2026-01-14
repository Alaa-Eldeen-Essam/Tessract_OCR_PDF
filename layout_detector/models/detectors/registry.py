from __future__ import annotations

from typing import Dict, Type

from .base import LayoutDetector
from .simple_cv_detector import SimpleCvConfig, SimpleCvDetector
from .tesseract_detector import TesseractConfig, TesseractDetector


DETECTOR_REGISTRY: Dict[str, Type[LayoutDetector]] = {
    SimpleCvDetector.name: SimpleCvDetector,
    TesseractDetector.name: TesseractDetector,
}


def available_detectors() -> Dict[str, Type[LayoutDetector]]:
    return dict(DETECTOR_REGISTRY)


def build_detector(name: str, options: dict | None = None) -> LayoutDetector:
    options = options or {}
    if name not in DETECTOR_REGISTRY:
        raise ValueError(f"Unknown detector: {name}")

    if name == SimpleCvDetector.name:
        config = SimpleCvConfig(
            min_area=options.get("min_area", SimpleCvConfig.min_area),
            kernel_width=options.get("kernel_width", SimpleCvConfig.kernel_width),
            kernel_height=options.get("kernel_height", SimpleCvConfig.kernel_height),
        )
        return SimpleCvDetector(config)

    if name == TesseractDetector.name:
        config = TesseractConfig(
            langs=options.get("langs", TesseractConfig.langs),
            min_confidence=options.get("min_confidence", TesseractConfig.min_confidence),
        )
        return TesseractDetector(config)

    return DETECTOR_REGISTRY[name]()
