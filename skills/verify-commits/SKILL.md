---
name: verify-commits
description: >-
  Audit every commit on the current branch and repair the ones GitHub will not
  mark "Verified". Reports each commit as verified, unsigned or rejected, then
  signs the broken ones with `git commit-tree -S` while keeping every tree
  byte-identical and every merge commit intact. Use when the user says
  "/verify-commits", "my commits are unverified", "fix the signatures", "sign my
  commits", "why does GitHub say unverified", or before opening a PR on a repo
  that requires signed commits. Also handles the case where a branch you merged
  from was rewritten, leaving two copies of the same work in your history.
---

# Verify commits

`scripts/verify_commits.py` does the work. It is fast because it batches: three
git processes read the whole range, one GraphQL request asks GitHub about every
commit at once, and only the signing itself runs per commit.

## Run it

Report first. Never rewrite history before the user has seen what will change.

```bash
python3 scripts/verify_commits.py                 # report only, default
python3 scripts/verify_commits.py --fix           # sign, local only
python3 scripts/verify_commits.py --fix --push    # sign, then force-with-lease
```

Useful flags:

- `--base <ref>` — start of the range. The default is the merge-base with
  `origin/main`, `origin/master` or `origin/HEAD`.
- `--no-remote` — skip the GitHub check when offline or on a non-GitHub remote.
- `--json` — machine-readable report.
- `--remap FILE` — replace a rewritten lineage. See below.

## What the report says

| Status | Meaning | Action |
|---|---|---|
| `verified` | GitHub accepts the signature. | none |
| `unverifiable` | Signed, but this machine has no `gpg` to check it. GitHub accepts it. | none |
| `UNSIGNED` | No signature at all. | sign it |
| `UNKNOWN_KEY` | Signed, but the key does not belong to the committer identity. | recommit as the user, then sign |

## Two traps this script exists for

**A local `G` is not proof.** GitHub also requires the key to belong to the
committer. A merge made with the GitHub "Update branch" button has committer
`GitHub <noreply@github.com>`. Sign it with your own key and GitHub answers
`unknown_key`. The script rewrites the committer to the user's own identity for
exactly those commits.

**A local `N` is not a defect.** When `gpg` is not installed, `%G?` reports `N`
for every GPG-signed commit, including the ones GitHub signed itself and shows
as Verified. The script reads the raw `gpgsig` header and trusts GitHub's answer
over the local one, so it never rewrites a commit that is already fine.

## Never rebase to re-sign

A rebase replays patches and hits real conflicts. Signing does not need that.
The script rebuilds each commit with the same tree and the same parents, adding
only the signature, so no conflict is possible. It then refuses to move the
branch unless the head tree is byte-identical and the commit count is what it
predicted.

Before any rewrite it saves `backup/<branch>-unsigned`. To undo:

```bash
git reset --hard backup/<branch>-unsigned
```

## When a branch you merged from was rewritten

Repairing branch A changes every hash on it. A branch B that already merged the
old A now holds both copies of the same work, and its PR shows every commit
twice. Do not rebase B onto the new A — the commits were written against an
older state and will conflict.

Instead give the script the old-to-new map. It repoints the parent links at the
new lineage and drops the stale copy. No patch is replayed, so nothing can
conflict. The script refuses any pair whose two commits do not have the same
tree.

```
# remap.txt — one pair per line
5e4aca8c8fb57d4f10b4d4d07307a220e0716b4c dde5707ea...
bfdd902dab2d20f66d2d5b2836e45980263d75aa f4957a92e...
```

```bash
python3 scripts/verify_commits.py --fix --remap remap.txt
```

Build the map by pairing the two lineages in order, oldest first. `git log
--format='%H %s'` on each branch gives the two lists to zip.

## Rules

- Report before you fix. Show the user the list and the count.
- Force-push only when the user asks. The command is
  `git push --force-with-lease origin <branch>`.
- Tell the user that every hash changed, so anyone else holding the branch must
  reset to the new head.
- Confirm the result against GitHub, not against `git log`. Re-run the report
  after pushing and state the tally plainly.
