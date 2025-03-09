---
---

## Status
show only modified files, no new files
```shell
git status -uno
```

show files that are not tracked and not ignored
```shell
git ls-files --others --exclude-standard
```
## Branches
### get latest from upstream
```bash
git fetch upstream
git rebase upstream/main
git push origin main
```

## Pull requests
## modify pull request locally / checkout fork branch
```shell
git fetch origin pull/ID/head:BRANCH_NAME
git checkout BRANCH_NAME
git push origin BRANCH_NAME
```
Note that this does NOT update the existing PR. It pushes a new branch, and then a new PR would need to be created.

### push to existing PR
```shell
git push git@github.com:[THE SOMEONE ELSE USER ID]/[PROJECT NAME].git [PR BRANCH NAME]:[LOCAL BRANCH NAME]

# Example:
git push git@github.com:someoneelse/main_project_name.git pr_change:pr_change
```
I am not sure if this needs permissions to the other user's repo, probably

## Tracking branches
### check tracking branches
```shell
git branch -vv
```
### change tracking branch
```shell
git branch [branchname] -u remote_name/remote_branch_name
# or
git branch branch_name --set-upstream-to remote_name/remote_branch_name
```
### rename branch
```shell
# -m is short for --move
git branch -m <oldname> <newname>
git push origin -u <newname>
# delete old remote branch
git push origin --delete <oldname>
```

## Undo / redo
**Redo after undo local**
[How to undo (almost) anything with Git | The GitHub Blog](https://github.blog/2015-06-08-how-to-undo-almost-anything-with-git/#redo-after-undo-local)

get list of commits when HEAD changed
```shell
git reflog
```

to restore project history as it was
```shell
git reset --hard <SHA>
```

## Stash
add single file to named stash
```shell
git stash push -m "LS collector" -- src/otelcollector/otelcol-config-extras.yml
```

apply stash by index (this does not delete the stash entry)
```shell
git stash apply 0
```

## Merging
checkout branch that you want to merge into (typically main)
run git merge with the name of the branch you want to merge into the current branch

example - assuming you are on `main`, this merges my-branch into main
```
git merge my-branch
```

when resolving conflict:
`ours` refers to the branch you are currently on
`theirs` refers to the branch you are merging in

## Rebasing
when there is a conflict and rebase stops...
to keep all changes from the branch you are rebasing onto  (`ours` in this case is the history in the remote branch)
```shell
git checkout --ours <filename>
```

to accept all changes from the new branch that is being rebased
```shell
git checkout --theirs <filename>
```

to accept all changes from all files
```shell
git checkout --ours .
```
## Search
Find commits that included a certain text
```shell
git log -S <string> path/to/file
```
or use regex
```shell
git log -G <regex> path/to/file
```
If path/to/file is not supplied, then it will include all files

git blame - for each line, shows the revision in which the line has appeared
```shell
git blame path/to/file
```

reverse blame - walks history forward instead backward, the commit range needs to be specified. This is useful to show the last revision in which aline appeared

## Commits
### Git amend a specific commit
```shell
# start interactive rebase from the commit you want to change
git rebase -i 'bbc643cd^'

# in the editor, change pick to edit for that commit
# make the changes, stage them, and then
git commit --amend --no-edit
git rebase --continue
```

### Unstage a file

unstage a file but keep the modifications
```shell
git reset HEAD <file>
```

revert file to how it was before the changes
```shell
git checkout -- <file>
```

### Diffing
ignore white space
```shell
git diff -w
```