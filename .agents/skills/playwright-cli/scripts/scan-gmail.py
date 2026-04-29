#!/usr/bin/env python3
"""Go through all Gmail tabs, snapshot each, then scan for actionable emails.

Usage:
  python3 scan-gmail.py [account_index]
  python3 scan-gmail.py 1   (second account)
"""

import subprocess
import sys
import time
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pwcli.gmail.scan import collect_snapshots, parse_each, format_results

SCRIPT_DIR = Path(__file__).resolve().parent
PARSE_SCRIPT = SCRIPT_DIR / 'parse-gmail-snapshot.py'
SNAP_DIR = Path.cwd() / '.playwright-cli'


def run(cmd, check=False):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if check and r.returncode != 0:
        print(f"Error: {' '.join(cmd)} failed:\n{r.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    return r


def check_session():
    r = run(['bunx', 'playwright-cli', 'list'])
    if 'status: open' not in r.stdout:
        print("No browser session open. Run first:\n  bunx playwright-cli open https://mail.google.com --headed",
              file=sys.stderr)
        sys.exit(1)


def main():
    account = sys.argv[1] if len(sys.argv) > 1 else '0'
    check_session()

    def goto(url):
        r = run(['bunx', 'playwright-cli', 'goto', url])
        if r.returncode != 0:
            print(f"  goto failed: {r.stderr.strip()}")

    snapshots = list(collect_snapshots(SNAP_DIR, account, goto))

    if not snapshots:
        all_snaps = list(SNAP_DIR.glob('page-*.yml'))
        if all_snaps:
            print("No new snapshots taken — existing snapshots found.")
            print(f"({len(all_snaps)} files in {SNAP_DIR})")
        else:
            print(f"No snapshots taken. Check that browser is open and Gmail is loaded.")
            print(f"  Snap dir: {SNAP_DIR}")
            print(f"  Dir exists: {SNAP_DIR.exists()}")
        return

    def parse(path):
        r = subprocess.run(
            [sys.executable, str(PARSE_SCRIPT), str(path)],
            capture_output=True, text=True, timeout=15)
        return r.stdout.strip()

    results = list(parse_each(parse, snapshots))
    out = format_results(results)

    print(f"{'=' * 60}")
    print(f"  Unread emails across all tabs (account {account})")
    print(f"{'=' * 60}\n")
    print(out if out else "  No unread emails found.\n")


if __name__ == '__main__':
    main()
