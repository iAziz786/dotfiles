---
name: search
description: This skill helps you with searching the web using `pi` command.
---

# search

Use CLI commands to search web with `pi` command.

DO NOT run these command directly in current context.

## When to use

Use for search, research.

## Instructions

Call these commands to search the web.

### Exa Search

Here is an example on how to use exa APIs.

```bash
curl -X POST "https://api.exa.ai/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $EXA_API_KEY" \
  -d '{"query": "YOUR QUERY"}'
```

DO NOT read $EXA_API_KEY from your environment variables.
Assume $EXA_API_KEY is available.

### Firecrawl Search

```bash
firecrawl search "YOUR QUERY"
```

### Tavily Search

```bash
tvly search "your first query"
```

### Serp API

```bash
serpapi search \
  q="YOUR QUERY" \
  hl="en" \
  google_domain="google.com"
```

If Serp API is not available fallback to Firecrawl Search.

```
```
