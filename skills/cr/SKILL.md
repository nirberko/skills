---
name: cr
description: >-
  Self-review gate for the current branch before a PR, driven by your own team's
  recurring review comments. The repo is auto-detected from the git remote and its
  ruleset is loaded from `~/.claude/cr/feedback/<repo>.md`. Two modes: RUN
  (default) — review the current diff against that repo's recurring comment
  categories and return GitHub-style inline comments: severity-tagged (🔴 blocker /
  🟡 should-fix / 🔵 nit), each anchored to file:line with the quoted code, a short
  TLDR comment, and a one-click `suggestion` fix, so issues get fixed before
  reviewers raise them; UPDATE (args contain "update") — fetch review comments
  newer than the last sync for the detected repo and improve that repo's ruleset
  from them. Use RUN when finishing a feature/fix, before committing or
  opening/updating a PR, or when the user says "review my changes", "am I ready to
  push", "pre-PR check", "did I miss anything". Use UPDATE when the user says "/cr
  update", "sync the checklist", or "learn from recent PRs".
---

# Pre-PR Self-Review Gate

Most review comments are not deep — they're the same mechanical issues, repo after
repo, PR after PR. This skill is the pre-emptive pass: it learns what your reviewers
actually say, then says it first.

The engine here is repo-agnostic. The recurring-comment categories live in a
per-repo ruleset file **outside** this skill, so it survives skill updates and never
leaves your machine:

```
~/.claude/cr/feedback/<repo>.md    the ruleset RUN reviews against
~/.claude/cr/state.json            UPDATE's per-repo sync state
```

Each ruleset has **two parts**, and they serve different jobs:

- **`## Mechanical checks`** — a table of binary, surface-routed checks RUN
  *executes* (one verdict per row that matches a changed surface). These are the
  comments a reviewer *always* leaves: quotable as a yes/no, tied to a recognizable
  surface (file glob / import / code construct). Example shape: "this colDef sets
  X?", "this query has Y?", "this file is free of Z?".
- **The prose categories** — judgment/contextual guidance RUN *reasons with* ("why
  needed?", "talk to design", abstraction calls). Not a yes/no against a surface.

The split matters: a binary trigger buried in dense prose gets read but not
*applied*. Mechanical checks are the part RUN runs deterministically; the categories
are the part it judges.

## Step 0 — Detect the repo and load its ruleset (both modes, do this first)

Resolve the repo name from the git remote, then the ruleset path:

```bash
REPO=$(basename -s .git "$(git remote get-url origin 2>/dev/null)" 2>/dev/null)
RULESET="$HOME/.claude/cr/feedback/$REPO.md"
```

- An explicit arg (`/cr myrepo`, `/cr update myrepo`) overrides detection.
- If `REPO` is empty (no remote) and no explicit arg was given, ask which ruleset
  name to use. Don't silently default.
- If `$RULESET` doesn't exist, **stop and say so** — RUN has nothing to review
  against. Offer both paths:
  - `/cr update` — derive a ruleset from this repo's own PR review history
    (recommended; that's the whole point of the skill)
  - copy this skill's `feedback/TEMPLATE.md` to `$RULESET` and write the rules by
    hand

  Never review blindly with no ruleset, and never substitute generic best practices
  for the team's actual comments.

Load `$RULESET` — its categories, severity examples, RUN sweep list, and final-gate
checklist ARE the ruleset for everything below. References to "the categories" /
"the checklist" mean that file's.

## Mode selection

- Args contain `update` → **UPDATE mode** (bottom of this file).
- Otherwise → **RUN mode**.

## RUN mode

**The deliverable is a set of GitHub-style inline comments, not a verdict.**
Output what a reviewer leaves *on the line in the diff*: the anchored code, a
one-line TLDR in your team's voice, and a `suggestion` block. A bare checklist or
a "ship-ready" verdict is NOT the product — the inline comments are. The
checklist is a secondary summary.

1. **Collect the review set — committed AND uncommitted work.** A branch's work
   often isn't committed yet; `main...HEAD` alone silently misses it. Gather all
   three and union the changed files:

   ```bash
   # Resolve the base branch, in priority order:
   # 1. explicit arg: `/cr base=develop` (or any non-mode arg naming a branch)
   # 2. the open PR's base: gh pr view --json baseRefName -q .baseRefName
   # 3. origin/main / main fallback
   BASE=$(gh pr view --json baseRefName -q .baseRefName 2>/dev/null)
   BASE=${BASE:+origin/$BASE}
   BASE=${BASE:-$(git rev-parse --verify -q origin/main >/dev/null && echo origin/main \
          || (git rev-parse --verify -q main >/dev/null && echo main || echo HEAD))}
   MB=$(git merge-base "$BASE" HEAD)          # three-dot base; tolerates a moved base

   git diff "$MB" HEAD                          # committed on this branch
   git diff                                     # unstaged working-tree edits
   git diff --cached                            # staged but uncommitted
   git ls-files --others --exclude-standard      # new untracked files (read each)
   ```

   The review set = committed ∪ staged ∪ unstaged ∪ untracked. **Only if all
   four are empty** is there genuinely nothing to review — say so explicitly
   (state the base, the commit count, and that the tree is clean), and stop.
   Don't infer "no changes" from the committed diff alone.

   **Scope is the diff, not the files.** Review ONLY lines this branch
   added/changed (new-side hunks of the diffs above, plus untracked files in
   full). Pre-existing code in a touched file is context, not a review target —
   never emit a finding anchored to an unchanged line. The one exception: the
   branch's change directly breaks pre-existing code (deleted a symbol it
   calls, changed a contract it relies on) — flag that at the *changed* line.

2. Read every changed hunk **plus enough surrounding context to judge it**.
   Verify symbols the diff references actually exist (don't flag a method that's
   really there; don't pass code that calls one you deleted). Evidence first —
   never review from the diff stat alone.

3. Walk every hunk against the categories in the loaded ruleset. Emit each issue
   as a **GitHub inline comment** — render it exactly like a comment sitting on
   the line in the PR diff, in this shape:

   ````
   **`S1`** · **`src/features/orders/OrderTable.tsx:135`** · #1 DRY
   ```ts
   135  await page.setDescription('Testing Description')
   ```
   move to const as you are reusing it
   ```suggestion
   await page.setDescription(DESCRIPTION)
   ```
   ````

   The four parts, in this order, every time:
   - **anchor line** — a **finding code** + `` `file:line` `` + ` · ` + `#N`
     category number + short category tag. All bold. The code is a stable
     handle the user can refer to ("apply S1, skip S2"):
     - `B1, B2, …` for 🔴 **blocker** findings
     - `S1, S2, …` for 🟡 **should-fix** findings
     - `N1, N2, …` for 🔵 **nit** findings

     Number sequentially *within each severity*, in output (file→line) order.
     (The severity emoji itself lives on the group header, step 5 — the letter
     prefix carries it per finding, so don't repeat the emoji.)
   - **code fence** — directly under the anchor, a plain ```` ```ts ```` (or
     matching lang) fence with the *exact* offending line(s) from the diff.
     **Prefix every line with its real file line number** (from the `cat -n`
     Read or the diff's new-side count), e.g. `135  <code>` — two spaces after
     the number, code verbatim. Multi-line spans get sequential numbers (`135`,
     `136`, `137`). Keep it to the 1–3 lines the comment is about; make the
     `:line` in the anchor match the first number.
   - **TLDR comment** — ONE line *under the code block* (it reads like a comment
     sitting on the code), max ~10 words, in your reviewers' actual voice:
     lowercase, blunt, no preamble. The shape to match: "move to const as you are
     reusing it", "add a unit test for this", "fix ts", "why 286?", "console log
     police 🚓". NOT "Consider extracting this into a reusable helper for better
     maintainability." When the loaded ruleset carries a verbatim reviewer quote
     for the rule, use that quote as the TLDR — it's already in the right voice.
   - **`suggestion` block** — a ```` ```suggestion ```` fence with the exact
     replacement lines (GitHub's native suggested-change format, one-click
     apply). Omit ONLY when the fix isn't a localized line edit (e.g. "add a
     test", "split this file") — then the TLDR line already carries the action.

   No "problem:" / "fix:" labels — the structure carries them. Don't pad.

4. As part of THIS review (do NOT invoke `/code-review` or any other review skill
   — /cr is standalone):
   - **(a) RUN sweep list** from the loaded ruleset (magic values, duplicated
     blocks, missing guards, and the repo-specific items it names).
   - **(b) Mechanical checks** — go through the `## Mechanical checks` table in the
     ruleset and, for **every row whose surface matches a changed file or
     construct** in the review set, answer its binary question against the actual
     code. This is not optional or best-effort: a matched row gets an explicit
     verdict. A failing answer becomes a finding at that severity, using the row's
     reviewer quote as the TLDR line. A passing answer becomes one ✓ line in the
     final gate. Rows whose surface doesn't match are skipped silently.

   Merge anything found in (a) and (b) into the same findings list (dedupe by line).

5. **Output in this order:**
   1. **One-line tally** — `## Review — N findings (X 🔴 · Y 🟡 · Z 🔵)`.
   2. **`### 🟡 Must fix (N)`** — group header with count, then the 🔴/🟡
      findings as step-3 inline comments, ordered by file then line (the order a
      reviewer scrolls the diff). Put a short divider line of box-drawing dashes
      — `────────────────────────` — on its own line *between* consecutive
      findings (not after the last). Use `### 🔴 Must fix (N)` if any blockers.
   3. **`### 🔵 Nits (N)`** — same grouped format, same dividers.
   4. **Final gate checklist** — the checklist from the loaded ruleset, one row
      per category, ✓ / ~ / ✗ with one-line evidence. Secondary summary only.
   5. Offer to apply the fixes (Edit them on request — the `suggestion` blocks
      are already the exact edits).

   Each finding carries its code (B/S/N + number) on the anchor, so the group
   header shows the emoji and the user can address findings by code. Use the
   `────` divider (not markdown `---`, which renders as a full-width rule and is
   too heavy between cards). If there are no 🔴/🟡 findings, say so in one plain
   line and list only nits (or "no findings"). Don't pad to look thorough. But
   never skip the inline comments and emit only the checklist.

   When the user later says "apply S1 and N2" or "fix the blockers", resolve
   those codes to the matching findings from this run.

### Severity scale (engine — repo examples live in the ruleset)

- 🔴 **blocker** — ships a bug/regression, breaks a caller, leaks data, or breaks
  a hard repo rule. A reviewer blocks merge on it.
- 🟡 **should-fix** — a recurring team review comment that *will* come back if
  unfixed: duplication, magic value, missing test, missing null/error path,
  convention violation. Reviewer requests changes.
- 🔵 **nit** — style/polish a reviewer might leave but wouldn't block: trivial
  comment, local naming, micro-DRY.

The concrete triggers per severity live under **Severity examples** in the loaded
ruleset. Judge against those, not against generic best practice.

When the user asks "is this a fix?" the severity already answers it: 🔴/🟡 = yes,
fix before pushing; 🔵 = optional.

**Findings ≠ PR-writing help.** Findings are changes to make in the *code*. Only
produce a PR description or inline reviewer-notes if the user explicitly asks,
and keep them in a clearly separate section — never mix them into the findings
list.

## UPDATE mode

Self-improvement loop. Operates on the detected repo (Step 0) and **only** that
repo's ruleset + state. Steps:

1. Read `~/.claude/cr/state.json` → `state[<REPO>]` → `lastPrNumber`,
   `lastUpdated`. A missing file is `{}`; a missing repo key is
   `lastPrNumber: 0`. Create the directory (`~/.claude/cr/feedback/`) if needed.
2. **Bootstrap when there's no ruleset yet.** If `$RULESET` doesn't exist, copy this
   skill's `feedback/TEMPLATE.md` to it first, so step 8 has a file to route into.
   On a bootstrap sync `lastPrNumber` is 0 — bound the fetch with `--limit` (a few
   hundred PRs) so it doesn't pull the repo's entire history. If the sync then finds
   no reviewer comments at all, **delete the copied file again** and say the repo has
   no review history to learn from — a ruleset of unfilled placeholders is worse than
   none, because RUN would review against it.
3. Fetch feedback newer than the last sync, with the script that ships beside this
   file — `scripts/fetch_pr_comments.sh` **in this SKILL.md's own directory**. Use
   that absolute path; don't assume `~/.claude/skills/cr/`, since the skill may be
   installed as a plugin.
   ```bash
   bash <this-skill-dir>/scripts/fetch_pr_comments.sh --since-pr <lastPrNumber> > /tmp/cr-new.jsonl
   ```
   Script outputs JSONL: `{pr, prAuthor, kind, author, path, body}`, bots excluded.
   `--repo owner/name`, `--limit N`, `--since DATE` also supported; with no
   `--repo` it uses the current repo's remote.
4. Filter to reviewer feedback: drop rows where `author == prAuthor`. Call the
   remaining rows **NEW** (may be empty when the repo is already synced).

5. **Restructure pass — runs every UPDATE, even when NEW is empty.** The ruleset
   format evolves, so each sync first brings the *existing* file up to the current
   format, independent of any new comments. Apply the routing rules to content
   already in `$RULESET`:
   - **Define mechanical:** a trigger is **mechanical** when a reviewer would
     *always* raise it, it's phrasable as a yes/no check, AND it's bound to a
     recognizable surface (a file glob, an import, or a code construct matchable in
     a diff). Everything else is **judgment** (needs taste, context, cross-file
     reasoning).
   - **Lift:** move every prose trigger that fits *mechanical* into the
     `## Mechanical checks` table as a row `surface | binary question | severity |
     verbatim quote`. Phrase the surface generically (`*ColDefs.tsx`, not the one
     file that first triggered it). Restructuring, not seeding — every row must
     trace to a quote already in the file.
   - **Split:** if any prose category exceeds **~12 triggers or ~25 lines**, split
     it into focused sub-categories. Dense prose is why RUN misses buried triggers:
     a wall of text gets read but not applied, so keep every category skimmable.
   Call the resulting edits **MIGRATED** (may be empty if the file already conforms).

6. **Decide whether there's anything to do:**
   - NEW empty AND MIGRATED empty → tell the user exactly: "✅ cr is up-to-date for
     <REPO> — no new review comments since PR #<lastPrNumber> (last synced
     <lastUpdated>), ruleset already in current format." and stop.
   - NEW empty but MIGRATED non-empty → write the restructured file, report what was
     lifted/split, and stop. Bump only the **Last updated** date; leave
     `lastPrNumber` unchanged (no new comments were learned).
   - NEW non-empty → continue.

7. Classify each NEW comment on **two** axes: **(a) class** — mechanical vs judgment
   per the step-5 definition; **(b) category** — which prose category it matches
   (propose a new category only if it recurs ≥3 times from ≥2 reviewers; else fold
   into the closest one).

8. Route each NEW comment into `$RULESET` by class:
   - **mechanical → the `## Mechanical checks` table** (add/merge a row, generic
     surface, verbatim quote). Never bury a mechanical trigger in prose — that's the
     exact failure this routing fixes.
   - **judgment → the prose categories** — update counts/rank order, add genuinely
     new examples (replace weaker ones; keep each category tight; re-run the step-5
     split if a category crosses the density limit).
   - **Line budget:** keep the prose-category body under ~200 lines, but count the
     `## Mechanical checks` table *separately* — never compress a mechanical trigger
     back into prose to save lines.
   - Update the "Derived from N comments across M PRs" line and the **Last updated**
     line (today's date, highest PR number fetched). On a bootstrap sync, replace
     the template's placeholder rows and header with the derived content.
9. Write `~/.claude/cr/state.json`, updating only `state[<REPO>]`:
   `{"lastUpdated": "<ISO date>", "lastPrNumber": <max PR number seen>,
   "totalCommentsAnalyzed": <running total>}`. Leave other repos' keys intact.
10. Report to the user: which repo, how many new comments, what was restructured
    (rows lifted, categories split), what the new comments changed, new state.

### Privacy

The ruleset is derived from your team's real review comments and lives only under
`~/.claude/cr/`. Never commit it into a repo, paste it into an issue, or include it
in a PR description — it quotes colleagues verbatim and often names internal
systems.
