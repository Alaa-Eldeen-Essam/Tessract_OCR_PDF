# Reusable Code: Layout Detection + OCR

## Purpose
This repo provides two small, practical tools for document processing:
- **Layout detection**: draw bounding boxes on scanned PDFs/images to visualize regions.
- **OCR**: extract text from PDFs/images to `.txt` files.

They can be used independently, or in sequence (detect → review → OCR).

## Overview
- `layout_detector/`: OpenCV-based layout detection (no OCR).
- `PDF_OCR/`: Tesseract-based OCR for English/Arabic PDFs and images.

Both are CLI tools with their own dependencies and setup.

## How to use (overall flow)
1) **Run detection** to inspect layout quality and tune parameters for your scan type.  
2) **Run OCR** on the same inputs when you are satisfied with the layout quality.

## Layout detection (CV)
From the repo root:
```powershell
cd layout_detector
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Run on a PDF:
```powershell
python app.py --input "D:\path\to\file.pdf" --output "outputs" --detector simple_cv --poppler-path "C:\path\to\poppler\bin"
```

Run on an image or a folder:
```powershell
python app.py --input "D:\path\to\image.jpg" --output "outputs" --detector simple_cv
python app.py --input "D:\path\to\folder" --output "outputs" --detector simple_cv
```

Notes:
- PDF processing requires **Poppler** (`pdftoppm.exe`) on PATH or provided via `--poppler-path`.
- Outputs are boxed images saved into `outputs` (or your chosen folder).
- See `layout_detector/README.md` for parameter tuning.

## OCR (PDF_OCR)
From the repo root:
```powershell
cd PDF_OCR
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Run OCR on a PDF or image:
```powershell
python main.py -i "D:\path\to\file.pdf"
python main.py -i "D:\path\to\image.jpg"
```

Run OCR on a folder (recursive):
```powershell
python main.py -i "D:\path\to\folder"
```

Notes:
- OCR requires **Tesseract** with `eng` and `ara` language packs, and **Poppler** for PDFs.
- Outputs are `.txt` files with the same base name (default output folder: `export`).
- See `PDF_OCR/README.md` for config options and CLI flags.
