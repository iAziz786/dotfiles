---
name: jj-vcs
description: "Use when working with Jujutsu (jj) version control. Covers install, setup, core concepts, CLI help discovery, and daily workflows. Also trigger on 'jj' questions, vcs help, git alternative, git migration, or when user wants to simplify their git workflow. Load references/*.md for detailed revsets, templates, git-command-table, config, and workflow guides."
license: MIT
compatibility: Designed for OpenCode and Claude Code
metadata:
  author: "Aziz"
  version: "1.0"
---

# Jujutsu (jj) — Pit of Success

## When To Use

Activate when user:
- Asks "how to use jj", "jj workflow", "jujutsu tutorial"
- Says "jj command for X" where X is a git-like operation
- Wants to install/setup jj or migrate from git
- Needs help with revsets, templates, bookmarks, or conflict resolution
- Encounters a jj error, conflict, or divergence
- See `references/` files for deeper dives on specific topics

## Quick Start

```bash
brew install jj                                    # macOS
jj config set --user user.name "Your Name"
jj config set --user user.email "you@example.com"
source <(COMPLETE=zsh jj)                          # dynamic completions
```

Requires Git >= 2.41.0.

## Core Concepts

### Working Copy IS a Commit
JJ auto-snapshots working copy on every command. No `git add`. The commit `@` is the working copy.

- `jj st` — status (creates auto-commit if changed)
- `jj commit` — set description + create new empty child
- `jj new` — create new empty child commit
- `jj describe` — edit description only

### Change ID vs Commit ID
| ID | Stable? | Use |
|---|---|---|
| Change ID (`kntqzsqt`) | YES — survives rebase/amend | Referencing work-in-progress |
| Commit ID (`7fd1a60b`) | NO — changes on rewrite | Content hash (Git SHA) |

### Bookmarks ≠ Git Branches
Bookmarks do NOT auto-advance on `jj new`. You move them explicitly:

```bash
jj bookmark create feat -r @   # create
jj bookmark move feat --to @   # advance
```

### First-Class Conflicts
Rebases/merges never interrupt. Conflicts are stored in the commit. Resolve when ready:

```bash
jj new <conflicted-commit>   # check it out
# edit conflict markers
jj squash                    # move resolution into commit
```

### Operation Log
Every mutation logged. Full safety net.

```bash
jj op log           # history of all operations
jj undo             # undo last
jj op restore <id>  # restore to any point
jj --at-op <id> log # read-only view of old state
```

## CLI Help & Discovery

```bash
jj --help          # all commands
jj help <command>  # full help
jj <command> -h    # brief help
jj help revsets    # revset language docs
jj help templates  # template language
```

### Consistent Flags
| Flag | Short | Use |
|---|---|---|
| `--revision` | `-r` | Select these revisions |
| `--source` | `-s` | Revisions + all descendants |
| `--branch` | `-b` | Whole topological branch |
| `--from` / `--to` | `-f` / `-t` | Content source/destination |
| `--onto` | `-o` | Place as children of this rev |
| `--insert-after` | `-A` | Insert between rev and its children |
| `--insert-before` | `-B` | Insert between rev and its parents |
| `--change` | `-c` | Push w/ auto-generated bookmark |

### Shortcuts
`jj b` = `jj bookmark`, `jj b c` = `jj bookmark create`, `jj b l` = `jj bookmark list`, `jj b m` = `jj bookmark move`

## Pit of Success — Daily Workflow

```bash
jj git clone https://github.com/user/repo      # start
jj describe -m "my feature"                     # set message
# edit files...
jj commit                                       # done with this change, start next
# ... later, push to GitHub:
jj git push -c <change-id>                      # auto-creates bookmark, pushes
```

To update from remote:
```bash
jj git fetch
jj rebase -b @ -o main                          # rebase your work onto latest main
```

To amend an old commit:
```bash
# make changes in working copy
jj squash --into <target-change-id>
```

Full workflow details in `references/workflows.md`.

## Reference Files

| File | Content |
|---|---|
| `references/workflows.md` | All 13 daily workflows with examples |
| `references/revsets.md` | Full revset language: operators, functions, patterns |
| `references/templates.md` | Template language: types, fields, expressions, config |
| `references/git-command-table.md` | Complete git→jj command mapping (35+ translations) |
| `references/config.md` | Config reference: keys, examples, macOS template |

## Gotchas

1. **Bookmarks don't auto-advance** — unlike git branches. Use `jj bookmark move`.
2. **Hidden commits** — rewritten commits are hidden but still exist (accessible by commit ID).
3. **Divergent changes** — same change ID rewritten both locally and on remote. Fix: `jj new <change-id>` then `jj abandon` unwanted side.
4. **Colocation** — `jj` puts git in detached HEAD. Run `git switch <branch>` before mutating git commands.
5. **`jj commit` ≠ `git commit`** — `jj commit` sets message + creates new empty child. Use `jj describe` to just edit message.
6. **Auto-snapshot** — every command snapshots working copy. Use `jj new @-` to stash work-in-progress.
7. **No staging area** — use `jj split` or `jj squash -i` instead of `git add -p`.
8. **`jj git push -c` creates bookmarks** — auto-generates bookmark name. Use `jj git push --bookmark <name>` for existing bookmarks.
