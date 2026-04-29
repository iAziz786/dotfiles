# Revsets

Jujutsu's query language for selecting commits. `jj log -r <revset>`.

## Operators (Strongest to Weakest)

| Op | Meaning | Example |
|---|---|---|
| `f(x)` | Function call | `bookmarks()`, `root()` |
| `x-` | Parents of x | `@-` = working copy's parent |
| `x+` | Children of x | `@+` = children of working copy |
| `p:x` | String/date pattern | `description:fix` |
| `x::` | Descendants of x (incl. x) | `main::` |
| `x..` | Not ancestors of x | `main..` |
| `::x` | Ancestors of x (incl. x + root) | `::main` |
| `..x` | Ancestors of x (excl. root) | `..main` |
| `x::y` | Descendants of x that are ancestors of y | `main::feature` |
| `x..y` | Ancestors of y not ancestors of x | `main..feature` |
| `::` | All visible commits | `jj log -r ::` |
| `..` | All visible commits except root | `jj log -r ..` |
| `~x` | NOT x | `~mine()` |
| `x & y` | Intersection | `bookmarks() & mine()` |
| `x ~ y` | In x but not in y | `all() ~ bookmarks()` |
| `x | y` | Union | `@ | main` |

### Binding Precedence (strongest to weakest)
1. `f(x)` — function call
2. `x-` / `x+` — parents / children
3. `p:x` — pattern
4. `x::` / `x..` / `::x` / `..x` — range operators
5. `~x` — NOT
6. `x & y` / `x ~ y` — AND / EXCEPT
7. `x | y` — OR

Parentheses override: `(x & y) | z`

## Functions

### Basic Sets
| Function | Returns |
|---|---|
| `all()` | All visible commits |
| `none()` | Empty set |
| `root()` | Virtual root commit (`00000000`) |
| `visible_heads()` | All visible heads (no descendants) |

### Bookmarks / Tags / Refs
| Function | Returns |
|---|---|
| `bookmarks()` | Commits with bookmarks |
| `tags()` | Commits with tags |
| `branches()` | Alias for `bookmarks()` |
| `remote_bookmarks()` | Remote-tracking bookmark targets |

### Set Operations
| Function | Returns |
|---|---|
| `heads(x)` | Heads within set x |
| `roots(x)` | Roots within set x |
| `parents(x)` | Parents of commits in x |
| `children(x)` | Children of commits in x |
| `ancestors(x)` | All ancestors of commits in x |
| `descendants(x)` | All descendants of commits in x |
| `connected(x)` | Connected subgraph containing x |
| `latest(x, n)` | Latest n commits per change in x |

### Metadata Filters
| Function | Returns |
|---|---|
| `description(pattern)` | Description matches pattern |
| `author(pattern)` | Author matches pattern |
| `committer(pattern)` | Committer matches pattern |
| `mine()` | Your commits (by user.email) |

### Commit Properties
| Function | Returns |
|---|---|
| `empty()` | No diff from parent(s) |
| `merges()` | Merge commits (2+ parents) |
| `mutable()` | Rewritable commits (not immutable) |
| `conflicts()` | Has unresolved conflicts |
| `divergent()` | Divergent changes (same change ID, different content) |

### Diff / File
| Function | Returns |
|---|---|
| `diff_contains(pattern)` | Diff contains pattern |
| `diff_files(pattern)` | Touches files matching pattern |
| `diff_lines(regex:pattern)` | Changed lines matching regex |

### Operations
| Function | Returns |
|---|---|
| `at_operation(x)` | Commits visible at operation x |
| `opset(x)` | Operation set |

## Patterns

Syntax: `type:value`

| Type | Example | Matches |
|---|---|---|
| `description:` | `description:fix` | Commit message contains "fix" |
| `author:` | `author:martin` | Author name/email contains "martin" |
| `committer:` | `committer:bot` | Committer name/email contains "bot" |
| `diff_contains:` | `diff_contains:TODO` | Patch adds/removes "TODO" |
| `diff_files:` | `diff_files:*.rs` | Touches Rust files |
| `regex:` | `diff_lines(regex:foo.*bar)` | Changed lines matching regex |

## Symbols & Syntax

| Symbol | Resolves to |
|---|---|
| `@` | Working copy commit |
| `<workspace>@` | Another workspace's working copy |
| `<name>` | Tag > bookmark > git ref > commit/change ID |
| `<name>@<remote>` | Remote-tracking bookmark |
| `<change-id>` | Visible commit by change ID |
| `<change-id>/<offset>` | Hidden/divergent commit (e.g. `xyz/1`) |
| `<commit-id>` | Any commit by full or unique-prefix commit ID |

Use quotes to prevent interpretation: `"x-"` is the symbol `x-`, not parents.

## Common Patterns

| Intent | Revset |
|---|---|
| Everything local | `::@` |
| My un-pushed work | `mine() & ~remote_bookmarks()@origin` |
| My stack (reviewable) | `heads(::@ ~ ::main)` |
| Range not on main | `main..@` |
| Conflicts I created | `mine() & conflicts()` |
| Empty commits I made | `mine() & empty()` |
| Last 5 commits | `latest(@-, 5)` |
| All bookmarks + root | `bookmarks() | root()` |
| Bookmarks not on remote | `bookmarks() ~ remote_bookmarks()@origin` |
| Merge commits in my work | `mine() & merges()` |
| Everything in repo | `::` or `all()` |
