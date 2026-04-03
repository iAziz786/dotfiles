# Review Output Contract

Use this exact markdown structure for every reviewer file.

## Round 1 Template

```markdown
# Pragmatic Review: <name>

## Cycle Info
- Cycle: <N>
- Round: 1

## Verdict
- <approved | concerns | blocked>

## Findings
- Severity: <critical | high | medium | low>
  File: <path:line or `None`>
  Issue: <concise problem>
  Why it matters: <impact on correctness, changeability, safety, or clarity>
- Severity: <...>
  File: <...>
  Issue: <...>
  Why it matters: <...>
- None

## Recommendations
- <specific next step or `None`>

## Assumptions
- <assumption, uncertainty, or `None`>
```

## Round 2 Template

Overwrite the same file. Round 2 contains only **validated** findings.

```markdown
# Pragmatic Review: <name>

## Cycle Info
- Cycle: <N>
- Round: 2 (Validation)

## Verdict
- <approved | concerns | blocked>

## Findings
- Severity: <critical | high | medium | low>
  File: <path:line or `None`>
  Issue: <concise problem>
  Why it matters: <impact on correctness, changeability, safety, or clarity>
  Validation: <confirmed|modified|new>
- Severity: <...>
  File: <...>
  Issue: <...>
  Why it matters: <...>
  Validation: <...>
- None

## Self-Critique
- Round 1 claimed: <finding that was dropped>
  Dropped because: <why it was invalid/stale/false positive>
- <repeat for each rejected finding>
- No findings rejected in validation pass

## Recommendations
- <specific next step or `None`>

## Assumptions
- <assumption, uncertainty, or `None`>
```

## Rules

- Keep the file concise.
- Keep `Verdict` to one line.
- `Findings` supports zero to many entries.
- For each finding, include `Severity`, `File`, `Issue`, and `Why it matters`.
- In round 2, add `Validation` field: `confirmed` (unchanged), `modified` (adjusted), or `new` (discovered during re-review).
- Put concrete failure mode inside `Why it matters`.
- Put rejected findings only in `Self-Critique`, never in `Findings`.
- Put softer concerns in `Assumptions`.
- Order findings by severity.
- Prefer concrete evidence over generic advice.
- Use `- None` in `Findings` when no valid findings remain.
- Use `None` when another section has nothing to report.
- In round 2, `Self-Critique` is required and must explain every rejected finding.
- Include `Cycle Info` header in both rounds for tracking.
