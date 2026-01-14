# Layout Detector (MVC)

Simple MVC-style layout detector that processes PDFs or image files and exports boxed images. Supports single files or batch folders, plus multiple detectors.

## Structure
- `app.py`: CLI entry point
- `controllers/`: pipeline orchestration
- `models/`: document + detector logic
- `views/`: rendering boxed overlays
- `utils/`: file and PDF helpers

## Setup
Run commands from the `layout_detector` folder.
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### System dependencies
- **Poppler** is required by `pdf2image` to render PDFs.
- **Tesseract OCR** is required if you use the `tesseract` detector.

## Usage
Single PDF:
```powershell
python app.py --input "samples\doc.pdf" --output "outputs" --detector simple_cv
```

Batch folder (recursive):
```powershell
python app.py --input "samples" --output "outputs" --detector tesseract --langs eng+ara
```

Image input:
```powershell
python app.py --input "samples\scan.jpg" --output "outputs"
```

## Output naming
- PDF pages: `<pdf_name>_page_<n>_boxes.png`
- Image files: `<image_name>_boxes.png`

## Detectors
- `simple_cv` (default): OpenCV-based contour merging. Good for consistent scanned layouts.
- `tesseract`: Uses Tesseract OCR to draw word boxes. Set `--langs` to `eng+ara` for English + Arabic.

## Notes
- This is a minimal baseline to match similar document formats.
- If boxes are too noisy, raise `--min-area` or adjust `--kernel-width`/`--kernel-height`.
