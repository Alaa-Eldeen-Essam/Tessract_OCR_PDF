from __future__ import annotations

from typing import Dict, Type

from .base import LayoutDetector
from .simple_cv_detector import SimpleCvConfig, SimpleCvDetector


DETECTOR_REGISTRY: Dict[str, Type[LayoutDetector]] = {
    SimpleCvDetector.name: SimpleCvDetector,
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
            adaptive_block_size=options.get(
                "adaptive_block_size", SimpleCvConfig.adaptive_block_size
            ),
            adaptive_c=options.get("adaptive_c", SimpleCvConfig.adaptive_c),
            remove_lines=options.get("remove_lines", SimpleCvConfig.remove_lines),
            line_length_ratio=options.get(
                "line_length_ratio", SimpleCvConfig.line_length_ratio
            ),
            line_thickness=options.get(
                "line_thickness", SimpleCvConfig.line_thickness
            ),
            border_margin=options.get("border_margin", SimpleCvConfig.border_margin),
            max_area_ratio=options.get("max_area_ratio", SimpleCvConfig.max_area_ratio),
        )
        return SimpleCvDetector(config)

    return DETECTOR_REGISTRY[name]()
