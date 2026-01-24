from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from models.document_model import Document
from models.detectors.registry import build_detector
from utils.file_utils import build_output_name, collect_inputs, ensure_output_dir
from views.render_view import draw_boxes


class PipelineController:
    def __init__(
        self,
        detector_name: str,
        detector_options: Dict[str, object] | None = None,
        view_options: Dict[str, object] | None = None,
        poppler_path: str | None = None,
    ) -> None:
        self.detector = build_detector(detector_name, detector_options)
        self.view_options = view_options or {}
        self.poppler_path = poppler_path

    def run(self, input_path: Path, output_dir: Path, dpi: int) -> List[Path]:
        files = collect_inputs(input_path)
        if not files:
            raise FileNotFoundError(f"No supported files found in {input_path}")

        output_dir = ensure_output_dir(output_dir)
        outputs: List[Path] = []
        for file_path in files:
            outputs.extend(self._process_file(file_path, output_dir, dpi))
        return outputs

    def _process_file(self, file_path: Path, output_dir: Path, dpi: int) -> List[Path]:
        document = Document(file_path)
        outputs: List[Path] = []
        for page in document.load_pages(dpi, poppler_path=self.poppler_path):
            boxes = self.detector.detect(page.image)
            rendered = draw_boxes(
                page.image,
                boxes,
                color=self.view_options.get("color", "red"),
                width=self.view_options.get("width", 2),
            )
            page_index = page.index if document.is_pdf else None
            output_name = build_output_name(page.source_name, page_index)
            output_path = output_dir / output_name
            rendered.save(output_path)
            outputs.append(output_path)
            page.image.close()
        return outputs
