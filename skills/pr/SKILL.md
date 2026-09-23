---
name: pr
description: >-
  Opens a GitHub PR for the current branch with a short body that a reader who
  has never seen the feature can follow. Finds the Jira ticket from the branch
  name or commits, reads the diff and the ticket, and writes the title and body
  in ASD-STE100 Simplified Technical English with the ubiquitous language from
  `AGENTS.md`: the goal, what changed, the result, and before/after
  screenshots when the change is visual. Shows a preview, and opens the PR only
  after you confirm. Also rewrites the body of an existing PR. Use when the user
  says "/pr", "open a PR", "create a PR", "make a pull request", "write the PR
  description", "update the PR body", or finishes a feature and asks to ship it
  for review.
---

# Open the PR

A PR body has one job: a reviewer who has never heard of the feature reads it
once and knows **why** the change exists, **what** it changes, and **what is
different after it merges**. Then they read the diff.

So the body is short. It is a summary, not a changelog. If the reader needs the
diff to understand the body, the body failed. If the body repeats the diff, the
body is too long.

## Step 0 — Check the branch

```bash
git branch --show-current
git status --porcelain
gh pr view --json number,url,state,body 2>/dev/null
gh repo view --json defaultBranchRef -q .defaultBranchRef.name
```

- **On the default branch** → stop. Ask for a branch name, and create it only
  after the user says yes.
- **Uncommitted changes** → list them, and ask: commit them first, or open the
  PR without them? Do not commit silently.
- **A PR is already open** → switch to update mode. Write a new body, show the
  diff against the current body, and use `gh pr edit` after confirmation.
- The base is the default branch unless the user names another.

## Step 1 — Find the Jira ticket

Look in this order and stop at the first hit. A key is `[A-Z][A-Z0-9]+-\d+`.

1. The user's args: `/pr CLU-1234`.
2. The branch name: `feature/CLU-1234-scan-filter`.
3. The commit messages on the branch: `git log <base>..HEAD --format=%s%n%b`.

If a key is found and a Jira tool is available (the Atlassian MCP
`getJiraIssue`), read the ticket: summary, description, acceptance criteria.
The ticket is the best source for **why**. Only read. Never transition,
comment on or edit the ticket from this skill.

If no key is found, ask once: "Which Jira ticket is this for? (or `none`)".
Never invent a key. With `none`, omit the Jira line.

The ticket URL: use the site from the Jira tool result. If there is no tool,
use the base URL from a recent merged PR body (`gh pr list --state merged
--limit 10 --json body`). If neither exists, write the bare key.

## Step 2 — Load the vocabulary

Read the ubiquitous language before you write a word of the body:

- `AGENTS.md` at the repo root (and any in the changed directories).
- `CONTEXT.md` and `CLAUDE.md`, if they exist — they often hold the same terms.

Use these terms **exactly**. If `AGENTS.md` calls it a "finding", the body
never says "issue", "alert" or "result" for the same thing. If a concept that
the body needs has no term there, use the word the code uses, and define it
once in the body.

If no file exists, use the terms from the code and the ticket. Do not stop to
ask for the file.

## Step 3 — Understand the change

```bash
git log <base>..HEAD --oneline
git diff <base>...HEAD --stat
git diff <base>...HEAD
```

Read the diff fully, not only the stat. Then answer these four questions for
yourself, in one sentence each. They become the body:

| Question | Source |
|---|---|
| **Goal** — what problem does this solve, and for whom? | The ticket, then the commits |
| **Before** — what did the system do before this change? | The removed lines, the ticket |
| **Change** — what did you build or change? Name each piece. | The diff |
| **Result** — what does the user or the system do now? | The diff, the ticket's acceptance criteria |

If you cannot answer **Goal** from the ticket, the commits or the code, ask the
user one question. Do not guess a motive.

Also check the repo's own conventions:

- `.github/pull_request_template.md` (or `.github/PULL_REQUEST_TEMPLATE/`). If
  it exists, keep its required sections and checkboxes, and fill them in the
  style below. The repo template wins over this skill's layout.
- The title format of recent merged PRs: `gh pr list --state merged --limit 10
  --json title -q '.[].title'`. Follow it (for example `[CLU-1234] ...` or
  `CLU-1234: ...`).

## Step 4 — Screenshots

A screenshot is needed when the change is **visible**: a UI component, a style,
a page, a layout, an email, or CLI output that a person reads. It is not needed
for a backend-only, config-only or test-only change.

When it is needed:

1. Say which screens changed, and ask the user for a **before** and an
   **after** screenshot of each.
2. The user can give GitHub attachment URLs, image URLs, or local file paths.
3. **The GitHub CLI cannot upload images to a PR body.** For a local file, put
   an HTML comment placeholder in the body, open the PR, and tell the user to
   drag the file into the PR description in the browser (`gh pr view --web`).
   Do not commit screenshots to the repo to get a URL.
4. If the user says to skip, keep the section with the placeholder comment so
   the gap is visible, and say so in the report.

You may offer to capture the screenshots yourself with the `run` skill when the
app runs locally. Only do it if the user says yes.

## Step 5 — Write the title and the body

### The title

- One line, 60 characters or fewer, after the ticket key.
- Imperative, and about the result: `Filter scans by status`, not `Added status
  filter changes to scan list component`.

### The body

Use this layout. Delete a section only where the table below says you can.

```markdown
**Jira:** [CLU-1234](https://example.atlassian.net/browse/CLU-1234)

### Why
<Two or three sentences. The problem before this change, and who has it.>

### What changed
- <One behavior per bullet. Name the piece, then what it does now.>
- <Three to six bullets. Group small edits into one bullet.>

### Result
<One or two sentences. What the user or the system can do now that it could
not do before.>

### Screenshots
| Before | After |
|---|---|
| <image> | <image> |

### How to test
1. <The shortest path a reviewer can follow to see the result.>
```

| Section | Keep it when |
|---|---|
| Jira | A ticket exists. |
| Why, What changed, Result | Always. |
| Screenshots | The change is visible (Step 4). |
| How to test | A reviewer can check the change by hand. Omit it for a pure refactor with tests. |

**Size.** The whole body fits on one screen: about 150 words of prose, not
counting the screenshots. If it is longer, cut. The diff holds the detail.

### Write it in ASD-STE100 Simplified Technical English

- One idea per sentence. 20 words or fewer per sentence.
- Active voice, present tense. Name the actor: "the scan list shows the
  status", not "the status is shown".
- No `-ing` verb as a noun, and no perfect tense. "has been added" → "adds".
- Condition before result: "if the scan fails, the page shows the error."
- Keep the articles. Do not stack more than three nouns.
- One word for one meaning across the whole body, and that word comes from
  `AGENTS.md` (Step 2).
- Substitute: ensure → make sure · utilize/leverage → use · implement → build ·
  prior to → before · in order to → to · via → with · additional → more ·
  currently → now · however → but · therefore → so · requires → needs ·
  functionality → the thing it actually does.
- **Exempt:** code, paths, identifiers, table names, commands and error
  strings. Put them in backticks and never reword them.
- Gloss an internal name the first time it appears: "`ScanRunner` (the worker
  that runs one scan)". A reader from another team must not need to open the
  code to follow the body.

**Explain the result, not the work.** "Users can filter the scan list by
status" beats "added a `status` param to `useScans` and a `Select` to
`ScanTable`". Name the file or function only where it helps the reviewer find
the change.

**Not this:** a list of every file, "various fixes", "refactored stuff", "this
PR aims to…", marketing words ("robust", "seamless", "powerful"), a greeting,
a sign-off, or an emoji.

### Example

```markdown
**Jira:** [CLU-1234](https://example.atlassian.net/browse/CLU-1234)

### Why
The scan list shows all scans in one table. To find the failed scans, users
scroll the full list. Accounts with many scans cannot find them at all.

### What changed
- `ScanTable` (the table on the Scans page) shows a **Status** filter above
  the table.
- `useScans` sends the selected status to the `scans` query.
- The `scans` resolver filters by status in the database, not in the browser.
- The URL keeps the filter, so a reload or a shared link shows the same list.

### Result
Users select **Failed** and see only the failed scans. The filter stays after
a reload.

### Screenshots
| Before | After |
|---|---|
| <!-- drag before.png here --> | <!-- drag after.png here --> |

### How to test
1. Open **Scans**.
2. Select **Failed** in the **Status** filter.
3. Reload the page. The filter stays.
```

## Step 6 — Preview, then confirm

Opening a PR is public and notifies people. Show the exact title and body, and
a header:

```
PR · owner/repo · feature/CLU-1234-scan-filter → main · draft
```

Then ask once: open it as a draft or ready for review, or change something?
**Never open or edit a PR before an explicit yes.** Apply every change the user
asks for, and show the preview again only if the change is large.

## Step 7 — Push and open

```bash
git push -u origin HEAD            # only if the branch is not on the remote, or is behind
gh pr create --base <base> --title "<title>" --body-file <tmp-file> [--draft]
# update mode:
gh pr edit <number> --title "<title>" --body-file <tmp-file>
```

- Write the body to a temp file and pass `--body-file`. Shell quoting breaks
  backticks and tables in `--body`.
- Never force-push. If the push is rejected, stop and tell the user why.
- Add reviewers, labels or assignees only if the user asks.
- If the commits must be signed and some are not, say so and point to
  `/verify-commits`. Do not re-sign here.
- End the body with the attribution line the environment asks for, if it asks
  for one.

## Step 8 — Report

One short block: the PR URL, draft or ready, the Jira key, and any gap left
open — for example, "screenshots: drag `before.png` and `after.png` into the
description." Then stop.

## Args

| Arg | Effect |
|---|---|
| *(none)* | Open a PR for the current branch against the default branch. |
| `CLU-1234` | Use that Jira ticket. |
| `draft` / `ready` | Skip the draft question. |
| `base=<branch>` | Open the PR against that branch. |
| `update` | Rewrite the body of the branch's open PR. |
| `dry-run` | Write and preview the title and body. Open nothing. |
