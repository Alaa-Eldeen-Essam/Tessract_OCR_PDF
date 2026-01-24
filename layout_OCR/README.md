# Layout OCR (self-contained)

Detect layout regions with CV, OCR each region with Tesseract, and merge the text into a single `.txt` per input file. This folder is standalone and does not import from other project folders.

## Setup
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### System dependencies
- **Poppler** is required for PDFs (`pdftoppm.exe`).
- **Tesseract OCR** with `eng` and `ara` language packs.

## Usage
Single PDF:
```powershell
python app.py --input "D:\path\to\file.pdf" --output "outputs" --poppler-path "C:\path\to\poppler\bin"
```

Single image:
```powershell
python app.py --input "D:\path\to\image.jpg" --output "outputs"
```

Batch folder (recursive):
```powershell
python app.py --input "D:\path\to\folder" --output "outputs"
```

## Reading order
The default reading order is **column-aware**: each column is read top-to-bottom, then the next column. Use `--rtl` for right-to-left column order.

### Profiles
- `default`: baseline settings.
- `arabic`: stronger RTL behavior with stricter line removal and wider column overlap tolerance.

Use a profile with CLI:
```powershell
python app.py --input "D:\path\to\file.pdf" --output "outputs" --profile arabic
```

Or use the included config:
```powershell
python app.py --input "D:\path\to\file.pdf" -c config_arabic.ini
```

## Config file (optional)
Create `config.ini` and pass `-c config.ini`. CLI flags override config values. Starter files are included at `layout_OCR/config.ini` and `layout_OCR/config_arabic.ini`.

Example:
```ini
[general]
dpi = 500
output_dir = outputs
include_page_breaks = false
fallback_full_page = true

[ocr]
lang = eng+ara
psm = 6
oem = 1
line_psm = 7
line_psm_height_ratio = 0.07
scale = 2.0
binarize = true
denoise = true
sharpen = true
crop_padding = 4
digits_pass = false
digits_height_ratio = 0.08
digits_whitelist = 0123456789-/:.,٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹
digits_psm = 7
digits_min_chars = 2
digits_pass_scope = short
digits_replace = false
whitelist =
extra_config =
digits_extra_config =

[cv]
min_area = 50
kernel_width = 10
kernel_height = 3
adaptive_block_size = 25
adaptive_c = 15
remove_lines = true
line_length_ratio = 0.15
line_thickness = 1
border_margin = 2
max_area_ratio = 0.85
merge_linefree = false
merge_iou_threshold = 0.7
merge_area_ratio = 0.25

[order]
rtl = false
column_overlap_ratio = 0.3

[debug]
enabled = false
dir = debug
box_color = red
box_width = 2
```

## Debugging
Use `--debug` and `--debug-dir` to save:
- ordered box overlays per page
- cropped region images per page

Example:
```powershell
python app.py --input "D:\path\to\file.pdf" --output "outputs" --debug --debug-dir "debug" --poppler-path "C:\path\to\poppler\bin"
```

## OCR quality tips
- Try `psm = 6` for blocks, `psm = 4` for columns, or `psm = 3` for auto layout.
- Use `line_psm` for short boxes (dates, IDs) to improve numeric accuracy.
- Enable `digits_pass` for number-heavy forms; adjust `digits_height_ratio` if needed.
- Use `digits_pass_scope = all` to run the digits pass on every box (better for numbers embedded in text).
- Use `digits_replace = true` to replace digit groups in text with digits pass results.
- For Arabic-Indic numbers, include both Arabic-Indic and Eastern Arabic-Indic digits in `digits_whitelist`.
- Increase `scale` if text is small; reduce if output becomes noisy.
- Disable `binarize` if faint text disappears.
- Increase `crop_padding` if characters near edges are clipped.
