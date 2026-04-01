# Review Output Contract

Use this exact markdown structure for every reviewer file.

## Round 1 Template

```markdown
# Pragmatic Review: <name>

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

Overwrite the same file and keep the same top-level title.

```markdown
# Pragmatic Review: <name>

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

## Self-Critique
- <what round 1 missed, overstated, or would now reframe>

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
- Put concrete failure mode, if relevant, inside `Why it matters` rather than inventing extra fields.
- Put softer concerns or uncertainty in `Assumptions` rather than adding custom sections.
- Order findings by severity.
- Prefer concrete evidence over generic advice.
- Use `- None` in `Findings` only when there are no findings.
- Use `None` when another section has nothing to report.
- In round 2, `Self-Critique` is required.
