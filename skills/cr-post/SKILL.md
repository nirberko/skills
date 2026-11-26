---
name: cr-post
description: >-
  Takes the findings from a `/cr` run and posts them on the GitHub PR as inline
  review comments, each anchored to the line it is about. Rewrites every finding
  as a one-sentence comment in ASD-STE100 Simplified Technical English — no
  severity code, no category number, no commit SHA, no hedges or AI filler, just
  the short sentence a colleague would type — keeps the one-click ```suggestion block, drops any finding whose line is
  not in the PR diff, dedupes against comments already on the PR, shows a preview,
  and posts the lot as ONE review after you confirm. Use when the user says
  "/cr-post", "post these on the PR", "put those comments on the PR", "leave the
  review on GitHub", "comment these on the diff", or after a `/cr` run asks to
  push the findings to the PR. Needs a `/cr` run first — this skill posts findings,
  it never produces them.
---

# Post the review on the PR

`/cr` leaves its findings in the terminal, where nobody else can see them.
This skill puts them on the PR: on the line, in one review, in the voice of a
person who read the diff.

**This skill posts. It does not review.** It never derives a finding from the
diff, and it never invents one. The findings come from `/cr`.

## Step 0 — Get the findings

Use the findings from the most recent `/cr` RUN **in this conversation**. Each one
already carries what a comment needs: `file:line`, the offending lines, a blunt
one-line TLDR, and often a `suggestion` block.

If this conversation has no `/cr` run, stop and ask: run `/cr` first (offer to do
it now), then come back. Do not review the diff inside this skill.

## Step 1 — Resolve the PR

```bash
gh pr view --json number,url,state,isDraft,headRefOid,baseRefName,author
```

- An explicit arg wins: `/cr-post 4213`, or a PR URL.
- **No PR for this branch** → stop. Say the branch has no open PR, and offer to
  open one (`gh pr create`) as a separate, confirmed step. Never open it silently.
- **PR is closed or merged** → say so and ask before you post.
- **The PR author is not the user** → say whose PR it is in the preview. Comments
  on someone else's PR are a real review with the user's name on it.

## Step 2 — Drop what cannot be posted, and say why

`/cr` reviews the working tree as well as the branch, so some findings have no
line on the PR. Check all of these **before** writing any comment:

| Check | Action when it fails |
|---|---|
| Local `HEAD` is the PR head commit (`headRefOid`) | Stop. Line numbers drift against unpushed commits. Tell the user to push, then rerun. |
| The finding's file is committed and pushed | Drop it. Name the file, and say the change is not on the PR yet. |
| The finding's line is in the PR diff (added or context line, new side) | Drop it. The line is pre-existing code outside a hunk. |
| No comment already sits on that line saying the same thing | Drop it as a duplicate. |

The last check keeps a second run from posting everything twice:

```bash
gh api "repos/{owner}/{repo}/pulls/<PR>/comments" --paginate -q '.[] | "\(.path):\(.line // .original_line)\t\(.user.login)\t\(.body)"'
```

**Then drop what is not worth a comment.** The user wants the PR review to be
about bugs, reuse and logic, not polish. Hold these back by default (the `all`
arg brings them in):

- Any 🔵 finding in a test file (`*.test.*`, `*.spec.*`, `test_*.py`,
  `*_test.*`, `__tests__/`, `tests/`, `test/`, `e2e/`, `fixtures/`, `mocks/`). In
  a test file, post only what is a must: a test that cannot fail, asserts the
  wrong thing, or will be flaky.
- Any finding that only asks to add, shorten or reword a code comment or doc. A
  doc that the change made *wrong* (tag `doc`, 🟡/🔴) still posts.
- Pure clean-code nits (naming, formatting, "could be shorter") when the review
  already has 🔴/🟡 comments. One review full of nits buries the real ones.

**Report every dropped or held-back finding with its reason.** A silent drop
reads as "posted", and the user stops looking at it.

## Step 3 — Rewrite each finding as a short human comment

The `/cr` TLDR is the raw material, not the comment. Write what a senior
colleague types between two meetings: short, exact, done. If a reader can tell
an AI wrote it, rewrite it.

**Length — the hard limit:**

- One sentence. Two only when the first one states a condition or a cause.
- 12 words or fewer per sentence is the target; 20 is the ceiling.
- The `suggestion` block does not count. When it carries the fix, the sentence
  only says what is wrong: `this throws on null.` + suggestion. Do not also say
  "use the suggestion below".
- Cut every word that does not change the meaning. Then cut one more.

**ASD-STE100 Simplified Technical English:**

- Active voice, present tense. Name the actor: "this throws", not "an error is
  thrown".
- No `-ing` verb and no gerund. "you are reusing it" → "you use it".
  "error handling is missing" → "handle the error".
- No perfect tense. "has been changed" → "changed".
- Imperative for the action: "add a guard.", "use formatDate."
- Condition before instruction: "if the list is empty, this throws."
- Keep the articles. Do not stack more than three nouns.
- One word for one meaning **across the whole review**. If comment 1 says
  "const", comment 4 does not say "constant".
- Substitute: ensure → make sure · verify → check · utilize/leverage → use ·
  implement → build · prior to → before · in order to → to · via → with ·
  additional → more · currently → now · however → but · therefore → so ·
  requires → needs · provide → give · modify → change · approximately → about ·
  functionality → the thing it actually does.
- **Exempt:** code, paths, identifiers, error strings, and the `suggestion`
  block. `AlertRunner` stays `AlertRunner`. Never reword code. Wrap identifiers
  in backticks.

**Never write these — they read as AI:**

- Hedges and soft openers: "consider", "you might want to", "it may be worth",
  "it would be better to", "perhaps", "I'd suggest", "potentially", "just a
  thought".
- Filler and justification tails: "for better maintainability", "for
  readability", "to improve clarity", "to avoid potential issues", "this ensures
  that", "this helps".
- Framing words: "note that", "it's important to", "keep in mind", "worth
  noting", "make sure to", "robust", "seamless", "streamline", "edge case
  handling".
- Em dashes (—), semicolons, bullet lists, headings, bold, or more than one
  sentence of explanation.
- Restating the code. The comment is anchored to it.
- Greeting, praise, thanks, sign-off, "As an AI", bot footer, or any mention
  that a ruleset or a tool exists.
- Severity code (`S1`, `B2`, `N3`), `#N` category, severity emoji, `TLDR:`,
  `problem:` / `fix:` labels.
- The commit SHA, or "in commit abc123". The comment sits on the line; that is
  enough.

**Human shape:**

- Lowercase start. End with a period, or a `?` for a question. Blunt is fine.
- A question is a valid comment, often the best one: `why 286?` ·
  `can this be null?`
- `nit:` is the one allowed prefix — a person writes that. Use it for the 🔵 ones.
- No emoji.
- Two findings on one line become **one** comment, not two.
- Keep the ` ```suggestion ` block whenever the fix is a localized line edit —
  one click for the author. Drop it when the fix is not ("add a test", "split
  this file"); then the sentence carries the action.
- Do not make every comment the same shape. Mix a statement, a question, an
  imperative. Ten comments that all read "X does Y. do Z." look generated.

**Examples**

| Finding | Posted comment |
|---|---|
| bug on an edge input | `divides by 0 when rows is empty.` |
| existing util not used | `we have formatCurrency in utils/money.ts.` |
| copied component | `same as StatusChip in components/common. use that.` |
| logic in two places | `useOrders has this filter too. share it.` |
| race | `runs before the fetch resolves, so data is undefined here.` |
| unguarded access | `can user be null here?` |
| feature gap | `the ticket says archived orders stay hidden. this shows them.` |
| missing test, risky logic | `add a test for the empty batch.` |
| magic number (nit) | `nit: why 286?` |
| fix is in the suggestion | `this throws on null.` + suggestion |

Not this: `Consider extracting this into a reusable helper for better
maintainability.` · `🟡 should-fix · #1 DRY: the value is being reused.` ·
`Great work! One small thing — it should be noted that…` · `This could
potentially lead to a runtime error if the user object is null. You might want
to add a null check to ensure robustness.`

**Last pass before the preview.** Read each comment and ask: would a busy
engineer type this exact text? If it has a hedge, a reason tail, a dash, or more
words than the point needs, cut it.

**Volume is part of looking human.** More than about 12 inline comments on one PR
reads like a bot. Over that, post the 🔴/🟡 findings only, and say in one line
how many nits you held back. If the 🔴/🟡 findings alone are over the limit,
keep them in this order — bugs and feature gaps, then reuse, then logic, then
tests — and list the rest in the report.

## Step 4 — Preview, then confirm

Posting on a PR is public and notifies people. Show exactly what will go up:

```
PR #4213 · owner/repo · 6 comments to post

src/features/orders/OrderTable.tsx:135   same string in 3 places. make it a const.   + suggestion
src/features/orders/useOrders.ts:88      throws when data is null.                    + suggestion
...

skipped 3:
  src/lib/format.ts:12   not committed yet
  src/lib/format.ts:44   line is not in the PR diff
  src/api/client.ts:20   a comment already says this
```

Ask once, plainly, whether to post. **Never post before an explicit yes.** Never
post a comment that was not in the preview.

## Step 5 — Post as one review

One review, one notification — the way a person leaves a pass. Build the comments
array and hand it to the script that ships beside this file (use its absolute path
in **this SKILL.md's own directory**; the skill may be installed as a plugin):

```bash
bash <this-skill-dir>/scripts/post_review.sh --comments /tmp/cr-post.json
```

`comments.json` is a JSON array of GitHub review comments:

```json
[
  {"path": "src/features/orders/OrderTable.tsx", "line": 135,
   "body": "same string in 3 places. make it a const.\n\n```suggestion\n  await page.setDescription(DESCRIPTION)\n```"},
  {"path": "src/lib/batch.ts", "start_line": 40, "start_side": "RIGHT", "line": 42,
   "body": "never exits when the batch is empty."}
]
```

Rules for the payload:

- `side` defaults to `RIGHT` — the new side of the diff, which is what an added or
  changed line needs. Use `LEFT` only to comment on a deleted line.
- A multi-line span needs `start_line` + `start_side`, and for a `suggestion`
  block the span must match the lines the block replaces, exactly.
- Never send `commit_id`. Without it GitHub anchors the review to the PR's
  latest commit, and no SHA shows on the comments. The script leaves it out.
- `event` is always `COMMENT`. GitHub rejects `APPROVE` and `REQUEST_CHANGES` on
  your own PR, and this is usually the user's own PR.
- Leave the review summary body empty by default. The inline comments are the
  product. Add one short line only if the user asks for it.

The script refuses to run when local `HEAD` is not the PR head, drops any comment
whose line is not commentable (printing it as JSONL on stderr), posts the rest,
and prints the review URL. `--dry-run` prints the payload and posts nothing.

**If the API still returns 422**, the request failed as a whole and nothing was
posted. The message names the offending field: re-check that comment's path and
line against `gh pr diff`, drop it, and post the rest. Do not retry the same
payload.

## Step 6 — Report

One short block: how many comments posted, the review URL, and the skipped list
again with reasons. Do not message the PR author anywhere else (no Slack DM);
the GitHub review notification is enough. If findings were held back by volume or by an arg, say which ones, so nothing
goes quiet.

Then stop. Applying the fixes is `/cr`'s job, not this skill's — never edit code
here.

## Args

| Arg | Effect |
|---|---|
| *(none)* | Post the 🔴/🟡 findings from the last `/cr` run. Ask about the nits. |
| `all` | Include the nits, and the findings Step 2 holds back by default (test-file nits, comment/doc asks). |
| `nits` | Nits only. |
| `S1 N2 …` | Only those findings, by their `/cr` code. The codes select; they are never posted. |
| `4213`, PR URL | Target that PR instead of the current branch's. |
| `dry-run` | Build the payload and preview it. Post nothing. |

## Privacy

The `/cr` ruleset quotes the user's colleagues verbatim and names internal
systems. Post the **comment**, never its provenance: no rule text, no reviewer
name, no "this comes from our checklist", no hint that a ruleset exists.
