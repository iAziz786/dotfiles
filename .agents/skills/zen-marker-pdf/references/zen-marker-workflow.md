# Zen Marker Workflow

This skill is for the `zen` SSH host, an Ubuntu 24.04 CPU-only VM.

## Tested Settings

- Host: `ssh zen`
- Remote temp work dir: `/tmp/marker-work.*`
- Remote venv: `/tmp/marker-venv`
- CPU torch: installed from `https://download.pytorch.org/whl/cpu`
- Swap: `/swapfile` at 12G worked
- Chunk size: 50 pages worked for a 497-page book

## Why This Exists

The default `marker_single` path was OOM-killed on this VM.
The chunked `PdfConverter` path worked when it was run with:

- `marker.processors.order.OrderProcessor`
- `marker.processors.text.TextProcessor`
- `disable_ocr=True`
- `force_layout_block="Text"`
- `disable_image_extraction=True`
- `pdftext_workers=1`

## Important Gotchas

- `page_range` must be a Python list of integers.
- Reuse the same `PdfConverter` and update `converter.config["page_range"]` per chunk.
- `marker_single` on the full document can get killed by the OOM killer.
- If `torch` is the CUDA build, reinstall the CPU wheel before converting.

## Manual Bootstrap Fallback

If the script fails, bootstrap the VM manually:

```bash
ssh zen 'sudo apt-get update && sudo apt-get install -y python3.12-venv'
ssh zen 'python3 -m venv /tmp/marker-venv'
ssh zen '/tmp/marker-venv/bin/pip install --upgrade pip'
ssh zen '/tmp/marker-venv/bin/pip install marker-pdf'
ssh zen '/tmp/marker-venv/bin/pip install --force-reinstall --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch'
```

If swap is missing:

```bash
ssh zen 'sudo fallocate -l 12G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile'
```

## Manual Conversion Fallback

Use the Python API instead of `marker_single`:

```python
from marker.converters.pdf import PdfConverter

converter.config["page_range"] = list(range(start, end + 1))
rendered = converter(pdf_path)
```
