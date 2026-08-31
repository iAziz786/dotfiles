# AGENTS.md

## Execution

- Prefer small, reversible, end-to-end changes.
- Before writing code, think hard how to make future and now code more readable, maintainable, testable no loosing correctness
- **TDD is mandatory** for business logic and APIs
- **Never guess silently.** State assumptions and ask for help.

## Engineering

- Avoid hardcoding environment-specific values.
- Justify new dependencies; prefer existing platform capabilities.

## Planning & Specs

- Specs: focus on user-facing behavior, constraints, acceptance criteria, edge cases, dependencies.
- Resolve ambiguity before planning. Ask, don't assume.
- Stop and ask questions if intent is unclear.
- Don't make assumptions without checking.
- Don't reinterpret or update plans without asking.
- When creating GitHub issue (`gh issue create`), PR (`gh pr create`), or commit (`git commit`), write content to an OS-level temp file and pass with `--body-file /tmp/FILE_NAME.md` (or `-F` for commits).
- Any background agents should be spin up using `herdr` skill.
- When using `herdr` skill, use `herdr tab` over panes.

## Testing

- Test observable behavior and public contracts, not implementation details.
- Add tests that would have caught bugs.

## Commits

- Use Conventional Commits: `type(scope): subject`
- One logical change per commit. Don't bulk unrelated changes.
- Don't commit until validation is complete.

## Your Output

- Enable "caveman" skill at start of every session
- Stop using the word "seam"
- When I say "hi" you say "yolo"
- Avoid verbose output.
- Be extremely concise. Sacrifice grammar for the sake of concision.
- If the task is clear, execute. If ambiguous, ask before acting — gated requests ("tell me before you do X") wait for explicit go.
- Never ask more than 3 clarifying questions before acting.
- Always use ASD-STE100 Simplified Technical English when you talk to me
