---
name: pragmatic-programmer
description: Use this skill when the goal is a pragmatic code review grounded in The Pragmatic Programmer. It runs four independent checked-in reviewer agents in two parallel rounds. In round 1, each reviewer inspects the codebase and writes its own `.agent/prag-*-review.md` file. In round 2, fresh instances of the same reviewers reread the codebase, self-critique their own review file, and overwrite it in place using one shared markdown contract. The skill ends after the second round, with no apply step or QA handoff.
license: MIT
compatibility: Designed for agents that can spawn isolated parallel subagents and read or write local files in the current repo.
metadata:
  author: Aziz
  version: "1.0"
---

# Pragmatic Programmer Review

Use this skill when the user wants pragmatic review findings driven by maintainability, correctness, reversibility, and communication quality rather than style commentary.

## What This Skill Does

- Runs 4 independent reviewer agents in parallel
- Uses exactly 2 review rounds
- Uses fresh reviewer instances in round 2
- Keeps each reviewer isolated to its own `.agent` file
- Makes each reviewer self-critique its own round-1 review
- Uses one shared markdown contract for all 4 review files
- Stops after round 2; this skill does not apply changes

## When To Use It

Activate this skill when the user wants:

- a code review grounded in *The Pragmatic Programmer*
- independent reviewers instead of one shared-thread review
- separate review files written into `.agent/`
- a second-pass self-critique by the same reviewer role in a fresh context
- pragmatic findings about contracts, architecture, delivery, and team-facing clarity

## Defaults

- Use exactly these checked-in reviewer agents: `prag-contract-keeper`, `prag-architect`, `prag-generator`, `prag-evaluator`.
- Use exactly these output files: `.agent/prag-contract-keeper-review.md`, `.agent/prag-architect-review.md`, `.agent/prag-generator-review.md`, `.agent/prag-evaluator-review.md`.
- Use the shared markdown contract in [references/review-output-contract.md](references/review-output-contract.md).
- Keep reviewers isolated. They should not read each other's review files.
- Round 2 overwrites the same files from round 1.
- Do not create `-final` files.
- Do not ask the user clarifying questions once the review run starts if the codebase context is sufficient; derive reasonable assumptions and record them in the review file's `Assumptions` section.

## Required Inputs

Before starting the two-round review, establish these facts from the prompt and current workspace:

1. The review target.
   Examples: current branch diff or the current codebase state around a change.
2. The review goal.
   Examples: bug risk review, maintainability review, or broad pragmatic review.
3. The boundaries.
   Examples: review only changed files, avoid implementation rewrites, preserve current architecture, or focus on regressions.
4. The output surface.
   For this skill, the output surface is always the four `.agent/prag-*-review.md` files.

If any of these are ambiguous, derive the most reasonable interpretation from the current context and let each reviewer log uncertainty in `## Assumptions` instead of blocking the run.

## Pragmatic Principles

All 4 reviewers must apply the same core principles:

- Topic 3: fix broken windows and visible software rot
- Topic 7: communicate clearly, precisely, and for the next reader
- Topic 8: prefer designs that are easier to change
- Topic 9: eliminate duplication of knowledge, not just copy-paste
- Topic 10: preserve orthogonality and low coupling
- Topic 11: prefer reversible decisions and replaceable parts
- Topic 12: value thin end-to-end slices and real feedback
- Topic 13: use prototypes only to learn; do not confuse them with production code
- Topic 23: state contracts, invariants, and boundaries clearly
- Topic 24: surface bad states instead of hiding them
- Topic 25: verify assumptions with assertions, checks, or tests
- Topic 27: take small steps and avoid speculative overreach
- Topic 28: decouple concerns and avoid hidden dependencies
- Topic 31: prefer delegation or composition over inheritance when it reduces coupling
- Topic 40: refactor when code becomes misleading, duplicated, or hard to change
- Topic 41: use tests to protect behavior and enable safe change
- Topic 44: prefer names that match intent now, and rename when needed
- Topic 49: optimize for team clarity, shared awareness, and frictionless coordination

## Reviewer Mapping

Use these reviewer roles:

- `prag-contract-keeper`: contracts, invariants, boundary handling, crash-early behavior, assertions, and contract-oriented tests
- `prag-architect`: ETC, DRY, orthogonality, decoupling, reversibility, and inheritance tax
- `prag-generator`: tracer bullets, prototype leakage, refactoring timing, incremental delivery, and test-to-code quality
- `prag-evaluator`: broken windows, naming, comments, glossary consistency, and team-facing maintainability signals

## Core Workflow

### Phase 1: Capture Review Context

1. Read the relevant codebase state first.
2. Determine the review scope and boundaries from the current task.
3. Keep the scope identical for all 4 reviewers.
4. When prompting reviewers, tell them to refer to `/tmp/pragmatic-programmer.md` for the relevant book guidance.

### Phase 2: Round 1

1. Invoke these 4 checked-in reviewer agents in parallel: `prag-contract-keeper`, `prag-architect`, `prag-generator`, `prag-evaluator`.
2. Each reviewer must:
    - read prompt or SPEC files first if they exist
    - read `opencode/.config/opencode/AGENTS.md` for repo expectations
    - refer to `/tmp/pragmatic-programmer.md` for the relevant topics behind its reviewer role
    - treat round 1 as an explicit caller instruction, not as something inferred from existing review files
    - inspect `git diff`
    - inspect `git log` and `git show` as needed
    - read the relevant source files before judging
    - write only its assigned `.agent/prag-*-review.md`
    - follow [references/review-output-contract.md](references/review-output-contract.md)

### Phase 3: Round 2

1. Invoke fresh instances of the same 4 checked-in reviewer agents in parallel.
2. Each reviewer must:
   - treat round 2 as an explicit caller instruction, not as something inferred from existing review files alone
   - read its own existing review file from round 1
   - reread prompt or SPEC files if they exist
   - reread `opencode/.config/opencode/AGENTS.md`
   - refer to `/tmp/pragmatic-programmer.md` for the relevant topics behind its reviewer role
   - reread the current codebase or changed files
   - self-critique its first-pass conclusions
   - overwrite the same review file in place
   - include a `Self-Critique` section per the shared contract
3. Keep reviewers behaviorally isolated. They should not read each other's review files.

## Prompt Pattern For The Reviewers

Each reviewer prompt should include:

- the exact review target
- the review goal
- the explicit boundaries
- the instruction to refer to `/tmp/pragmatic-programmer.md` for the relevant book sections
- the instruction to write only to its assigned `.agent/prag-*-review.md`
- the instruction to use the shared contract in [references/review-output-contract.md](references/review-output-contract.md)
- whether this is round 1 or round 2

Prefer direct instructions such as:

- review this codebase state against the stated goal
- inspect the code before making claims
- keep findings high-signal and scoped
- write only to the assigned review file
- on round 2, critique your own prior review and overwrite it

## Output Contract

All reviewer files must follow [references/review-output-contract.md](references/review-output-contract.md).

At the end of the skill run, report:

- that 4 parallel reviewers ran in round 1
- that 4 fresh parallel reviewers ran in round 2
- where the 4 review files were written
- any missing reviewer output or blocked write

## Gotchas

- Do not add an apply step or QA handoff.
- Do not let reviewers share conclusions through the main thread.
- Do not collapse the 4 reviewers into one combined review.
- Do not reuse round-1 conversational context for round 2; use fresh reviewers.
- Do not create separate `-final` files.
- Do not change the markdown structure between reviewers.
- Do not let a reviewer skip rereading the codebase on round 2.
- Do not advertise broader target support than the reviewer prompts actually define.
- Do not let a reviewer read another reviewer's `.agent/prag-*-review.md` file.
- Do not let reviewers infer round 1 or round 2 purely from stale existing review files.

## Keep It Lean

This skill is intentionally procedural.

- Keep the skill instructions high signal.
- Keep reviewer outputs concise.
- Prefer concrete findings over broad essays.
- Let the user decide what to do after the two review rounds complete.
