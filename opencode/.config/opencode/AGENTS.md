# AGENTS.md

## General Execution Protocol

- Prefer small, reversible, end-to-end changes.
- Default to working in small, testable increments.
- TDD is mandatory for business logic, service objects, and API handlers or
  endpoints:
  - write a failing test first,
  - make the smallest change that passes,
  - refactor once validation is green.
- If test-first is skipped for infrastructure work, exploratory spikes, or
  difficult-to-control integration boundaries, provide a one-sentence
  justification and add the missing test immediately after the behavior is
  understood and stable.
- NEVER guess silently. State assumptions, verify them where possible, and ask
  for help when needed.
- Use parallel exploration when useful, especially for large or unfamiliar
  codebases.
- Follow a `review -> iterate -> review` loop.
- Exit the review loop only when:
  - requirements are satisfied,
  - validation passes,
  - no unresolved correctness or contract risks remain,
  - important tradeoffs are documented.

## Stuck Protocol

If blocked after **2 consecutive failed attempts** on the same problem, or if no
new signal is produced after a reasonable investigation, stop and escalate.

Escalation must include:

- what was attempted,
- what failed and why,
- what evidence was gathered,
- what information, access, or decision is needed to continue.

Do not fabricate APIs, behavior, or missing requirements.

## Output

- PREFER high information density and task-focused output.
- Omit conversational filler, but NEVER omit error handling or type definitions.
- Include only information that helps the next decision or action.
- Be explicit about uncertainty, tradeoffs, open risks, and incomplete
  verification.
- Do not include implementation code in specs or planning documents.

## Context And Memory Discipline

Treat context as limited working memory.

- Preserve only the information needed for the current step.
- When a task spans many steps, persist important state in durable artifacts
  rather than relying on transient context alone.
- Default to using fresh General or Explore agents for codebase exploration,
  broad search, scoped code changes, file edits, and review work unless doing
  so would clearly add unnecessary overhead.
- Keep the main context reserved for coordination, the current decision, and
  final synthesis, not for carrying the full working set of the task.

## Engineering Guardrails

- Prefer reversible changes; if a change is difficult to undo, state why.
- Design for maintainability, replacement, and extension.
- Keep coupling low, boundaries clear, and interfaces small and stable.
- Avoid duplicating knowledge across code, config, schemas, and docs.
- Prefer composition and delegation over inheritance.
- Prefer simple, explicit solutions over clever ones.
- Avoid hardcoding volatile policy or environment-specific values.
- Verify important assumptions with tests, assertions, or explicit contracts.
- Build in small, end-to-end slices that can be validated independently.
- Do not introduce fragile, duplicated, or easy-to-misuse patterns unless
  explicitly required.
- Justify any new dependency. Prefer existing platform capabilities or small
  local helpers when they are sufficient.
- When a tradeoff increases coupling, reduces replaceability, or introduces
  irreversibility, explain why it is worth it.

## Planning And Specs

- Keep specifications focused on user-facing behavior, constraints, acceptance
  criteria, and boundary contracts.
- Do not include implementation logic in specs. Interface definitions, API
  contracts, schemas, IDLs, or DSL shapes are encouraged when they define the
  external behavior or required contract.
- Avoid unnecessary architecture detail unless it is required to make a
  decision.
- Resolve ambiguity before planning. Ask instead of assuming.
- A good spec or planning artifact should cover:
  - problem statement,
  - intended user-facing behavior,
  - acceptance criteria,
  - edge cases and exclusions,
  - dependencies and open questions.

## GitHub Issues

Use the `github-issue-spec` skill when creating GitHub issues as planning artifacts.

## Commit Discipline

- Commit messages should follow Conventional Commits (`type(scope): subject`)
  using a short imperative subject and a scope that matches the feature area
  when practical.
- Do not include `SPEC*.md` files in commits unless explicitly requested.
- Do not commit changes until validation is complete, or explicitly state the
  validation gap.
- Each commit must represent one logical, reviewable change. Do not bulk
  commits across unrelated concerns.
- If a change introduces a non-obvious tradeoff, document it briefly in the
  commit message or accompanying review note.

## Testing

- Test observable behavior and public contracts, not implementation details.
- Add or update tests to cover the intended behavior change.
- Use the smallest test surface that gives confidence.
- For bug fixes, add coverage that would have caught the bug.
- Prefer integration-style tests over brittle low-level tests when they better
  protect behavior and contracts.
- Treat missing tests as a risk to resolve, not a reason to guess.

## Tooling

- In new JavaScript or TypeScript setups, prefer `bun` and `bunx` where
  compatible.
- In new Python setups, prefer `uv` where compatible.
- Prefer `rg` over `grep` and `fd` over `find` when available.
- For unfamiliar commands, read `--help` or official docs before use.
- Do not assume a tool is installed; verify availability before depending on it.
- For Jira workflows, use `acli` when it is available and configured.

## Decision Criteria

- Maintainability is required.
- Prefer pit-of-success designs that make the correct path the easiest path.
- Prefer designs that are easy to use correctly and hard to misuse.
- Prefer the approach that best supports future change with minimal rework.
- Prefer consistency with the existing codebase unless there is a clear benefit
  to changing direction.
- When multiple approaches are valid, choose the one with:
  - clearer ownership,
  - lower complexity,
  - better maintainability,
  - lower long-term cognitive load.
- Prefer fixes that prevent the class of bug, not only the specific instance.
- When introducing a non-obvious design, document the tradeoff briefly.
