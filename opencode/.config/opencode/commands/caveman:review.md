---
description: One-line code review using caveman style - terse, actionable, no throat-clearing
argument-hint: [file-or-code-snippet]
allowed-tools: [Read, Grep, Edit, Bash]
---

# Caveman Review

## Arguments

The user invoked this command with: $ARGUMENTS

## Instructions

When this command is invoked:

1. If user provided a file path or code snippet, analyze it
2. If no argument provided, check for open PR with `gh pr view` or look at current file changes
3. Review the code for:
   - Bugs/errors
   - Security issues
   - Performance problems
   - Maintainability concerns
   - Missing edge case handling
4. Provide feedback in caveman one-line format

## Review Format

```
L<line>: <severity>: <problem>. <fix>.
```

**Severity levels:** bug, risk, nit, q

## Severity Indicators

| Emoji | Severity | Meaning |
|-------|----------|---------|
| 🔴 | bug | Bug, security risk, or crash potential |
| 🟡 | risk | Performance issue, maintainability concern |
| 🟢 | nit | Style, readability, minor suggestion |
| ⚪ | q | Question about intent or approach |

## Rules

- One line per issue
- Include line number (L42:)
- Severity indicator upfront
- Terse description of problem
- Actionable fix suggestion
- Drop articles and filler
- Technical terms exact
- **Skip praise** - don't compliment, only identify issues
- **Skip obvious** - don't state what the code clearly does
- If code looks good, say **'LGTM'** and stop

## Examples

**Bad:**
```
On line 42, I noticed that you're checking for the user variable but you're not handling the case where it might be null, which could lead to a runtime error. I would suggest adding a guard clause to check for null before accessing properties on the user object.
```

**Good:**
```
L42: 🔴 bug: user null. Add guard.
```

**Bad:**
```
The authentication middleware on line 55 is using the less-than-or-equal operator for token expiry comparison, but this is incorrect because it will allow expired tokens. You should change it to use the less-than operator instead.
```

**Good:**
```
L55: 🔴 bug: token expiry use <= not <. Fix comparison.
```

**Bad:**
```
I see that you're creating a new database connection on every request in the handler function. This is going to cause performance issues under load because establishing a connection is expensive. You should use connection pooling instead.
```

**Good:**
```
L23: 🟡 perf: new DB conn per request. Use pool.
```

**Bad:**
```
The variable name 'x' on line 78 is not very descriptive. It would be better to rename it to something more meaningful like 'userCount' or 'totalUsers' so that other developers can understand what it represents without having to read the surrounding code.
```

**Good:**
```
L78: 🟢 nit: var name 'x' unclear. Rename to userCount.
```

## Batch Reviews

For multiple issues, list each on its own line:

```
L12: 🔴 bug: SQL injection risk. Use parameterized query.
L34: 🟡 perf: nested loop O(n²). Consider hash lookup.
L67: 🟢 nit: fn too long. Split into smaller units.
```

## Example Usage

```
/caveman-review src/auth.ts           # Review specific file
/caveman-review                       # Review current PR/changes
/caveman-review "function foo() { ... }"  # Review code snippet
/caveman-review L45-60                # Review specific lines
```
