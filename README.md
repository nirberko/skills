# skills

Four agent skills for the things that eat the most time on an unfamiliar codebase:
understanding code you didn't write, getting a design approved, and getting through
review. Plus an output style, for when the problem isn't the code — it's that the
answer didn't land.

- **`/learn`** — an interactive tutor that traces one real flow in *your* repo, one
  small stop at a time, and quizzes you before moving on.
- **`/explain`** — one complete plain-language answer about anything you don't
  understand: a PR thread, a stack trace, a feature, a ticket.
- **`/tech-design`** — a design doc written *gradually*, one checkpointed section at a
  time, in Simplified Technical English, that an engineer from another team can follow
  without asking you a question, ready to publish to Confluence.
- **`/cr`** — a pre-PR self-review that learns your team's recurring review comments
  and leaves them on your diff before a reviewer does.
- **Plain** *(output style)* — every answer, every turn: context first, then
  Simplified Technical English, in your project's own vocabulary.

They're prompt-only. No servers, no API keys, no config files to maintain.

## Install

<details open>
<summary><strong>Claude Code</strong></summary>

```
/plugin marketplace add nirberko/skills
/plugin install nirberko-skills
```

The skills work immediately. The `Plain` output style is opt-in — turn it on with
`/config` → **Output style** → **Plain**, or set it directly in `~/.claude/settings.json`:

```json
{ "outputStyle": "Plain" }
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
cp -R skills/output-styles/* ~/.claude/output-styles/
```

</details>

## Reference

| Skill | Invoked | What it does |
|---|---|---|
| `learn` | you or the model | Multi-turn tutorial on one flow in this repo. Picks a trace with you, splits it into 6–10 stops, then teaches one idea per turn: plain-language claim, a real ≤10-line snippet with `file.py:42` citations, a multiple-choice check. Saves every lesson to an Obsidian vault so it accumulates and can be resumed. |
| `explain` | you or the model | One-shot explainer. Classifies the input (PR URL, pasted review comment, code block, error, feature name, ticket), reads the actual code, and answers with a moving-parts table, an execution-order flow, and cited line numbers. Nothing is assumed obvious. |
| `tech-design` | you or the model | Writes a technical design in eight checkpointed phases instead of one turn: reads the code first, rates every term in the request known/assumed/unknown, states the gap before proposing anything, tests each goal against its non-goal, and gets an approach agreed *in ordinary words* before a single table or endpoint is named. Then names the new pieces, walks one item through the whole system — including the quiet run, the deletion, and the crash halfway — and gives each piece a section covering why-this-way, what-it-owns, how-it-fails and the traps. Every sentence of the document is ASD-STE100 Simplified Technical English, with the glossary pass doubling as its approved Technical Names list. Output is Confluence HTML+ (native @mention chips, status pills, panels) or plain markdown, with Mermaid flows rendered as images and every URL verified 200 before publishing. |
| `cr` | you | Reviews the current branch — committed *and* uncommitted — against your repo's ruleset, and returns GitHub-style inline comments: severity code, `file:line`, the offending lines, a blunt one-line TLDR, and a one-click ` ```suggestion ` fix. |

Trigger phrases: `/learn`, "teach me X", "walk me through X" · `/explain`, "what does
this do", "I don't understand this PR comment" · `/tech-design`, "write a design doc
for X", "draft a TDR" · `/cr`, "review my changes", "am I ready to push".

`tech-design` and the **Plain** output style share one register: ASD-STE100 Simplified
Technical English. Plain controls how answers land in the terminal; `tech-design`
controls how the document reads. The rule set is the same, so a design doc and the
conversation about it sound like one voice.

`learn` and `explain` are two halves of the same problem. `explain` is one answer;
`learn` is a course. Ask `explain` when you need to get on with it, `learn` when
you'll be living in that code for a while.

## `tech-design` ships no house rules either

Same principle as `cr`. The *structure* of a good design doc is portable — section
order, an Overview table, a Design Summary made of real models and file paths, Option
1/Option 2 with an actual recommendation, phases with a Definition of Done. That's
what the skill ships.

What isn't portable is the handful of things your team always checks: which database
a new table belongs in, whether a change has to work on two engines, how migrations
are staged, how a feature is flagged and monitored, who's allowed to call the new API.
Ship those as generic "best practices" and you get a doc full of sections nobody
needed.

So `tech-design` reads them from a house file, whichever exists first:

```
docs/tech-design.md          # version-controlled, shared with the team
.github/tech-design.md
~/.claude/tech-design/<repo>.md   # if it quotes internal systems, keep it out of git
```

No file, and a change that touches infrastructure? It offers once to derive one by
reading your team's accepted designs and extracting the questions that recur across
them — then moves on. It won't invent a house rule it can't point at in a real prior
design.

The one rule it will not bend: **the reviewer is an engineer from another team who
has never opened this code.** Every acronym glossed inline where it first appears,
every file path given a clause saying what it does, and no Glossary section — because
a reader shouldn't have to memorize a list before the design starts.

## `Plain` is `explain` with no trigger

The three skills above are things you invoke. `Plain` is not — it's an
[output style](https://code.claude.com/docs/en/output-styles), which means it edits the
system prompt and applies to every response until you turn it off.

It exists for the sentence you shouldn't have to type twice: *"wait, I don't understand
where you've got to here."* Three standing rules:

1. **Give a little bit of context.** Never open mid-thought. What was asked, where the
   work is now, what this message changes. Name a file, table, or term the first time
   it appears.
2. **Write ASD-STE100 Simplified Technical English** — the aerospace maintenance-manual
   standard. Active voice, present tense, one word per meaning, ≤20 words per
   procedural sentence, no noun stacks deeper than three, articles kept. Code, paths,
   commands, and error strings are exempt and stay verbatim.
3. **Use the ubiquitous language from `CONTEXT.md`.** If the repo has one, its terms are
   used exactly as defined — no invented synonyms. If it doesn't, the codebase and your
   own wording are the vocabulary instead. It never blocks on a missing file.

`keep-coding-instructions: true`, so Claude Code's engineering behavior is untouched —
this changes how it explains, not what it does. A closing rule stops the obvious failure
mode: it must not substitute an explanation for the work, and must not re-state context
in every message of a long thread.

Adapted from Matt Pocock's [`wait-what`](https://github.com/mattpocock/skills) skill,
which asks for this once. This asks for it always.

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
