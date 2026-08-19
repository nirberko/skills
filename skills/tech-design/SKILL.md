---
name: tech-design
description: Write a technical design document (TDR / design doc / RFC) gradually, one section at a time, with the user in the loop. Reads the code first, then interrogates the request until every term is defined, states the gap and why it is a gap, tests goals against non-goals, and agrees an approach in ordinary words before any table or endpoint is named. Then names the new pieces, walks one item through the system including the failure cases, and gives each its own section covering why-this-way, what-it-owns, how-it-fails and the traps. Writes every sentence of the document in ASD-STE100 Simplified Technical English. Outputs Confluence-ready HTML+ (@mention chips, status pills, panels) or plain markdown. Use when the user asks to create, draft or write a tech design, design doc, TDR, RFC, architecture doc or design review, says "how should we build X" or "I need this reviewed", or hands over a feature that needs designing before it is built. Also works on an existing half-written design.
---

# Tech Design

A design doc is not a write-up of a decision already made. It is how the
decision gets made, in the open, in words a reviewer can argue with.

So write it **gradually**. Read first, ask a lot, agree the shape, then write
section by section with the user in the loop. A document produced in one turn is
a guess with headings on it, and reviewing it costs more than writing it did.

The reader is a competent engineer from **another team** who has never opened
this code, and who often reads English as a second language. They must get
through the whole design without asking anyone a question, and a reviewer must be
able to map each line to the eventual diff.

**The document is written in ASD-STE100 Simplified Technical English.** Short
sentences, active voice, approved words, one word for one meaning, and every
internal term glossed inline where it first appears. Rules, the substitution
table, and the worked examples are in `references/ste.md`. The **conversation**
with the user stays natural English - STE applies to the document, not to the
questions you ask about it.

Default output is Confluence HTML+ rather than markdown, because it unlocks
native Confluence nodes: real @mention chips, the Status pill, info panels, and
round-trip-safe updates that preserve inline comments. Write plain markdown
instead when the user isn't on Confluence.

## Reference files

| File | Open it at |
|---|---|
| `references/conventions.md` | Phase 1. Section order, style, outsider rules, diagrams, house patterns. |
| `references/interrogating.md` | Phase 2. The glossary pass, question rounds, the fuzzy-word table. |
| `references/ste.md` | Phase 8, and any time you draft doc prose. The STE writing rules, approved verb forms, the word substitutions, and where STE gives way. |
| `references/sections.md` | Phase 7b. Every section: when it earns its place, what good looks like, what to ask, how it goes wrong. Includes the per-component template. |
| `references/review.md` | Before handing over. The variation walk-through, the edge-case sweep, the self-check. |
| `references/publishing.md` | Only when the user asks to publish. |

## First: size the design

Eight phases on a one-table change is worse than no process. The user wanted a
document and got an interview. Size it before running anything:

| Lane | When | What you run | User turns |
|---|---|---|---|
| **Quick** | One component, no new infrastructure, reversible. A column, an endpoint, a flag. | Phase 1, a single question batch, then write the whole doc in one pass | 1-2 |
| **Normal** | Most designs. A few new pieces, real unknowns, one team | All phases, checkpoints merged in pairs | 3-5 |
| **Full** | New infrastructure, a migration on live data, several teams, or hard to undo | All phases, every checkpoint separate | 5-8 |

- **Reversible and small → Quick.** Save the ceremony for one-way doors.
- **Touches live data, money, permissions, or another team's contract → at least
  Normal.**
- **Unsure → Quick.** Escalating mid-run costs one sentence ("this is bigger than
  it looked, switching to the full workflow"); starting heavy has already spent
  the user's turns.
- **The user can force a lane.** "Just write it", "quick version", "don't ask me
  questions" → Quick, no negotiation. State what you assumed instead of asking.

In Quick, still run Phase 1 and the glossary pass. They are what stop the doc
citing a file that doesn't exist.

## The rule that governs the whole skill

**Never write more than one section ahead of the user.** If you find yourself
drafting three sections because you are confident, stop. Confidence is exactly
when a wrong assumption gets baked in quietly.

## Which mode

**New doc** - a feature request, a ticket, a problem. Start at Phase 1.

**Existing doc** - the user points at a file or a Confluence page. Read it in
full, then say in one message:

```
What this doc already settles:      <list>
What it asserts without support:    <list>
What a reviewer will ask for next:  <list>
What I'd work on first:             <one thing>
```

Then join at the phase covering the biggest gap. Do not restart from Phase 1 and
re-derive what is already agreed.

---

## Phase 1 - Read, before asking anything

Every question the code already answers spends the user's patience for nothing.
Three things happen here, in this order.

**a. Load the conventions.** `references/conventions.md`.

**b. Load the house patterns, if any.** Every org has recurring things a design
is expected to address: which database a new table belongs in, whether a change
has to work on two engines, how migrations are staged, how a feature is flagged
and monitored. These are org-specific, so this skill ships none. Use the first
that exists:

- `docs/tech-design.md` or `.github/tech-design.md` in the current repo
- `~/.claude/tech-design/<repo>.md`

If none exists and the change touches infrastructure, say so once and offer to
derive one - see *House patterns* in `references/conventions.md`. Do not block on
it, and never invent house rules you can't point at.

**c. Read the code and find the precedent.** Fill in this block. It becomes the
Current Architecture section later:

```
What exists now:    the components involved, one line each
Data flow:          what calls what, what reads and writes where
Where it lives:     repos, services, jobs, queues, tables, with paths
Limits today:       timeouts, batch sizes, rate caps, known bottlenecks
Who depends on it:  what else reads this data or calls this path
Similar prior art:  has something this shape been built here already?
Couldn't find:      named holes, with what you searched for
```

A design that mirrors an accepted one gets reviewed faster. If the user has a
corpus of past designs - a Confluence space, a `docs/designs/` directory - grep
it for the closest prior design of the same shape (a schema change, a new API, a
migration) and mirror its structure and its section names.

Then say in one short message what you learned and what you couldn't find. That
message does two jobs: it shows your work, and it invites correction on the parts
you got wrong before those parts turn into a design.

---

## Phase 2 - The glossary pass

**Open `references/interrogating.md` now.**

This is the phase people skip and the cheapest one here. Pull every noun that
carries meaning out of the request and rate it **known** (found it in the code,
here is where) / **assumed** (I have a definition, nobody confirmed it) /
**unknown** (I do not know what this refers to). Show the whole table, including
the known rows, so the user can correct a `known` you got wrong.

Two hard rules:

1. **Every `assumed` gets confirmed before it reaches the doc.** An assumed
   definition that turns out wrong invalidates every section built on it, and you
   find out at review.
2. **No `unknown` term is ever written into the doc.** Not with a hedge, not in
   brackets. Ask.

The glossary is a working artifact for the conversation. **It never becomes a
section of the document** - the doc defines each term inline, in the sentence
that first uses it. See *Write so an outsider understands* in
`references/conventions.md`. The pass is what makes those inline glosses possible
and correct.

**The pass has a second job: it is the document's approved Technical Names list.**
STE runs on about 900 approved words, which cannot describe a real system, so the
standard lets a project approve its own names for things and its own verbs for
actions. Every term you rated `known`, or confirmed from `assumed`, is approved
for this document and used freely. Every term still `unknown` is not approved and
does not appear - which is rule 2 above, arrived at from the other direction. If
the project keeps a house file, record its standing list there. Details in
`references/ste.md` → *Technical Names and Technical Verbs*.

---

## Phase 3 - Question rounds

Batched, not drip-fed. Every question carries **why you are asking** and **the
default you will use if the user doesn't answer**, so no round can block. Use
`AskUserQuestion` where the answers are choosable, plain text where they are
open. Full question bank in `references/interrogating.md`.

| Round | Theme |
|---|---|
| **1** | Gates and glossary. Who reviews this and what will they push back on? Deadline? Is the approach already decided or genuinely open? Plus every `unknown` term. |
| **2** | The problem. How often, how many, since when, what's the evidence, what happens if we do nothing. |
| **3** | Boundaries. What must this not change? What are we explicitly not doing? Hard constraints, SLAs, compliance. |
| **4** | Shape of the solution. What must it fit alongside, volume and growth, latency tolerance, who operates it after it ships. |
| **5+** | Per-section, asked as you write each one in Phase 8. |

Discipline: delete every question Phase 1 answered; merge questions with the same
answer; chase every fuzzy word ("scalable", "real-time", "robust", "just") using
the table in `references/interrogating.md`; and whenever a constraint appears, ask
**"who decided that, and can it change?"** Half the constraints in design docs are
preferences nobody has re-examined.

In Quick lane this is one batch, not five rounds.

---

## Phase 4 - Say what's wrong, in plain words

Before proposing anything. This feeds the Problem part of the Requirements
section:

```
Today:          what happens now, in ordinary words
The gap:        what should happen and doesn't
Why it's a gap: who is hurt, how often, how badly, what it costs
Scale:          numbers, not "a lot"
Evidence:       incidents, dashboards, tickets, the actual log line
Confidence:     every claim tagged proven / likely / guess
```

**"Why it's a gap" is the load-bearing part.** A reviewer who accepts the current
state and the gap but doesn't feel the why will approve the doc and never
prioritise the work. If the honest answer is "it annoys us", write that. An
accurate small reason beats an inflated large one, which gets found out.

**Keep the symptom, the trigger, and the cause separate.** The last thing that
changed is usually the trigger, not the cause. Blaming it is how the wrong thing
gets fixed.

**No solution words in here.** The moment "because we have no cache" appears, the
section has stopped describing a problem and started defending an answer.

**Carry the confidence tags into the doc**, inline in the sentence. Docs get
forwarded and hedges fall off first; a guess that arrives at a reviewer as fact is
how designs get built for problems that don't exist. Format in
`references/conventions.md`.

**Checkpoint.** Show today, the gap, and the why. Ask one question: *does this
match what you see?* Do not propose a solution until the problem is agreed.

---

## Phase 5 - Goals and non-goals

Written together, because they define each other, and agreed before anything is
designed. A goal added later invalidates the design; a goal named now shapes it.

**A goal is an outcome, not a task.** Test each candidate:

- Is it a result, not a piece of work? "p99 under 500ms" yes; "add a cache" no.
- Can someone say yes or no after it ships? If not, it's a mood.
- **Can you imagine a reasonable design that fails this goal?** If not it's a
  platitude - delete it. "Should be maintainable" fails this test.
- Does it name who benefits?

Group them the way reviewers read them: functional, operational (latency,
reliability, cost), security, and any SLA or SLO you are signing up to.

**A non-goal is something a reasonable reader would otherwise assume is
included.** That is the whole test. "We are not rewriting the frontend" is a real
non-goal if the frontend touches this; "we are not building a spaceship" is noise
that buries the two real ones. Each one says which kind it is:

| Kind | Must also record |
|---|---|
| **Not now** | The trigger - what has to become true for this to come back. "Not now" with no trigger is "never" wearing a friendlier word. |
| **Not ever** | The reason. This is often the most valuable line in the doc, because it stops the same argument in three months. |
| **Someone else's** | Who, and whether they know. |

**Every non-goal traces to something that came up.** If you can't point at the
question, the ticket, or the sentence that raised it, you invented a strawman.
Cut it.

**Checkpoint.** Show both lists and ask specifically: *what did I put in Goals
that you'd move to Non-Goals, and what's missing from either?* That gets better
answers than "look OK?"

---

## Phase 6 - The approach, in ordinary words

**Before any component, table, endpoint, queue or library is named.**

Write two or three candidate approaches. Each is a short paragraph a non-engineer
could follow: what the system will do differently, not what will be built.

```
Approach A - <plain name, e.g. "do the work when it's asked for, not overnight">
  What changes:  <2-4 sentences, ordinary words, no component names>
  Why it works:  <one sentence tying it to the gap from Phase 4>
  Costs you:     <the real downside - effort, risk, something it makes harder>
  Rough size:    <a range, e.g. 1-2 weeks>
```

Rules:

- **No nouns from the stack.** No Kafka, no Redis, no "a new service". If the
  paragraph can't be written without them, you are describing an implementation,
  not an approach.
- **Two minimum**, unless you can say in one line why there is genuinely one way.
  A single option is not a decision and reviewers know it.
- **Name the one you'd pick, and why, in one sentence.** A menu with no
  recommendation pushes your job onto the reviewer.
- **Real downsides only.** If every alternative has a fatal flaw and yours
  doesn't, you wrote the alternatives to lose. Reviewers can tell, and it costs
  you the room.

**Checkpoint - the biggest one here.** The user picks. Do not move on without a
pick. Whatever they don't pick becomes `Possible Solutions` in the doc with the
reason recorded, which answers the "why not just…" question every reviewer asks.

---

## Phase 7a - Name the pieces, then walk one item through

Only once the approach is picked. A **piece** is anything with its own
responsibility and its own way of failing: a table, a store, a job, a service, a
queue, a new API surface, a column set that changes what is true.

List them one line each, then show how work moves between them as a plain-text
sketch or a small diagram. Then do the thing that proves the design works:

**Walk one item through the whole system, numbered, in ordinary words.** One
commit, one request, one row. Then the variations that matter:

- nothing has changed since last time (should usually be: almost nothing happens.
  If a quiet run is expensive, the design has a problem)
- the item changes
- the item goes away entirely - who closes, deletes, or cleans up?
- a dependency rejects us or is down
- the process dies halfway through

**If you can't narrate one of those, that's a hole in the design, not a gap in
the writing.** Go back and fix the design. This walk-through is the cheapest
bug-finder here, and it becomes the End-to-End Flow section. The fuller sweep,
including what happens to rows that already exist, is in `references/review.md`.

**Every new piece gets its own section.** The Design Summary opens with how they
fit together; each piece then gets a numbered subsection of its own.

**Checkpoint.** Agree the piece list before writing any of it. A piece added
later re-opens every section written so far. **If the list runs past five**, say
so and ask whether some collapse into one. Five new components for one design is
usually two designs.

## Phase 7b - Choose the sections

**Open `references/sections.md` now.**

The canonical section order is in `references/conventions.md`. It is a starting
point, not a form. **A design with five sections that all say something beats
twelve where seven say "N/A".** Propose the section list for *this* design as a
short table - section, and one line on why it's in or out - and let the user cut
or add. The per-piece subsections from 7a go in the list too, by name.

Always in: Overview, Requirements, Design Summary, Open questions.

Four sections are risk-carrying, and dropping one silently is how a design ships
with a hole in it:

> **Migration & Backfill, Rollout & Rollback, Security & Access, Cost.** If one is
> skipped, the doc records a single line saying why. "No new infrastructure, so no
> cost change" is a fine line. Silence is not - silence reads as "not considered",
> and that is the reviewer's first question.

For a small design these are bold run-in paragraphs inside the Design Summary
rather than top-level sections. Either is fine. Absent is not.

---

## Phase 8 - Write it, one section at a time

Copy `assets/tech-design-template.html` as the starting structure and write to a
file the user can watch grow (default: the repo or a scratch directory, as
`<name>-tech-design.html`). For markdown output, same sections, plain markdown.

The loop, per section:

1. **Ask the section's questions first** - they are listed per section in
   `references/sections.md`. Usually one to three.
2. **Draft the section.**
3. **Show it and stop.** Name the assumptions you made in it and ask one specific
   question about the part you are least sure of.
4. **Move on after a response** - or, if the user goes quiet, state the assumption
   in **bold** in the doc and continue. Never block, never bury.

**One piece per section.** Never describe two components in one section: the
reviewer has to hold both in their head to check either. Each component section
answers the same six things - full template and worked examples in
`references/sections.md`:

```
What it is       one or two sentences. What job it does in the system
Why it exists    what breaks without it
Why this way     the local alternative you rejected, and why. Not the global
                 approach - the choice inside this piece
What it owns     the data, decisions or calls only this piece makes. And what
                 it does not own
The detail       the substance: location, Reuses list, schema, query, contract,
                 config
How it fails     errors, retries, ordering, what a crash halfway leaves behind
Traps            the specific way an implementer gets this wrong
```

**"Why this way" and "Traps" are what make a component section worth reading.**
Without them it is a schema dump the reader has to reverse-engineer the reasoning
from, and the next person changes it and breaks an invariant nobody wrote down.
The trap is usually the thing you only saw because you thought it through. Write
it down; it is the most expensive knowledge in the document.

While writing:

- **Write it in STE.** Open `references/ste.md` before drafting the first
  paragraph. The rules that catch the most: one idea per sentence, 25 words
  maximum, active voice with the actor named, present tense, no `-ing` word used
  as a verb or a noun, no more than three nouns stacked, and one word for one
  meaning across every section. Draft the sentence, then run it past the
  substitution table.
- **Be concrete.** Real model classes, schemas, queries, YAML/SQL, exact file
  paths. Name what each component **reuses** - reusing existing code over
  building new is a first-class value in review, so make it visible.
- **Keep a live Open Questions list.** Add to it the moment something is
  unresolved. Reconstructed at the end it contains the ones you remember and none
  of the ones you quietly assumed away. Each gets an owner and what it blocks.
- **Diagrams: render the flows you designed, placeholder the ones you inferred.**
  A pipeline or state machine you are proposing gets a real rendered Mermaid
  diagram (recipe and the curl check in `references/conventions.md`). An
  architecture diagram of an existing system you inferred rather than read stays a
  placeholder with a written brief, because a wrong diagram is believed far longer
  than a wrong paragraph and it gets screenshotted into other documents.
- **The detailed design is where the approved Technical Names carry the
  precision.** Schemas, queries, class and column names go in unchanged. What does
  not come with them is loose prose: the sentences around the code follow the same
  STE rules as every other section, and every internal term and acronym is glossed
  inline where it first appears.
- **Traps are written as STE warnings.** Start with the command, put the condition
  before the instruction, one instruction per sentence, and say what happens if the
  reader gets it wrong. `references/ste.md` → *Traps and warnings*.
- **Write the failure paths.** Happy-path-only designs pass review and fail in
  production.

---

## Output, self-check, publish

Run the self-check in `references/review.md` before handing anything over. Then
**publish only when the user asks.** It is an outward-facing write: confirm the
title, space, and parent page first, then follow `references/publishing.md`.
Default to a draft unless they say publish live, and return the page URL.

---

## Rules

1. **Read before you ask.** Every question the code answers is patience spent for
   nothing.
2. **No undefined term reaches the doc.** Confirm the assumed ones, ask about the
   unknown ones, and gloss each one inline where it first appears. Never add a
   glossary section.
3. **Every sentence of the document is STE.** The writing rules never relax. Only
   the word list gives way, and only in a sentence that makes a judgement.
4. **Problem agreed before solution proposed.** Phase 4 has a hard checkpoint.
5. **The approach in ordinary words before anything is named.** Phase 6 has the
   hardest checkpoint.
6. **A goal is checkable; a non-goal is something a reader would otherwise
   assume.** Both tested, not listed.
7. **One section ahead of the user, maximum.**
8. **New pieces get named, then each gets its own section** with why-this-way and
   traps.
9. **Walk one item through the system before writing any of it**, including the
   boring case, the deletion case, and the failure case.
10. **Sections are chosen, not stamped.** But a skipped Migration, Rollout,
    Security or Cost section says why in one line.
11. **Confidence tagged** - proven, likely, guess.
12. **Render diagrams you designed; placeholder diagrams you inferred.**
13. **Publish only when asked.**

## Anti-patterns

Do not:

- Produce the whole document in one message outside Quick lane. That's a guess
  with headings, and reviewing it costs more than writing it did.
- Reach for component names in Phase 6. "We'll add a queue" is not a high-level
  approach, it's a decision nobody agreed to.
- Paste the glossary table into the document. Definitions live in the sentence
  that uses the term. It is the approved Technical Names list, not a section.
- Write the document in ordinary English and then try to convert it. Converting
  prose to STE afterwards produces short sentences that still hide the actor.
  Draft each sentence in STE the first time.
- Interrogate the user in STE. The document is controlled English; the
  conversation is not.
- Approve a Technical Name to avoid rewriting a sentence. A Technical Name names a
  thing in the system. It is not a licence to keep `leverage`.
- Write alternatives you designed to lose.
- List non-goals nobody would have assumed. It pads the doc and hides the two
  real ones.
- Let "scalable", "real-time" or "robust" survive into the doc without a number
  next to it.
- Describe three new components in one section because they are "part of the same
  design".
- Write a component section that is a schema and nothing else.
- Skip the walk-through because the design "obviously works". The variations are
  where it doesn't.
- Draw a rendered architecture diagram of a system you inferred rather than read.
- Save Open Questions for the end.
- Skip Cost or Security silently because they felt like overhead. One line saying
  why costs nothing and stops the reviewer's first question.
- Write a design that is correct for new data and undefined for the rows that
  already exist. That is the most common way a reviewed design fails in
  production.

## Scope note

The template is shaped for a backend or full-stack change, which is the common
case. Trim the Data Model and API sections for a pure frontend or infrastructure
design, and keep Requirements → Design Summary → Tasks & Phases.
