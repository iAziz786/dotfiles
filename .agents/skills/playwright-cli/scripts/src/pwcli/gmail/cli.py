"""CLI entry point for gmail snapshot parser."""

import sys
import json

from pwcli.gmail import extract_emails, format_summary


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    if not args or args[0] in ('-h', '--help'):
        print("Usage: parse-gmail-snapshot.py <snapshot.yml> [--json] [--body] [--all]",
              file=sys.stderr)
        return 1

    filepath = args[0]
    show_body = '--body' in args
    as_json = '--json' in args
    all_emails = '--all' in args

    emails = extract_emails(filepath, unread_only=not all_emails)

    if as_json:
        print(json.dumps(emails, indent=2))
    else:
        print(format_summary(emails, show_body=show_body))

    return 0


if __name__ == '__main__':
    sys.exit(main())
