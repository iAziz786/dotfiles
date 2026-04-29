# Checking email with playwright-cli

## Workflow

1. **Open Gmail headed** — `bunx playwright-cli open https://mail.google.com --headed`. Sign in manually; cookies persist.
2. **Scan all tabs** — `python3 scripts/scan-gmail.py [account_index]`. Goes through Primary, Social, Updates, Forums (skips Promotions), snapshots each, and shows unread emails grouped by tab. Default account index is `0`. Pass `1` for second account.
3. **User picks email** — click the subject link: `bunx playwright-cli click "link <subject>"`
4. **Read body** — snapshot, then `python3 scripts/parse-gmail-snapshot.py .playwright-cli/page-*.yml --body`

## Individual parsing

```bash
python3 scripts/parse-gmail-snapshot.py page.yml           # unread only (default)
python3 scripts/parse-gmail-snapshot.py page.yml --all     # include read emails
python3 scripts/parse-gmail-snapshot.py page.yml --body    # show full body
python3 scripts/parse-gmail-snapshot.py page.yml --json    # JSON output
```

## Pitfalls

- **Stale page**: always `reload` before snapshotting.
- **Truncated output**: use the script, don't read raw YAML.
- **Account not in switcher**: sign in once headed first.
- **Escaped quotes**: some emails (e.g. Clarity) have `\"` in body → YAML wraps in single quotes. Parser handles it.
- **Promotions tab skipped** by default (too noisy). Check manually via URL if needed.
