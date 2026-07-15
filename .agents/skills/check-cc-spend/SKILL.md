---
name: check-cc-spend
description: Use when checking YES BANK credit card spending. Extract and sum transactions from Gmail transaction alerts. Triggers on "what did I spend", "credit card transactions", "check my spends", "YES BANK spend summary", "how much did I spend".
license: MIT
compatibility: Designed for OpenCode and Claude Code
metadata:
  author: Aziz
  version: "1.0"
disable-model-invocation: true
---

# Check Credit Card Spend

Extract YES BANK credit card spending details from Gmail transaction alert emails and compute the total in INR.

## When To Use

Activate this skill when the user:
- Asks "what did I spend on my credit card"
- Wants to check YES BANK credit card transactions
- Needs a spending summary for a date range

## Input

Provide a start date in `YYYY-MM-DD` format (e.g., `2024-01-01`).

**Default date rule** (when user omits the date):
- If **today is between 1-13** of the month → default to **14th of the previous month**
- If **today is between 14-31** of the month → default to **14th of the current month**

Example: If today is 2024-05-09 → default is 2024-04-14. If today is 2024-05-20 → default is 2024-05-14.

## Prerequisites

- `playwright-cli` must be installed and available in PATH
- A Gmail browser session must be active (headed or persistent profile)
- If not signed in, the agent will open Gmail and wait for manual sign-in

## Output Contract

Produces a spending report with:
- Markdown table: Date | Time | Amount | Merchant
- Subtotals per currency (INR, USD, SGD)
- Grand Total in INR using approximate exchange rates (USD ≈ ₹83.5, SGD ≈ ₹61.5)
- Disclaimer that rates are approximate and actual bill may differ

## Process

1. **Open Gmail with `playwright-cli`**
   - Use a headed session: `playwright-cli open https://mail.google.com --headed`
   - Wait for the user to sign in manually if needed.

2. **Run the extraction script**
   ```bash
   cd ~/.agents/skills/check-cc-spend/scripts
   python3 extract-yesbank.py --date YYYY-MM-DD
   ```
   
   The script will:
   - Navigate to Gmail search for YES BANK transaction alerts
   - Open **every email thread** (not just previews)
   - Extract all `has been spent` transactions
   - Deduplicate and compute totals
   - Convert USD/SGD to INR using approximate rates

3. **Manual fallback** (if script fails)
   - Search: `from:alerts@yes.bank.in "Transaction Alert" "spent" after:YYYY/MM/DD`
   - Open each thread individually (Enter → extract → press `u` to go back)
   - Parse `has been spent` lines for amount, merchant, date

## Gotchas

- **Thread hiding**: Gmail groups multiple alerts into one conversation. The list view only shows the latest message. **Always open the thread body.**
- **Date formats**: Gmail search uses `YYYY/MM/DD`; alert bodies use `DD-MM-YYYY`.
- **Currency symbols**: Watch for `INR`, `USD`, `SGD` and commas inside Indian amounts (e.g., `INR 2,500.00`).
- **Declined transactions**: Only count `has been spent` alerts; ignore `is declined` or `declined due to` messages.

## Script Location

`~/.agents/skills/check-cc-spend/scripts/extract-yesbank.py`

## Example Output

```
Found 20 transactions after 2024-04-15

| Date       | Time     | Amount       | Merchant            |
|------------|----------|--------------|---------------------|
| 2024-05-09 | 08:09 AM | USD 56.64    | FIREWORKS.AI        |
| 2024-05-08 | 04:56 PM | INR 294.75   | HERDORA             |
| ...        | ...      | ...          | ...                 |

Total INR: ₹10,038.67
Total USD: $100.65 → ₹8,404.28
Total SGD: $1.38 → ₹84.87
Grand Total (INR): ₹18,527.81

* Exchange rates are approximate; actual bill may differ slightly.
```
