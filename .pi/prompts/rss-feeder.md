---
description: Check RSS/Atom feeds, add/remove feeds, or summarise recent posts by category from personal OPML
---

# RSS Feeder

Fetches, summarises, and manages feeds from a personal OPML subscription list.

## Paths (absolute)

- OPML: `/Users/aziz/.agents/skills/rss-feeder/assets/feeds.opml`
- Script: `/Users/aziz/.agents/skills/rss-feeder/scripts/feeder.py`
- Skill root: `/Users/aziz/.agents/skills/rss-feeder/`

All `--opml` arguments must be the absolute path above.

## Config

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

---

## Workflow 1: check-updates

### Step 1 — Determine the time window

- Default lookback: `default_days` from config (1 day).
- If the user specifies a period ("last 3 days", "this week"), use that instead.
- Convert to an integer number of days.

### Step 2 — Fetch feed metadata

Run:
```bash
uv run /Users/aziz/.agents/skills/rss-feeder/scripts/feeder.py fetch --opml /Users/aziz/.agents/skills/rss-feeder/assets/feeds.opml --days <N>
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
uv run /Users/aziz/.agents/skills/rss-feeder/scripts/feeder.py list-categories --opml /Users/aziz/.agents/skills/rss-feeder/assets/feeds.opml
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
uv run /Users/aziz/.agents/skills/rss-feeder/scripts/feeder.py resolve-url --url "<url>" [--nitter-base "<nitter_base_url>"]
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

### Step 5 — Confirm with user

### Step 6 — Write to OPML

Run:
```bash
uv run /Users/aziz/.agents/skills/rss-feeder/scripts/feeder.py add-feed \
  --opml /Users/aziz/.agents/skills/rss-feeder/assets/feeds.opml \
  --category "<category>" \
  --url "<resolved_url>" \
  --title "<title>" \
  [--html-url "<original_url>"]
```

---

## Workflow 3: remove-feed

### Step 1 — Identify the feed

### Step 2 — Confirm

### Step 3 — Remove

Run:
```bash
uv run /Users/aziz/.agents/skills/rss-feeder/scripts/feeder.py remove-feed --opml /Users/aziz/.agents/skills/rss-feeder/assets/feeds.opml --url "<url>"
```

---

## Gotchas

- **`uv` must be installed.** Verify with `uv --version` before running any script command. If missing, instruct the user: `brew install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`.
- **OPML is modified at runtime.** When `add-feed` or `remove-feed` runs, it edits `assets/feeds.opml` in place. If the skill directory is ever re-cloned or overwritten, migrate `feeds.opml` manually.
- **`rssfr-*` attributes are Feeder-app-specific.** They are preserved on existing entries and added as empty defaults on new entries. Do not strip them.
- **`feedparser` normalises RSS and Atom.** Both formats work. If `published_parsed` is `None`, treat such posts as current and include them.
- **YouTube `@handle` resolution requires an HTTP fetch.** May break if YouTube changes their page structure. If it fails, ask the user to provide a `youtube.com/channel/<ID>` URL directly.
- **Playwright MCP availability.** Check whether Playwright MCP is configured before using it. If not available, WebFetch is the fallback.
- **X/Twitter without nitter.** If `nitter_base_url` is empty and the user tries to add a Twitter/X URL, inform the user and stop.
- **Paywalled articles.** Use RSS `description` fallback with `[paywalled/JS-required]` label. Do not retry or attempt to bypass.
- **Empty categories** with no posts in the time window should be omitted entirely.
- **Fetch errors vs. empty feeds.** A feed in `errors` means HTTP/parse failure. A feed with empty `posts` was reachable but had no new posts.
- **Nested subcategories** use leaf name only when passing to `--category`.
- **YouTube RSS feeds have daily outages.** ~2-3 hours daily (typically ~5am–8am UTC). If consistently unavailable, retry later.
