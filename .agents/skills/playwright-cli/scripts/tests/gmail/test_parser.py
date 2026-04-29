"""Tests for pwcli.gmail parser."""

from pathlib import Path

from pwcli.common import split_row_blocks
from pwcli.gmail import extract_emails, format_summary, _is_unread

FIXTURES = Path(__file__).parent / 'fixtures'


# ── _is_unread ───────────────────────────────────────────────────────

def test_is_unread_standard():
    block = _first_block('inbox.yml', 'Security alert')
    assert _is_unread(block) is True


def test_is_read_no_unread_label():
    block = _first_block('inbox.yml', 'feat: add new endpoint')
    assert _is_unread(block) is False


def test_is_unread_escaped_quotes():
    block = _first_block('inbox-escaped.yml', 'Microsoft Clarity')
    assert _is_unread(block) is True


# ── extract_emails (unread_only default) ─────────────────────────────

def test_unread_only_default():
    emails = extract_emails(FIXTURES / 'inbox.yml')
    senders = [e['sender'] for e in emails]
    assert 'Google' in senders
    assert 'corp . stmnts @ ici.' in senders
    assert 'GitHub' not in senders


def test_all_emails_with_flag():
    emails = extract_emails(FIXTURES / 'inbox.yml', unread_only=False)
    assert len(emails) == 3


def test_escaped_quotes_parsed():
    emails = extract_emails(FIXTURES / 'inbox-escaped.yml')
    assert len(emails) == 1
    assert emails[0]['sender'] == 'Microsoft Clarity'
    assert emails[0]['subject'] == 'Welcome to Clarity! You have new recordings.'


# ── sender extraction ────────────────────────────────────────────────

def test_sender_normal():
    emails = extract_emails(FIXTURES / 'inbox.yml', unread_only=False)
    senders = {e['sender'] for e in emails}
    assert 'Google' in senders
    assert 'GitHub' in senders
    assert 'corp . stmnts @ ici.' in senders


# ── subject extraction ───────────────────────────────────────────────

def test_subject_normal():
    emails = extract_emails(FIXTURES / 'inbox.yml', unread_only=False)
    subjects = {e['subject'] for e in emails}
    assert 'Security alert' in subjects
    assert 'Re: feat: add new endpoint' in subjects
    assert 'Account Statement from ICICI Bank' in subjects


# ── attachment detection ─────────────────────────────────────────────

def test_attachment_detected():
    emails = extract_emails(FIXTURES / 'inbox.yml', unread_only=False)
    icici = [e for e in emails if e['sender'] == 'corp . stmnts @ ici.'][0]
    assert 'attachments' in icici
    assert 'statement.txt' in icici['attachments']


def test_no_attachment_on_plain_email():
    emails = extract_emails(FIXTURES / 'inbox.yml', unread_only=False)
    google = [e for e in emails if e['sender'] == 'Google'][0]
    assert 'attachments' not in google


# ── timestamp extraction ─────────────────────────────────────────────

def test_timestamp_extracted():
    emails = extract_emails(FIXTURES / 'inbox.yml', unread_only=False)
    google = [e for e in emails if e['sender'] == 'Google'][0]
    assert google['timestamp'] == 'Wed, Apr 29, 2026, 5:36 PM'


# ── body / snippet ───────────────────────────────────────────────────

def test_snippet_extracted():
    emails = extract_emails(FIXTURES / 'inbox.yml', unread_only=False)
    google = [e for e in emails if e['sender'] == 'Google'][0]
    assert 'snippet' in google
    assert 'new sign-in' in google['snippet']


# ── format_summary ───────────────────────────────────────────────────

def test_format_summary_no_body():
    emails = extract_emails(FIXTURES / 'inbox.yml', unread_only=False)
    out = format_summary(emails)
    assert 'Google' in out
    assert 'Security alert' in out
    assert 'GitHub' in out
    assert '📎' in out


def test_format_summary_with_body():
    emails = extract_emails(FIXTURES / 'inbox.yml', unread_only=False)
    out = format_summary(emails, show_body=True)
    assert '────' in out
    assert 'new sign-in' in out


# ── split_row_blocks ────────────────────────────────────────────────

def test_split_row_blocks_count():
    with open(FIXTURES / 'inbox.yml') as f:
        content = f.read()
    blocks = split_row_blocks(content)
    assert len(blocks) == 3


def test_split_row_blocks_escaped():
    with open(FIXTURES / 'inbox-escaped.yml') as f:
        content = f.read()
    blocks = split_row_blocks(content)
    assert len(blocks) == 1


# ── helpers ──────────────────────────────────────────────────────────

def _first_block(name, hint):
    path = FIXTURES / name
    with open(path) as f:
        content = f.read()
    blocks = split_row_blocks(content)
    for b in blocks:
        if hint in b:
            return b
    raise AssertionError(f'No block containing "{hint}" in {path}')
