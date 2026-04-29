---
name: rss-feeder
description: >
  Use when the user asks "what's new in my feeds", "check my feeds",
  "what's updated today", "what's new in Kubernetes this week", "latest from
  AWS", "what's happening in AI", "add a feed", "remove a feed", "subscribe
  to", or any question about recent updates from a topic that might be in the
  feed list. Manages RSS/Atom feeds from a personal OPML file: fetches and
  summarises recent posts by category, adds feeds (including YouTube channels
  and X/Twitter via nitter), and removes feeds.
license: MIT
compatibility: Requires Python 3.11+, uv, and internet access. Playwright MCP optional for JS-rendered pages.
metadata:
  author: iAziz786
  version: "1.0"
---

# RSS Feeder

Fetches, summarises, and manages feeds from a personal OPML subscription list stored in `assets/feeds.opml`.

## Config

> Edit these values to change defaults. **Read this block at skill activation before starting any workflow.**

```yaml
default_days: 1
nitter_base_url: ""     # e.g. https://nitter.net — enables X/Twitter feeds
max_words_per_post: 150
```

## When To Use

- "check my feeds" / "what's new in my feeds"
- "what's updated today" / "what happened this week"
- "what's new in Kubernetes / AWS / AI / Postgres / ..."
- "latest from [any source in my feeds]"
- "add a feed" / "subscribe to X"
- "remove a feed" / "unsubscribe from X"

## Paths (relative to skill root)

- OPML: `assets/feeds.opml`
- Script: `scripts/feeder.py`
- Skill root: `.agents/skills/rss-feeder/`

All `--opml` arguments must be the **absolute path** to `assets/feeds.opml`.
Resolve it from the skill root before running any command.

---

## Workflow 1: check-updates

### Step 1 — Determine the time window

- Default lookback: `default_days` from config (1 day).
- If the user specifies a period ("last 3 days", "this week"), use that instead.
- Convert to an integer number of days.

### Step 2 — Fetch feed metadata

Run:
```bash
uv run scripts/feeder.py fetch --opml <abs-path-to-feeds.opml> --days <N>
```

This returns JSON:
```json
{
  "results": [
    {
      "category": "Cloud",
      "feed_name": "AWS News Blog",
      "feed_url": "...",
      "posts": [
        {
          "title": "...",
          "url": "...",
          "published": "2026-04-15T10:00:00+00:00",
          "description": "...short plain-text from RSS..."
        }
      ]
    }
  ],
  "errors": [
    {"feed_name": "...", "feed_url": "...", "error": "..."}
  ]
}
```

Note any feeds in `errors` — they will be reported as `[unavailable]` in output.

### Step 3 — Crawl article pages (parallel agents)

For each feed object in `results`, launch one parallel sub-agent. Each agent receives:
- The feed name and category
- The list of posts (title, url, rss description)
- These instructions:

> For each post:
> 1. Attempt to fetch the full article at `url`.
>    - If Playwright MCP is available, use it first (handles JS-rendered pages).
>    - Otherwise use WebFetch.
> 2. If fetch returns no meaningful content (403, empty body, paywall gate, pure JS shell):
>    fall back to the `description` field from the RSS feed and append `[paywalled/JS-required]` to the summary.
> 3. Summarise the article in at most `max_words_per_post` words (150 by default).
> 4. Return a list: `[{title, url, published, summary}]`

Collect all per-feed results.

### Step 4 — Assemble and format output

Group by OPML category. Within each category, list feeds alphabetically.

Use this output template:

```
## <Category>

### <Feed Name>
- **[<Title>](<url>)** — <one-line date>
  <summary paragraph, ≤150 words>

- **[<Title>](<url>)** ...

[+N more posts not shown]   ← if feed has >10 posts this period
```

After all categories, if there were fetch errors:

```
---
### Unavailable feeds
- **<Feed Name>** — <error reason>
```

If a category had zero posts in the time window, omit it entirely.

---

## Workflow 2: add-feed

### Step 1 — List existing categories

Run:
```bash
uv run scripts/feeder.py list-categories --opml <abs-path-to-feeds.opml>
```

Returns JSON array of category name strings.

### Step 2 — Present category picker

Show the user a numbered list:
```
Existing categories:
1. Cloud
2. Science
3. AI
...
N. [New category]
```

Ask: "Which category should this feed go in? (pick a number or type a new name)"

### Step 3 — Ask for the feed URL

Ask: "What is the URL for the feed? (can be a YouTube channel, RSS/Atom URL, or website)"

### Step 4 — Resolve the URL

Run:
```bash
uv run scripts/feeder.py resolve-url --url "<url>" [--nitter-base "<nitter_base_url>"]
```

Returns:
```json
{
  "resolved_url": "https://...",
  "title": "optional detected title",
  "type": "rss|atom|youtube|nitter|unknown",
  "warning": "optional warning message"
}
```

Handle each case:
- **`rss` / `atom` / `youtube` / `nitter`**: proceed with `resolved_url`.
- **`unknown` with warning**: show the warning to the user and ask them to provide the correct RSS/Atom URL directly.
- **`twitter` with no nitter_base_url set**: inform the user that X/Twitter requires a nitter bridge. Show the instruction to set `nitter_base_url` in SKILL.md config and stop.

### Step 5 — Confirm with user

Show:
```
Feed to add:
  Title:    <title or ask user>
  URL:      <resolved_url>
  Category: <chosen category>

Add this feed? (yes / edit)
```

If the title was not detected, ask the user for a display name.

### Step 6 — Write to OPML

Run:
```bash
uv run scripts/feeder.py add-feed \
  --opml <abs-path-to-feeds.opml> \
  --category "<category>" \
  --url "<resolved_url>" \
  --title "<title>" \
  [--html-url "<original_url>"]
```

Response will be `{"status": "added", ...}` or `{"status": "skipped", "reason": "URL already exists in OPML"}`.

Report the result to the user.

---

## Workflow 3: remove-feed

### Step 1 — Identify the feed

Ask the user for the feed name or URL to remove.

If unclear, run `list-categories` and show a summary of all feeds (read the OPML directly or run `fetch --days 0` is not valid — read OPML with the Read tool and present the feed names grouped by category).

### Step 2 — Confirm

Show the matching entry and ask: "Remove **<Feed Name>** (`<url>`) from **<Category>**? (yes/no)"

### Step 3 — Remove

Run:
```bash
uv run scripts/feeder.py remove-feed --opml <abs-path-to-feeds.opml> --url "<url>"
```

Report `removed` or `not_found` to the user.

---

## Gotchas

- **`uv` must be installed.** Verify with `uv --version` before running any script command. If missing, instruct the user: `brew install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`.

- **Absolute OPML path is required.** The script's `--opml` arg must be an absolute path. Resolve the skill root directory first, then append `assets/feeds.opml`.

- **OPML is modified at runtime.** When `add-feed` or `remove-feed` runs, it edits `assets/feeds.opml` in place inside the skill directory. This is intentional — the skill owns its data. If the skill directory is ever re-cloned or overwritten, migrate `feeds.opml` manually.

- **`rssfr-*` attributes are Feeder-app-specific.** They are preserved on existing entries and added as empty defaults on new entries. Do not strip them.

- **`feedparser` normalises RSS and Atom.** Both formats work. `entry.published_parsed` may be `None` for some feeds — the script falls back to `entry.updated_parsed`. If both are absent, `published` will be `null` in the JSON; treat such posts as current and include them.

- **YouTube `@handle` resolution requires an HTTP fetch.** The script fetches the channel page and extracts `channelId` from the JSON-LD or page source. This may break if YouTube changes their page structure. If it fails, ask the user to provide a `youtube.com/channel/<ID>` URL directly.

- **Playwright MCP availability.** Check whether Playwright MCP is configured before using it. If not available, WebFetch is the fallback. Do not error-block the entire run on this.

- **X/Twitter without nitter.** If `nitter_base_url` is empty and the user tries to add a Twitter/X URL, `resolve-url` returns a warning. Inform the user and stop — do not store an unresolvable URL in the OPML.

- **Paywalled articles.** AWS, GCP, and most engineering blogs are freely crawlable. Medium, some newsletters, and WSJ/Bloomberg will gate content. The RSS `description` fallback with `[paywalled/JS-required]` label is the correct response — do not retry or attempt to bypass.

- **Empty categories.** When a category has no posts in the requested time window, omit it from the output entirely. Do not show empty sections.

- **Fetch errors vs. empty feeds.** A feed in `errors` means the HTTP fetch or parse failed. A feed with an empty `posts` array means it was reachable but had no posts in the time window. Report only the former as `[unavailable]`.

- **Nested subcategories are not visible to the add-feed picker by default.** `k8s` (inside Cloud) and `Safety` (inside AI) are subcategories. `list-categories` returns them with their full path (e.g. `Cloud/k8s`). When using `add-feed --category`, pass the leaf name only (e.g. `k8s`) — the script searches recursively. If the user specifies a path like `Cloud/k8s`, strip it to the leaf before passing to `--category`.

- **Dead feeds are silently excluded, not always reported as errors.** `feedparser` reports HTTP status in `parsed.status`. The script now checks for `>= 400` and moves such feeds to `errors`. However, feeds that time out at the TCP level may still appear as empty results rather than errors. If a feed is consistently absent from output, check its URL manually.

- **YouTube RSS feeds have daily outages.** Since February 2026, YouTube's RSS feeds (`/feeds/videos.xml?channel_id=...`) return 404 for approximately 2–3 hours daily (typically ~5am–8am UTC). This affects all YouTube channels. If your Feeder app shows new content but the skill reports `[unavailable]`, the feeds are likely in their downtime window. Retry later or check if your OPML contains outdated `youtube.com/feeds` URLs that YouTube may have deprecated.
