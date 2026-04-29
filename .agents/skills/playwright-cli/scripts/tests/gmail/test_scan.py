"""Tests for pwcli.gmail.scan."""

from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from pwcli.gmail.scan import (
    find_new, snapshot_paths, tab_url, collect_snapshots, parse_each, format_results, TABS,
)


# ── find_new ─────────────────────────────────────────────────────────

def test_find_new_returns_newest(tmp_path):
    (tmp_path / 'a.yml').write_text('')
    (tmp_path / 'b.yml').write_text('')
    before = {tmp_path / 'a.yml', tmp_path / 'b.yml'}
    (tmp_path / 'c.yml').write_text('')
    after = before | {tmp_path / 'c.yml'}
    result = find_new(before, after)
    assert result == tmp_path / 'c.yml'


def test_find_new_returns_none_when_no_new():
    before = {Path('/d/a.yml'), Path('/d/b.yml')}
    after = before
    assert find_new(before, after) is None


def test_find_new_returns_none_when_superset_but_empty():
    assert find_new(set(), set()) is None


# ── tab_url ──────────────────────────────────────────────────────────

def test_tab_url_primary():
    assert tab_url('0', 'inbox') == 'https://mail.google.com/mail/u/0/#inbox'


def test_tab_url_category():
    assert tab_url('1', 'category/social') == 'https://mail.google.com/mail/u/1/#category/social'


# ── format_results ───────────────────────────────────────────────────

def test_format_results_single():
    results = [('Primary', '1. sender\n   subject')]
    out = format_results(results)
    assert 'Primary' in out
    assert 'sender' in out
    assert 'subject' in out


def test_format_results_multiple():
    results = [
        ('Primary', '1. A\n   x'),
        ('Social', '2. B\n   y'),
    ]
    out = format_results(results)
    assert 'Primary' in out
    assert 'Social' in out
    assert 'A' in out
    assert 'B' in out


def test_format_results_empty_output_skipped():
    results = [('Primary', '')]
    assert format_results(results) == ''


def test_format_results_all_empty():
    results = [('Primary', ''), ('Social', '')]
    assert format_results(results) == ''


# ── parse_each ───────────────────────────────────────────────────────

def test_parse_each_yields_output():
    def fake_parse(path):
        return f"parsed:{path.name}"

    snaps = [('Inbox', Path('/d/snap1.yml')), ('Social', Path('/d/snap2.yml'))]
    results = list(parse_each(fake_parse, snaps))
    assert len(results) == 2
    assert results[0] == ('Inbox', 'parsed:snap1.yml')
    assert results[1] == ('Social', 'parsed:snap2.yml')


# ── collect_snapshots (integration-style) ────────────────────────────

def test_collect_snapshots_empty_when_no_snap_dir(tmp_path):
    snap_dir = tmp_path / '.playwright-cli'
    snap_dir.mkdir()
    calls = []

    def goto(url):
        calls.append(url)
        # Simulate creating a snapshot after goto
        (snap_dir / f'page-{len(calls)}.yml').write_text('')

    results = list(collect_snapshots(snap_dir, '0', goto, wait_fn=lambda: None))
    assert len(results) == len(TABS)
    assert len(calls) == len(TABS)
    for i, (label, path) in enumerate(results):
        assert label == TABS[i][0]
        assert path.exists()
        assert path.parent == snap_dir


def test_collect_snapshots_no_new_file_still_calls_goto(tmp_path):
    """If goto doesn't produce a snapshot, that tab is skipped."""
    snap_dir = tmp_path / '.playwright-cli'
    snap_dir.mkdir()
    calls = []

    def goto(url):
        calls.append(url)
        # Don't create any snapshot

    results = list(collect_snapshots(snap_dir, '0', goto, wait_fn=lambda: None))
    assert len(results) == 0  # no snapshots produced
    assert len(calls) == len(TABS)  # but all tabs were visited


# ── snapshot_paths ───────────────────────────────────────────────────

def test_snapshot_paths_empty_dir(tmp_path):
    d = tmp_path / '.playwright-cli'
    assert not d.exists()
    paths = snapshot_paths(d)
    assert d.exists()  # creates the dir
    assert paths == set()


def test_snapshot_paths_finds_yml(tmp_path):
    d = tmp_path / '.playwright-cli'
    d.mkdir()
    (d / 'page-1.yml').write_text('')
    (d / 'page-2.yml').write_text('')
    (d / 'readme.txt').write_text('')
    paths = snapshot_paths(d)
    assert len(paths) == 2
    assert all(p.suffix == '.yml' for p in paths)
    assert all('page-' in p.name for p in paths)
