---
name: zen-marker-pdf
description: Convert local PDF files to markdown through the ssh zen Ubuntu VM using marker. Use when the PDF must be processed on zen, especially for large books or CPU-only runs that need chunked conversion, one-time marker bootstrap, and the markdown downloaded back to local /tmp.
license: MIT
compatibility: Requires SSH/SCP access to host `zen`, sudo on the VM for one-time bootstrap, and internet access on the VM to install marker if needed.
metadata:
  author: Aziz
  version: "1.0"
  remote_host: zen
  default_chunk_size: "50"
---

# Zen Marker PDF Conversion

Use this skill for PDF-to-markdown jobs that must run on the `zen` VM rather than locally.

## What This Skill Does

- Copies a local PDF to `zen`
- Bootstraps marker on the VM if it is missing
- Forces the VM onto CPU-only torch
- Adds swap if the VM is too small for the full marker stack
- Converts the PDF in chunks with marker's Python API
- Downloads the markdown back to the local machine

## When To Use It

Activate this skill when the user wants to:

- Convert a PDF to markdown through `ssh zen`
- Use marker on the remote VM instead of local hardware
- Process a large book or long PDF on a CPU-only Ubuntu VM
- Recover from marker OOMs by chunking the conversion

## Preferred Workflow

1. Run the bundled script:

   ```bash
   python3 scripts/zen_marker_convert.py "/path/to/book.pdf" --output "/tmp/book.md"
   ```

2. Let the script handle the remote bootstrap, conversion, and download.

3. If the user wants a different local destination, pass `--output`.

## Available Scripts

- `scripts/zen_marker_convert.py` - End-to-end SSH, bootstrap, chunked conversion, and download.

## Gotchas

- Do not rely on `marker_single` for the full document on `zen`; the default pipeline can OOM on the VM.
- Use chunked `PdfConverter` runs instead of a full single-pass conversion.
- `page_range` must be a `list[int]`, not a string like `0-1`.
- Reuse one `PdfConverter` instance and update `converter.config["page_range"]` for each chunk.
- Install CPU-only torch after `marker-pdf`; the default wheel path can pull CUDA packages and waste memory.
- If the VM still OOMs, increase swap or lower the chunk size.

## Reference

See [references/zen-marker-workflow.md](references/zen-marker-workflow.md) for the tested VM settings and fallback commands.
