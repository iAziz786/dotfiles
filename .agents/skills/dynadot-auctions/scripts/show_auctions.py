#!/usr/bin/env python3
"""
Dynadot Auctions Display Script
Shows current active expired auctions and closeout domains.
Requires DYNADOT_API_KEY environment variable.
"""

import urllib.request
import urllib.error
import urllib.parse
import os
import json
import sys
import argparse

API_KEY = os.environ.get('DYNADOT_API_KEY')
if not API_KEY:
    print("Error: DYNADOT_API_KEY environment variable not set", file=sys.stderr)
    sys.exit(1)

BASE_URL = "https://api.dynadot.com/api3.json"


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Show Dynadot domain auctions and closeout domains',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Show page 1, 10 auctions + 5 closeouts
  %(prog)s --page 2                 # Show page 2 of auctions
  %(prog)s --page 3 --per-page 20   # Show page 3, 20 auctions per page
  %(prog)s --closeouts-only         # Show only closeout domains
  %(prog)s --auctions-only          # Show only active auctions
  %(prog)s --no-number-start        # Filter out domains starting with numbers
        """
    )
    parser.add_argument(
        '--page', '-p',
        type=int,
        default=1,
        help='Page number to fetch (default: 1)'
    )
    parser.add_argument(
        '--per-page', '-n',
        type=int,
        default=10,
        help='Number of auctions per page (default: 10)'
    )
    parser.add_argument(
        '--auctions-only', '-a',
        action='store_true',
        help='Show only active auctions, skip closeouts'
    )
    parser.add_argument(
        '--closeouts-only', '-c',
        action='store_true',
        help='Show only closeout domains, skip auctions'
    )
    parser.add_argument(
        '--no-number-start', '-N',
        action='store_true',
        help='Filter out domains that start with a number (0-9)'
    )
    return parser.parse_args()


def fetch_open_auctions(count_per_page=10, page_index=1):
    """Fetch active expired domain auctions."""
    params = {
        'key': API_KEY,
        'command': 'get_open_auctions',
        'currency': 'usd',
        'type': 'expired',
        'count_per_page': str(count_per_page),
        'page_index': str(page_index)
    }
    query = urllib.parse.urlencode(params)
    url = f"{BASE_URL}?{query}"
    
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        return {'error': str(e)}


def fetch_closeout_domains(count_per_page=5, page_index=1):
    """Fetch expired closeout domains (buy now)."""
    params = {
        'key': API_KEY,
        'command': 'get_expired_closeout_domains',
        'count_per_page': str(count_per_page),
        'page_index': str(page_index)
    }
    query = urllib.parse.urlencode(params)
    url = f"{BASE_URL}?{query}"
    
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        return {'error': str(e)}


def starts_with_number(domain):
    """Check if domain starts with a number (0-9)."""
    return domain and domain[0].isdigit()


def display_auctions(data, limit=10, filter_numbers=False):
    """Display auction list in readable format."""
    if data.get('status') != 'success':
        error = data.get('error', 'Unknown error')
        print(f"Error fetching auctions: {error}")
        return
    
    auctions = data.get('auction_list', [])
    
    # Filter out domains starting with numbers if requested
    if filter_numbers:
        auctions = [a for a in auctions if not starts_with_number(a.get('domain', ''))]
    
    auctions = auctions[:limit]
    
    if not auctions:
        print("No active auctions found.")
        return
    
    print(f"\n{'Domain':<25} {'Bid':>8} {'Renew':>8} {'Bids':>5} {'Time Left':>15}")
    print("-" * 70)
    
    for a in auctions:
        domain = a['domain']
        bid = f"${a['current_bid_price']}"
        renewal = f"${a['renewal_price']}"
        bids = f"{a['bids']}"
        time_left = a['time_left']
        
        print(f"{domain:<25} {bid:>8} {renewal:>8} {bids:>5} {time_left:>15}")
        
        # Extra details on second line
        details = []
        if a.get('links') and a['links'] != '-1':
            details.append(f"links: {a['links']}")
        if a.get('age'):
            details.append(f"age: {a['age']}y")
        if a.get('dyna_appraisal') and a['dyna_appraisal'] != '-':
            details.append(f"appraisal: {a['dyna_appraisal']}")
        
        if details:
            print(f"  {', '.join(details)}")


def display_closeouts(data, limit=5, filter_numbers=False):
    """Display closeout domains in readable format."""
    resp = data.get('GetExpiredCloseoutDomainsResponse', {})
    
    if resp.get('Status') != 'success':
        error = data.get('error', 'Unknown error')
        print(f"Error fetching closeouts: {error}")
        return
    
    domains = resp.get('CloseoutDomains', [])
    
    # Filter out domains starting with numbers if requested
    if filter_numbers:
        domains = [
            d for d in domains 
            if not starts_with_number(d.get('closeoutItem', {}).get('domainName', ''))
        ]
    
    domains = domains[:limit]
    
    if not domains:
        print("No closeout domains found.")
        return
    
    print(f"\n{'Domain':<25} {'Price':>8} {'Renew':>8} {'Links':>7}")
    print("-" * 55)
    
    for d in domains:
        item = d.get('closeoutItem', {})
        domain = item.get('domainName', 'N/A')
        price = f"${item.get('currentPrice', 'N/A')}"
        renewal = f"${item.get('renewalPrice', 'N/A')}"
        links = str(item.get('inboundLinks', 'N/A'))
        
        print(f"{domain:<25} {price:>8} {renewal:>8} {links:>7}")


def main():
    """Main entry point."""
    args = parse_args()
    
    print("=== DYNADOT AUCTIONS ===")
    print(f"Fetching live data...\n")
    
    # Fetch auctions
    if not args.closeouts_only:
        print(f"--- Active Expired Auctions (Page {args.page}, {args.per_page} per page) ---")
        auctions = fetch_open_auctions(count_per_page=args.per_page, page_index=args.page)
        display_auctions(auctions, limit=args.per_page, filter_numbers=args.no_number_start)
    
    # Fetch closeouts
    if not args.auctions_only:
        if not args.closeouts_only:
            print()
        print("--- Expired Closeout Domains (Buy Now) ---")
        closeouts = fetch_closeout_domains(count_per_page=5, page_index=1)
        display_closeouts(closeouts, limit=5, filter_numbers=args.no_number_start)
    
    print("\n---")
    print(f"Tip: Use --page N to see more auctions. Example: python3 {sys.argv[0]} --page 2")


if __name__ == '__main__':
    main()
