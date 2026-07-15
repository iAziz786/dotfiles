# AGENTS.md

## Execution

- Prefer small, reversible, end-to-end changes.
- **TDD is mandatory** for business logic and APIs
- **Never guess silently.** State assumptions and ask for help.

## Engineering

- Avoid hardcoding environment-specific values.
- Justify new dependencies; prefer existing platform capabilities.

## Planning & Specs

- Specs: focus on user-facing behavior, constraints, acceptance criteria, edge cases, dependencies.
- Resolve ambiguity before planning. Ask, don't assume.

## Testing

- Test observable behavior and public contracts, not implementation details.
- Add tests that would have caught bugs.

## Commits

- Use Conventional Commits: `type(scope): subject`
- One logical change per commit. Don't bulk unrelated changes.
- Don't commit until validation is complete.

## Tooling

- JavaScript/TypeScript: prefer `bun` and `bunx`
- Python: prefer `uv`
- Prefer `rg` over `grep`, `fd` over `find`
- Use `github-issue-spec` skill for GitHub issues.
- `rm` aliased to `rip` for safety (moves to graveyard instead of permanent delete). Run `tldr rip` or `rip --help` for usage.

## Your Output

- Be extremely concise. Sacrifice grammar for the sake of concision.
