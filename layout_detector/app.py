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

    parser.add_argument("--min-area", type=int, default=200, help="Min contour area")
    parser.add_argument("--kernel-width", type=int, default=25, help="Merge kernel width")
    parser.add_argument(
        "--kernel-height", type=int, default=7, help="Merge kernel height"
    )
    parser.add_argument(
        "--adaptive-block-size",
        type=int,
        default=25,
        help="Adaptive threshold block size (odd number)",
    )
    parser.add_argument(
        "--adaptive-c",
        type=int,
        default=15,
        help="Adaptive threshold C value",
    )
    parser.add_argument(
        "--line-length-ratio",
        type=float,
        default=0.15,
        help="Remove long lines (ratio of page size)",
    )
    parser.add_argument(
        "--line-thickness",
        type=int,
        default=1,
        help="Line thickness for removal",
    )
    parser.add_argument(
        "--border-margin",
        type=int,
        default=2,
        help="Zero out a thin border margin",
    )
    parser.add_argument(
        "--max-area-ratio",
        type=float,
        default=0.85,
        help="Ignore boxes larger than this ratio of page area",
    )
    parser.add_argument(
        "--no-remove-lines",
        action="store_true",
        help="Disable line removal preprocessing",
    )

    parser.add_argument(
        "--poppler-path",
        default=None,
        help="Optional: Path to Poppler bin folder if not on PATH",
    )

    parser.add_argument("--box-color", default="red", help="Box color")
    parser.add_argument("--box-width", type=int, default=2, help="Box line width")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    detector_options = {
        "min_area": args.min_area,
        "kernel_width": args.kernel_width,
        "kernel_height": args.kernel_height,
        "adaptive_block_size": args.adaptive_block_size,
        "adaptive_c": args.adaptive_c,
        "line_length_ratio": args.line_length_ratio,
        "line_thickness": args.line_thickness,
        "border_margin": args.border_margin,
        "max_area_ratio": args.max_area_ratio,
        "remove_lines": not args.no_remove_lines,
    }
    view_options = {"color": args.box_color, "width": args.box_width}

    controller = PipelineController(
        args.detector, detector_options, view_options, poppler_path=args.poppler_path
    )
    outputs = controller.run(Path(args.input), Path(args.output), dpi=args.dpi)

    for output_path in outputs:
        print(output_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
