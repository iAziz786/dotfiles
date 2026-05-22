---
name: dynadot-auctions
description: Show current Dynadot domain auctions, bids, and expired closeout domains. Use when the user asks about domain auctions, current bids, expired domains, closeout domains, backorder auctions, or Dynadot aftermarket listings. Triggers on phrases like "show auctions", "current bids", "expired domains", "closeout domains", "Dynadot auctions", or "domain listings".
license: MIT
compatibility: Designed for OpenCode and Claude Code
metadata:
  author: user
  version: "1.0"
---

# Dynadot Auctions

## When To Use

Activate this skill when the user wants to:
- View current domain auctions on Dynadot
- Check bids on active auctions
- Browse expired/closeout domains
- See backorder auctions
- Monitor aftermarket domain listings

Trigger phrases:
- "show me auctions"
- "current bids"
- "expired domains"
- "closeout domains"
- "Dynadot auctions"
- "domain listings"
- "backorder auctions"

## What This Skill Does

Fetches live auction data from Dynadot's Legacy API (api3.json) and presents it in a readable format.

### Quick Start

Run the bundled script to see current auctions:

```bash
python3 .agents/skills/dynadot-auctions/scripts/show_auctions.py
```

Or from anywhere:

```bash
python3 /path/to/.agents/skills/dynadot-auctions/scripts/show_auctions.py
```

### Pagination

```bash
# Page 2
python3 show_auctions.py --page 2

# Page 3 with 20 items per page
python3 show_auctions.py --page 3 --per-page 20

# Only auctions (skip closeouts)
python3 show_auctions.py --auctions-only

# Only closeouts
python3 show_auctions.py --closeouts-only

# Filter out domains starting with numbers
python3 show_auctions.py --no-number-start

# Combine flags: page 2, no number-starting domains
python3 show_auctions.py --page 2 --no-number-start
```

### Supported Commands

| Command | Description | Required Params |
|---------|-------------|---------------|
| `get_open_auctions` | Active expired auctions | `count_per_page`, `page_index` |
| `get_closed_auctions` | Recently ended auctions | `startDate`, `endDate` (YYYY-MM-DD) |
| `get_open_backorder_auctions` | Active backorder auctions | None |
| `get_expired_closeout_domains` | Fixed-price closeout domains | None |
| `get_auction_details` | Specific auction details | `domain` |

### API Endpoint

```
https://api.dynadot.com/api3.json
```

### Authentication

Requires `DYNADOT_API_KEY` environment variable. The key is available in your Dynadot account under **Tools → API**.

**Note**: The script assumes `DYNADOT_API_KEY` is set and does not validate it. Ensure the environment variable is exported before running.

### Example: Get Open Auctions

```bash
curl "https://api.dynadot.com/api3.json?key=$DYNADOT_API_KEY&command=get_open_auctions&currency=usd&type=expired&count_per_page=20&page_index=1"
```

Parameters:
- `key` — Your Dynadot API key
- `command` — `get_open_auctions`
- `currency` — `usd`, `eur`, or `cny` (optional, default: USD)
- `type` — `expired` for expired domain auctions (optional)
- `count_per_page` — Number of results per page (e.g., 20)
- `page_index` — Page number (1-based)

### Response Format

```json
{
  "status": "success",
  "auction_list": [
    {
      "auction_id": 38943284,
      "domain": "020mf.com",
      "current_bid_price": "43.03",
      "renewal_price": "10.88",
      "bids": 0,
      "bidders": 0,
      "time_left": "10 hours, 41 min",
      "end_time": "2026/05/23 18:29 IST",
      "end_time_stamp": 1779541190000,
      "links": "26",
      "age": 9,
      "dyna_appraisal": "$822.00"
    }
  ]
}
```

### Example: Get Expired Closeout Domains

```bash
curl "https://api.dynadot.com/api3.json?key=$DYNADOT_API_KEY&command=get_expired_closeout_domains"
```

Response includes:
- `domainName` — Domain name
- `currentPrice` — Fixed buy-now price
- `renewalPrice` — Annual renewal cost
- `endTimeStamp` — When the closeout ends

## Gotchas

- **Auction API access required**: Contact Dynadot support to enable auction API access on your account. Without it, auction endpoints return 403 Forbidden.
- **Rate limits**: Regular accounts: 1 thread, 60/min. Bulk: 5 threads, 600/min. Super Bulk: 35 threads, 6000/min.
- **Pagination params**: Use `count_per_page` and `page_index` — NOT `page`, `limit`, `offset`, or other common names.
- **Date format**: For `get_closed_auctions`, use `startDate` and `endDate` in YYYY-MM-DD format (e.g., `2026-05-01`).
- **No sandbox support**: Auction endpoints do not work in the sandbox environment.
- **Key propagation**: Wait 10-20 minutes after generating a new API key before using it.
- **Account balance**: Some auction purchases require account balance; payment methods vary by auction type.
