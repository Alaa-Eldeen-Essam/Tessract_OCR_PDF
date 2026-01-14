import argparse
import configparser
from pathlib import Path
from typing import Optional

from .model import OcrModel
from .view import ConsoleView


class OcrController:
    SUPPORTED_EXTENSIONS = {
        ".pdf",
        ".png",
        ".jpg",
        ".jpeg",
        ".tif",
        ".tiff",
        ".bmp",
        ".webp",
    }

    def __init__(self) -> None:
        self.view = ConsoleView()

    def _parse_args(self) -> argparse.Namespace:
        extensions = ", ".join(sorted(self.SUPPORTED_EXTENSIONS))
        parser = argparse.ArgumentParser(
            description="OCR PDF or image files to text with Tesseract."
        )
        parser.add_argument(
            "-i",
            "--input",
            required=True,
            help=(
                "PDF/image file or folder of supported files (recursive) "
                f"({extensions})"
            ),
        )
        parser.add_argument(
            "-c",
            "--config",
            default=None,
            help="Optional config file path (defaults to config.ini if present)",
        )
        parser.add_argument(
            "-l", "--lang", default=None, help="Tesseract language(s)"
        )
        parser.add_argument(
            "-d", "--dpi", type=int, default=None, help="Render DPI for PDF pages"
        )
        parser.add_argument(
            "--image-dpi",
            type=int,
            default=None,
            help="Assumed DPI for image inputs (Tesseract --dpi)",
        )
        parser.add_argument(
            "-o", "--output-dir", default=None, help="Optional output directory"
        )
        return parser.parse_args()

    def _resolve_config_path(self, args: argparse.Namespace) -> Optional[Path]:
        if args.config:
            return Path(args.config)
        default_path = Path("config.ini")
        if default_path.is_file():
            return default_path
        return None

    def _load_config(self, config_path: Path) -> dict:
        parser = configparser.ConfigParser()
        parser.read(config_path, encoding="utf-8")
        if "ocr" not in parser:
            return {}
        section = parser["ocr"]
        return {
            "lang": section.get("lang"),
            "dpi": section.get("dpi"),
            "image_dpi": section.get("image_dpi"),
            "output_dir": section.get("output_dir"),
        }

    def _collect_inputs(self, input_path: Path) -> list[Path]:
        if input_path.is_dir():
            return sorted(
                [
                    path
                    for path in input_path.rglob("*")
                    if path.is_file()
                    and path.suffix.lower() in self.SUPPORTED_EXTENSIONS
                ]
            )
        if (
            input_path.is_file()
            and input_path.suffix.lower() in self.SUPPORTED_EXTENSIONS
        ):
            return [input_path]
        return []

    def run(self) -> int:
        args = self._parse_args()
        config_path = self._resolve_config_path(args)

        if args.config and (not config_path or not config_path.is_file()):
            self.view.error(f"Config file not found: {args.config}")
            return 2

        config = {}
        if config_path:
            try:
                config = self._load_config(config_path)
            except (configparser.Error, OSError) as exc:
                self.view.error(f"Failed to read config: {config_path} ({exc})")
                return 2

        input_path = Path(args.input)
        files = self._collect_inputs(input_path)

        if not files:
            extensions = ", ".join(sorted(self.SUPPORTED_EXTENSIONS))
            self.view.error(
                "Input must be a PDF/image file or folder containing: "
                f"{extensions}"
            )
            return 2

        lang = args.lang or config.get("lang") or "eng+ara"

        dpi_raw = args.dpi if args.dpi is not None else config.get("dpi")
        if dpi_raw in (None, ""):
            dpi = 300
        else:
            try:
                dpi = int(dpi_raw)
            except ValueError:
                self.view.error("DPI must be an integer.")
                return 2

        if dpi <= 0:
            self.view.error("DPI must be a positive integer.")
            return 2

        image_dpi_raw = (
            args.image_dpi
            if args.image_dpi is not None
            else config.get("image_dpi")
        )
        if image_dpi_raw in (None, ""):
            image_dpi = None
        else:
            try:
                image_dpi = int(image_dpi_raw)
            except ValueError:
                self.view.error("Image DPI must be an integer.")
                return 2
            if image_dpi <= 0:
                self.view.error("Image DPI must be a positive integer.")
                return 2

        output_dir_value = args.output_dir
        if output_dir_value in (None, ""):
            output_dir_value = config.get("output_dir")
        if output_dir_value in (None, ""):
            output_dir_value = "export"
        output_dir = Path(output_dir_value)

        model = OcrModel(lang=lang, dpi=dpi, image_dpi=image_dpi)

        for input_file in files:
            self.view.info(f"OCR: {input_file.name}")
            text = model.extract_text(input_file)
            target_dir = output_dir or input_file.parent
            target_dir.mkdir(parents=True, exist_ok=True)
            output_path = target_dir / f"{input_file.stem}.txt"
            output_path.write_text(text, encoding="utf-8")
            self.view.success(f"Wrote: {output_path}")
        return 0
