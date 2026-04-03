---
name: pragmatic-programmer
description: Use this skill when the goal is a pragmatic code review grounded in The Pragmatic Programmer that iterates through review cycles. Each cycle runs 4 reviewers (2 rounds with validation), consolidates findings, applies fixes, and repeats up to 5 times. Pauses for user clarification on ambiguity and reports regressions with ASCII diagrams.
license: MIT
compatibility: Designed for agents that can spawn isolated parallel subagents and read or write local files in the current repo.
metadata:
  author: Aziz
  version: "2.0"
---

# Pragmatic Programmer Review

Use this skill when the user wants pragmatic review findings that lead to actual fixes, with multiple review cycles driven by maintainability, correctness, reversibility, and communication quality.

## What This Skill Does

- Runs **iterative review-fix cycles** (max 5 cycles)
- Each cycle consists of:
  - **Round 1**: 4 independent reviewers in parallel (fresh inspection)
  - **Round 2**: Same 4 reviewers validate and consolidate (only retain valid findings)
  - **Consolidation**: Gather validated findings from all 4 reviewers
  - **Fixer**: One isolated `general` agent applies the fixes
- Tracks cycle state in `.agent/` folder
- Pauses for user clarification on ambiguity (does not count as a cycle)
- Reports regressions with ASCII diagrams at the 5-cycle limit

## When To Use It

Activate this skill when the user wants:

- a code review grounded in *The Pragmatic Programmer*
- iterative refinement with actual fixes, not just reports
- validated findings (round 2 filters out stale findings)
- safe stopping with clear regression explanations

## Defaults

- Reviewer agents: `prag-contract-keeper`, `prag-architect`, `prag-generator`, `prag-evaluator`
- Review files: `.agent/prag-*-review-r1.md` and `.agent/prag-*-review-r2.md` (where * is the agent name)
- Consolidated fix brief: `.agent/fix-brief.md`
- State directory: `.agent/`
- Max cycles: 5
- Reviewers isolated: they never read each other's files

## Required Inputs

Before starting, establish:

1. **Review target**: current branch diff, specific files, or full codebase
2. **Review goal**: bug risk, maintainability, or broad pragmatic review
3. **Boundaries**: changed files only, preserve architecture, no rewrites, etc.
4. **Allowed modification surface**: which files the fixer can touch

If ambiguous, make reasonable assumptions and log them in state files.

## Pragmatic Principles

All reviewers apply these:

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

- `prag-contract-keeper`: contracts, invariants, boundary handling, crash-early behavior, assertions
- `prag-architect`: ETC, DRY, orthogonality, decoupling, reversibility, inheritance tax
- `prag-generator`: tracer bullets, prototype leakage, refactoring timing, incremental delivery
- `prag-evaluator`: broken windows, naming, comments, glossary consistency, team signals

## Core Workflow

### Phase 0: Initialize State

Create state directory `.agent/` (if it doesn't exist)

State files:
- `prag-*-review-r1.md` (round 1, overwritten each cycle)
- `prag-*-review-r2.md` (round 2, validated, overwritten each cycle)
- `fix-brief.md` (consolidated, overwritten each cycle)
- `apply-summary.md` (fixer output, overwritten each cycle)
- `iteration-log.md` (cycle history)
- `regression-report.md` (final)

### Phase 1: Round 1 - Fresh Review

Spawn 4 reviewers in parallel. Each must:

- Read prompt/SPEC files if they exist
- Read `opencode/.config/opencode/AGENTS.md`
- Refer to the Pragmatic Principles section above
- Inspect `git diff`, `git log`, relevant source
- Write only to its assigned `.agent/prag-*-review-r1.md` file
- Follow the review output contract

Each reviewer performs independent first-pass analysis without reading prior reviews.

### Phase 2: Round 2 - Validation & Consolidation

Spawn the same 4 reviewers in parallel (fresh instances). Each must:

- Perform independent review first
- Then read its own round-1 file
- Validate each finding from round 1:
  - **confirmed**: finding is still valid, evidence holds (mark as `confirmed`)
  - **dropped**: finding is stale, false positive, or already fixed (exclude from Findings, explain in Self-Critique)
  - **modified**: finding is partially valid but needs adjustment (mark as `modified`)
  - **new**: discovered during re-review (mark as `new`)
- Write only **validated findings** to the same file
- Include `Self-Critique` explaining what was dropped and why
- Follow the review output contract

Rejected findings do not appear in round-2 output. Only the Self-Critique mentions them.

### Phase 3: Consolidation

Read all 4 round-2 review files from `.agent/` folder. Build `.agent/fix-brief.md` containing:

- Summary of validated findings across all 4 reviewers
- Grouped by severity (critical, high, medium, low)
- Specific file paths and line references
- Clear description of what needs fixing
- Any cross-reviewer conflicts or ambiguities

If no findings remain after validation, the cycle is clean. Skip to Phase 5.

If findings exist and this is the first cycle, proceed to Phase 3.5 to get user confirmation before applying fixes.

### Phase 3.5: User Confirmation (First Cycle Only)

After building `.agent/fix-brief.md` on the first cycle, pause and use `question` tool:

- **Question**: "Review findings have been consolidated. Do you want to proceed with applying fixes?"
- **Options**: ["Yes, proceed with fixes", "Stop"]
- **If user selects "Stop"**: Exit the skill entirely, do not proceed to Phase 4
- **If user selects "Yes, proceed with fixes"**: Continue to Phase 4 (Fixer Agent)

This confirmation is asked only once before the first fix cycle. Subsequent cycles proceed automatically.

### Phase 4: Fixer Agent

**Prerequisite**: User must have confirmed in Phase 3.5 (first cycle only).

Spawn one isolated `general` subagent via `task` tool.

Fixer agent must:

- Read `.agent/fix-brief.md`
- Read the 4 review files from `.agent/` for context
- Apply only validated findings
- Preserve stated boundaries
- Not renegotiate whether a finding is correct
- Write `apply-summary.md` listing what changed

The fixer can modify any files needed to address findings. No restrictions on file types.

### Phase 5: Stop or Continue

**Stopping conditions:**

1. **Clean cycle**: No findings in round 2 + no changes in fixer
2. **Cycle limit reached**: 5 cycles completed
3. **User pause**: Ambiguity requires clarification (does not count toward 5 cycles)
4. **User declined fixes**: User chose "Stop" in Phase 3.5

**On clean cycle**: Log success, stop.

**On cycle 5 with remaining issues**: Generate regression report (see below).

**On ambiguity**: Pause, ask user, resume same cycle.

**On user declined fixes**: Log "Fixes declined by user", stop immediately.

### Phase 6: Regression Report (Cycle 5 Stop)

When stopping at cycle 5 with unresolved issues, generate ASCII report:

```
================================================================================
                    PRAGMATIC PROGRAMMER REVIEW: REGRESSION REPORT
================================================================================

WHY WE STOPPED
--------------
Maximum cycle limit (5) reached with outstanding issues remaining.

CYCLE SUMMARY
-------------
Cycle 1: X findings -> Y applied
Cycle 2: X findings -> Y applied
Cycle 3: X findings -> Y applied
Cycle 4: X findings -> Y applied
Cycle 5: X findings -> Y applied

OUTSTANDING ISSUES
------------------
[From round-2 review files of cycle 5]

REGRESSION ANALYSIS
-------------------
[Diagram showing issue persistence across cycles]

Example ASCII diagram format:

    Cycle 1          Cycle 2          Cycle 3          Cycle 4          Cycle 5
    ┌──────┐         ┌──────┐         ┌──────┐         ┌──────┐         ┌──────┐
    │Issue A│────────>│Issue A│────────>│Issue A│────────>│Issue A│────────>│Issue A│
    └──────┘         └──────┘         └──────┘         └──────┘         └──────┘
         │ Attempted fix failed or incomplete
         v
    [Root cause explanation]

POSSIBLE CAUSES
---------------
- Fix attempts not addressing root cause
- New issues introduced by fixes
- Test coverage gaps preventing verification
- Architectural constraints blocking clean solutions

RECOMMENDATIONS
---------------
- Manual intervention required
- Consider breaking into smaller PRs
- Add missing tests before next fix attempt
- Re-evaluate architecture if issues persist

================================================================================
```

Use `question` tool to ask user:

- "Do you want to continue despite cycle limit?"
- "Should we focus on specific findings?"
- "Any architectural changes needed?"

After user response, resume from current state or reset as directed.

## Ambiguity Pause

When any agent encounters ambiguity that blocks progress:

1. Record the ambiguity in `iteration-log.md` with:
   - Timestamp
   - Current cycle and phase
   - Exact question that needs user input
   - What decision is blocked
2. Use `question` tool to ask the user
3. Pause the current phase (does not increment cycle count)
4. **Resume Procedure:**
   - Wait for user response via the question tool
   - Append user response to `.agent/iteration-log.md` with timestamp
   - Incorporate user answer into the current phase's work
   - Continue from the exact point where the pause occurred
   - Do not restart the phase; resume with the context intact

Do not guess when the stakes are high. Prefer pausing with a clear question.

## Prompt Patterns

**For reviewers (both rounds):**

Include:
- Review target
- Review goal
- Boundaries
- Round number (1 or 2)
- Instruction to refer to the Pragmatic Principles section above
- Output file path
- Contract reference

**For fixer:**

Include:
- Path to `.agent/fix-brief.md`
- Allowed modification surface
- Boundaries to preserve
- Instruction to write `apply-summary.md`

## State Management

State directory: `.agent/`

Review files (overwritten each cycle):
- `prag-contract-keeper-review-r1.md` (round 1)
- `prag-contract-keeper-review-r2.md` (round 2, validated)
- `prag-architect-review-r1.md` (round 1)
- `prag-architect-review-r2.md` (round 2, validated)
- `prag-generator-review-r1.md` (round 1)
- `prag-generator-review-r2.md` (round 2, validated)
- `prag-evaluator-review-r1.md` (round 1)
- `prag-evaluator-review-r2.md` (round 2, validated)
- `fix-brief.md` (consolidated)
- `apply-summary.md` (fixer output)

Global files:
- `iteration-log.md` (cycle history, pause reasons)
- `regression-report.md` (final report)

## Output Contract

Review files follow [references/review-output-contract.md](references/review-output-contract.md).

At skill completion, report:
- Cycles completed
- Final state (clean stop, limit reached, user paused)
- Location of review files (in `.agent/` folder)
- Location of regression report (if applicable)

## Gotchas

- Round 2 must only contain validated findings; rejected ones go in Self-Critique only
- Do not let reviewers read each other's files
- Fixer must not re-review; only apply
- Ambiguity pause does not count as a cycle
- Fresh reviewer instances for every round
- Use `task` tool for fixer, not inline
- Keep ASCII diagrams readable in terminal
- **User confirmation in Phase 3.5 only happens once before the first fix cycle**
- If user declines fixes in Phase 3.5, the skill stops entirely

## Keep It Lean

This skill balances thoroughness with pragmatism:

- 5 cycles is enough to catch most patterns without infinite loops
- Validation round filters noise before fixing
- ASCII diagrams are terminal-friendly
- Pauses preserve user agency without losing progress
