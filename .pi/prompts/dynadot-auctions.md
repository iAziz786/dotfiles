---
description: Fetch and display Dynadot domain auctions, bids, closeout domains via API or bundled script.
---

# Dynadot Auctions

## Quick Start

```bash
python3 /Users/aziz/Documents/github.com/iAziz786/dotfiles/.agents/skills/dynadot-auctions/scripts/show_auctions.py
```

### Pagination & Filters

```bash
python3 /path/to/scripts/show_auctions.py --page 2
python3 /path/to/scripts/show_auctions.py --page 3 --per-page 20
python3 /path/to/scripts/show_auctions.py --auctions-only
python3 /path/to/scripts/show_auctions.py --closeouts-only
python3 /path/to/scripts/show_auctions.py --no-number-start
python3 /path/to/scripts/show_auctions.py --page 2 --no-number-start
```

## API Commands

| Command | Description | Required Params |
|---------|-------------|----------------|
| `get_open_auctions` | Active expired auctions | `count_per_page`, `page_index` |
| `get_closed_auctions` | Recently ended | `startDate`, `endDate` (YYYY-MM-DD) |
| `get_open_backorder_auctions` | Active backorder auctions | None |
| `get_expired_closeout_domains` | Fixed-price closeouts | None |
| `get_auction_details` | Specific auction | `domain` |

**Endpoint:** `https://api.dynadot.com/api3.json`

**Auth:** Requires `DYNADOT_API_KEY` env var (set in Dynadot → Tools → API).

### Get Open Auctions (curl)

```bash
curl "https://api.dynadot.com/api3.json?key=$DYNADOT_API_KEY&command=get_open_auctions&currency=usd&type=expired&count_per_page=20&page_index=1"
```

Params: `key`, `command`, `currency` (usd/eur/cny), `type` (expired), `count_per_page`, `page_index`.

### Get Expired Closeout Domains (curl)

```bash
curl "https://api.dynadot.com/api3.json?key=$DYNADOT_API_KEY&command=get_expired_closeout_domains"
```

## Gotchas

- **Auction API access** must be enabled by Dynadot support — otherwise 403.
- **Rate limits**: 1 thread/60 req per min (regular), 5/600 (bulk), 35/6000 (super bulk).
- **Pagination**: use `count_per_page` & `page_index` — NOT `page`, `limit`, `offset`.
- **Date format**: YYYY-MM-DD for `get_closed_auctions`.
- **No sandbox** for auction endpoints.
- **Key propagation**: wait 10-20 min after generating new API key.
- Some purchases need account balance.
