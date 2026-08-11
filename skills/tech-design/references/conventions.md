# Tech Design Conventions

The shape of a design document that gets reviewed quickly and built from
accurately. A design is read once by people who will argue with it, and then
kept as the record of what was decided. Optimize for both.

## Table of Contents
- [Section order](#section-order)
- [Overview table](#overview-table)
- [Write so an outsider understands](#write-so-an-outsider-understands)
- [Writing the Requirements](#writing-the-requirements)
- [Style rules](#style-rules)
- [Writing the Design Summary](#writing-the-design-summary)
- [Weighing alternatives](#weighing-alternatives)
- [End-to-End Flow](#end-to-end-flow)
- [Tasks & Phases](#tasks--phases)
- [Open questions](#open-questions)
- [House patterns](#house-patterns)
- [Diagrams, tables, code](#diagrams-tables-code)
- [Tone](#tone)

## Section order

Canonical order. Drop sections that don't apply - a small design is just
Overview → Requirements → Design Summary → Open questions:

1. `## 📋 Overview` - the metadata table (always)
2. `## 🎯 Requirements` - scope of the change (can grow into a mini-PRD)
3. `## 💻 Technical Overview` - optional; bulleted breakdown by concern, for larger designs
4. `## 🧑‍🎨 Design Summary` - the core, split into themed subsections
5. `## Possible Solutions` - only when comparing options (Option 1 / Option 2 + recommendation)
6. `## 🔄 End-to-End Flow` - runtime walkthrough, when the feature has a non-trivial flow
7. `## ✅ Tasks & Phases` - phased delivery plan, for anything multi-step
8. `## Did Not Address` - explicit scope exclusions (only when useful)
9. `## ❓ Open questions` - unresolved decisions

Emoji headers are the house style here: 📋 Overview, 🎯 Requirements, 💻 Technical
Overview, 🧑‍🎨 Design Summary, 🔄 End-to-End Flow, ✅ Tasks & Phases, ❓ Open
questions. Drop them if the team's existing designs don't use them - match the
corpus you're writing into. Inside the Design Summary, themed emoji subsections
are common: 🗄️ Data Model, ⚙️ core engine/logic, 🔌 API, 🚨 new risks, 🛡️ access
control.

## Overview table

Two-column key/value table. Rows, and only these rows: **Status, Owner,
Contributors, Goals, Prototype, Tickets**. Do not add extra rows - keep it to
these six, and drop a row entirely when it's empty or N/A (no Prototype row for a
non-UI design). Status is one of `NOT STARTED` / `IN PROGRESS` / `DONE`. Goals is
one or two sentences, not a list.

## Write so an outsider understands

Assume the reviewer is a competent engineer from **another team** who has never
opened this code. They must be able to follow the whole design without asking
anyone a question. This is a hard requirement, not a nice-to-have.

- **Plain English, short sentences.** One idea per sentence. Prefer the everyday
  word: "runs after", not "is invoked downstream of". No clever phrasing.
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
- **Say what a thing does, not only where it lives.** Every file path, class,
  table, or service gets a clause explaining its job: "`AlertRunner` (evaluates one
  alert against current data and emits instances)".
- **Explain why before how.** Open each Design Summary subsection with one
  sentence on the problem that piece solves, then the mechanics.
- **Spell out the current behavior you are changing.** A reader who does not know
  today's flow cannot judge the new one. One or two sentences is enough.
- **Diagrams and tables over paragraphs.** They are the fastest way for a stranger
  to get the shape. Label every box and column.
- **Explanatory does not mean long.** Total length stays the same or shrinks:
  glosses and a "why" sentence buy their space back by replacing vague prose,
  hedging, and repeated detail. If a section grows past a screen, cut detail that
  belongs in the PR instead of trimming the explanation.

Quick self-check before finishing: pick three sentences at random. If any needs
insider knowledge the doc never gave, rewrite it. Then confirm there is no
term-definition list anywhere; if one crept in, delete it and fold each definition
into the sentence that first uses the term.

## Writing the Requirements

Requirements is the "what and why". In the best designs it reads as a mini-PRD,
not a terse bullet list. Scale it to the size of the change:

- **Open with a short prose framing.** One or two sentences stating what the
  change does and for whom, with the key domain terms **bolded** mid-sentence.
  Terms the rest of the doc leans on get defined here only if they appear here,
  and only inline in the framing sentence. Not as a definitions list.
- **Then a numbered `Scope` list** - each item one concrete capability the design
  must deliver, product-facing, with a nested sub-bullet per case where needed.
- **Optionally a "Tech approach (high level)" bullet block** - 3-5 bullets naming
  the mechanism you're building on, so a reviewer sees the shape before the detail.

For larger designs, nest PRD-style subsections under Requirements, using only the
ones that apply: `Background`, `Problem Statement`, `Proposed Solution`,
`Extendibility`, `Monitoring & Alerts`, `Potential Side Effects`.

Keep requirements outcome-shaped: what the user or system gets, not how every
piece is built. Implementation constraints and test-design details belong in the
Design Summary.

## Style rules

- **No revision history or meta-narrative.** The doc describes the current design
  only. Never write "changed from vN" or "the previous version did X", and don't
  keep Did-Not-Address bullets whose only purpose is referencing a dropped earlier
  direction. Dead alternatives simply disappear.
- **No self-justification about the doc's evolution.** Don't sell "why this beats
  the approach we're replacing". This is different from - and must not be confused
  with - the encouraged inline **Why X?** blocks (see Design Summary): a short
  technical justification for a non-obvious *component choice* is good and
  expected.
- **Short headings, no parentheticals.** "Mock service in the web app", not "The
  mock - WireMock service in the web app (mirror of the auth mock)". Cut
  qualifiers like "(non-product)".
- **No infra minutiae.** Image versions, port numbers, CLI flags, and volume
  mounts belong in the PR, not the design. Name the service and the file it lives
  in; one line.
- **One heading level per depth.** The Design Summary may use themed `##`/`###`
  subsections and numbered components, but don't stack a fourth level - sub-parts
  of a component get **bold run-in labels** as their own paragraph, not `####`.
- **Phases list deliverables only.** No "verify by hand: …" walkthrough bullets
  and no narration bullets ("Submit. Then …") - every phase bullet is a
  deliverable, a Definition-of-Done condition, or a concrete task.
- **Never use em dashes (`—`)** anywhere in the doc - headings, bullets, or body
  prose. Only the regular dash `-`.

## Writing the Design Summary

The core. Organize it into **themed subsections** (emoji `##`/`###`: 🗄️ Data
Model, ⚙️ the core engine, 🔌 API) or **numbered components** ("### 1. REST
Endpoint - `POST /exports/{format}`"). Don't write it as one flat prose blob.

For each component or subsection, pull in what it needs:

- **Location.** The exact directory or file the component lives in.
- **"Reuses:" list.** Name the existing utilities, models, services, and hooks the
  component builds on. Reusing existing code over building new is a first-class
  value in review - make it visible. A **Reuse vs Build** two-column table is the
  idiom when a change spans many pieces.
- **DB tables** as a Column / Type / Null / Notes spec table, plus constraints and
  indexes as bullets. Say **which** database, explicitly, when the system has more
  than one. Real model classes are fine too when precision helps.
- **Schema changes to an existing table** as separate **Removed / New / Renamed /
  Unchanged** field tables.
- **UI features** as a field-mapping table per page or table: "UI column → backend
  source", with a source legend.
- **API** as real queries, mutations, or REST endpoints (`POST /path/{param}` with
  a field table). For a schema change, show **old query vs new query** as two code
  blocks with `# will be deprecated` / `# new-field` comments.
- **Config** as real JSON or YAML blocks.
- **Inline "Why X?" blocks** - a bolded mini-header (**Why a queue here?**)
  followed by a short technical justification, whenever a component choice is
  non-obvious. Encouraged.

Prefer concrete code, file paths, and tables over prose. A reviewer should be able
to map each line to a diff.

## Weighing alternatives

When more than one approach is real, enumerate them:

```
#### Option 1 - <name>
<one-line description>
Pros:
* ...
Cons:
* ...

#### Option 2 - <name>
...
```

Close with an explicit first-person recommendation: **"In my opinion, Option 1 is
better and recommended because …"** (simpler, less maintenance, faster to ship).
For performance-sensitive designs, back the choice with a metrics table and a
per-approach estimate of the critical path.

## End-to-End Flow

For a change with a non-trivial runtime path, add a `## 🔄 End-to-End Flow`
section near the end, before Open questions: a **numbered walkthrough** of one
full run - what the user does, then what each system does in order, ending with an
**End state** paragraph describing the observable result. Inline the concrete
records and values produced at each step.

This is the narrative complement to the structural Design Summary.

## Tasks & Phases

For anything multi-step, add `## ✅ Tasks & Phases`. Each phase gets:

- **Definition of Done** - bullets stating the observable end conditions.
- **Tasks** - a numbered list of concrete work items.
- **Tasks Dependencies** - the ordering as arrows: `1 → 2 → [3,4,5] → 6`
  (brackets mean parallelizable).

For migration and rollout designs, interleave explicit deploy steps between phases
wherever a deploy has to land before the next step is safe. Make them their own
line, in caps, so nobody reorders them by accident.

When tickets exist, render the breakdown as a checkbox list with each task linked
to its ticket, grouped by the teams that own them.

## Open questions

`## ❓ Open questions` holds concrete unresolved tensions, not vague "TBDs". Each
bullet names the decision and its options or tradeoff. Tag decisions owned by
someone outside engineering *(product)*, *(design)*, *(legal)*. Keep resolved ones
in place, struck through with a short "✅ resolved (reason)", so the review history
stays readable.

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

Patterns that are near-universal and worth addressing even with no house file:

- **Where the data lives**, and how it stays isolated between customers or
  environments.
- **Migration**: what has to run, in what order, and whether it's reversible.
- **Backward compatibility** for anything already being read. The standard move
  for reshaping a hot table is to build the new one, expose it through a view with
  the old shape so readers are untouched, dual-write, switch reads, then drop the
  old columns:
  ```
  UI V1 → API V1 → back-compat view (V2→V1) → Table V2 ← Writer V2
  ```
- **Rollout and rollback**: the flag that gates it, and what happens when it's off.
- **Observability**: the metric, log, or alert that tells you it's working.
- **Access control** on any new API or data path.

## Diagrams, tables, code

**Use rendered Mermaid diagrams** for anything with real structure: pipelines,
request flow across services, state machines, call sequences, table lineage, phase
dependencies. A picture is the fastest way for a reader from another team to get
the shape.

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
- **ASCII diagrams stay** for small inline shapes where a rendered image is
  overkill (a 3-step arrow chain, a step-evolution line).
- Tables are the default idiom: DB column specs, field mappings, Removed/New/
  Renamed field sets, Reuse vs Build, task IDs, metrics, trade-off comparisons.
- Code fences with correct language tags (`python`, `graphql`, `sql`, `yaml`,
  `json`, `typescript`).

## Tone

Plain, engineering-direct, and explanatory. Write for an engineer from another
team: simple English, jargon defined on first use, every component's purpose
stated. First person is fine for design rationale ("In my opinion #1 is not a good
solution because …"). No marketing language. It's a document another engineer
reviews and then builds from.
