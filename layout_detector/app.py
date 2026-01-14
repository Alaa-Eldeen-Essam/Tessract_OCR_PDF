from __future__ import annotations

import argparse
from pathlib import Path

from controllers.pipeline_controller import PipelineController
from models.detectors.registry import available_detectors


def build_parser() -> argparse.ArgumentParser:
    detector_names = sorted(available_detectors().keys())

    parser = argparse.ArgumentParser(
        description="Detect layout blocks in PDFs or images and export boxed images."
    )
    parser.add_argument("--input", "-i", required=True, help="PDF, image, or folder")
    parser.add_argument("--output", "-o", default="output", help="Output folder")
    parser.add_argument(
        "--detector",
        "-d",
        default="simple_cv",
        choices=detector_names,
        help=f"Detector to run: {', '.join(detector_names)}",
    )
    parser.add_argument("--dpi", type=int, default=200, help="PDF render DPI")

    parser.add_argument("--langs", default="eng+ara", help="Tesseract languages")
    parser.add_argument(
        "--min-confidence",
        type=int,
        default=50,
        help="Tesseract minimum confidence",
    )

    parser.add_argument("--min-area", type=int, default=200, help="Min contour area")
    parser.add_argument("--kernel-width", type=int, default=25, help="Merge kernel width")
    parser.add_argument(
        "--kernel-height", type=int, default=7, help="Merge kernel height"
    )

    parser.add_argument("--box-color", default="red", help="Box color")
    parser.add_argument("--box-width", type=int, default=2, help="Box line width")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    detector_options = {
        "langs": args.langs,
        "min_confidence": args.min_confidence,
        "min_area": args.min_area,
        "kernel_width": args.kernel_width,
        "kernel_height": args.kernel_height,
    }
    view_options = {"color": args.box_color, "width": args.box_width}

    controller = PipelineController(args.detector, detector_options, view_options)
    outputs = controller.run(Path(args.input), Path(args.output), dpi=args.dpi)

    for output_path in outputs:
        print(output_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
