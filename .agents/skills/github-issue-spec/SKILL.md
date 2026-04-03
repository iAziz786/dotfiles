---
name: github-issue-spec
description: Create a well-formed GitHub issue as a spec-style planning artifact. Use when the user asks to create a GitHub issue, open a ticket, write an issue body, plan a feature or bug as a GitHub issue, file a spec, or open a planning artifact. Follows the required template format with Problem, Acceptance Criteria, Edge Cases & Exclusions, and Dependencies. Resolves ambiguity before drafting. Does not embed implementation details unless explicitly requested.
license: MIT
compatibility: Designed for OpenCode and Claude Code
metadata:
  author: Aziz
  version: "1.0"
---

# GitHub Issue Spec Creation

Create planning artifacts as GitHub issues using a structured template format.

## When To Use

Activate this skill when the user:
- Asks to "create a GitHub issue" or "open a ticket"
- Wants to "write an issue" or "file a spec"
- Needs to plan a feature, bug, or task as a GitHub issue
- Mentions "planning artifact" or "spec-style issue"

## Before Drafting

Resolve these questions before writing the issue body:

1. **What is the user-facing problem?**
   - One paragraph only
   - User-facing behavior only
   - No internal architecture or implementation details

2. **What are the observable acceptance criteria?**
   - Use checkboxes: `- [ ] Observable behaviour N`
   - Must be verifiable from outside the system
   - No implementation steps

3. **What is explicitly out of scope?**
   - List edge cases and exclusions
   - Define boundaries clearly

4. **Are there dependencies or open questions?**
   - Links to related issues
   - Decisions needed before work starts

5. **Which repository?**
   - If ambiguous, ask the user
   - Do not assume the current repo is the target

## Required Output Template

Use exactly this structure, adapting content for the specific task:

```md
## Problem
One paragraph. User-facing behaviour only. No internal architecture.

## Acceptance Criteria
- [ ] Observable behaviour 1
- [ ] Observable behaviour 2

## Edge Cases & Exclusions
- What this explicitly does not cover

## Dependencies / Open Questions
- Links to related issues or decisions needed before work starts
```

## Rules

- **Problem section:** One paragraph maximum. Focus on user impact, not technical cause.
- **Acceptance Criteria:** Observable behaviors only. The user should be able to verify each criterion is met without looking at code.
- **No implementation details** in any section unless the user explicitly requests them.
- **Edge Cases:** Be explicit about what's excluded. Prevents scope creep.
- **Dependencies:** Flag blockers early. Include decision points that need resolution.

## Gotchas

- The agent may try to describe the technical implementation in the Problem section. Stop this — user-facing behavior only.
- The agent may omit Edge Cases when they're uncomfortable. Force explicit exclusions.
- The agent may assume the current working directory's repo is the target. Always confirm if ambiguous.
- The agent may write implementation steps as acceptance criteria. Check each one — would a user verify this from outside?

## Output

Return the drafted issue body in the required template format. Do not create the actual GitHub issue unless explicitly asked — the skill drafts the spec, the user decides when to file it.
