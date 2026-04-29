# Workflows

This reference covers all common JJ workflows with copy-paste commands.

## 1. Clone & First Commit
```bash
jj git clone https://github.com/user/repo
cd repo
jj describe -m "Start my feature"    # set commit message
# edit files...
jj new                                # commit + create new empty child
```

## 2. Push to GitHub

### Option A: Auto-generated bookmark name
```bash
jj git push -c <change-id>            # JJ creates bookmark, pushes
jj git push --dry-run -c <change-id>  # preview first
```

### Option B: Named bookmark
```bash
jj bookmark create feat -r @-         # create on parent (working copy is empty)
jj bookmark track feat
jj git push
```

### Update existing bookmark after review
```bash
# Rewriting commits (force push)
jj new your-feature-                  # NOTE: trailing hyphen = parent
# address comments
jj squash
jj git push --bookmark your-feature   # auto force-push

# Adding commits (no force push)
jj new your-feature
# address comments
jj commit -m 'address pr comments'
jj bookmark move your-feature --to @-
jj git push
```

## 3. Rebase Stack
```bash
jj rebase -b @ -o main                # rebase current branch onto main
jj rebase -s <source> -o <dest>       # rebase source+descendants onto dest
jj rebase -b <branch> -o main         # rebase a whole bookmark's branch
jj rebase -r <rev> -B <insert-before> # insert rev between rev- and rev
jj rebase -r <rev> -A <insert-after>  # insert rev between rev and rev+
```

## 4. Amend an Old Commit
```bash
# make changes to working copy
jj squash --into <target-change-id>   # move working copy changes into target
jj squash --from @- --into @          # opposite: pull parent changes into current
```

## 5. Split a Commit
```bash
jj split -r <rev>                     # interactive: select which changes go where
jj split file1 file2                  # split file1+file2 into first commit, rest into second
```

## 6. Interactive Squash
```bash
jj squash -i                          # move selected changes from @ into @-
jj squash -i --from X --into Y        # move selected changes from X into Y
```

## 7. Conflict Resolution
```bash
jj new <conflicted-commit>            # check out conflicted commit
# resolve conflict markers in editor
jj squash                             # move resolution into the conflicted commit
jj log                                # verify: conflict label gone
```

Alternatively, use an external merge tool:
```bash
jj resolve                            # use external merge tool for 2-sided conflicts
jj restore                            # pick one side of the conflict
```

See `jj help resolve` for merge tool config.

## 8. Absorb (Auto-Fixup)
```bash
# Edit working copy to fix a bug in a parent commit
jj absorb                             # auto-distribute changes to correct parent commits
```

Useful when you made a small fix and want it incorporated into the correct commit in a stack.

## 9. Undo / Restore
```bash
jj undo                               # undo last operation
jj redo                               # redo the undo
jj op log                             # find operation to restore to
jj op log -p                          # show operations with diffs
jj op restore <op-id>                 # full repo restore to that operation
jj --at-operation <op-id> log         # look at old state (read-only)
```

## 10. Stash Equivalent
```bash
jj new @-                             # abandon working copy, keep as sibling commit
jj edit <old-change-id>               # restore that sibling commit to working copy
jj new <old-change-id>                # alternative: create child on old commit
```

## 11. Merge
```bash
jj new A B                            # create merge commit with parents A and B
```

JJ correctly shows diff of a merge commit (diff vs merged parents). Rebasing merge commits with custom conflict resolutions works.

## 12. Multiple Workspaces
```bash
jj workspace add ../repo-feat         # new workspace linked to same repo
jj workspace list                     # list all workspaces
jj workspace root --name <workspace>  # path to a specific workspace
jj workspace forget ../repo-feat      # forget workspace (delete files separately)
jj workspace update-stale             # fix stale working copy
```

## 13. Arrange (Reorder Multiple Commits)
```bash
jj arrange                            # interactive reorder of commits in a stack
```

Replaces manual rebase juggling when you need to reorder a whole stack.

## 14. Describe / Edit Commit Message
```bash
jj describe                           # edit working copy description
jj describe -m "msg"                  # set directly
jj describe <rev>                     # edit any commit's description
```

## 15. Show / Diff
```bash
jj diff                               # diff working copy vs parent
jj diff -r <rev>                      # diff a revision vs its parent
jj diff --from A --to B               # diff two arbitrary revisions
jj show <rev>                         # description + diff
jj file annotate <path>               # blame a file
```

## 16. Revert
```bash
jj restore <paths>...                 # discard working copy changes to files
jj restore -c <rev> file              # undo changes to a file in a specific rev
jj revert -r <rev> -B @               # create commit that undoes another commit
```

## 17. Bookmarks
```bash
jj b                                  # alias for jj bookmark
jj b l                                # list bookmarks
jj b l --all                          # all bookmarks (incl. remote-tracking)
jj b l --tracked                      # only tracked ones
jj b c feat -r @                      # create bookmark on @
jj b m feat --to @                    # move bookmark to @
jj b advance                          # auto-advance bookmarks forward
jj b d feat                           # delete bookmark
jj track feat --remote=origin         # start tracking remote bookmark
jj untrack feat --remote=origin       # stop tracking
```

## 18. Git Fetch / Pull
```bash
jj git fetch                          # fetch all remotes
jj git fetch --remote origin          # fetch specific remote
jj git fetch --remote origin main     # fetch specific bookmark
```

There is no `jj pull`. Update workflow:
```bash
jj git fetch
jj rebase -b @ -o main                # rebase your work on latest main
```

## 19. Init a New Repo
```bash
jj git init myproject                 # colocated: creates .jj/ and .git/
jj git init --no-colocate myproject   # non-colocated: .jj/ only
jj git init --git-repo=../existing    # jj repo backed by existing git repo
```

## 20. Cherry-Pick / Duplicate
```bash
jj duplicate <source> -o <dest>       # copy a commit on top of another
```
