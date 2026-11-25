---
name: reply
description: >-
  Replies to the open review threads on your GitHub PR. Reads every unresolved
  thread where a reviewer is waiting on you, checks the code at the PR head to
  see if the point is already fixed, and drafts one short reply per thread in
  ASD-STE100 Simplified Technical English — the reply a busy engineer types
  ("done.", "on purpose, the API sends null here.", "good catch, fixing."), with
  no thanks-for-the-feedback, no hedges, no commit SHA, nothing that reads as AI.
  Shows a preview with your stance per thread, and posts only after you confirm.
  Never edits code. Use when the user says "/reply", "reply to the comments on my
  PR", "answer the review", "respond to the PR threads", "reply to the
  reviewers", or after pushing fixes for review comments.
---

# Reply to the threads on my PR

A reviewer left comments. Some you fixed, some you did on purpose, some are
questions. This skill answers each open thread in the voice of the author: one
short line, in the thread, on GitHub.

**This skill replies. It does not change code.** If a thread needs a fix that is
not in the PR yet, say so in the preview and let the user decide: fix first,
or reply that the fix comes.

## Step 1 — Resolve the PR and who you are

```bash
gh pr view --json number,url,state,headRefOid,author
gh repo view --json owner,name -q '.owner.login + "/" + .name'
gh api user -q .login
```

- An explicit arg wins: `/reply 4213`, or a PR URL.
- No PR for this branch → stop and say so.
- The PR is not the user's → say whose PR it is, and ask before you go on. The
  replies go up with the user's name.

## Step 2 — Collect the threads that wait on you

```bash
gh api graphql -F owner=OWNER -F name=REPO -F pr=NUMBER -f query='
query($owner:String!,$name:String!,$pr:Int!){
  repository(owner:$owner,name:$name){ pullRequest(number:$pr){
    reviewThreads(first:100){ nodes{
      id isResolved isOutdated path line originalLine
      comments(first:50){ nodes{
        databaseId author{login} body createdAt url diffHunk originalCommit{oid}
      } }
    } }
  } }
}'
```

Keep a thread only when **all** of these hold:

- `isResolved` is false.
- The last comment is not by the user. If the user spoke last, the ball is with
  the reviewer.
- The last comment is not from a bot (`[bot]` login, CodeRabbit, Copilot,
  SonarCloud …). The `bots` arg brings them in.

Also read the PR conversation (`gh pr view NUMBER --comments`). Keep a top-level
comment only when it asks the user something or @mentions them, and the user
did not answer after it.

Report every thread you skip and why, in one line each, so nothing goes quiet.

## Step 3 — Find out what is true for each thread

Do not draft from the comment text alone. For each kept thread:

1. Read the whole thread, not only the last comment.
2. Read the code **at the PR head** around `path:line` (the file, not only the
   `diffHunk`).
3. Compare with the code the reviewer saw:
   `git diff <originalCommit> HEAD -- <path>`. `isOutdated: true` is a strong
   hint that the line changed.
4. Pick one stance:

| Stance | When | Reply shape |
|---|---|---|
| **fixed** | the change the reviewer asked for is on the PR head | `done.` · `fixed.` · `moved it to utils/money.ts.` |
| **will fix** | the reviewer is right, the fix is not pushed | `good catch, fixing.` · `right, will fix.` |
| **disagree** | the code is right as is, and you can say why from the code, the ticket or a fact | `on purpose. the API sends null for drafts.` |
| **answer** | the comment is a question | the answer, in one line |
| **later** | valid, but out of scope for this PR | `out of scope here. opened ORD-412.` (only if a ticket exists) |
| **ask** | you cannot tell what the reviewer means | one short question back |

Rules for the stance:

- **fixed** only when you saw the fix in the code. If you are not sure, it is
  **will fix** or **ask**, never **fixed**.
- **disagree** needs a reason you can point to. "I prefer it" is not a reason.
  When you have no strong reason, do not argue: pick **will fix** or ask the user.
- Never invent a ticket key, a test result or a fact about the runtime.
- When the stance is a judgement call (disagree, later), mark it in the preview
  so the user checks it.

## Step 4 — Write the reply

Write as the PR author: first person, a person who knows this code and has
five minutes. If a reader can tell an AI wrote it, rewrite it.

**Length:**

- One sentence. Two only when the second gives the reason.
- 12 words or fewer is the target. 20 is the ceiling.
- `done.` is a complete reply. Do not add to it what the diff already shows.

**ASD-STE100 Simplified Technical English:**

- Active voice, present tense, or simple past for what you did: "moved it",
  "changed it". No perfect tense: "has been fixed" → "fixed".
- No `-ing` gerunds as nouns: "error handling is missing" → "handle the error".
  The short progressive "fixing." is fine; a person types it.
- Condition before result: "if the list is empty, the guard returns early."
- One word for one meaning across all replies.
- Substitute: ensure → make sure · utilize/leverage → use · implement → add or
  build · via → with · currently → now · however → but · therefore → so ·
  requires → needs · modify → change · in order to → to.
- **Exempt:** code, paths, identifiers, ticket keys, error strings. Wrap
  identifiers in backticks.

**Never write these — they read as AI:**

- "Thanks for the feedback", "Great catch!", "Good point!", "You're absolutely
  right", "I appreciate", "Happy to", "Let me know if…", "Hope this helps".
  A plain `good catch,` at the start is fine, at most once or twice per PR.
- Hedges: "I think it might be worth", "perhaps", "potentially",
  "it could be argued".
- Filler and reason tails: "for better maintainability", "to improve
  readability", "this ensures that", "as suggested".
- "I have addressed this", "This has been updated", "Addressed in the latest
  commit".
- Em dashes (—), semicolons, bullet lists, headings, bold, emoji.
- The commit SHA, "in commit abc123", or a link to a commit. The thread shows
  the change.
- Any mention of a tool, a skill or an AI.

**Human shape:**

- Lowercase start. End with a period or a `?`.
- Do not repeat the reviewer's point back to them.
- Mix the shapes. Ten replies that all read "good catch, fixed." look generated.
  Most fixed threads get a bare `done.` or `fixed.`.
- A ` ```suggestion ` block is for reviewers. Do not put one in a reply.
- On a top-level PR comment, start with `@login` of the person you answer.

**Examples**

| Reviewer said | Reply |
|---|---|
| "this can be null" (fixed) | `done.` |
| "use formatCurrency from utils" (fixed) | `switched to formatCurrency.` |
| "why 286?" | `max rows the export API accepts. made it a const.` |
| "move this to a hook?" (disagree) | `only used here. I'd keep it inline for now.` |
| "add a test for empty input" (not pushed) | `right, adding one.` |
| "this breaks for archived orders" (unclear) | `breaks how? archived ones are filtered in useOrders.` |
| "rename to isActive" (nit, fixed) | `renamed.` |

Not this: `Thanks for the great catch! I've addressed this in the latest commit
by adding a null check to ensure robustness.` · `Good point — I have updated the
implementation accordingly. Let me know if you have any other concerns!`

**Last pass before the preview.** Read each reply and ask: would the author type
this exact text? If it has a thank-you, a hedge, a dash, or a word the point
does not need, cut it.

## Step 5 — Preview, then confirm

Replies are public and notify the reviewer. Show exactly what goes up:

```
PR #4213 · owner/repo · 5 replies

src/orders/useOrders.ts:88      @dana: "can this be null?"
  fixed      → done.
src/orders/OrderTable.tsx:135   @dana: "why 286?"
  answer     → max rows the export API accepts. made it a const.
src/lib/batch.ts:40             @omer: "move this to a hook?"
  disagree ⚠ → only used here. I'd keep it inline for now.
src/lib/batch.ts:61             @omer: "add a test for empty input"
  will fix ⚠ → right, adding one.   (not on the PR yet)
conversation                    @dana: "is the flag on in staging?"
  answer     → @dana yes, on since Monday.

skipped 2:
  src/api/client.ts:20   you replied last
  src/api/client.ts:31   bot thread (sonarcloud)
```

- `⚠` marks a judgement call (disagree, later) or a promise the code does not
  show yet. Point to those in one line, so the user reads them.
- If a reply states a fact you could not check (staging state, a ticket), ask
  for it instead of guessing.
- Ask once whether to post. The user can edit, drop or change the stance of any
  line. **Never post before an explicit yes, and never post a reply that was not
  in the preview.**

## Step 6 — Post

Reply in the thread, to the thread's **first** comment (GitHub does not take a
reply to a reply):

```bash
gh api -X POST "repos/OWNER/REPO/pulls/NUMBER/comments/FIRST_COMMENT_ID/replies" \
  -f body='done.'
```

Top-level PR comment:

```bash
gh pr comment NUMBER --body '@dana yes, on since Monday.'
```

- Pass every body with single quotes or `--body-file`, so `$` and backticks in
  code survive the shell.
- Do not resolve threads by default. The reviewer resolves. With the `resolve`
  arg, resolve only the **fixed** threads after the reply posts:

  ```bash
  gh api graphql -F id=THREAD_ID -f query='
  mutation($id:ID!){ resolveReviewThread(input:{threadId:$id}){ thread{ isResolved } } }'
  ```

- If one post fails, keep going with the rest, and list the failure in the
  report. Do not retry the same call in a loop.

## Step 7 — Report

One short block: how many replies posted, which threads you resolved (if any),
the skipped list with reasons, and every **will fix** thread as a to-do, so the
promise does not get lost. Then stop. Do not start the fixes unless the user
asks.

## Args

| Arg | Effect |
|---|---|
| *(none)* | Reply to every open thread that waits on you, on the current branch's PR. |
| `4213`, PR URL | Target that PR. |
| `@dana` | Only threads where that reviewer spoke last. |
| `fixed` | Only the threads that the PR head already fixes. Quick pass after a push. |
| `bots` | Include bot threads. |
| `resolve` | Resolve the **fixed** threads after the reply posts. |
| `dry-run` | Preview only. Post nothing. |
