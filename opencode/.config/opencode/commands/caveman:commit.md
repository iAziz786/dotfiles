---
description: Generate terse conventional commit message using caveman style (≤50 char subject, why over what)
argument-hint: [diff-or-description]
allowed-tools: [Bash, Read, Write]
---

# Caveman Commit

## Arguments

The user invoked this command with: $ARGUMENTS

## Instructions

When this command is invoked:

1. If user provided a diff or file changes description, analyze it
2. If no argument provided, run `git diff --cached --stat` to see staged changes, or `git diff --stat` for unstaged
3. Identify the type of change:
   - `feat`: New feature
   - `fix`: Bug fix
   - `docs`: Documentation only
   - `style`: Formatting, no code change
   - `refactor`: Code change, neither fix nor feature
   - `perf`: Performance improvement
   - `test`: Adding/updating tests
   - `chore`: Build/tooling/config changes
4. Generate terse commit message for the current staged changes. Conventional Commits format. Why over what.

## Commit Message Format

```
type(scope): terse caveman description

Why this change matters (optional body, also in caveman style)
```

## Rules

- Subject line: ≤50 characters
- Use Conventional Commits type prefix
- Subject must be **imperative** (command form)
- **lowercase after type** (e.g., `feat: add login` not `feat: Add login`)
- **No period on subject** line
- Body: only when 'why' isn't obvious from subject
- Explain **why**, not just **what**
- Drop articles (a/an/the)
- Use short synonyms
- Fragments OK
- No filler words (just, really, basically)

## Examples

**Bad:**
```
feat: implement user authentication with JWT tokens and bcrypt hashing
```

**Good:**
```
feat(auth): JWT login with bcrypt

Token expiry 24h. Hash cost 12. Fix #234.
```

**Bad:**
```
fix: there was a bug in the middleware that was checking the token expiry incorrectly
```

**Good:**
```
fix(auth): token expiry check use < not <=

Edge case: midnight rollover. Fix #456.
```

**Bad:**
```
refactor: I updated the database connection logic to use connection pooling instead
```

**Good:**
```
refactor(db): pool reuse connections

Skip handshake overhead. Pool size 10.
```

## Example Usage

```
/caveman-commit                     # Generate from staged changes
/caveman-commit "added login form"  # Generate from description
/caveman-commit fix: handle null user in auth middleware
```
