# Layout Detector (MVC)

Simple MVC-style layout detector that processes PDFs or image files and exports boxed images. Supports single files or batch folders.

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
- Windows Poppler install:
  - If you have admin: `choco install poppler` (run shell as Administrator).
  - No admin: download a Poppler zip release, extract, and add the `bin` folder to PATH or pass `--poppler-path "C:\path\to\poppler\bin"`.

## Usage
Single PDF:
```powershell
python app.py --input "samples\doc.pdf" --output "outputs" --detector simple_cv
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

## Notes
- This is a minimal baseline to match similar document formats.
- If boxes are too noisy, raise `--min-area` or adjust `--kernel-width`/`--kernel-height`.
- If a full-page box appears (borders/tables), try lowering `--line-length-ratio`, lowering `--max-area-ratio`, or disable line removal with `--no-remove-lines`.

## Simple CV parameter guide
These parameters control how the CV detector groups text into boxes. Small changes can have large effects.

- `--min-area`: Minimum contour area (pixels). Higher values reduce noise but may drop small stamps/short lines.
- `--kernel-width` / `--kernel-height`: Size of the merge kernel. Larger values merge nearby text into bigger blocks; too large can fuse whole sections.
- `--adaptive-block-size`: Window size for adaptive thresholding (odd number). Larger values smooth lighting changes but can blur thin text.
- `--adaptive-c`: Threshold offset. Higher values remove faint text; lower values keep more but increase noise.
- `--line-length-ratio`: Ratio of page size used to detect long lines. Lower values remove more lines (tables/borders) but may delete long text strokes.
- `--line-thickness`: Expected line thickness for removal. Increase if borders are thick; decrease if thin lines are being missed.
- `--border-margin`: Zeros out a thin border strip. Use to suppress page frames; too large can crop near-edge text.
- `--max-area-ratio`: Rejects boxes larger than this portion of the page. Lower values prevent full-page boxes; too low can drop big text blocks.
- `--no-remove-lines`: Disables line removal. Useful if underlines are part of the text or if line removal deletes content.

Related inputs:
- `--dpi`: PDF render DPI. Higher DPI improves detection on small text but increases runtime and memory.
- `--poppler-path`: Use when Poppler is not on PATH; points to the folder containing `pdftoppm.exe`.
