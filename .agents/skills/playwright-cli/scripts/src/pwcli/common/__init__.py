"""Shared utilities for parsing playwright-cli YAML snapshots."""

import re


def split_row_blocks(content, min_indent=4):
    """Split YAML content into per-row blocks.

    Each block starts with a `- row "..."` or `- 'row "..."'` line
    (single-quoted variant occurs when the text contains escaped quotes).
    """
    starts = [m.start() for m in re.finditer(
        rf'^(\s{{{min_indent},}})- \'?row "', content, re.MULTILINE)]
    blocks = []
    for i, s in enumerate(starts):
        e = starts[i + 1] if i + 1 < len(starts) else len(content)
        blocks.append(content[s:e])
    return blocks


def cell_text(line):
    """Extract the text inside a gridcell from a YAML line."""
    m = re.search(r'gridcell "([^"]+)"', line)
    return m.group(1) if m else ''


def indent_of(line):
    return len(line) - len(line.lstrip())
