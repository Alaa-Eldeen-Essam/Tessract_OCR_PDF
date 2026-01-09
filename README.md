# PDF OCR

Simple MVC-style Python app that OCRs English or Arabic PDFs with Tesseract and writes a .txt file with the same base name.

## Requirements
- Python 3.9+
- Tesseract OCR with language packs `eng` and `ara`
- Poppler (required by pdf2image for PDF rendering)

## Conda environment (optional)
```bash
conda create -n pdf-ocr python=3.10
conda activate pdf-ocr
```

## Setup
```bash
pip install -r requirements.txt
```

## System dependencies
Check (Windows PowerShell):
```powershell
where tesseract
where pdftoppm
```

Check (Ubuntu):
```bash
which tesseract
which pdftoppm
```

Install if missing (Windows, winget):
```powershell
winget install --id UB-Mannheim.TesseractOCR -e
winget install --id Poppler.Poppler -e
```

Install if missing (Windows, Chocolatey):
```powershell
choco install tesseract -y
choco install poppler -y
```

Install if missing (Ubuntu):
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-ara poppler-utils
```

If Tesseract is not on PATH, point to it in code before OCR:
```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

## Configuration
Create `config.ini` in the project root (or pass `--config path\to\config.ini`).

Example:
```ini
[ocr]
lang = eng+ara
dpi = 300
output_dir = export
```

Notes:
- `output_dir` defaults to `export` and is created if it does not exist.
- Higher DPI can improve OCR accuracy but increases processing time and memory usage.
- CLI flags override config values.

## Usage
Single file:
```bash
python main.py -i path\to\file.pdf
```

Batch folder:
```bash
python main.py -i path\to\folder\with\pdfs
```

Optional output directory, language, and DPI:
```bash
python main.py -i input.pdf -o output_dir -l eng+ara -d 300
```

Use a config file explicitly:
```bash
python main.py -i input.pdf -c config.ini
```