# Configuration

## Config Layers (overriding order)

1. **Built-in** — `cli/src/config/` in source (cannot edit)
2. **User** — `jj config edit --user` (personal across all repos)
3. **Repo** — `jj config edit --repo` (per-repo, outside working tree for security)
4. **Workspace** — `jj config edit --workspace` (per-workspace)
5. **CLI** — command-line flags override everything

Find paths: `jj config path --user`, `jj config path --repo`, `jj config path --workspace`

### User Config File Locations
| OS | Path |
|---|---|
| macOS | `~/Library/Application Support/jj/config.toml` |
| Linux | `~/.config/jj/config.toml` (or `$XDG_CONFIG_HOME/jj/config.toml`) |
| Windows | `%APPDATA%/jj/config.toml` |

## Essential Config

```toml
[user]
name = "Your Name"
email = "you@example.com"
```

## UI Settings

```toml
[ui]
default-command = ["log", "--reversed"]   # what `jj` (no subcommand) runs
color = "auto"                            # always / never / auto / debug
pager = "auto"                            # always / never / auto
paginate = "auto"                         # built-in pager
```

### Editor
JJ respects `$EDITOR` and `$JJ_EDITOR` env vars. The `$JJ_EDITOR` takes precedence.

```toml
[ui]
editor = "code --wait"   # VS Code
```

## Colors

```toml
[colors]
commit_id = "cyan"
change_id = "green"
description = "yellow"
"working_copy change_id" = { bold = true }
"working_copy commit_id" = { underline = true }
"diff added" = { fg = "green", bold = true }
"diff removed" = { fg = "red", bold = true }
"diff modified" = { fg = "blue" }
"diff added token" = { bg = "#002200", underline = false }
"diff removed token" = { bg = "#221111", underline = false }
conflict = { fg = "red", bold = true }
empty = { fg = "default", italic = true }
change_id = "green"
```

Available colors: `black`, `red`, `green`, `yellow`, `blue`, `magenta`, `cyan`, `white`, `default`, `bright-*`, `ansi-color-<0-255>`, `#hex`

Style properties: `fg`, `bg`, `bold`, `dim`, `italic`, `underline`, `reverse`

Label composition: `"working_copy commit_id"` = style for commit_id within working_copy context.

## Templates

```toml
[templates]
draft_commit_description = 'concat(builtin_draft_commit_description, "\n", diff.git())'
new_description = '''if(parents.len() > 1, "Merge branch\n", "")'''
commit_trailers = 'format_signed_off_by_trailer(self)'
duplicate_description = '''concat(description.trim_end(), "\n\n(cherry picked from commit ", commit_id, ")\n")'''

[template-aliases]
"format_short_id(id)" = "id.shortest(12)"
```

## Revsets

```toml
[revsets]
bookmark-advance-from = 'heads(::to & bookmarks())'   # which bookmarks to auto-advance
bookmark-advance-to = '@'                              # where to advance them to

[revset-aliases]
trunk = 'main@origin'                                  # alias for common patterns
```

## Bookmarks / Remotes

```toml
# Auto-track ALL remote bookmarks
[remotes.origin]
auto-track-bookmarks = "*"

# Control bookmark list order
[ui]
bookmark-list-sort-keys = ["name"]                     # or name- for descending
tag-list-sort-keys = ["name"]
```

## Git

```toml
[git]
# Disable colocation (git repo hidden inside .jj/)
colocate = false

# Auto-commit signing
sign-on-push = true
sign-commits = true
signing-key = "ssh-ed25519 AAA..."                     # or gpg key fingerprint
signing-behavior = "own"                               # own / all / drop
```

## Snapshot

```toml
[snapshot]
auto-track = "all()"                    # track everything not gitignored
# auto-track = "none()"                 # only track explicitly with `jj file track`
# auto-track = 'files("*.py")'          # only track .py files
```

## Conflict Markers

```toml
[ui]
conflict-marker-style = "jj"            # default: jj's diff format
# conflict-marker-style = "snapshot"    # show each side's contents
# conflict-marker-style = "git"         # git-style diff3 markers (2-sided only)
```

## Commit Signing

```toml
[git]
sign-commits = true
signing-key = "ssh-ed25519 AAAAC3..."   # or gpg key
```

## Full macOS Template

```toml
# ~/Library/Application Support/jj/config.toml
[user]
name = "Your Name"
email = "you@example.com"

[ui]
default-command = ["log", "--reversed"]
color = "auto"
editor = "code --wait"
conflict-marker-style = "jj"
bookmark-list-sort-keys = ["name"]

[colors]
"working_copy change_id" = { bold = true }
commit_id = "cyan"
"working_copy commit_id" = { underline = true }
"diff added" = { fg = "green", bold = true }
"diff removed" = { fg = "red", bold = true }
conflict = { fg = "red", bold = true }

[templates]
draft_commit_description = 'concat(builtin_draft_commit_description, "\n", diff.git())'
commit_trailers = 'format_signed_off_by_trailer(self)'

[snapshot]
auto-track = "all()"

[git]
colocate = true

[revset-aliases]
trunk = 'main@origin'
```

## JSON Schema Support

Add to TOML config file for editor validation:

```toml
#:schema https://raw.githubusercontent.com/jj-vcs/jj/main/docs/config-schema.json
```
