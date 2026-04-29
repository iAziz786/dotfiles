"""Core scan logic — testable, no I/O side effects."""

import time
from pathlib import Path

TABS = [
    ('Primary', 'inbox'),
    ('Social', 'category/social'),
    ('Updates', 'category/updates'),
    ('Forums', 'category/forums'),
]


def find_new(before, after):
    """Return the newest file in `after` that wasn't in `before`, or None."""
    new_files = after - before
    if not new_files:
        return None
    return max(new_files, key=lambda f: f.stat().st_mtime)


def snapshot_paths(snap_dir):
    """Return set of page-*.yml paths in snap_dir. Creates dir if missing."""
    snap_dir.mkdir(parents=True, exist_ok=True)
    return set(snap_dir.glob('page-*.yml'))


def tab_url(account, tab_path):
    return f"https://mail.google.com/mail/u/{account}/#{tab_path}"


def collect_snapshots(snap_dir, account, goto_fn, wait_fn=None):
    """Go through each tab, call goto_fn(url), wait, yield (label, path).

    Yields (label, Path) for tabs where goto_fn produced a new snapshot file.
    """
    if wait_fn is None:
        wait_fn = lambda: time.sleep(2)

    before = snapshot_paths(snap_dir)
    for label, path in TABS:
        goto_fn(tab_url(account, path))
        wait_fn()
        after = snapshot_paths(snap_dir)
        new = find_new(before, after)
        if new:
            yield label, new
        before = after


def parse_each(parse_fn, snapshots):
    """Run parse_fn on each snapshot, yield (label, output)."""
    for label, path in snapshots:
        output = parse_fn(path)
        yield label, output


def format_results(results):
    """Format (label, output) pairs into a printable summary."""
    lines = []
    for label, output in results:
        if not output:
            continue
        lines.append(f"  ── {label} ──\n")
        lines.append(output)
        lines.append('')
    return '\n'.join(lines)
