# Git → JJ Command Table

All `jj` commands work on any commit (not just working copy), even when omitted below.

## Setup & Repos

| Use Case | Git | Jujutsu |
|---|---|---|
| Create empty repo | `git init` | `jj git init` |
| Create repo from existing | — | `jj git init --git-repo=<path>` |
| Clone | `git clone <url>` | `jj git clone <url>` |
| Colocated clone | — | `jj git clone <url>` (default, + `.git`) |
| Non-colocated clone | — | `jj git clone --no-colocate <url>` |
| Remote add | `git remote add <name> <url>` | `jj git remote add <name> <url>` |

## Fetch / Push

| Use Case | Git | Jujutsu |
|---|---|---|
| Fetch all | `git fetch` | `jj git fetch` |
| Fetch one remote | `git fetch <remote>` | `jj git fetch --remote <remote>` |
| Push all bookmarks | `git push --all` | `jj git push --all` |
| Push one bookmark | `git push <remote> <branch>` | `jj git push --bookmark <name>` |
| Push w/ auto-bookmark | — | `jj git push -c <change-id>` |

## Status / Diff / Log

| Use Case | Git | Jujutsu |
|---|---|---|
| Status | `git status` | `jj st` |
| Diff working copy | `git diff HEAD` | `jj diff` |
| Diff a revision | `git diff <rev>^ <rev>` | `jj diff -r <rev>` |
| Diff A to B | `git diff A B` | `jj diff --from A --to B` |
| Diff range A..B | `git diff A...B` | `jj diff -r A..B` |
| Show commit | `git show <rev>` | `jj show <rev>` |
| Log graph | `git log --oneline --graph` | `jj log -r ::@` |
| Log all | `git log --oneline --graph --all` | `jj log -r 'all()'` |
| Blame | `git blame <file>` | `jj file annotate <path>` |
| Grep files | `git grep foo` | `grep foo $(jj file list)` |
| List tracked files | `git ls-files` | `jj file list` |

## Commits & Changes

| Use Case | Git | Jujutsu |
|---|---|---|
| Add file | `git add filename` | *(auto-tracked)* |
| Remove file | `git rm filename` | `rm filename` *(auto-committed)* |
| Untrack (keep file) | `git rm --cached` | `jj file untrack <path>` |
| Commit | `git commit -a` | `jj commit` |
| Set message | *(in commit)* | `jj describe` |
| Amend | `git commit --amend` | `jj squash` (on @) |
| Fixup to old commit | `git commit --fixup=X` | `jj squash --into X` |
| Interactive fixup | `git add -p; git commit --amend` | `jj squash -i` |
| Split commit | *(edit in rebase -i)* | `jj split` |
| Split arbitrary rev | *(not supported)* | `jj split -r <rev>` |
| Interactive diff edit | *(not supported)* | `jj diffedit -r <rev>` |
| Auto-absorb fixups | *(not supported)* | `jj absorb` |
| Abandon (reset hard) | `git reset --hard` | `jj abandon` |
| Empty current commit | `git reset --hard` (same as abandon) | `jj restore` |

## Branching / Bookmarks

| Use Case | Git | Jujutsu |
|---|---|---|
| List branches | `git branch` | `jj bookmark list` or `jj b l` |
| Create branch | `git branch <name> <rev>` | `jj bookmark create <name> -r <rev>` |
| Move branch forward | `git branch -f <name> <rev>` | `jj bookmark move <name> --to <rev>` |
| Move backward | `git branch -f <name> <rev>` | `jj bookmark move <name> --to <rev> --allow-backwards` |
| Delete branch | `git branch -d <name>` | `jj bookmark delete <name>` |
| New branch + switch | `git switch -c topic main` | `jj new main` (no bookmark) or `jj b c topic -r @` |
| Switch to branch | `git switch topic` | `jj new topic` |

## Rebase / History Editing

| Use Case | Git | Jujutsu |
|---|---|---|
| Rebase branch onto | `git rebase B A` | `jj rebase -b A -o B` |
| Rebase subgraph onto | `git rebase --onto B A^` | `jj rebase -s A -o B` |
| Reorder commits | `git rebase -i` | `jj rebase -r C --before B` |
| Reorder multiple | `git rebase -i` | `jj arrange` |
| Cherry-pick | `git cherry-pick <src>` | `jj duplicate <src> -o <dest>` |
| Revert a commit | `git revert <rev>` | `jj revert -r <rev> -B @` |
| Merge | `git merge A` | `jj new @ A` |

## Stash

| Use Case | Git | Jujutsu |
|---|---|---|
| Stash | `git stash` | `jj new @-` |
| Stash pop | `git stash pop` | `jj edit <old-change-id>` |
| View stashes | `git stash list` | `jj log -r '(mine() & empty())-'` |

## Undo

| Use Case | Git | Jujutsu |
|---|---|---|
| Undo last | *(reflog gymnastics)* | `jj undo` |
| Redo | — | `jj redo` |
| View operations | — | `jj op log` |
| Restore to operation | — | `jj op restore <op-id>` |
| View old state | — | `jj --at-operation <op-id> log` |

## Tags

| Use Case | Git | Jujutsu |
|---|---|---|
| List tags | `git tag -l` | `jj tag list` |
| Create tag | `git tag <name> <rev>` | `jj tag set <name> -r <rev>` |
| Delete tag | `git tag -d <name>` | `jj tag delete <name>` |

## Misc

| Use Case | Git | Jujutsu |
|---|---|---|
| Rebase continue | `git rebase --continue` | *(never needed)* |
| Merge continue | `git merge --continue` | *(never needed)* |
| Cherry-pick continue | `git cherry-pick --continue` | *(never needed)* |
| Resolve conflicts | `git mergetool` | `jj resolve` |
| Root path | `git rev-parse --show-toplevel` | `jj workspace root` |
| Stash before rebase | `git stash; git rebase; git stash pop` | *(not needed — auto-rebase)* |
| Interactive rebase for amend | `git rebase -i` | `jj squash --into <rev>` |

## Key Differences

- **No staging area** — use `jj split`, `jj squash -i`, or commits instead of index
- **No interrupted operations** — conflicts stored in commits, resolve when ready
- **Auto-rebase** — descendants of rewritten commits automatically get rewritten
- **Change IDs** — stable across rewrites, unlike commit IDs
- **Bookmarks ≠ branches** — bookmarks don't auto-advance
