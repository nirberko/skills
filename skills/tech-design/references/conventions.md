# Tech Design Conventions

The shape of a design document that gets reviewed quickly and built from
accurately. A design is read once by people who will argue with it, and then kept
as the record of what was decided. Optimize for both.

The document is written in **ASD-STE100 Simplified Technical English**. The rules,
the approved word substitutions, and the worked examples are in `ste.md`.

This file holds the invariants: what order the sections go in, how to write so a
stranger can follow it, the style rules, and how to draw things. **Per-section
guidance** - what each section is for, when it earns its place, what to ask, how it
goes wrong - is in `sections.md`.

## Table of Contents
- [Section order](#section-order)
- [Write so an outsider understands](#write-so-an-outsider-understands)
- [The register: Simplified Technical English](#the-register-simplified-technical-english)
- [Confidence tags](#confidence-tags)
- [Style rules](#style-rules)
- [House patterns](#house-patterns)
- [Diagrams, tables, code](#diagrams-tables-code)
- [Tone](#tone)

## Section order

Canonical order. **Sections are chosen, not stamped** - drop the ones that don't
apply. A small design is just Overview → Requirements → Design Summary → Open
questions. Details on when each earns its place: `sections.md`.

1. `## 📋 Overview` - the metadata table (always)
2. `## 🎯 Requirements` - the problem, scope, goals and non-goals (always)
3. `## 🏛️ Current Architecture` - when something already exists that this changes
4. `## 💻 Technical Overview` - optional; bulleted breakdown by concern, for larger designs
5. `## 🧑‍🎨 Design Summary` - the core, with its fixed menu of subsections (always; see below)
6. `## Possible Solutions` - when comparing options (Option 1 / Option 2 + recommendation)
7. `## 🖥️ Frontend` - when the change has a UI; carries the end-to-end user flow
8. `## 🔄 End-to-End Flow` - runtime walkthrough plus the variations, when the backend flow is non-trivial
9. `## 🚦 Rollout & Rollback` ⚠️
10. `## 🧪 Testing Strategy`
11. `## 📊 Monitoring & Observability`
12. `## 💰 Cost` ⚠️
13. `## ✅ Tasks & Phases` - phased delivery plan, for anything multi-step
14. `## Did Not Address` - explicit scope exclusions (only when useful)
15. `## ⚠️ Risks` - the top three, with mitigations
16. `## 🔗 References` - prior art, tickets, incidents
17. `## ❓ Open questions` - **always last.** Unresolved decisions, each with an owner

**The Design Summary has a fixed, predictable menu.** In this order: 🗄️ Data
model, 🔌 API, ⚙️ Core engine behavior, 🛡️ Access control, ⚡ Performance, 🔍
Filtering & query surfaces, 🚚 Migration & backfill. Drop a slot that does not
apply (with the ⚠️ one-line rule below for Migration and Access control); never
reorder, and never invent a new slot when the content fits an existing one. A
reader who has seen one design from this skill finds everything in the next one
without hunting. Per-slot guidance is in `sections.md`.

**The four ⚠️ sections may be skipped, but not silently.** The four: Migration &
Backfill and Security & Access (both live inside the Design Summary menu), plus
Rollout & Rollback and Cost. A skipped one leaves a single line saying why: *"No
cost change - no new infrastructure."* Silence reads as "not considered", and
that is the reviewer's first question.

**Section length follows complexity, not importance.** A straightforward
mechanism gets one paragraph, even when it is user-facing or central to the
product. A subtle mechanism gets the space it needs. Never pad a simple slot to
make it look thorough - a padded section costs reading time and hides the
sections that actually need arguing with.

Emoji headers are the house style here. Drop them if the team's existing designs
don't use them - match the corpus you're writing into.

## Write so an outsider understands

Assume the reviewer is a competent engineer from **another team** who has never
opened this code. They must be able to follow the whole design without asking
anyone a question. This is a hard requirement, not a nice-to-have.

- **Plain English, short sentences.** One idea per sentence, 25 words at most.
  Prefer the everyday word: "runs after", not "is invoked downstream of". No clever
  phrasing. This is STE rule territory - the full set is in `ste.md`.
- **Active voice, with the actor named.** "The uploader writes `sent_at`", not
  "`sent_at` is written". A passive sentence hides who does the thing, and who does
  the thing is most of a design.
- **One word for one meaning.** Do not call the same thing a job, a run, and a task
  across three sections. Pick one word and keep it everywhere.
- **Explain every internal term inline, the first time it appears**, in a short
  parenthetical or a clause in the same sentence. This covers domain terms, infra
  terms, and every acronym. Example: "the `enriched_orders` table (the stage where
  per-source rows are already stitched into one order)".
- **Never open with a glossary.** No `Vocabulary`, `Terminology`, `Definitions`,
  or `Glossary` section, and no upfront bullet list of "some terms first, because
  the rest of the doc depends on them". A reader should not have to memorize a
  list before the design starts. Every term is defined where it is first used and
  nowhere else. The doc opens with Overview then Requirements; Requirements starts
  with the prose framing of the change, not with definitions.

  This is why the skill runs a glossary **pass** in Phase 2 (see
  `interrogating.md`): the pass is a working artifact for the conversation that
  makes the inline glosses correct. It never becomes a section.
- **Say what a thing does, not only where it lives.** Every file path, class,
  table, or service gets a clause explaining its job: "`AlertRunner` (evaluates one
  alert against current data and emits instances)".
- **Explain why before how.** Open each Design Summary subsection with one
  sentence on the problem that piece solves, then the mechanics.
- **Spell out the current behavior you are changing - in one or two sentences,
  never more.** A reader who does not know today's flow cannot judge the new one,
  and the same reader will not read a long recap. "Explains well" and "reads
  fast" are both requirements; length is a budget, not a proxy for care.
- **Diagrams and tables over paragraphs.** They are the fastest way for a stranger
  to get the shape. Label every box and column.
- **The approved Technical Names carry the precision in the detailed design.**
  Schemas, queries, class and column names go in unchanged. The prose around them
  follows the same rules as every other section.
- **Explanatory does not mean long.** Total length stays the same or shrinks:
  glosses and a "why" sentence buy their space back by replacing vague prose,
  hedging, and repeated detail. If a section grows past a screen, cut detail that
  belongs in the PR instead of trimming the explanation.

Self-check for this, and for everything else, is in `review.md`.

## The register: Simplified Technical English

The rules above are the reason for the register, and STE is the standard that
enforces them. Three points belong here; everything else is in `ste.md`.

**It applies to the document, not to the conversation.** Questions, checkpoints,
and the message that shows what you read in Phase 1 stay natural English.

**The glossary pass is the approved Technical Names list.** STE runs on about 900
approved words, and the standard lets a project approve its own names for things
and verbs for actions. Phase 2 produces that list. This is also why there is no
glossary section: STE asks that a Technical Name is defined for the reader, and
this skill defines it inline at first use. Same rule, one place.

**The word list gives way in a sentence that makes a judgement**, and nowhere
else. Possible Solutions rationale, **Why this way**, Traps, and Risks argue, and
the dictionary is thin there. The writing rules still apply to those sentences:
short, active, present tense, no `-ing` verbs. The first-person recommendation
below is unaffected.

## Confidence tags

Anything you could not verify carries its tag **inline, in the sentence**, not in
a footnote and not as a hedge:

```
The nightly job takes 40 minutes (**proven** - see the run history dashboard).
The slowdown started with the March schema change (**likely** - the timing
  matches, not reproduced).
Provider rate limits are the ceiling here (**guess** - cheapest check is one
  throttled run).
```

| Tag | Means | Also record |
|---|---|---|
| **proven** | Reproduced, or the evidence is direct | Where the evidence is |
| **likely** | Fits everything seen, not directly confirmed | What would confirm it |
| **guess** | Plausible, untested | The cheapest way to find out |

Tags survive forwarding; hedged prose does not. Docs get forwarded and the hedges
fall off first, so a guess that arrives at a reviewer as fact is how a design gets
built for a problem that doesn't exist. If most of the problem section is `guess`,
say that at the top rather than burying it.

## Style rules

- **No revision history or meta-narrative.** The doc describes the current design
  only. Never write "changed from vN" or "the previous version did X", and don't
  keep Did-Not-Address bullets whose only purpose is referencing a dropped earlier
  direction. Dead alternatives simply disappear.
- **No self-justification about the doc's evolution.** Don't sell "why this beats
  the approach we're replacing". This is different from - and must not be confused
  with - the encouraged inline **Why X?** blocks: a short technical justification
  for a non-obvious *component choice* is good and expected.
- **Short headings, no parentheticals.** "Mock service in the web app", not "The
  mock - WireMock service in the web app (mirror of the auth mock)". Cut
  qualifiers like "(non-product)".
- **"Not too technical" is a hard rule, not a tone preference.** The test for
  every detail: does it change what a reviewer approves, or what an implementer
  builds first? If not, cut it - it belongs in the PR. This is the rule behind
  the two below.
- **No infra minutiae.** Image versions, port numbers, CLI flags, and volume
  mounts belong in the PR, not the design. Name the service and the file it lives
  in; one line.
- **No schema internals.** Indexes, primary-key mechanics, and constraint
  internals belong in the PR. The design names the tables, what each means, and
  the columns that carry a decision - see 🗄️ Data model in `sections.md`.
- **No phase headers in Requirements.** Phasing is a delivery detail; it lives in
  Tasks & Phases. Requirements describe what ships now. Mention a future
  extension in one sentence where it justifies a design choice, and nowhere else.
- **Explicit scope statements are quoted, not diluted.** When the user narrows
  the scope ("only X migrates"), the doc says so plainly and describes no work
  outside it.
- **One heading level per depth.** The Design Summary may use themed `##`/`###`
  subsections and numbered components, but don't stack a fourth level - sub-parts
  of a component get **bold run-in labels** as their own paragraph, not `####`.
- **Numbers, not adjectives.** "3 seconds", not "slow". "40,000 rows per tenant",
  not "a lot of data". No fuzzy word survives into the doc unchased - the table is
  in `interrogating.md`.
- **Phases list deliverables only.** No "verify by hand: …" walkthrough bullets
  and no narration bullets ("Submit. Then …") - every phase bullet is a
  deliverable, a Definition-of-Done condition, or a concrete task.
- **No `-ing` word used as a verb or a noun.** "The job is reading the table" →
  "the job reads the table". "Handling of retries happens here" → "this component
  retries the call". Approved Technical Names keep theirs.
- **No more than three nouns stacked.** Break the cluster with a preposition: "the
  tenant sync job retry backoff config value" → "the config value for the retry
  backoff in the tenant sync job".
- **No empty openings.** Delete "There is", "There are", and "It should be noted
  that". Name the subject and start with the fact.
- **Never use em dashes (`—`)** anywhere in the doc - headings, bullets, or body
  prose. Only the regular dash `-`.

## House patterns

Most review comments on a design are not about the design. They're about the
handful of things that team always checks: which database a new table belongs in,
whether a change has to work on more than one engine, how a migration is staged,
how a feature is flagged, how it's monitored, who is allowed to call the new API.

Those are org-specific, so this skill ships none. They live in a house file:

- `docs/tech-design.md` or `.github/tech-design.md` in the repo, if the team
  wants it version-controlled and shared, or
- `~/.claude/tech-design/<repo>.md`, if it quotes internal systems and shouldn't
  be committed.

Read whichever exists and address every applicable pattern in it explicitly.

**If neither exists** and the change touches infrastructure, offer once to derive
one, then move on. Deriving it means reading the team's accepted designs - a
Confluence space, a `docs/designs/` directory - and extracting the questions that
recur across them: which storage, which engine, which migration path, which flag,
which alert channel, which permission model. Write those as a checklist. Do not
guess at house rules you cannot point to in a real prior design, and never put a
derived file that quotes internal systems into a public repo.

Record the Confluence `cloudId` / `spaceId` / `parentId` here too, so the next
design doesn't ask again - see `publishing.md`.

Patterns that are near-universal and worth addressing even with no house file are
the four ⚠️ sections plus observability - where the data lives and how it stays
isolated between customers, what migration has to run and whether it's reversible,
backward compatibility for anything already being read, the flag that gates the
rollout and what happens when it's off, the metric that says it's working, and
access control on any new API or data path. Each is written up in `sections.md`.

## Diagrams, tables, code

**Use rendered Mermaid diagrams** for anything with real structure: pipelines,
request flow across services, state machines, call sequences, table lineage, phase
dependencies. A picture is the fastest way for a reader from another team to get
the shape.

**In moderation.** Add a diagram where a picture shows what prose struggles to -
the data model, a write path versus a read path, a staged migration. Two or three
small diagrams beat many, and a trivial flow gets no diagram at all. A diagram
that repeats what one sentence already said is decoration, and decoration erodes
trust in the diagrams that matter.

**But only for a flow you designed.** An architecture diagram of an **existing**
system you inferred rather than read stays a placeholder with a written brief. A
wrong diagram is believed far longer than a wrong paragraph, and it gets
screenshotted into other documents:

```
[DIAGRAM NEEDED - current state]
Show: <the boxes>
Arrows: <what flows where, and in which direction>
Highlight: <the bottleneck, or the new pieces>
```

Describe the picture well enough that someone else can draw it. If the user would
rather you attempt one, they'll say so - then mark it clearly as a draft to check.

### Rendering a Mermaid diagram

In **markdown** output, a plain ```mermaid fence renders on GitHub and most
viewers. **Confluence cannot render a mermaid fence**, so render it to an image via
mermaid.ink and embed an `<img>`:

1. Write the diagram to a file, e.g. `flow.mmd`:
   ```
   graph LR
     A[Producer] --> B[(Object store)]
     B --> C{Job}
   ```
2. Base64-encode it, URL-safe (`+/` → `-_`), no newlines:
   ```bash
   B64=$(base64 < flow.mmd | tr -d '\n' | tr '+/' '-_')
   echo "https://mermaid.ink/img/$B64?type=png&bgColor=FFFFFF"
   ```
3. Embed it, wrapped in a `<p>`, with an `alt` that says what the diagram shows:
   ```html
   <p><img src="https://mermaid.ink/img/Z3JhcGggTFIK...?type=png&amp;bgColor=FFFFFF"
           alt="Producer writes to the object store, the job reads it" width="760" /></p>
   ```

Rules:

- **Verify every URL before publishing** - `curl -s -o /dev/null -w '%{http_code}'`
  must return `200`. A syntax error in the Mermaid source returns an error image,
  which silently ships as a broken diagram.
- `?type=png` for a crisp raster (the default reply is JPEG); `bgColor=FFFFFF` so
  it doesn't sit on transparency. Use `/svg/` instead of `/img/` when the diagram
  has a lot of small text.
- `&` inside an HTML attribute must be written `&amp;`.
- Set `width` (600-900) so a wide graph doesn't overflow the page.
- Keep each diagram to one idea and under ~15 nodes. Two small diagrams beat one
  unreadable one. Label every node and edge - an unlabeled arrow explains nothing.
- Keep the `.mmd` source alongside the doc so the diagram can be regenerated.

### Text sketches

**Plain-text box-and-arrow sketches are encouraged**, not a fallback. They are
cheap, editable, reviewable in a diff, and they carry most of what a picture
would - especially for showing what each side of a handover owns:

```
PRODUCER  (runs inside the policy, every cycle)
  1. ask the database which items changed
  2. build the artifact, store it
      -> makes ZERO external API calls

                    state table
                         |
                         v

UPLOADER  (its own schedule, every 15 minutes)
  1. ask the table what's built but not sent
  2. send it, write back "sent"
      -> owns ALL external calls, and therefore all rate limiting
```

Use one in the Design Summary alongside the rendered diagram; they do different
jobs, and the sketch is the one you can always write today.

### Tables and code

- Tables are the default idiom: DB column specs, field mappings, Removed/New/
  Renamed/Unchanged field sets, Reuse vs Build, owner → columns, task IDs,
  metrics, trade-off comparisons, risks.
- Code fences with correct language tags (`python`, `graphql`, `sql`, `yaml`,
  `json`, `typescript`).

## Tone

Plain, engineering-direct, and explanatory. Write for an engineer from another
team who often reads English as a second language: Simplified Technical English,
every internal term defined at first use, every component's purpose stated.

First person is fine for design rationale ("In my opinion #1 is not a good
solution because …"), and it already passes STE - it is short, active, and its
subject is named. No marketing language. It's a document another engineer reviews
and then builds from.

Explanatory does not mean soft. STE makes a warning sharper, not milder: a trap
written as a command with its condition first is the clearest sentence in the
document. See `ste.md` → *Traps and warnings*.
