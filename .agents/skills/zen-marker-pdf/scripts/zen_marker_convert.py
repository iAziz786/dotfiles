#!/usr/bin/env python3
"""Convert a local PDF to markdown through the ssh `zen` VM using marker.

The script bootstraps the remote VM if needed, forces CPU-only torch,
ensures swap exists when possible, converts in chunks, and downloads the
resulting markdown back to the local machine.
"""

from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
import textwrap
from pathlib import Path


DEFAULT_REMOTE = "zen"
DEFAULT_REMOTE_VENV = "/tmp/marker-venv"
DEFAULT_REMOTE_SWAP_GB = 12
DEFAULT_CHUNK_SIZE = 50


def run(cmd: list[str], *, input_text: str | None = None) -> str:
    result = subprocess.run(
        cmd,
        input=input_text,
        text=True,
        capture_output=True,
        check=True,
    )
    if result.stderr:
        sys.stderr.write(result.stderr)
    return result.stdout


def ssh_shell(remote: str, script: str) -> str:
    return run(["ssh", remote, "bash", "-s"], input_text=script)


def scp_to(remote: str, local_path: Path, remote_path: str) -> None:
    subprocess.run(["scp", str(local_path), f"{remote}:{remote_path}"], check=True)


def scp_from(remote: str, remote_path: str, local_path: Path) -> None:
    subprocess.run(["scp", f"{remote}:{remote_path}", str(local_path)], check=True)


def ensure_remote_venv(remote: str, venv: str) -> None:
    bootstrap = textwrap.dedent(
        f"""
        set -euo pipefail

        if [ ! -x {shlex.quote(venv)}/bin/python ]; then
          if ! python3 -m venv {shlex.quote(venv)} >/dev/null 2>&1; then
            sudo apt-get update
            sudo apt-get install -y python3.12-venv
            python3 -m venv {shlex.quote(venv)}
          fi
          {shlex.quote(venv)}/bin/pip install --upgrade pip
          {shlex.quote(venv)}/bin/pip install marker-pdf
        fi

        if ! {shlex.quote(venv)}/bin/python - <<'PY'
        import importlib.util
        import sys

        sys.exit(0 if importlib.util.find_spec("marker") else 1)
        PY
        then
          {shlex.quote(venv)}/bin/pip install marker-pdf
        fi

        if ! {shlex.quote(venv)}/bin/python - <<'PY'
        import torch
        import sys

        sys.exit(0 if "+cpu" in torch.__version__ else 1)
        PY
        then
          {shlex.quote(venv)}/bin/pip install --force-reinstall --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch
        fi
        """
    ).strip()
    ssh_shell(remote, bootstrap)


def ensure_remote_swap(remote: str, size_gb: int) -> None:
    current = run(["ssh", remote, "swapon", "--show"])
    if "/swapfile" in current:
        return

    swap_script = textwrap.dedent(
        f"""
        set -euo pipefail
        if [ -f /swapfile ]; then
          sudo swapoff /swapfile || true
          sudo rm -f /swapfile
        fi
        sudo fallocate -l {size_gb}G /swapfile
        sudo chmod 600 /swapfile
        sudo mkswap /swapfile
        sudo swapon /swapfile
        swapon --show
        """
    ).strip()
    ssh_shell(remote, swap_script)


def remote_convert(
    remote: str, venv: str, pdf_path: str, out_path: str, chunk_size: int
) -> None:
    python_script = textwrap.dedent(
        f"""
        from pathlib import Path
        import gc
        import sys

        from marker.converters.pdf import PdfConverter
        from marker.models import create_model_dict
        from marker.providers.pdf import PdfProvider

        pdf_path = {pdf_path!r}
        out_path = Path({out_path!r})
        chunk_size = {chunk_size}

        artifact_dict = create_model_dict()
        converter = PdfConverter(
            artifact_dict=artifact_dict,
            processor_list=[
                "marker.processors.order.OrderProcessor",
                "marker.processors.text.TextProcessor",
            ],
            renderer="marker.renderers.markdown.MarkdownRenderer",
            config={
            "disable_ocr": True,
                "force_layout_block": "Text",
                "disable_image_extraction": True,
                "pdftext_workers": 1,
            },
        )

        provider = PdfProvider(
            pdf_path,
            {
            "disable_ocr": True,
                "force_layout_block": "Text",
                "page_range": [0],
            },
        )
        page_count = provider.page_count
        print(f"pages: {page_count}", file=sys.stderr)

        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as out:
            for start in range(0, page_count, chunk_size):
                end = min(start + chunk_size - 1, page_count - 1)
                converter.config["page_range"] = list(range(start, end + 1))
                rendered = converter(pdf_path)
                if start:
                    out.write("\n\n")
                out.write(f"<!-- pages {start}-{end} -->\n\n")
                out.write(rendered.markdown.rstrip())
                out.write("\n")
                print(f"chunk {start}-{end} done", file=sys.stderr)
                del rendered
                gc.collect()

        print(out_path)
        """
    ).strip()
    env = os.environ.copy()
    env["TORCH_DEVICE"] = "cpu"
    subprocess.run(
        ["ssh", remote, "env", "TORCH_DEVICE=cpu", f"{venv}/bin/python", "-"],
        input=python_script,
        text=True,
        check=True,
        env=env,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a local PDF to markdown through ssh zen using marker.",
    )
    parser.add_argument("input_pdf", type=Path, help="Local PDF to convert")
    parser.add_argument(
        "--output",
        type=Path,
        help="Local markdown path. Defaults to /tmp/<pdf-stem>.md",
    )
    parser.add_argument("--remote", default=DEFAULT_REMOTE, help="SSH host alias")
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=DEFAULT_CHUNK_SIZE,
        help="Pages per remote marker chunk",
    )
    parser.add_argument(
        "--remote-venv",
        default=DEFAULT_REMOTE_VENV,
        help="Remote virtualenv path",
    )
    parser.add_argument(
        "--swap-size-gb",
        type=int,
        default=DEFAULT_REMOTE_SWAP_GB,
        help="Swap size to create on the remote host if none exists",
    )
    parser.add_argument(
        "--keep-remote",
        action="store_true",
        help="Keep the remote temp directory after download",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not args.input_pdf.exists():
        raise SystemExit(f"Input PDF not found: {args.input_pdf}")

    output = args.output or Path("/tmp") / f"{args.input_pdf.stem}.md"
    output.parent.mkdir(parents=True, exist_ok=True)

    remote_tmp = run(
        ["ssh", args.remote, "mktemp", "-d", "/tmp/marker-work.XXXXXX"]
    ).strip()
    remote_pdf = f"{remote_tmp}/input.pdf"
    remote_md = f"{remote_tmp}/output.md"

    try:
        scp_to(args.remote, args.input_pdf, remote_pdf)
        ensure_remote_venv(args.remote, args.remote_venv)
        ensure_remote_swap(args.remote, args.swap_size_gb)
        remote_convert(
            args.remote, args.remote_venv, remote_pdf, remote_md, args.chunk_size
        )
        scp_from(args.remote, remote_md, output)
    finally:
        if not args.keep_remote:
            subprocess.run(["ssh", args.remote, "rm", "-rf", remote_tmp], check=False)

    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
