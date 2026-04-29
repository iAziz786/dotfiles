# Templates

Templates control how JJ displays commits, diffs, and other objects. Set in `~/.jj/config.toml`.

## Commit Type Fields

| Field | Type | Description |
|---|---|---|
| `change_id` | `ChangeId` | Stable identifier |
| `commit_id` | `CommitId` | Content hash |
| `author` | `Signature` | author.name, author.email, author.time, author.tz |
| `committer` | `Signature` | committer.name, committer.email, committer.time, committer.tz |
| `description` | `String` | Full commit message |
| `parents` | `Vec<Commit>` | Parent commits |
| `children` | `Vec<Commit>` | Child commits |
| `empty()` | `Boolean` | No diff from parent(s) |
| `conflicts()` | `Boolean` | Has unresolved conflicts |
| `branches()` / `bookmarks()` | `Vec<RefName>` | Bookmarks pointing here |
| `tags()` | `Vec<RefName>` | Tags pointing here |
| `working_copies()` | `Vec<Workspace>` | Workspaces with this checked out |
| `diff()` | `Diff` | Diff as inline-colored text |
| `diff_git()` | `Diff` | Git-format diff |
| `trailers()` | `Vec<Trailer>` | Commit trailers (Signed-off-by, etc.) |

### Signature Fields
`author.name`, `author.email`, `author.timestamp`, `author.tz` (same for `committer`)

### Timestamp Fields
`author.timestamp.format("<fmt>")` — uses chrono format strings.

## Types

| Type | Methods |
|---|---|
| `String` | `.shortest(n)`, `.first_line()`, `.trim_end()`, `.contains(s)` |
| `ChangeId` | `.shortest(n)` |
| `CommitId` | `.shortest(n)` |
| `Vec<T>` | `.len()`, `.first()`, `.last()`, `.skip(n)`, `.map(\|x| ...)`, `.join(sep)` |
| `Boolean` | `not`, `and`, `or` |
| `RefName` | `.name()`, `.remote()` |
| `Signature` | `.name()`, `.email()`, `.timestamp()` |
| `Diff` | `.git()` |

## Expressions

| Expression | Effect |
|---|---|
| `change_id.shortest(8)` | Short change ID |
| `commit_id.shortest(8)` | Short commit ID |
| `description.first_line()` | First line of message |
| `description.trim_end()` | No trailing whitespace |
| `separated(" ", bookmarks())` | Join bookmarks with spaces |
| `separated(" ", bookmarks().map(\|b\| b.name()))` | Just bookmark names |
| `if(condition, then, else)` | Conditional |
| `concat(a, b, ...)` | String concatenation |
| `"literal" ++ expr` | String literal + expression |
| `label("label_name", content)` | Color/style a section |
| `indent(" ", content)` | Indent content |
| `pad_left(n, content)` / `pad_right(n, content)` | Pad to width |

### Boolean Operations
| Expression | Equivalent |
|---|---|
| `not expr` | `!expr` |
| `expr1.and(expr2)` | `expr1 && expr2` |
| `expr1.or(expr2)` | `expr1 \|\| expr2` |

## Config Examples

### Draft Commit Description (default message in editor)
```toml
[templates]
draft_commit_description = '''
  concat(
    builtin_draft_commit_description,
    "\nJJ: ignore-rest\n",
    diff.git(),
  )
'''
```

### Custom New Commit Message
```toml
[templates]
new_description = '''
  if(parents.len() > 1,
    "Merge " ++ parents.skip(1).map(|p| if(
      p.bookmarks(),
      p.bookmarks().first().name(),
      p.change_id().shortest(8)
    )).join(", ") ++ " into " ++ if(
      parents.first().bookmarks(),
      parents.first().bookmarks().first().name(),
      parents.first().change_id().shortest(8)
    ) ++ "\n",
    ""
  )
'''
```

### Auto-Trailers (Signed-off-by, Change-Id)
```toml
[templates]
commit_trailers = '''
  format_signed_off_by_trailer(self) ++
  if(!trailers.contains_key("Change-Id"),
    format_gerrit_change_id_trailer(self)
  )
'''
```

### Duplicate Description
```toml
[templates]
duplicate_description = '''
  concat(
    description.trim_end(),
    "\n\n(cherry picked from commit ",
    commit_id,
    ")\n"
  )
'''
```

### Custom Log Format
```toml
[template-aliases]
"format_short_id(id)" = "id.shortest(12)"
"format_commit(commit)" = '''
  concat(
    change_id.shortest(8), " ",
    commit_id.shortest(8), " ",
    author.email, " ",
    description.first_line(),
  )
'''
```

## Colors & Styles

```toml
[colors]
commit_id = "cyan"
change_id = "green"
"working_copy commit_id" = { underline = true }
"diff added" = { fg = "green", bold = true }
"diff removed" = { fg = "red", bold = true }
"diff added token" = { bg = "#002200", underline = false }
"diff removed token" = { bg = "#221111", underline = false }
```

Available colors: `black`, `red`, `green`, `yellow`, `blue`, `magenta`, `cyan`, `white`, `default` + `bright-*` variants, hex codes (`#ff1525`), ANSI 256 (`ansi-color-81`).

Style properties: `fg`, `bg`, `bold`, `dim`, `italic`, `underline`, `reverse`.

Label selectors compose like CSS: `"working_copy commit_id"` = commit_id within working_copy.
