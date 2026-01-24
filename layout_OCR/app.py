from __future__ import annotations

import argparse
from pathlib import Path

from controllers.pipeline_controller import PipelineController
from models.detectors.simple_cv_detector import SimpleCvConfig
from utils.config_utils import get_config_value, load_config, to_bool


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Detect layout blocks, OCR each region, and merge text per file."
    )
    parser.add_argument("--input", "-i", required=True, help="PDF, image, or folder")
    parser.add_argument("--output", "-o", default=None, help="Output folder")
    parser.add_argument("--config", "-c", default=None, help="Optional config.ini")
    parser.add_argument(
        "--profile",
        default=None,
        help="Profile name: default or arabic",
    )

    parser.add_argument("--dpi", type=int, default=None, help="PDF render DPI")
    parser.add_argument("--lang", default=None, help="Tesseract languages, e.g. eng+ara")
    parser.add_argument("--psm", type=int, default=None, help="Tesseract page segmentation mode")
    parser.add_argument("--oem", type=int, default=None, help="Tesseract OCR engine mode")
    parser.add_argument(
        "--ocr-whitelist",
        default=None,
        help="Whitelist for main OCR pass",
    )
    parser.add_argument(
        "--ocr-extra-config",
        default=None,
        help="Extra tesseract config for main OCR pass",
    )
    parser.add_argument(
        "--line-psm",
        type=int,
        default=None,
        help="PSM used for short line boxes",
    )
    parser.add_argument(
        "--line-psm-height-ratio",
        type=float,
        default=None,
        help="Max box height ratio for line PSM",
    )
    parser.add_argument(
        "--digits-pass",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Enable a digits-only OCR pass for short boxes",
    )
    parser.add_argument(
        "--digits-height-ratio",
        type=float,
        default=None,
        help="Max box height ratio for digits pass",
    )
    parser.add_argument(
        "--digits-whitelist",
        default=None,
        help="Whitelist for digits pass",
    )
    parser.add_argument(
        "--digits-psm",
        type=int,
        default=None,
        help="PSM for digits-only pass",
    )
    parser.add_argument(
        "--digits-min-chars",
        type=int,
        default=None,
        help="Minimum digits to accept digits pass",
    )
    parser.add_argument(
        "--digits-extra-config",
        default=None,
        help="Extra tesseract config for digits pass",
    )
    parser.add_argument(
        "--digits-pass-scope",
        choices=["short", "all", "none"],
        default=None,
        help="Digits pass scope: short, all, or none",
    )
    parser.add_argument(
        "--digits-replace",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Replace digit groups in text using digits pass",
    )
    parser.add_argument(
        "--ocr-scale",
        type=float,
        default=None,
        help="Upscale factor for OCR crops",
    )
    parser.add_argument(
        "--ocr-binarize",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Binarize OCR crops with Otsu thresholding",
    )
    parser.add_argument(
        "--ocr-denoise",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Denoise OCR crops with median blur",
    )
    parser.add_argument(
        "--ocr-sharpen",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Sharpen OCR crops before OCR",
    )
    parser.add_argument(
        "--crop-padding",
        type=int,
        default=None,
        help="Padding in pixels added around each detected box",
    )
    parser.add_argument("--poppler-path", default=None, help="Poppler bin folder path")
    parser.add_argument("--tesseract-cmd", default=None, help="Path to tesseract.exe")

    parser.add_argument(
        "--rtl",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Right-to-left column order",
    )
    parser.add_argument(
        "--column-overlap-ratio",
        type=float,
        default=None,
        help="Horizontal overlap ratio to group columns",
    )
    parser.add_argument(
        "--include-page-breaks",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Insert page separators in output text",
    )
    parser.add_argument(
        "--fallback-full-page",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="OCR full page if no boxes are detected",
    )

    parser.add_argument("--min-area", type=int, default=None, help="Min contour area")
    parser.add_argument("--kernel-width", type=int, default=None, help="Merge kernel width")
    parser.add_argument("--kernel-height", type=int, default=None, help="Merge kernel height")
    parser.add_argument(
        "--adaptive-block-size",
        type=int,
        default=None,
        help="Adaptive threshold block size (odd number)",
    )
    parser.add_argument(
        "--adaptive-c",
        type=int,
        default=None,
        help="Adaptive threshold C value",
    )
    parser.add_argument(
        "--remove-lines",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Enable line removal preprocessing",
    )
    parser.add_argument(
        "--line-length-ratio",
        type=float,
        default=None,
        help="Remove long lines (ratio of page size)",
    )
    parser.add_argument(
        "--line-thickness",
        type=int,
        default=None,
        help="Line thickness for removal",
    )
    parser.add_argument(
        "--border-margin",
        type=int,
        default=None,
        help="Zero out a thin border margin",
    )
    parser.add_argument(
        "--max-area-ratio",
        type=float,
        default=None,
        help="Ignore boxes larger than this ratio of page area",
    )
    parser.add_argument(
        "--merge-linefree",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Merge boxes from a pass without line removal",
    )
    parser.add_argument(
        "--merge-iou-threshold",
        type=float,
        default=None,
        help="IOU threshold to dedupe merged boxes",
    )
    parser.add_argument(
        "--merge-area-ratio",
        type=float,
        default=None,
        help="Area ratio to treat boxes as duplicates",
    )

    parser.add_argument("--box-color", default=None, help="Box color for debug overlay")
    parser.add_argument("--box-width", type=int, default=None, help="Box line width for debug overlay")
    parser.add_argument(
        "--debug",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Save debug crops and ordering overlays",
    )
    parser.add_argument("--debug-dir", default=None, help="Debug output folder")

    return parser


def pick(value, config, section: str, key: str, default, cast):
    if value is not None:
        return value
    return get_config_value(config, section, key, default, cast)


def profile_defaults(name: str, cv_defaults: SimpleCvConfig) -> dict:
    base = {
        "general": {
            "dpi": 500,
            "output_dir": "output",
            "include_page_breaks": False,
            "fallback_full_page": True,
        },
        "ocr": {
            "lang": "eng+ara",
            "psm": 6,
            "oem": 1,
            "scale": 2.0,
            "binarize": True,
            "denoise": True,
            "sharpen": True,
            "crop_padding": 4,
            "line_psm": 7,
            "line_psm_height_ratio": 0.07,
            "digits_pass": False,
            "digits_height_ratio": 0.08,
            "digits_whitelist": "0123456789-/:.,٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹",
            "digits_psm": 7,
            "digits_min_chars": 2,
            "digits_pass_scope": "short",
            "digits_replace": False,
            "whitelist": None,
            "extra_config": None,
            "digits_extra_config": None,
        },
        "order": {
            "rtl": False,
            "column_overlap_ratio": 0.3,
        },
        "cv": {
            "min_area": cv_defaults.min_area,
            "kernel_width": cv_defaults.kernel_width,
            "kernel_height": cv_defaults.kernel_height,
            "adaptive_block_size": cv_defaults.adaptive_block_size,
            "adaptive_c": cv_defaults.adaptive_c,
            "remove_lines": cv_defaults.remove_lines,
            "line_length_ratio": cv_defaults.line_length_ratio,
            "line_thickness": cv_defaults.line_thickness,
            "border_margin": cv_defaults.border_margin,
            "max_area_ratio": cv_defaults.max_area_ratio,
            "merge_linefree": cv_defaults.merge_linefree,
            "merge_iou_threshold": cv_defaults.merge_iou_threshold,
            "merge_area_ratio": cv_defaults.merge_area_ratio,
        },
    }

    if name.lower() != "arabic":
        return base

    base["order"].update(
        {
            "rtl": True,
            "column_overlap_ratio": 0.4,
        }
    )
    base["cv"].update(
        {
            "min_area": max(30, cv_defaults.min_area),
            "kernel_width": max(8, cv_defaults.kernel_width - 2),
            "kernel_height": cv_defaults.kernel_height,
            "adaptive_c": max(10, cv_defaults.adaptive_c - 3),
            "line_length_ratio": 0.1,
            "line_thickness": max(2, cv_defaults.line_thickness),
            "border_margin": max(3, cv_defaults.border_margin),
            "max_area_ratio": 0.75,
            "merge_linefree": True,
            "merge_iou_threshold": 0.7,
            "merge_area_ratio": 0.2,
        }
    )
    base["ocr"].update(
        {
            "digits_pass": True,
            "digits_height_ratio": 0.1,
            "digits_whitelist": "0123456789-/:.,٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹",
            "digits_pass_scope": "all",
            "digits_replace": True,
        }
    )
    return base


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    config = load_config(args.config)

    defaults = SimpleCvConfig()
    profile_name = pick(args.profile, config, "general", "profile", "default", str)
    profile = profile_defaults(profile_name, defaults)

    output_dir = pick(
        args.output, config, "general", "output_dir", profile["general"]["output_dir"], str
    )
    dpi = pick(args.dpi, config, "general", "dpi", profile["general"]["dpi"], int)
    poppler_path = pick(args.poppler_path, config, "general", "poppler_path", None, str)
    tesseract_cmd = pick(args.tesseract_cmd, config, "general", "tesseract_cmd", None, str)

    ocr_options = {
        "lang": pick(args.lang, config, "ocr", "lang", profile["ocr"]["lang"], str),
        "psm": pick(args.psm, config, "ocr", "psm", profile["ocr"]["psm"], int),
        "oem": pick(args.oem, config, "ocr", "oem", profile["ocr"]["oem"], int),
        "scale": pick(args.ocr_scale, config, "ocr", "scale", profile["ocr"]["scale"], float),
        "binarize": pick(
            args.ocr_binarize, config, "ocr", "binarize", profile["ocr"]["binarize"], to_bool
        ),
        "denoise": pick(
            args.ocr_denoise, config, "ocr", "denoise", profile["ocr"]["denoise"], to_bool
        ),
        "sharpen": pick(
            args.ocr_sharpen, config, "ocr", "sharpen", profile["ocr"]["sharpen"], to_bool
        ),
        "crop_padding": pick(
            args.crop_padding, config, "ocr", "crop_padding", profile["ocr"]["crop_padding"], int
        ),
        "line_psm": pick(args.line_psm, config, "ocr", "line_psm", profile["ocr"]["line_psm"], int),
        "line_psm_height_ratio": pick(
            args.line_psm_height_ratio,
            config,
            "ocr",
            "line_psm_height_ratio",
            profile["ocr"]["line_psm_height_ratio"],
            float,
        ),
        "digits_pass": pick(
            args.digits_pass, config, "ocr", "digits_pass", profile["ocr"]["digits_pass"], to_bool
        ),
        "digits_height_ratio": pick(
            args.digits_height_ratio,
            config,
            "ocr",
            "digits_height_ratio",
            profile["ocr"]["digits_height_ratio"],
            float,
        ),
        "digits_whitelist": pick(
            args.digits_whitelist,
            config,
            "ocr",
            "digits_whitelist",
            profile["ocr"]["digits_whitelist"],
            str,
        ),
        "digits_psm": pick(
            args.digits_psm, config, "ocr", "digits_psm", profile["ocr"]["digits_psm"], int
        ),
        "digits_min_chars": pick(
            args.digits_min_chars,
            config,
            "ocr",
            "digits_min_chars",
            profile["ocr"]["digits_min_chars"],
            int,
        ),
        "digits_pass_scope": pick(
            args.digits_pass_scope,
            config,
            "ocr",
            "digits_pass_scope",
            profile["ocr"]["digits_pass_scope"],
            str,
        ),
        "digits_replace": pick(
            args.digits_replace,
            config,
            "ocr",
            "digits_replace",
            profile["ocr"]["digits_replace"],
            to_bool,
        ),
        "whitelist": pick(args.ocr_whitelist, config, "ocr", "whitelist", None, str),
        "extra_config": pick(args.ocr_extra_config, config, "ocr", "extra_config", None, str),
        "digits_extra_config": pick(
            args.digits_extra_config, config, "ocr", "digits_extra_config", None, str
        ),
    }

    order_options = {
        "rtl": pick(args.rtl, config, "order", "rtl", profile["order"]["rtl"], to_bool),
        "column_overlap_ratio": pick(
            args.column_overlap_ratio,
            config,
            "order",
            "column_overlap_ratio",
            profile["order"]["column_overlap_ratio"],
            float,
        ),
    }

    detector_options = {
        "min_area": pick(
            args.min_area, config, "cv", "min_area", profile["cv"]["min_area"], int
        ),
        "kernel_width": pick(
            args.kernel_width, config, "cv", "kernel_width", profile["cv"]["kernel_width"], int
        ),
        "kernel_height": pick(
            args.kernel_height, config, "cv", "kernel_height", profile["cv"]["kernel_height"], int
        ),
        "adaptive_block_size": pick(
            args.adaptive_block_size,
            config,
            "cv",
            "adaptive_block_size",
            profile["cv"]["adaptive_block_size"],
            int,
        ),
        "adaptive_c": pick(
            args.adaptive_c, config, "cv", "adaptive_c", profile["cv"]["adaptive_c"], int
        ),
        "remove_lines": pick(
            args.remove_lines, config, "cv", "remove_lines", profile["cv"]["remove_lines"], to_bool
        ),
        "line_length_ratio": pick(
            args.line_length_ratio,
            config,
            "cv",
            "line_length_ratio",
            profile["cv"]["line_length_ratio"],
            float,
        ),
        "line_thickness": pick(
            args.line_thickness, config, "cv", "line_thickness", profile["cv"]["line_thickness"], int
        ),
        "border_margin": pick(
            args.border_margin, config, "cv", "border_margin", profile["cv"]["border_margin"], int
        ),
        "max_area_ratio": pick(
            args.max_area_ratio, config, "cv", "max_area_ratio", profile["cv"]["max_area_ratio"], float
        ),
        "merge_linefree": pick(
            args.merge_linefree, config, "cv", "merge_linefree", profile["cv"]["merge_linefree"], to_bool
        ),
        "merge_iou_threshold": pick(
            args.merge_iou_threshold,
            config,
            "cv",
            "merge_iou_threshold",
            profile["cv"]["merge_iou_threshold"],
            float,
        ),
        "merge_area_ratio": pick(
            args.merge_area_ratio,
            config,
            "cv",
            "merge_area_ratio",
            profile["cv"]["merge_area_ratio"],
            float,
        ),
    }

    view_options = {
        "color": pick(args.box_color, config, "debug", "box_color", "red", str),
        "width": pick(args.box_width, config, "debug", "box_width", 2, int),
    }

    debug_enabled = pick(args.debug, config, "debug", "enabled", False, to_bool)
    debug_dir_value = pick(args.debug_dir, config, "debug", "dir", "debug", str)
    debug_dir = Path(debug_dir_value) if debug_enabled else None

    include_page_breaks = pick(
        args.include_page_breaks,
        config,
        "general",
        "include_page_breaks",
        profile["general"]["include_page_breaks"],
        to_bool,
    )
    fallback_full_page = pick(
        args.fallback_full_page,
        config,
        "general",
        "fallback_full_page",
        profile["general"]["fallback_full_page"],
        to_bool,
    )

    controller = PipelineController(
        detector_options=detector_options,
        ocr_options=ocr_options,
        order_options=order_options,
        view_options=view_options,
        poppler_path=poppler_path,
        tesseract_cmd=tesseract_cmd,
    )
    outputs = controller.run(
        Path(args.input),
        Path(output_dir),
        dpi=dpi,
        debug_dir=debug_dir,
        include_page_breaks=include_page_breaks,
        fallback_full_page=fallback_full_page,
    )

    for output_path in outputs:
        print(output_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
