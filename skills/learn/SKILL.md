---
name: learn
description: Interactive step-by-step codebase tutor. Traces a real end-to-end flow in this repo and teaches it one small stop at a time - plain-language explanation, a short real code snippet with file path and line numbers, then a multiple-choice question to verify understanding before continuing. Deliberately short per stop; extra depth only when asked. Saves every lesson, code reference and answer into an Obsidian vault so the knowledge accumulates and can be revised or resumed later. Use when the user says "/learn", "teach me", "explain how X works step by step", "walk me through X", "I don't understand how X works", "guide me before I build X", "tutor me on X", or asks to understand a feature/flow/mechanism instead of asking for it to be implemented. Also use when the user is about to start a task in an unfamiliar area and wants to understand it first, or asks what they have already learned about part of the platform.
---

# Learn

Teach the user one flow in this repo, interactively, until they can trace it alone.

The user is a real engineer who leans on the agent too much and wants to actually
understand the code. Treat them as smart but unfamiliar. Assume no prior
knowledge of any internal name, table, DAG, or acronym.

**The failure mode of this skill is too much text, not too little.** A stop the
user skims is a stop they did not learn. One idea, one snippet, one question,
next.

## Hard rules

1. **One stop per response.** Never dump the whole flow. Ever.
2. **One idea per stop.** If a stop needs "and also", it is two stops.
3. **Stay inside the budget** (below). Overflow goes in the drawer, not the stop.
4. **Every claim comes from a file you actually read.** Use Read/Grep/Glob
   yourself - no subagents, no memory, no guessing. Wrong line numbers destroy
   the whole point of this skill.
5. **Always cite `path/to/file.py:123`.** The user will open it and check.
6. **End every stop with a question**, then wait. No auto-advance.
7. **Do not write the feature during a lesson.** If the user asks for code,
   say the lesson is paused and confirm before switching to build mode.
8. Plain words. Any internal term gets a one-line definition on first use.

## The budget

Per stop, hard caps:

- **Prose: ~100 words total**, code excluded. Count them.
- **Code: one snippet, <=10 lines.** Trim bodies to `...`. Keep only the lines
  you are about to talk about.
- **File citations: one primary.** A second is allowed only if the stop is
  literally about the hop between two files.
- **Reading bullets: <=3**, one short line each.
- Sentences short. No paragraph over 2 sentences.

Cut ruthlessly. These do NOT belong in a stop:

| Cut this | Why |
|---|---|
| "14 of 93 call sites do X" | Counts are trivia unless the count IS the lesson |
| A second enforcement site "for completeness" | One place teaches the idea |
| Side gotchas unrelated to this stop's idea | Drawer, or its own stop |
| Restating what the previous stop said | They just read it |
| Historical / design-rationale asides | Drawer |
| Two snippets in one stop | Pick the one that carries the idea |

## Phase 1 - scope it

Before reading anything, settle two things (one `AskUserQuestion`, both
questions in the same call):

If the user only wants to understand one thing right now and does not want a
course, they want `explain`, not this. Say so in one line and hand off.

- **Where does the flow start and end?** Offer 2-4 concrete traces you can
  actually teach. Example for "how an order gets charged": (a) full trace - HTTP
  handler -> order service -> payment call -> DB write, (b) just the retry logic
  in isolation, (c) how the existing test harness exercises it.
- **Current level?** "Never seen this code" / "Seen it, don't get the flow" /
  "Know the flow, want the details". This sets depth, not tone.

## Phase 2 - build the real trace

Do the research now, before teaching:

1. Check this repo's own docs first - `CLAUDE.md` / `AGENTS.md` often point at
   `.cursor/rules/*.mdc` or `.claude/skills/`. A matching rule file saves a lot
   of grepping.
2. Follow the actual call chain in the code. Entry point -> next hop -> next.
3. Turn it into **6-10 numbered stops**. Each stop = one idea, small enough to
   fit the budget. More than 10 means the scope is too wide - narrow it.

**Name each stop as a plain-language claim or question**, not a file name.
"How does the app find a handler it has never heard of?" beats "utils.py".

Show the numbered plan (one line each, with the file for each stop), say roughly
how long it will take, and ask to start. Do not teach yet.

## Phase 3 - teach, one stop at a time

Each stop uses exactly this shape:

```
## Stop 3 of 8 - How raw provider JSON becomes our columns

**Short version:** the provider sends its own field names; this file renames them to ours.

<code block: <=10 lines, real, trimmed>
`src/providers/acme/transform.py:42-50`

- line 44 - reads the provider field
- line 47 - writes our column name
- line 49 - drops anything unmapped, silently

**Watch out:** a typo in the mapping is not an error, just a missing column.

*Deeper if you want: why the mapping lives here and not in the API client.*
```

Rules for the shape:

- **Short version** = one sentence, no jargon. It replaces the old
  "in one sentence" + "why it exists" pair - fold the "why" in only if it fits
  the sentence, otherwise skip it.
- **Watch out** = at most one line, and only when there is a real trap. Skip it
  freely.
- **Deeper drawer** = one italic line naming 1-2 things you deliberately left
  out. Name them, do not explain them. If the user asks, open the drawer with
  the `explain` skill scoped to that one thing (`--quick` depth), spend one extra
  response, then continue the lesson. The stop budget still applies to the
  lesson; the drawer response is the exception, not a new baseline.
- Unfamiliar concept? One everyday comparison, <=1 sentence. Then back to code.

Then the check, via `AskUserQuestion`:

- **Quiz** (default) - one question, 4 options, exactly one correct. Header max
  12 chars. Options short. Distractors must be plausible: pull them from real
  neighbouring code, a common misconception, or the previous stop. No joke
  options. Never hint the answer in the wording.

  **Position the correct answer randomly.** The default pull is to list it first -
  resist it, or the user learns to click option 1 without reading. Pick the slot
  mechanically: first line number cited in this stop, mod 4 -> 0=A, 1=B, 2=C,
  3=D. Never the same slot twice in a row (collision -> shift down one). Over a
  full lesson all four slots should get used.
- **Explain-back** (every 3rd stop or so) - "In your own words, what does X hand
  to Y?" Free text. Grade it honestly.

After they answer:
- Correct -> one line confirming, plus one line on why a tempting wrong option
  is wrong. Two lines total, then move on.
- Wrong -> do not just give the answer. Point at the line that settles it, ask
  again. Second miss -> explain differently (analogy, or a concrete input value
  traced through), then move on. Never make them feel slow.

Then ask what's next: **continue / repeat this stop / go deeper here / skip ahead**.

**"Go deeper here" and second-miss recovery both route through the `explain`
skill**, scoped to the one thing that is unclear - it grounds the extra detail in
real cited code instead of prose. Record the result in the vault as a one-line
`Deeper:` pointer, not the full answer.

## Phase 4 - close

When the stops are done:

1. The whole flow in <=10 lines, file per line, in order - their cheat sheet.
2. 2-3 things they can now do without help ("you can find where field X is set
   by grepping Y").
3. What was deliberately left out, so they know their own edges.
4. Now offer to build the original task, with them driving.

## The vault

Everything taught is written to an Obsidian vault outside the skill, so it
survives skill updates:

```
~/.claude/learn-vault/
├── Flows/<Topic Name>.md      one note per guide
└── Concepts/<Term>.md         one note per internal term explained
```

No setup needed - create the directory on first use, and the user opens it as a
vault whenever they like. Plain markdown, `[[wikilinks]]`, nothing exotic.

**Write as you go, not at the end.** Create the flow note at Phase 2 with the
numbered plan, then append each stop right after the user answers its question.
A session that dies mid-lesson must leave the finished stops behind.

**The note obeys the same budget as the lesson.** It is a cheat sheet to skim in
six months, not a transcript. Same snippet, same <=100 words. If a deeper drawer
was opened, record it as a one-line `Deeper:` pointer, not the full answer.

**Flow note shape:**

```markdown
---
tags: [flow, backend]
started: 2026-07-29
status: in-progress   # -> complete at Phase 4
---

# Order Charge Flow

**Trace:** HTTP handler -> order service -> payment call -> DB write
**Plan:** 1. <stop> 2. <stop> ...

## Stop 1 - <plain-language title>
<the short version + the reading bullets. Nothing more.>

`path/to/file.py:42-50`
```python
<the same trimmed snippet shown in the lesson>
```

Concepts: [[Idempotency key]], [[Retry budget]]
Deeper: why the retry budget is per-order (asked, answered in session)

**Q:** <question asked>
**Answered:** C (correct) | B -> correct was C. Missed because <what tripped them>. #review
```

**Concept notes** - one per internal term: a domain noun, an in-house acronym, a
table or DAG name, a magic status string. Created the first time the term is
defined. **3-5 lines, hard cap:** what it is in plain words, where it lives in
code, `[[links]]` to flows that use it. Update instead of duplicating if the note
already exists.

Tag every missed question `#review` so the user can search `tag:#review` and
revise their own weak spots.

## Reusing the vault

At Phase 1, always check the vault first:

- Flow note exists with `status: in-progress` -> offer to resume from the last
  recorded stop instead of restarting.
- Flow note exists and is complete -> the user has seen this. Offer: re-quiz from
  the recorded questions, go deeper on stops marked `#review`, or teach an
  adjacent flow instead.
- Related concept notes exist -> reference them (`you already know [[Idempotency key]]`)
  rather than re-teaching from zero.

Also read the vault when the user asks what they've already learned, or asks a
question that a past lesson covered. Cited line numbers in old notes may have
drifted - re-verify against the file before repeating them.
