#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["feedparser", "httpx", "beautifulsoup4", "lxml"]
# ///
"""
feeder.py — RSS Feeder skill helper script.

Subcommands:
  fetch           Parse OPML and fetch all RSS feeds for last N days.
                  Outputs JSON: [{category, feed_name, feed_url, posts: [{title, url, published, description}]}]

  resolve-url     Resolve any URL (YouTube channel, nitter-wrapped X, plain RSS/Atom)
                  to a canonical RSS/Atom feed URL.
                  Outputs JSON: {resolved_url, title, type}

  list-categories List all category names from the OPML.
                  Outputs JSON: ["Cloud", "AI", ...]

  add-feed        Append a new feed to the OPML under a given category.
                  Skips silently if URL already exists.

  remove-feed     Remove a feed from the OPML by URL.

Usage examples:
  uv run feeder.py fetch --opml ../assets/feeds.opml --days 1
  uv run feeder.py resolve-url --url "https://www.youtube.com/@veritasium"
  uv run feeder.py list-categories --opml ../assets/feeds.opml
  uv run feeder.py add-feed --opml ../assets/feeds.opml --category "Science" --url "https://example.com/feed.xml" --title "Example Blog"
  uv run feeder.py remove-feed --opml ../assets/feeds.opml --url "https://example.com/feed.xml"
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from xml.etree import ElementTree as ET


# ---------------------------------------------------------------------------
# OPML helpers
# ---------------------------------------------------------------------------


def load_opml(opml_path: str) -> ET.ElementTree:
    tree = ET.parse(opml_path)
    return tree


def save_opml(tree: ET.ElementTree, opml_path: str) -> None:
    ET.indent(tree, space="  ")
    tree.write(opml_path, encoding="UTF-8", xml_declaration=True)


def iter_feeds(root: ET.Element, parent_category: str = "") -> list[dict]:
    """
    Walk the OPML outline tree and yield flat feed records.
    Returns list of {category, title, xml_url, html_url, attrs}.
    """
    feeds = []
    for outline in root.findall("outline"):
        feed_type = outline.get("type", "")
        title = outline.get("title") or outline.get("text", "")
        xml_url = outline.get("xmlUrl", "")

        if feed_type == "rss" and xml_url:
            feeds.append(
                {
                    "category": parent_category,
                    "title": title,
                    "xml_url": xml_url,
                    "html_url": outline.get("htmlUrl", ""),
                }
            )
        else:
            # It's a folder/category outline — recurse
            child_category = title if title else parent_category
            feeds.extend(iter_feeds(outline, child_category))
    return feeds


def all_xml_urls(root: ET.Element) -> set[str]:
    return {f["xml_url"] for f in iter_feeds(root)}


def find_category_outline(parent: ET.Element, category: str) -> ET.Element | None:
    """
    Recursively find a folder outline matching category name (case-insensitive).
    Searches all levels of the OPML hierarchy so nested categories like
    'k8s' (inside Cloud) and 'Safety' (inside AI) are reachable.
    """
    for outline in parent.findall("outline"):
        if outline.get("type") == "rss":
            continue  # Feed entry, not a folder
        title = outline.get("title") or outline.get("text", "")
        if title.lower() == category.lower():
            return outline
        # Recurse into subcategories
        found = find_category_outline(outline, category)
        if found is not None:
            return found
    return None


# ---------------------------------------------------------------------------
# subcommand: list-categories
# ---------------------------------------------------------------------------


def cmd_list_categories(args: argparse.Namespace) -> None:
    tree = load_opml(args.opml)
    body = tree.getroot().find("body")
    categories = _collect_categories(body)
    print(json.dumps(categories, ensure_ascii=False, indent=2))


def _collect_categories(parent: ET.Element, path_prefix: str = "") -> list[str]:
    """
    Recursively collect all category folder names from the OPML.
    Nested categories are returned with their path, e.g. 'Cloud/k8s'.
    Top-level categories are returned without a prefix.
    """
    categories = []
    for outline in parent.findall("outline"):
        if outline.get("type") == "rss":
            continue  # Skip feed entries
        title = outline.get("title") or outline.get("text", "")
        if not title:
            continue
        full_name = f"{path_prefix}/{title}" if path_prefix else title
        categories.append(full_name)
        # Recurse for nested subcategories
        categories.extend(_collect_categories(outline, full_name))
    return categories


# ---------------------------------------------------------------------------
# subcommand: fetch
# ---------------------------------------------------------------------------


def cmd_fetch(args: argparse.Namespace) -> None:
    import feedparser

    tree = load_opml(args.opml)
    body = tree.getroot().find("body")
    feeds = iter_feeds(body)

    cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)

    results = []
    errors = []

    for feed in feeds:
        xml_url = feed["xml_url"]
        try:
            parsed = feedparser.parse(xml_url)
            # feedparser swallows HTTP errors — check status explicitly
            http_status = getattr(parsed, "status", 200)
            if http_status >= 400:
                raise RuntimeError(f"HTTP {http_status}")
            # bozo indicates a malformed feed; only raise if no entries were parsed
            if parsed.get("bozo") and not parsed.entries:
                exc = parsed.get("bozo_exception")
                if exc:
                    raise exc
            posts = []
            for entry in parsed.entries:
                # Determine published date; fall back to updated
                pub = entry.get("published_parsed") or entry.get("updated_parsed")
                if pub:
                    pub_dt = datetime(*pub[:6], tzinfo=timezone.utc)
                else:
                    pub_dt = None

                if pub_dt and pub_dt < cutoff:
                    continue  # Too old

                posts.append(
                    {
                        "title": entry.get("title", "(no title)"),
                        "url": entry.get("link", ""),
                        "published": pub_dt.isoformat() if pub_dt else None,
                        "description": _clean_html(
                            entry.get("summary")
                            or entry.get("content", [{}])[0].get("value", "")
                        ),
                    }
                )

            if posts:
                results.append(
                    {
                        "category": feed["category"],
                        "feed_name": feed["title"],
                        "feed_url": xml_url,
                        "posts": posts,
                    }
                )
        except Exception as exc:
            errors.append(
                {
                    "feed_name": feed["title"],
                    "feed_url": xml_url,
                    "error": str(exc),
                }
            )

    output = {"results": results, "errors": errors}
    print(json.dumps(output, ensure_ascii=False, indent=2))


def _clean_html(html: str) -> str:
    """Strip HTML tags, return plain text truncated to ~500 chars for context."""
    from bs4 import BeautifulSoup

    if not html:
        return ""
    text = BeautifulSoup(html, "lxml").get_text(separator=" ", strip=True)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text[:500] if len(text) > 500 else text


# ---------------------------------------------------------------------------
# subcommand: resolve-url
# ---------------------------------------------------------------------------


def cmd_resolve_url(args: argparse.Namespace) -> None:
    url = args.url.strip()
    result = resolve_url(url, nitter_base=args.nitter_base or "")
    print(json.dumps(result, ensure_ascii=False, indent=2))


def resolve_url(url: str, nitter_base: str = "") -> dict:
    """
    Given any URL, return {resolved_url, title, type, warning?}.
    Types: rss, atom, youtube, nitter, unknown
    """
    import httpx

    # Already looks like a feed URL
    if _looks_like_feed(url):
        return {"resolved_url": url, "title": "", "type": "rss"}

    # YouTube channel URL patterns
    yt_match = _match_youtube(url)
    if yt_match:
        return _resolve_youtube(url, yt_match)

    # X / Twitter
    x_match = _match_twitter(url)
    if x_match:
        return _resolve_twitter(x_match, nitter_base)

    # Try fetching the page and looking for <link rel="alternate" type="application/rss+xml">
    try:
        resp = httpx.get(url, follow_redirects=True, timeout=15)
        resp.raise_for_status()
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(resp.text, "lxml")
        for link in soup.find_all(
            "link", type=re.compile(r"application/(rss|atom)\+xml")
        ):
            feed_href = link.get("href", "")
            if feed_href:
                if not feed_href.startswith("http"):
                    # Relative URL — make it absolute
                    from urllib.parse import urljoin

                    feed_href = urljoin(url, feed_href)
                title = link.get("title", "")
                return {"resolved_url": feed_href, "title": title, "type": "rss"}
    except Exception as exc:
        return {
            "resolved_url": url,
            "title": "",
            "type": "unknown",
            "warning": str(exc),
        }

    return {
        "resolved_url": url,
        "title": "",
        "type": "unknown",
        "warning": "Could not detect a feed URL for this page. Please provide the RSS/Atom URL directly.",
    }


def _looks_like_feed(url: str) -> bool:
    feed_indicators = [
        "feed.xml",
        "feed.atom",
        "rss.xml",
        "atom.xml",
        "/rss",
        "/feed",
        "/feeds/",
        ".rss",
        ".atom",
        "feeds/videos.xml",
        "posts.atom",
        "index.xml",
        "/blog/rss",
    ]
    lower = url.lower()
    return any(ind in lower for ind in feed_indicators)


def _match_youtube(url: str) -> tuple[str, str] | None:
    """Return (kind, identifier) tuple where kind is 'channel_id' or 'handle', or None."""
    patterns = [
        (r"youtube\.com/channel/([A-Za-z0-9_-]+)", "channel_id"),
        (r"youtube\.com/@([A-Za-z0-9_.-]+)", "handle"),
        (r"youtube\.com/c/([A-Za-z0-9_-]+)", "handle"),
        (r"youtube\.com/user/([A-Za-z0-9_-]+)", "handle"),
    ]
    for pattern, kind in patterns:
        m = re.search(pattern, url)
        if m:
            return (kind, m.group(1))
    return None


def _resolve_youtube(original_url: str, match: tuple) -> dict:
    import httpx

    kind, identifier = match

    if kind == "channel_id":
        rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={identifier}"
        return {"resolved_url": rss_url, "title": "", "type": "youtube"}

    # handle — need to scrape the channel page for the actual channel_id
    try:
        resp = httpx.get(
            original_url,
            follow_redirects=True,
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0 (compatible; RSS-Feeder-Skill/1.0)"},
        )
        resp.raise_for_status()
        # Look for channel_id in og:url or in page source
        m = re.search(r'"channelId"\s*:\s*"([A-Za-z0-9_-]+)"', resp.text)
        if not m:
            m = re.search(r"channel_id=([A-Za-z0-9_-]+)", resp.text)
        if not m:
            # Try og:url meta tag
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(resp.text, "lxml")
            og_url = soup.find("meta", property="og:url")
            if og_url:
                m2 = re.search(r"/channel/([A-Za-z0-9_-]+)", og_url.get("content", ""))
                if m2:
                    channel_id = m2.group(1)
                    rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
                    return {"resolved_url": rss_url, "title": "", "type": "youtube"}

        if m:
            channel_id = m.group(1)
            rss_url = (
                f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
            )
            return {"resolved_url": rss_url, "title": "", "type": "youtube"}

    except Exception as exc:
        return {
            "resolved_url": original_url,
            "title": "",
            "type": "unknown",
            "warning": f"Could not extract YouTube channel_id: {exc}",
        }

    return {
        "resolved_url": original_url,
        "title": "",
        "type": "unknown",
        "warning": "Could not extract YouTube channel_id from page. Try providing the channel URL with /channel/ID directly.",
    }


def _match_twitter(url: str) -> str | None:
    """Return Twitter/X username or None."""
    m = re.search(r"(?:twitter\.com|x\.com)/([A-Za-z0-9_]+)(?:/|$)", url)
    if m and m.group(1) not in ("i", "home", "explore", "notifications", "messages"):
        return m.group(1)
    return None


def _resolve_twitter(username: str, nitter_base: str) -> dict:
    if not nitter_base:
        return {
            "resolved_url": "",
            "title": f"@{username}",
            "type": "twitter",
            "warning": (
                f"X/Twitter accounts have no public RSS feed. "
                f"Set nitter_base_url in SKILL.md config to enable. "
                f"Example: https://nitter.net — then the feed would be "
                f"{{nitter_base}}/{username}/rss"
            ),
        }
    base = nitter_base.rstrip("/")
    rss_url = f"{base}/{username}/rss"
    return {"resolved_url": rss_url, "title": f"@{username}", "type": "nitter"}


# ---------------------------------------------------------------------------
# subcommand: add-feed
# ---------------------------------------------------------------------------


def cmd_add_feed(args: argparse.Namespace) -> None:
    tree = load_opml(args.opml)
    root = tree.getroot()
    body = root.find("body")

    existing = all_xml_urls(body)
    if args.url in existing:
        print(json.dumps({"status": "skipped", "reason": "URL already exists in OPML"}))
        return

    category_outline = find_category_outline(body, args.category)
    if category_outline is None:
        # Create new category
        category_outline = ET.SubElement(
            body,
            "outline",
            {
                "title": args.category,
                "text": args.category,
            },
        )

    ET.SubElement(
        category_outline,
        "outline",
        {
            "text": args.title,
            "title": args.title,
            "type": "rss",
            "xmlUrl": args.url,
            "htmlUrl": args.html_url or "",
            "rssfr-numPosts": "0",
            "rssfr-useNotifications": "0",
            "rssfr-updateInterval": "",
        },
    )

    save_opml(tree, args.opml)
    print(
        json.dumps(
            {
                "status": "added",
                "category": args.category,
                "title": args.title,
                "url": args.url,
            }
        )
    )


# ---------------------------------------------------------------------------
# subcommand: remove-feed
# ---------------------------------------------------------------------------


def cmd_remove_feed(args: argparse.Namespace) -> None:
    tree = load_opml(args.opml)
    root = tree.getroot()
    body = root.find("body")

    removed = _remove_feed_recursive(body, args.url)
    if removed:
        save_opml(tree, args.opml)
        print(json.dumps({"status": "removed", "url": args.url}))
    else:
        print(json.dumps({"status": "not_found", "url": args.url}))


def _remove_feed_recursive(parent: ET.Element, url: str) -> bool:
    for child in list(parent):
        if child.get("xmlUrl") == url:
            parent.remove(child)
            return True
        if _remove_feed_recursive(child, url):
            return True
    return False


# ---------------------------------------------------------------------------
# CLI wiring
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="RSS Feeder skill helper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # fetch
    p_fetch = sub.add_parser(
        "fetch", help="Fetch recent posts from all feeds in the OPML"
    )
    p_fetch.add_argument("--opml", required=True, help="Path to feeds.opml")
    p_fetch.add_argument(
        "--days", type=int, default=1, help="Look back N days (default: 1)"
    )

    # resolve-url
    p_resolve = sub.add_parser(
        "resolve-url", help="Resolve any URL to a canonical RSS/Atom feed URL"
    )
    p_resolve.add_argument("--url", required=True, help="URL to resolve")
    p_resolve.add_argument(
        "--nitter-base",
        default="",
        help="Nitter instance base URL for X/Twitter accounts",
    )

    # list-categories
    p_cats = sub.add_parser(
        "list-categories", help="List all category names from the OPML"
    )
    p_cats.add_argument("--opml", required=True, help="Path to feeds.opml")

    # add-feed
    p_add = sub.add_parser("add-feed", help="Add a feed to the OPML")
    p_add.add_argument("--opml", required=True, help="Path to feeds.opml")
    p_add.add_argument(
        "--category", required=True, help="Category name (existing or new)"
    )
    p_add.add_argument("--url", required=True, help="RSS/Atom feed URL")
    p_add.add_argument("--title", required=True, help="Feed title/name")
    p_add.add_argument(
        "--html-url", default="", help="Optional: HTML page URL for the feed"
    )

    # remove-feed
    p_remove = sub.add_parser("remove-feed", help="Remove a feed from the OPML by URL")
    p_remove.add_argument("--opml", required=True, help="Path to feeds.opml")
    p_remove.add_argument("--url", required=True, help="RSS/Atom feed URL to remove")

    args = parser.parse_args()

    dispatch = {
        "fetch": cmd_fetch,
        "resolve-url": cmd_resolve_url,
        "list-categories": cmd_list_categories,
        "add-feed": cmd_add_feed,
        "remove-feed": cmd_remove_feed,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
