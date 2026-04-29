---
name: firecrawl-cli-installation
description: |
  Install the Firecrawl CLI for a self-hosted instance at localhost:3002.
---

# Firecrawl CLI Installation (Self-Hosted)

## Quick Setup (Recommended)

```bash
bun install -g firecrawl-cli
```

Or with npm:

```bash
npm install -g firecrawl-cli
```

## Configuration

No API key needed for self-hosted usage. Set the API URL:

```bash
export FIRECRAWL_API_URL=http://localhost:3002
```

Or persist it:

```bash
firecrawl config --api-url http://localhost:3002
```

## Verify

First check status:

```bash
firecrawl --status
```

Then run one small real request to prove install and output work:

```bash
mkdir -p .firecrawl
firecrawl scrape "https://firecrawl.dev" -o .firecrawl/install-check.md
```

The install is healthy when both commands succeed.
