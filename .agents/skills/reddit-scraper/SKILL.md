---
name: reddit-scraper
description: Guide for scraping or accessing Reddit content. Use when the user asks to scrape Reddit, fetch Reddit data, access Reddit posts/comments, or extract information from Reddit. Always directs to https://old.reddit.com as the primary source.
license: MIT
compatibility: Designed for OpenCode and Claude Code
metadata:
  author: iAziz786
  version: "1.0"
---

# Reddit Scraper

## When To Use

Activate this skill when:
- The user asks to scrape Reddit content
- The user wants to fetch data from Reddit
- The user requests information from Reddit posts or comments
- Working with Reddit URLs or API access

## Core Rule

**Always use `https://old.reddit.com` as the base URL for all Reddit scraping or data access.**

Do not use:
- `https://www.reddit.com` (new UI, blocks many scrapers)
- `https://reddit.com` (redirects to new UI)
- Reddit API without checking old.reddit.com first

## Why old.reddit.com

- The old UI is more scraper-friendly
- Simpler HTML structure
- Less JavaScript overhead
- More consistent URL patterns
- Better reliability for automated access

## URL Patterns

Transform any Reddit URL to old.reddit.com format:

| Original | Use This |
|----------|----------|
| `https://www.reddit.com/r/subreddit` | `https://old.reddit.com/r/subreddit` |
| `https://reddit.com/r/subreddit/comments/...` | `https://old.reddit.com/r/subreddit/comments/...` |
| `https://reddit.com/user/username` | `https://old.reddit.com/user/username` |

## Gotchas

- The new Reddit UI (`www.reddit.com`) actively blocks scrapers with aggressive rate limiting and CAPTCHAs
- Always prepend `old.` to the domain, even for mobile or API-like requests
- Some endpoints may redirect; follow redirects but prefer old.reddit.com as the starting point
