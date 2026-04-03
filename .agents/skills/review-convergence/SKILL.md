---
name: review-convergence
description: Use this skill when the user wants an autonomous iterative review loop over changed files, docs, issues, PRs, or other artifacts. It runs a sequential A-then-B general-agent review cycle through files in /tmp/<workspace>-<usecase>, has each reviewer validate the other's findings across rounds, applies valid changes with an isolated general subagent spawned via the task tool, and keeps looping until two consecutive review rounds produce no findings.
license: MIT
compatibility: Designed for agents that can spawn isolated general subagents and read or write local files plus target artifacts such as repo files or GitHub issues.
metadata:
  author: Aziz
  version: "1.0"
  state_root: "/tmp"
---

# Review Convergence

Use this skill when the goal is not just review, but converged review followed by changes and re-review.

## What This Skill Does

- Runs a sequential `general` review cycle: Reviewer A, then Reviewer B, then an apply agent
- Makes agents communicate only through files, not shared conversational state
- Has each reviewer do its own artifact review and validate the other reviewer's findings across rounds
- Hands valid findings to an isolated `general` subagent (spawned via task tool) to apply changes
- Reruns the review/apply loop on the updated artifact
- Repeats until two consecutive review rounds produce no findings

## When To Use It

Activate this skill when the user wants:

- review feedback to converge before changes are applied
- independent reviewers instead of one shared-thread review
- iteration files stored outside the repo worktree
- the same convergence loop to work for local files, docs, issues, PRs, or similar artifacts
- the current task context and goal turned into a repeatable review/apply/re-review workflow

## Defaults

- The caller decides the target artifact each time.
- The target can be local files, GitHub artifacts, or whichever target the task is about.
- Use a state directory at `/tmp/<workspace>-<usecase>`.
- Derive `<workspace>` from the current workspace or repository folder name.
- Derive `<usecase>` from a short slug of the current task goal.
- Do not ask the user clarifying questions once the loop starts; derive missing details from context, make reasonable assumptions, and log them.
- Keep the skill instructions high-level and script-free unless a later iteration proves scripts are needed.

## Required Inputs

Before starting the loop, establish these facts from the current prompt and context:

1. The target artifact.
2. The review goal.
3. The boundaries.
   Examples: keep it high-level, avoid implementation details, preserve specific business rules, do not update GitHub yet.
4. The allowed modification surface.
   Examples: local files only, issue body only, whichever target the task is about.

If any of these are ambiguous, derive the most reasonable interpretation from the current context, record the assumption in `iteration-log.md`, and continue.

## State Directory

Create and use one state directory for the full run:

`/tmp/<workspace>-<usecase>`

Keep all iteration artifacts there so the two reviewers and the apply agent can coordinate without sharing conversational context.

Recommended files:

- `target-snapshot.md`
- `review-a.md`
- `review-b.md`
- `apply-summary.md`
- `iteration-log.md`

Use the filenames above unless the current task already has a stronger established contract.

## Core Workflow

### Phase 1: Capture the Current State

1. Read the current artifact state.
2. Write a clean snapshot into the state directory so each later agent can review the same material.
3. Record the goal, boundaries, and stopping rule in `iteration-log.md`.

### Phase 2: Run Reviewer A

Spawn one `general` agent for Reviewer A.

Reviewer A:
- Reviews the current state against the stated goal and boundaries.
- If a prior `review-b.md` exists from the previous round, validate B's prior findings after finishing the independent review.
- Writes findings to `review-a.md`.

On round 1, omit any cross-validation section because there is no prior `review-b.md`.

### Phase 3: Run Reviewer B

Spawn one `general` agent for Reviewer B after Reviewer A finishes.

Reviewer B:
- Reviews the current state independently.
- Reads `review-a.md` from the current round after finishing the independent review.
- Validates A's findings as valid, partially valid, or invalid.
- Adds net-new findings if A missed anything.
- Writes the full result to `review-b.md`.

Keep both reviewers focused on:

- true gaps
- wording issues
- unnecessary detail
- anything that violates the user's stated goal

Do not let either reviewer apply changes directly.

### Phase 4: Apply Changes

Spawn an isolated `general` subagent via the task tool after Reviewer B finishes. Do **not** do this work inline in the current orchestrating context.

- `review-a.md`
- `review-b.md`
- the current artifact snapshot

Rules for the apply agent:

- apply valid and partially valid findings from the current round
- modify only the current target surface
- preserve the user's stated boundaries
- do not add unrelated improvements
- do not renegotiate whether a finding is correct
- write `apply-summary.md` with what changed

### Phase 5: Stop or Loop

1. Refresh `target-snapshot.md` from the updated artifact state.
2. Check whether the current round produced any findings from either reviewer.
3. Check whether `apply-summary.md` shows no changes were needed.

Count the round as clean only when:

- Reviewer A has no own findings
- Reviewer B has no own findings
- Reviewer B raises no net-new findings
- the apply agent made no changes

Stop only after two consecutive clean rounds.

If the current round is not clean, reset the clean-round counter to zero and start the next round.

## Prompt Pattern For The Reviewers

Each reviewer prompt should include:

- the exact target snapshot to review
- the review goal
- the explicit boundaries and preserved requirements
- the instruction to write only to its assigned file in `/tmp/<workspace>-<usecase>`
- whether it should also validate the other reviewer's findings from the relevant round

Prefer direct instructions such as:

- review this artifact against the stated goal
- finish your own review before reading the other review file
- keep the feedback high-signal and scoped
- write only to the assigned state file
- do not modify the target artifact

## Output Contract

At the end of the loop, report:

- where the state directory lives
- which artifact was updated
- how many review/apply rounds were needed
- that two consecutive clean review rounds were reached

## Gotchas

- Do not ask the user clarifying questions once the loop starts; derive and log assumptions instead.
- Do not let the two reviewers silently share conclusions through the main thread; the files are the coordination layer.
- Do not let Reviewer A read `review-b.md` until A has finished its own independent review for the round.
- Do not let Reviewer B read `review-a.md` until B has finished its own independent review for the round.
- Do not let the apply agent become another reviewer; it should implement accepted findings, not renegotiate them.
- **Spawn the apply agent as an isolated `general` subagent via the task tool, not inline in the current context**; inline apply work contaminates the orchestrating context with artifact details that should stay scoped to the apply step.
- Do not stop after one clean round; the loop ends only after two consecutive clean rounds.
- If the task target changes mid-run, refresh the snapshot and log the change before continuing.
- Keep state in `/tmp/<workspace>-<usecase>` rather than the repo unless the user explicitly wants the artifacts checked in.

## Minimal File Contract

Use these files by default:

- `target-snapshot.md`
- `review-a.md`
- `review-b.md`
- `apply-summary.md`
- `iteration-log.md`

Keep each file concise. `review-a.md` should contain A's own findings and, on rounds after the first, A's validation of the prior `review-b.md`. `review-b.md` should contain B's own findings, B's validation of the current `review-a.md`, and any net-new findings B identified. `apply-summary.md` should say what changed or that no changes were needed.

## Keep It Lean

This skill is intentionally procedural rather than tool-heavy. If repeated real runs show the same file-management or state-bookkeeping work being recreated over and over, then add scripts in a later version.
