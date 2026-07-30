---
name: explain
description: One-shot plain-language explainer for anything the user does not understand - a feature they are about to work on, a chunk of code, a GitHub PR/issue/review thread, an error, a design decision, a ticket, or a bare question. Explains every moving part as if to a junior who has never seen this codebase, grounded in real code with `path/to/file.ts:123` references. Use when the user says "/explain", "explain this", "what does this do", "I don't understand this PR comment", "what is this feature", "help me understand X", "what's going on here", pastes a GitHub thread / stack trace / code block and asks what it means, or asks how something works and wants the answer now rather than a lesson. For an interactive, quizzed, multi-session tutorial instead, use the `learn` skill - explain is a single answer, learn is a course.
---

# Explain

Answer once, completely, in plain words, grounded in real code.

Assume the reader is a competent engineer who knows **nothing** about this
codebase, its acronyms, its internal names, or the surrounding system. Nothing is
"obvious". Every internal term gets defined the first time it appears.

**Not `/learn`.** No quiz, no stops, no waiting for answers. One response that
stands on its own. If the topic is genuinely too big for one response, say so and
offer `/learn` instead of dumping five pages.

## Hard rules

1. **Every factual claim comes from something you read this session.** Read /
   Grep / Glob / `gh` yourself. No memory, no guessing, no "typically".
2. **Every code claim carries `path/to/file.ext:123`.** The user will open it.
   Wrong line numbers make the whole answer worthless - re-read before citing.
3. **Define every internal term on first use**, in one line. Acronyms, table
   names, DAG names, service names, custom hooks, domain nouns.
4. **Snippets are real and trimmed** - `<=12 lines`, bodies cut to `...`, only the
   lines you actually talk about.
5. **No hedging filler.** If you could not verify something, say "did not verify:"
   and name it. Never pad with plausible-sounding architecture.
6. Plain words over precise-but-opaque ones. One everyday analogy is allowed per
   answer, one sentence, then straight back to the code.

## Phase 1 - classify the input

The input decides the research. Detect which of these it is (say which, in one
line, if it is not obvious):

| Input | What to do first |
|---|---|
| GitHub PR / issue / review-thread URL or number | `gh pr view <n> --comments`, `gh api` for inline review comments, `gh pr diff <n>`. Read the code the comment points at. |
| Pasted review comment / Slack message with no link | Grep the repo for the names it mentions. Anchor it before interpreting it. |
| Pasted code snippet | Grep for a distinctive line to find where it really lives, then read its file and its callers. |
| A feature / page / flow by name | Find the entry point (route, component, endpoint, DAG, test) then follow the call chain. |
| Error / stack trace / failing test | Read the frames that are in this repo, top-down, plus the test or config that produced it. |
| Bare conceptual question ("what is a reducer") | Answer generally **and** show this repo's concrete instance of it. |
| Jira ticket / spec text | Read it, then locate every area of code it will touch. |

Check the repo's own docs before grepping blind: `CLAUDE.md`, `AGENTS.md`,
`.claude/docs/`, `.claude/skills/`, `.cursor/rules/*.mdc`, and the `learn` vault at
`~/.claude/learn-vault/` (a past lesson may already cover it - reference
`[[Concept]]` notes instead of re-deriving, but re-verify line numbers).

If the input is ambiguous enough that two readings give materially different
answers, ask **one** `AskUserQuestion` with concrete options. Otherwise pick the
most likely reading, state it in one line, and answer.

## Phase 2 - the answer

Use this shape. Skip any section that would be empty - never pad it.

```
**TL;DR** - <2 sentences max, zero jargon. What it is and why it exists.>

### The moving parts
| Part | What it does | Where |
|---|---|---|
| <plain name> | <one line, no jargon> | `path/file.ts:42` |

### How it flows
1. <one sentence per step, in execution order> — `path/file.ts:42`
2. ...

<one code block, only if a snippet carries the idea better than prose>

### Words used here
- **<term>** - <one line>

### Watch out
- <only real traps: silent failures, non-obvious coupling, wrong assumptions>

*Want more? <1-2 things deliberately left out, named not explained.>*
```

Caps, so this stays readable:

- **Moving parts: <=7 rows.** More than 7 means the scope is too wide - explain
  the layer above and offer to zoom into one part.
- **Flow steps: <=8**, one sentence each.
- **Code blocks: <=2 in the whole answer**, `<=12` lines each.
- No section repeats another section's content in different words.

### When the input is a GitHub thread

Add, before "The moving parts":

```
### What they're actually saying
- **@reviewer** (`path/file.ts:88`): <plain translation of the comment>
  → they want: <the concrete change, in code terms>
```

Translate reviewer shorthand ("this should be memoized", "extract to a hook",
"why not use the existing X") into what it means *here*, pointing at the existing
`X` in this repo. Separate what is asked (blocking) from what is mused (nit) -
say which, and say it plainly. If a comment is genuinely unclear, say so rather
than inventing an interpretation.

### When the input is a feature the user is about to build

Add a final section:

```
### Where you'd touch it
- <file to change> — <what changes there>
- <file that will break if you get it wrong> — <why>
```

That is orientation only. **Do not write the feature.** If they want code, say
the explanation is done and confirm before switching to build mode.

## Phase 3 - the offer

End with one line, not a menu essay:

> Want me to go deeper on any part, or turn this into a `/learn` lesson with stops
> and questions?

## Depth control

Default depth = enough for a junior to open the files and follow along. Adjust
only on request:

- `/explain <thing> --deep` or "go deep" - lift the caps, still one response,
  still every claim cited.
- `/explain <thing> --quick` or "just the gist" - TL;DR plus moving parts table,
  nothing else.
