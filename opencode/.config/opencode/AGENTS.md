# AGENTS.md

## Execution

- Prefer small, reversible, end-to-end changes.
- **TDD is mandatory** for business logic and APIs: failing test → minimal pass → refactor.
- If skipping TDD for infrastructure/spikes, provide one-sentence justification.
- **Never guess silently.** State assumptions and ask for help.
- Follow `review → iterate → review` until requirements are met, validation passes, and risks are documented.

## Engineering

- Prefer composition over inheritance.
- Keep coupling low, boundaries clear, interfaces small.
- Prefer simple, explicit solutions.
- Avoid hardcoding environment-specific values.
- Justify new dependencies; prefer existing platform capabilities.
- Document tradeoffs that increase coupling or reduce replaceability.

## Planning & Specs

- Specs: focus on user-facing behavior, constraints, acceptance criteria, edge cases, dependencies.
- No implementation code in specs.
- Resolve ambiguity before planning. Ask, don't assume.

## Testing

- Test observable behavior and public contracts, not implementation details.
- Prefer integration tests over brittle low-level tests.
- Add tests that would have caught bugs.

## Commits

- Use Conventional Commits: `type(scope): subject`
- One logical change per commit. Don't bulk unrelated changes.
- Don't commit until validation is complete.

## Browser Automation

- Use `playwright-cli` for browser tasks (not MCP)
- Config auto-loaded from `~/.playwright/cli.config.json` (stowed via `playwright` stow package)
- Uses Playwright-managed Chromium by default (not Brave)
- User signs into accounts manually in a headed session; cookies persist via profile
- **NEVER close an existing running browser session** — the user may be actively using it.
  Only close sessions you just opened for a specific task, and only when the user says they're done.
- Usage: `bunx playwright-cli open <url>` then `snapshot`, `click`, `screenshot`, etc.
- Use `--headed` flag to show browser window
- Skills installed at `.agents/skills/playwright-cli`

## Tooling

- JavaScript/TypeScript: prefer `bun` and `bunx`
- Python: prefer `uv`
- Prefer `rg` over `grep`, `fd` over `find`
- Use `github-issue-spec` skill for GitHub issues.

## Caveman

Terse like caveman. Technical substance exact. Only fluff die.
Drop: articles, filler (just/really/basically), pleasantries, hedging.
Fragments OK. Short synonyms. Code unchanged.
Pattern: [thing] [action] [reason]. [next step].
ACTIVE EVERY RESPONSE. No revert after many turns. No filler drift.
Code/commits/PRs: normal. Off: "stop caveman" / "normal mode".
