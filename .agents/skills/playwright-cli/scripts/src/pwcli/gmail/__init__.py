"""Parse gmail data from playwright-cli YAML snapshot."""

import re

from pwcli.common import split_row_blocks, cell_text, indent_of

SKIP_CELLS = {'Not starred', 'Not important'}
SKIP_PREFIXES = ('Important', 'Not starred', 'Not important')

MONTHS = r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)'
DAYS = r'(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)'


def extract_emails(filepath, unread_only=True):
    with open(filepath) as f:
        content = f.read()
    blocks = split_row_blocks(content)
    emails = []
    for b in blocks:
        e = _parse_block(b)
        if not e:
            continue
        if unread_only and not _is_unread(b):
            continue
        emails.append(e)
    return emails


def format_summary(emails, show_body=False):
    lines_out = []
    for i, e in enumerate(emails, 1):
        ts = e.get('timestamp', '')
        sender = e.get('sender', '?')
        subject = e.get('subject', '?')
        snippet = e.get('snippet', '')
        body = e.get('body', '')
        atts = e.get('attachments', [])

        ts_short = _short_ts(ts)

        line = f"{i:3d}. [{ts_short}] {sender}"
        if atts:
            line += " [📎]"
        lines_out.append(line)
        lines_out.append(f"     {subject}")

        if show_body:
            display = body or snippet
            if display:
                lines_out.append(f"     {'─' * 60}")
                lines_out.append(f"     {display}")
        elif snippet:
            s = snippet[:180]
            lines_out.append(f"     {s}{'…' if len(snippet) > 180 else ''}")

        lines_out.append('')
    return '\n'.join(lines_out)


# ── internal ─────────────────────────────────────────────────────────


def _is_unread(block):
    first = block.split('\n')[0]
    txt = first.split('"')[1] if '"' in first else ''
    parts = txt.split(',')
    return any('unread' in p.strip().lower() for p in parts[:3])


def _parse_block(block):
    lines = block.split('\n')
    email = {}

    _extract_sender(email, lines)
    _extract_subject(email, lines)
    _extract_timestamp(email, lines)
    _extract_body(email, lines)
    _extract_attachments(email, lines)

    if not email.get('subject') and not email.get('sender'):
        return None
    return email


def _extract_sender(email, lines):
    for i, line in enumerate(lines):
        ct = cell_text(line)
        if not ct or ct in SKIP_CELLS or ct.startswith(SKIP_PREFIXES):
            continue
        base = indent_of(line)
        for j in range(i + 1, min(i + 6, len(lines))):
            nl = lines[j]
            ni = indent_of(nl)
            if ni <= base:
                break
            m = re.search(r'- generic \[ref=e\d+\]:\s*(.*)$', nl)
            if not m:
                continue
            val = m.group(1).strip().strip('"')
            if val and val not in SKIP_CELLS | {'-'} and not val.isdigit():
                email['sender'] = val
                return


def _extract_subject(email, lines):
    for i, line in enumerate(lines):
        if 'link "' not in line:
            continue
        base = indent_of(line)
        for j in range(i + 1, min(i + 10, len(lines))):
            nl = lines[j]
            ni = indent_of(nl)
            if ni <= base:
                break
            m = re.search(r'- generic \[ref=e\d+\]:\s*(.*)$', nl)
            if m:
                val = m.group(1).strip().strip('"')
                if val and val != '-' and not val.startswith('[') and \
                   val not in SKIP_CELLS and len(val) > 2:
                    if 'subject' not in email:
                        email['subject'] = val
            tm = re.search(r'- text:\s+(.+)$', nl)
            if tm:
                val = tm.group(1).strip()
                if val:
                    email['snippet'] = val
        if 'subject' in email:
            return


def _extract_timestamp(email, lines):
    for line in lines:
        m = re.search(rf'gridcell "((?:{DAYS}), [^"]+)"', line)
        if m:
            email['timestamp'] = m.group(1)
            return
    for line in lines:
        m = re.search(rf'gridcell "({MONTHS} [^"]+)"', line)
        if m:
            email['timestamp'] = m.group(1)
            return


def _extract_body(email, lines):
    texts = []
    for line in lines:
        m = re.search(r'- text:\s+(.+)$', line)
        if m:
            val = m.group(1).strip()
            if val:
                texts.append(val)
    if texts:
        email['body'] = ' '.join(texts)


def _extract_attachments(email, lines):
    atts = []
    for i, line in enumerate(lines):
        m = re.search(r'Attachment:\s+(\S+)', line)
        if m:
            fname = m.group(1).strip().strip('"').rstrip('.')
            if fname and fname not in atts:
                atts.append(fname)
        m = re.search(r'generic\s+"([^"]+\.\w+)"', line)
        if m:
            fname = m.group(1).strip()
            is_attach = False
            for j in range(i + 1, min(i + 4, len(lines))):
                if 'Attachment:' in lines[j]:
                    is_attach = True
                    break
            if is_attach and fname not in atts:
                atts.append(fname)
    if atts:
        email['attachments'] = atts


def _short_ts(ts):
    if ',' in ts:
        parts = ts.split(',')
        if len(parts) >= 3:
            return f"{parts[1].strip()} {parts[2].strip()}"
    return ts
