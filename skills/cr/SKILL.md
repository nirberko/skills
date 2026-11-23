---
name: cr
description: >-
  Self-review gate for the current branch before a PR, driven by your own team's
  recurring review comments. The repo is auto-detected from the git remote and its
  ruleset is loaded from `~/.claude/cr/feedback/<repo>.md`. Two modes: RUN
  (default) — first learns the feature (PR body, Jira ticket, earlier PRs of the
  same task, since one PR is often a small slice of a larger task), then reviews
  the current diff for what matters most: bugs and broken logic, reuse of
  existing components/utils/hooks instead of new copies, and the repo's recurring
  comment categories. Returns GitHub-style inline comments: severity-tagged
  (🔴 blocker / 🟡 should-fix / 🔵 nit), each anchored to file:line with the quoted
  code, a short TLDR comment, and a one-click `suggestion` fix. It stays quiet on
  clean-code polish, code comments and test-file style unless a fix is a must.
  UPDATE (args contain "update") — fetch review comments
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

## Review priorities (these win over the ruleset)

The user's order of what matters, highest first. Spend the review's effort in this
order, and when the ruleset's severity for an item disagrees, these rules win:

1. **It works.** No bugs, no regressions, no broken callers, and the change
   actually does what the feature needs. This is the main job of the review.
2. **Reuse.** New code uses the components, utils, hooks, types and consts that
   already exist (in the repo, or added by earlier PRs of the same task) instead
   of making a second copy. New logic that two places need lives in one shared
   place.
3. **Good logic.** The approach is sound: right layer, no fragile assumption, edge
   cases (null, empty, loading, error, concurrency) handled, contracts kept.
4. **Tests.** Wanted, but second-tier. A missing test is 🟡 only when the logic is
   risky and nothing covers it; otherwise 🔵.
5. **Clean code.** Lowest. Naming, formatting, small refactors, "could be
   shorter", file layout → 🔵 at most, and only a few. Do not demote a real
   duplication (that is reuse, #2) to clean code.

What to **leave out** of the review entirely unless a fix is a must:

- **Code comments and docs.** Never ask to add a comment, JSDoc or docstring,
  never flag a "hollow" or terse doc. Flag a doc or comment only when the change
  made it *wrong* in a way that would make the next reader or caller misuse the
  code (step 5(c)).
- **Clean-code findings in test files.** Test files are `*.test.*`, `*.spec.*`,
  `test_*.py`, `*_test.*`, and anything under `__tests__/`, `tests/`, `test/`,
  `e2e/`, `fixtures/`, `mocks/`. In a test file, report only what is a must:
  a test that cannot fail, asserts the wrong thing, tests the mock instead of the
  code, will be flaky (real timers, order dependence, shared state), or breaks
  the suite. Skip duplication, magic values, naming, structure and style there —
  even when a ruleset row matches.
- **Ruleset rows about pure style or comments.** When such a row fails, demote it
  to 🔵 (or skip it in a test file), whatever severity the ruleset gives it.

Keep the nit count small — about five at most. If there are more, keep the ones
nearest to reuse or logic and drop the rest without listing them.

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
  for the team's actual comments. The built-in checks that run next to the ruleset
  are RUN step 5(c)–(e): misleading docs, correctness, and reuse.

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
   A doc comment that the change made wrong is this case too — see step 5(c)
   for where to anchor it.

2. **Understand the feature before you judge the code.** A PR is often one small
   step of a larger task. Reviewed alone, a step looks incomplete or odd; reviewed
   with the task in mind, the real gaps show. Gather, cheaply:

   ```bash
   gh pr view --json number,title,body,url 2>/dev/null          # this PR's intent
   git log --format='%s%n%b' "$MB"..HEAD                         # commit messages
   KEY=$(git branch --show-current | grep -oE '[A-Z][A-Z0-9]+-[0-9]+' | head -1)
   # earlier and parallel PRs of the same task (ticket key in title/branch/body)
   gh pr list --state all --search "$KEY" --limit 20 \
     --json number,title,state,headRefName,mergedAt
   ```

   - If a ticket key exists and an Atlassian/Jira tool is connected, read the
     ticket (and its parent epic if it has one) for the goal and acceptance
     criteria. No key, or no tool → use the PR body and commits.
   - For each related PR, read its title and body, and skim `gh pr diff <n>
     --name-only` plus the parts that touch the same area. You want: what earlier
     PRs already built (helpers, components, types this PR should reuse), and what
     is planned for later (stated in a PR body, ticket, or `TODO(KEY)`).
   - Cap it: about five related PRs, newest first. This is context, not a second
     review — never emit a finding on another PR's code.

   Write down, for yourself, one or two sentences: what the feature is, and what
   this PR's slice of it is. Use that to judge:
   - **Does the diff do what this slice should?** A gap against the ticket or PR
     body is a finding (🔴 when the feature is broken without it).
   - **Don't flag as missing** what an earlier PR already did or a later PR is
     stated to do. But do flag code in this PR that would make the planned next
     step hard or wrong.
   - **Reuse across PRs**: a helper an earlier PR added, which this PR copies
     instead of using, is a reuse finding.

3. Read every changed hunk **plus enough surrounding context to judge it**.
   Verify symbols the diff references actually exist (don't flag a method that's
   really there; don't pass code that calls one you deleted). Evidence first —
   never review from the diff stat alone.

4. Walk every hunk against the categories in the loaded ruleset, filtered through
   the review priorities above. Emit each issue as a **GitHub inline comment** —
   render it exactly like a comment sitting on the line in the PR diff, in this
   shape:

   ````
   **`S1`** · **`src/features/orders/OrderTable.tsx:135`** · #1 DRY
   ```ts
   135  const total = rows.reduce((s, r) => s + r.price * r.qty, 0)
   ```
   we have sumLineItems in utils/orders.ts, use it
   ```suggestion
   const total = sumLineItems(rows)
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
     (The severity emoji itself lives on the group header, step 6 — the letter
     prefix carries it per finding, so don't repeat the emoji.) For a built-in
     check, use its tag instead of a ruleset number: `bug`, `logic`, `reuse`,
     `feature`, `doc`.
   - **code fence** — directly under the anchor, a plain ```` ```ts ```` (or
     matching lang) fence with the *exact* offending line(s) from the diff.
     **Prefix every line with its real file line number** (from the `cat -n`
     Read or the diff's new-side count), e.g. `135  <code>` — two spaces after
     the number, code verbatim. Multi-line spans get sequential numbers (`135`,
     `136`, `137`). Keep it to the 1–3 lines the comment is about; make the
     `:line` in the anchor match the first number.
   - **TLDR comment** — ONE line *under the code block* (it reads like a comment
     sitting on the code), max ~10 words, in your reviewers' actual voice:
     lowercase, blunt, no preamble. The shape to match: "we have X in utils, use
     it", "if rows is empty this divides by 0", "this runs before the fetch
     resolves", "why 286?". NOT "Consider extracting this into a reusable helper
     for better maintainability." When the loaded ruleset carries a verbatim
     reviewer quote for the rule, use that quote as the TLDR — it's already in
     the right voice.
   - **`suggestion` block** — a ```` ```suggestion ```` fence with the exact
     replacement lines (GitHub's native suggested-change format, one-click
     apply). Omit ONLY when the fix isn't a localized line edit (e.g. "add a
     test", "move this to a shared hook") — then the TLDR line already carries
     the action.

   No "problem:" / "fix:" labels — the structure carries them. Don't pad.

5. As part of THIS review (do NOT invoke `/code-review` or any other review skill
   — /cr is standalone):
   - **(a) RUN sweep list** from the loaded ruleset (magic values, duplicated
     blocks, missing guards, and the repo-specific items it names). In test
     files, keep only the must-fix items (see the review priorities).
   - **(b) Mechanical checks** — go through the `## Mechanical checks` table in the
     ruleset and, for **every row whose surface matches a changed file or
     construct** in the review set, answer its binary question against the actual
     code. A matched row gets an explicit verdict. A failing answer becomes a
     finding, using the row's reviewer quote as the TLDR line, at the row's
     severity — unless the review priorities demote it (style/comment rows → 🔵;
     non-must rows in test files → skip). A passing answer becomes one ✓ line in
     the final gate. Rows whose surface doesn't match are skipped silently.
   - **(c) Misleading docs only** — a built-in check, narrow on purpose. Do not
     look for missing, short or "hollow" docs, and never ask to add a comment.
     Flag only a doc comment or inline comment in or next to the change that the
     change made **wrong**, where the wrong text would make a caller or the next
     reader misuse the code: it says the function returns `null` but it now
     throws, names a param that no longer exists, states a unit or rule the code
     no longer follows → 🟡 "jsdoc says X, code now does Y" (🔴 when it would
     lead a caller into a bug). Anchor on the doc lines, so the `suggestion` can
     replace them — even when those lines are unchanged, because the branch's
     change made them wrong (the step-1 exception). Write the corrected doc from
     what the code actually does, in the repo's doc style.
   - **(d) Correctness** — a built-in check, and the most important one. For each
     changed behavior:
     - Trace one realistic input through the changed code end to end, then the
       edge inputs: null/undefined, empty list, zero, loading and error states,
       a second call while the first is still running, a stale value from a
       closure or cache.
     - Find every caller of a function, component, endpoint or type whose
       contract changed (`grep`/`rg` the name) and check each still works.
     - Check the two sides of a boundary agree: frontend query vs. backend
       schema, request vs. handler, writer vs. reader of a stored field,
       migration vs. model.
     - Check the change against the feature from step 2 — wrong condition, wrong
       field, inverted flag, off-by-one, missing branch.
     A real bug is 🔴. A logic weakness that is not yet a bug but will break
     under a likely input or the next planned step is 🟡. Name the input that
     breaks it in the TLDR ("if rows is empty this divides by 0").
   - **(e) Reuse** — a built-in check, second only to correctness. For every new
     function, component, hook, util, type, const or style block the branch adds:
     - Search the repo for one that already does the same: `rg` by likely names
       and by behavior keywords, and look in the shared places (`utils/`, `lib/`,
       `common/`, `shared/`, `components/`, `hooks/`, design-system packages),
       plus what earlier PRs of the same task added (step 2).
     - Check the diff against itself: two new pieces that do the same thing.
     - Check the other way: new logic the branch writes inline in two or more
       places, or that clearly belongs to a shared layer (a formatter inside a
       component, a fetch helper inside a page), should be extracted.
     Found an existing one → 🟡 with its path in the TLDR ("we have
     formatCurrency in utils/money.ts, use it") and a `suggestion` that calls it.
     Only flag when the existing piece really fits (same behavior, same inputs) —
     read it first. A near-miss that would need changes to fit is 🔵 at most.
     In test files, skip reuse findings unless the copy is large.

   Merge anything found in (a)–(e) into the same findings list (dedupe by line;
   when two findings land on one line, keep the higher-priority one).

6. **Output in this order:**
   1. **Context line** — one line from step 2: `**Feature:** <what it is> ·
      **this PR:** <its slice> · related: #12, #15` (leave out "related" when
      there are none).
   2. **One-line tally** — `## Review — N findings (X 🔴 · Y 🟡 · Z 🔵)`.
   3. **`### 🟡 Must fix (N)`** — group header with count, then the 🔴/🟡
      findings as step-4 inline comments. Order: bugs and feature gaps first,
      then reuse, then logic, then the rest; within each, by file then line. Put
      a short divider line of box-drawing dashes — `────────────────────────` —
      on its own line *between* consecutive findings (not after the last). Use
      `### 🔴 Must fix (N)` if any blockers.
   4. **`### 🔵 Nits (N)`** — same grouped format, same dividers. About five at
      most (see the review priorities).
   5. **Final gate checklist** — the checklist from the loaded ruleset, one row
      per category, ✓ / ~ / ✗ with one-line evidence, then the built-in rows:
      `Feature intent — matches / gaps`, `Correctness — N behaviors traced`,
      `Reuse — N new pieces searched`, `Misleading docs — N found`.
      Secondary summary only.
   6. Offer to apply the fixes (Edit them on request — the `suggestion` blocks
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

- 🔴 **blocker** — ships a bug/regression, breaks a caller, leaks data, leaves
  the feature not working for its slice, or breaks a hard repo rule. A reviewer
  blocks merge on it.
- 🟡 **should-fix** — duplicates a component/util/hook that already exists (or
  copies logic that should be shared), a logic weakness that a likely input or
  the next planned step will break, a missing null/error path, a missing test
  for risky untested logic, a doc made wrong by the change, a recurring team
  comment about any of these. Reviewer requests changes.
- 🔵 **nit** — clean-code polish a reviewer might leave but wouldn't block:
  naming, formatting, a small refactor, a magic value that is used once, a
  missing test for simple logic. Few of them, never in test files.

The concrete triggers per severity live under **Severity examples** in the loaded
ruleset. Judge against those, after the review priorities have filtered them —
not against generic best practice.

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
