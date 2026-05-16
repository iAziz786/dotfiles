#!/usr/bin/env python3
"""Extract YES BANK credit card transactions from Gmail threads."""

import subprocess
import re
import json
import time
import sys
import argparse
from datetime import datetime, timedelta

# Exchange rates (approximate)
USD_RATE = 83.5
SGD_RATE = 61.5

def compute_default_date():
    """Compute default start date based on current day of month."""
    today = datetime.now()
    if today.day <= 13:
        # 14th of previous month
        target = today.replace(day=14) - timedelta(days=32)
        target = target.replace(day=14)
    else:
        # 14th of current month
        target = today.replace(day=14)
    return target.strftime("%Y-%m-%d")

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        print(f"Error: {cmd}\n{r.stderr}", file=sys.stderr)
    return r

def get_thread_refs():
    """Get current YES BANK thread refs from search results."""
    r = run(["playwright-cli", "--raw", "snapshot"])
    content = r.stdout
    blocks = re.findall(
        r'row "([^"]+)".*?\[ref=(e\d+)\].*?\[cursor=pointer\]',
        content, re.DOTALL
    )
    yes_blocks = [
        (text, ref) for text, ref in blocks
        if 'YES BANK' in text or 'Transaction Alert' in text
    ]
    return yes_blocks

def click_thread(ref):
    r = run(["playwright-cli", "click", ref])
    time.sleep(2.5)
    return r

def extract_bodies():
    """Use eval to extract all email bodies from the thread view."""
    js = """
    (() => {
        const bodies = [...document.querySelectorAll('.a3s, .ii, .gs')];
        const unique = [];
        const seen = new Set();
        for (const b of bodies) {
            const text = b.innerText.trim();
            if (text && text.includes('has been spent') && !seen.has(text.slice(0, 150))) {
                seen.add(text.slice(0, 150));
                unique.push(text);
            }
        }
        return unique;
    })()
    """
    r = run(["playwright-cli", "--raw", "eval", js])
    try:
        return json.loads(r.stdout.strip())
    except Exception as e:
        print(f"  Parse error: {e}", file=sys.stderr)
        return []

def go_back():
    run(["playwright-cli", "press", "u"])
    time.sleep(2.5)

def parse_transaction(text):
    """Parse a single email body for transaction details."""
    if 'has been spent' not in text:
        return None

    if 'declined' in text.lower():
        return None

    spent_match = re.search(
        r'(INR|USD|SGD)\s+([\d,]+\.\d{2})\s+has been spent',
        text
    )
    if not spent_match:
        return None

    currency = spent_match.group(1)
    amount_str = spent_match.group(2).replace(',', '')
    amount = float(amount_str)

    date_match = re.search(r'on\s+(\d{2}-\d{2}-\d{4})', text)
    date = date_match.group(1) if date_match else None

    time_match = re.search(r'at\s+(\d{2}:\d{2}:\d{2}\s+(?:am|pm))', text)
    time_str = time_match.group(1) if time_match else None

    merchant_match = re.search(
        r'at\s+([A-Z][A-Z\s*\.&,\-_\*]+?)\s+on\s+\d{2}-\d{2}-\d{4}',
        text
    )
    merchant = merchant_match.group(1).strip() if merchant_match else 'Unknown'

    return {
        'date': date,
        'time': time_str,
        'currency': currency,
        'amount': amount,
        'merchant': merchant,
    }

def navigate_to_search(start_date):
    """Navigate Gmail to the YES BANK search results."""
    # Convert YYYY-MM-DD to YYYY/MM/DD for Gmail
    gmail_date = start_date.replace('-', '/')
    search_url = (
        "https://mail.google.com/mail/u/0/#search/"
        f"from:alerts@yes.bank.in+%22Transaction+Alert%22+%22spent%22+after:{gmail_date}"
    )
    print(f"Navigating to Gmail search: after:{gmail_date}")
    run(["playwright-cli", "goto", search_url])
    time.sleep(3)

def main():
    parser = argparse.ArgumentParser(
        description="Extract YES BANK credit card spends from Gmail"
    )
    parser.add_argument(
        "--date",
        help="Start date in YYYY-MM-DD format (default: 14th of current or previous month based on today)"
    )
    args = parser.parse_args()

    start_date = args.date or compute_default_date()
    print(f"Searching transactions after: {start_date}\n")

    navigate_to_search(start_date)

    all_transactions = []
    processed_threads = set()
    max_iterations = 20

    for iteration in range(max_iterations):
        threads = get_thread_refs()
        if not threads:
            print(f"[{iteration}] No threads found. Stopping.")
            break

        target = None
        for text, ref in threads:
            thread_id = ref
            if thread_id not in processed_threads:
                target = (text, ref)
                processed_threads.add(thread_id)
                break

        if not target:
            print(f"[{iteration}] All threads processed. Stopping.")
            break

        text, ref = target
        print(f"[{iteration+1}] Opening thread {ref}...")
        print(f"  Preview: {text[:80]}")

        click_thread(ref)
        bodies = extract_bodies()
        print(f"  Found {len(bodies)} unique spent message(s)")

        for body in bodies:
            tx = parse_transaction(body)
            if tx:
                all_transactions.append(tx)
                print(f"  -> {tx['date']} {tx['time']} | {tx['currency']} {tx['amount']:.2f} | {tx['merchant']}")

        go_back()

    # Deduplicate
    seen = set()
    unique_transactions = []
    for tx in all_transactions:
        key = (tx['date'], tx['time'], tx['currency'], tx['amount'], tx['merchant'])
        if key not in seen:
            seen.add(key)
            unique_transactions.append(tx)

    # Compute totals
    totals = {}
    for tx in unique_transactions:
        curr = tx['currency']
        totals[curr] = totals.get(curr, 0.0) + tx['amount']

    inr_total = totals.get('INR', 0.0)
    usd_total = totals.get('USD', 0.0)
    sgd_total = totals.get('SGD', 0.0)

    usd_in_inr = usd_total * USD_RATE
    sgd_in_inr = sgd_total * SGD_RATE
    grand_total = inr_total + usd_in_inr + sgd_in_inr

    # Output
    print("\n" + "=" * 70)
    print(f"Found {len(unique_transactions)} transactions after {start_date}")
    print("=" * 70 + "\n")

    print("| Date       | Time     | Amount       | Merchant            |")
    print("|------------|----------|--------------|---------------------|")
    for tx in unique_transactions:
        amt = f"{tx['currency']} {tx['amount']:,.2f}"
        merchant = tx['merchant'] or 'Unknown'
        print(f"| {tx['date']} | {tx['time']} | {amt:12s} | {merchant:19s} |")

    print()
    if inr_total > 0:
        print(f"Total INR: ₹{inr_total:,.2f}")
    if usd_total > 0:
        print(f"Total USD: ${usd_total:,.2f} → ₹{usd_in_inr:,.2f}")
    if sgd_total > 0:
        print(f"Total SGD: S${sgd_total:,.2f} → ₹{sgd_in_inr:,.2f}")
    print(f"\nGrand Total (INR): ₹{grand_total:,.2f}")
    print("\n* Exchange rates are approximate; actual bill may differ slightly.")

if __name__ == '__main__':
    main()
