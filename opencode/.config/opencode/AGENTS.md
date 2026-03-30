# AGENTS.md

## General

- ALWAYS read prompt and SPEC files first if present before implementing
- ALWAYS use parallel agent for code exploration
- ALWAYS FOLLOW TDD, red phase to green phase
- NEVER write untested code
- ASK FOR HELP if you are stuck, NEVER speculate
- ALWAYS follow review -> iterate -> review loop; break when review requirements satisfied and tests pass

## Output

- ALWAYS keep it concise
- ONLY include necessary information

## Engineering Guardrails

- MUST prefer reversible changes; if a change is hard to undo, state why.
- MUST design for change, replacement, and extension.
- SHOULD keep coupling loose and boundaries clear.
- SHOULD hide implementation details behind small, stable interfaces.
- MUST avoid duplicating knowledge across code, config, schemas, or docs.
- PREFER composition and delegation over inheritance.
- PREFER simple solutions over clever ones.
- AVOID hardcoding volatile policy or environment-specific values.
- ONLY introduce irreversible or tightly coupled designs when the benefit is
  clear and immediate.
- IF a design increases coupling or reduces replaceability, explain the tradeoff.
- VERIFY important assumptions with tests, assertions, or explicit contracts.
- BUILD changes in small, end-to-end, testable steps.

## Tools

- ALWAYS use `bun`, `bunx` over `node`, `npm`, `yarn`, etc.
- ALWAYS `uv` over `pip`
- Use ripgrep (`rg`) instead of `grep`, use `fd` instead of `find`
- For jira use `acli` CLI -- acli jira workitem create/view etc.
- ALWAYS use `--help` for unfimilar commands before using them

## Planning

- NEVER include implementation code in the output/file of spec

## Decision Criteria

- Maintainability is REQUIRED.
- You MUST prefer pit-of-success designs: make the correct path the easiest
  path.
- When multiple approaches are valid, DEFAULT TO the one with clearer
  ownership, less complexity, and lower long-term cognitive load.
- For bug fixes and feature work, PREFER the path that would have prevented
  the bug in the first place or naturally guides future work into the pit
  of success.
- You MUST NOT introduce fragile, duplicated, or easy-to-misuse patterns
  unless explicitly required.

### GitHub Issues

- ALWAYS use GitHub Issues SPEC planning
- ALWAYS ask when there is ambiguity which repo to use for spec writing

When creating an issue, ALWAYS keep this in mind:

#### Key Characteristics

- Specification-style writing: Treats the issue like a mini-spec document
- No implementation details: Focuses on user-facing behavior, not internal architecture
- Complete but concise: Covers all use cases without being verbose
- Forward-looking: Shows how it integrates with existing and planned features

## Commit Instructions

- NEVER include SPEC*.md files in commits
- ALWAYS Follow Conventional Commits
  - <https://www.conventionalcommits.org/en/v1.0.0/>

## Tests

- ALWAYS test behaviour, NEVER implementation details
