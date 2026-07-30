# skills

Three agent skills for the two things that eat the most time on an unfamiliar
codebase: understanding code you didn't write, and getting through review.

- **`/learn`** — an interactive tutor that traces one real flow in *your* repo, one
  small stop at a time, and quizzes you before moving on.
- **`/explain`** — one complete plain-language answer about anything you don't
  understand: a PR thread, a stack trace, a feature, a ticket.
- **`/cr`** — a pre-PR self-review that learns your team's recurring review comments
  and leaves them on your diff before a reviewer does.

They're prompt-only. No servers, no API keys, no config files to maintain.

## Install

<details open>
<summary><strong>Claude Code</strong></summary>

```
/plugin marketplace add nirberko/skills
/plugin install nirberko-skills
```

</details>

<details>
<summary><strong>Codex, and other agents</strong></summary>

```bash
npx skills@latest add nirberko/skills
```

</details>

<details>
<summary><strong>By hand</strong></summary>

```bash
git clone https://github.com/nirberko/skills
cp -R skills/skills/* ~/.claude/skills/
```

</details>

## Reference

| Skill | Invoked | What it does |
|---|---|---|
| `learn` | you or the model | Multi-turn tutorial on one flow in this repo. Picks a trace with you, splits it into 6–10 stops, then teaches one idea per turn: plain-language claim, a real ≤10-line snippet with `file.py:42` citations, a multiple-choice check. Saves every lesson to an Obsidian vault so it accumulates and can be resumed. |
| `explain` | you or the model | One-shot explainer. Classifies the input (PR URL, pasted review comment, code block, error, feature name, ticket), reads the actual code, and answers with a moving-parts table, an execution-order flow, and cited line numbers. Nothing is assumed obvious. |
| `cr` | you | Reviews the current branch — committed *and* uncommitted — against your repo's ruleset, and returns GitHub-style inline comments: severity code, `file:line`, the offending lines, a blunt one-line TLDR, and a one-click ` ```suggestion ` fix. |

Trigger phrases: `/learn`, "teach me X", "walk me through X" · `/explain`, "what does
this do", "I don't understand this PR comment" · `/cr`, "review my changes", "am I
ready to push".

`learn` and `explain` are two halves of the same problem. `explain` is one answer;
`learn` is a course. Ask `explain` when you need to get on with it, `learn` when
you'll be living in that code for a while.

## `cr` learns your team, not mine

`cr` ships with **no rules**. Generic "best practice" review is noise — the comments
that actually block your PRs are specific to your repo and your reviewers.

So `cr` derives them:

```
/cr update
```

That reads your repo's PR review history over the GitHub API, filters out your own
comments, classifies what's left, and writes a ruleset to:

```
~/.claude/cr/feedback/<repo>.md
```

Two kinds of rule come out of it. **Mechanical checks** are the ones a reviewer
*always* leaves — phrasable as a yes/no, bound to a surface (`*Table.tsx`, "any new
endpoint", "files importing the logger"). `/cr` executes those deterministically
against every matching file in your diff. **Categories** are the judgment calls
("why is this needed?", "talk to design first") that it reasons with instead.

Then `/cr` reviews against that file, quoting your reviewers' own words back at you:

`````
**`S1`** · **`src/features/orders/OrderTable.tsx:135`** · #1 DRY
```ts
135  await page.setDescription('Testing Description')
```
move to const as you are reusing it
```suggestion
await page.setDescription(DESCRIPTION)
```
`````

Re-run `/cr update` every few weeks. It syncs only comments newer than the last run
and re-tightens the file as it grows.

Requires the [`gh`](https://cli.github.com) CLI, authenticated, plus `jq`.

### Your rules stay yours

`~/.claude/cr/feedback/` and `~/.claude/cr/state.json` live outside the skill, so
plugin updates can't clobber them — and nothing derived from your team's reviews ever
lands in a repo. That file quotes colleagues verbatim and usually names internal
systems. Don't commit it, don't paste it into a PR description.

Same for `/learn`: lessons are written to `~/.claude/learn-vault/`, which you can
open directly as an [Obsidian](https://obsidian.md) vault (plain markdown and
`[[wikilinks]]` — Obsidian is optional). Missed quiz answers get tagged `#review` so
you can search your own weak spots later.

## Why these three exist

I wrote them for myself, in a codebase I was new to, in a team whose review bar was
higher than my own. Three things kept happening:

1. I'd ask an agent to explain something and get five pages of confident prose I
   couldn't verify. Hence the hard rule in `learn` and `explain`: **every claim comes
   from a file read this session, with a line number you can open.**
2. I'd read an explanation, nod, and retain nothing. Hence the quiz in `learn` — one
   idea per stop, and you don't advance until you can answer.
3. I'd get the same review comment for the fourth time. Hence `cr`.

They're deliberately opinionated about brevity. `learn` caps a stop at ~100 words and
one snippet, because the failure mode of a tutor is too much text, not too little.

## License

MIT
