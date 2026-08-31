# The section catalog

The canonical order is in `conventions.md`. It is a starting point, not a form.
**A design with five sections that all say something beats twelve where seven say
"N/A".**

Each entry below has: what the section is for, when it earns its place, what good
looks like, what to ask before writing it, and how it usually goes wrong.

Every section is written in Simplified Technical English - see `ste.md`. The rules
that shape these sections most: one idea per sentence, so a set of related facts
becomes a table; active voice with the actor named, which is why ownership is
stated as "only the uploader writes `sent_at`"; and one word for one meaning across
all of them.

## Quick reference

| Section | Include when |
|---|---|
| 📋 Overview | Always |
| 🎯 Requirements | Always - framing, the problem, scope, goals, non-goals. No phase headers |
| 🏛️ Current Architecture | Something already exists that this changes |
| 💻 Technical Overview | Larger designs, as a breakdown by concern |
| 🧑‍🎨 Design Summary - the fixed menu | Always |
| ├ 🗄️ Data model | The design adds or changes tables |
| ├ 🔌 API | The design adds or changes an API surface |
| ├ ⚙️ Core engine behavior | There is a rule, automation, or engine - with its lifecycle table |
| ├ 🛡️ Access control | ⚠️ New data, new surface, new auth path, or a boundary crossed |
| ├ ⚡ Performance | A path with a real load, latency, or volume question |
| ├ 🔍 Filtering & query surfaces | Users or systems search, filter, or list the new data |
| └ 🚚 Migration & backfill | ⚠️ Existing data, traffic, or clients must move |
| Possible Solutions | More than one credible approach existed |
| 🖥️ Frontend | The change has a UI - carries the end-to-end user flow |
| 🔄 End-to-End Flow | The backend runtime path is non-trivial |
| 🚦 Rollout & Rollback | ⚠️ It reaches production |
| 🧪 Testing Strategy | Correctness is hard to eyeball, or it spans services |
| 📊 Monitoring & Observability | It runs in production |
| 💰 Cost | ⚠️ New infrastructure, per-unit cost drivers, or vendor spend |
| ✅ Tasks & Phases | Anything multi-step. Phasing lives here and only here |
| Did Not Address | Explicit scope exclusions worth naming |
| ⚠️ Risks | Anything with real downside |
| 🔗 References | There is prior art, a ticket, or an incident to point at |
| ❓ Open questions | Always, and always the last section |

⚠️ = **skipping requires a one-line reason in the doc.** "No new infrastructure,
so no cost change" is a fine line. Silence is not - silence reads as "not
considered", and that is the reviewer's first question.

**The menu is fixed on purpose.** A reader who has seen one design from this
skill finds the data model, the API, and the migration story in the same place in
the next one. Drop a slot that does not apply; never reorder the slots, and never
invent a new slot when the content fits an existing one.

**Slot length follows complexity, not importance.** A straightforward mechanism
gets one paragraph, even when it is user-facing. A subtle mechanism gets the
space. Never pad a simple slot to look thorough.

## Table of Contents
- [📋 Overview](#-overview)
- [🎯 Requirements](#-requirements)
- [🏛️ Current Architecture](#️-current-architecture)
- [💻 Technical Overview](#-technical-overview)
- [🧑‍🎨 Design Summary and its fixed menu](#-design-summary)
- [One subsection per new component](#one-subsection-per-new-component)
- [Possible Solutions](#possible-solutions)
- [🖥️ Frontend](#️-frontend)
- [🔄 End-to-End Flow](#-end-to-end-flow)
- [🚚 Migration & Backfill](#-migration--backfill-️)
- [🚦 Rollout & Rollback](#-rollout--rollback-️)
- [🧪 Testing Strategy](#-testing-strategy)
- [📊 Monitoring & Observability](#-monitoring--observability)
- [🛡️ Security & Access](#️-security--access-️)
- [💰 Cost](#-cost-️)
- [✅ Tasks & Phases](#-tasks--phases)
- [⚠️ Risks and ❓ Open questions](#️-risks-and--open-questions)
- [🔗 References](#-references)

---

## 📋 Overview

**For:** letting someone decide in five seconds whether to read the rest.

Two-column key/value table. Rows, and only these rows: **Status, Owner,
Contributors, Goals, Prototype, Tickets**. Do not add extra rows, and drop a row
entirely when it's empty or N/A (no Prototype row for a non-UI design). Status is
one of `NOT STARTED` / `IN PROGRESS` / `DONE`. Goals is one or two sentences, not
a list.

**Ask:** who owns this, who's contributing, is there a ticket or epic yet?

**Goes wrong:** left half-empty because it's "just admin". An owner-less design
gets no decision made about it.

---

## 🎯 Requirements

**For:** the "what and why", and agreement on it before anyone argues about the
fix. In the best designs it reads as a mini-PRD, not a terse bullet list. Scale it
to the size of the change.

**Contains, in this order:**

**1. A short prose framing.** One or two sentences stating what the change does
and for whom, with the key domain terms **bolded** mid-sentence. Terms the rest of
the doc leans on get defined here only if they appear here, and only inline in the
framing sentence. Never as a definitions list.

**2. The problem** - from Phase 4:

```
Today:          what happens now, in ordinary words
The gap:        what should happen and doesn't
Why it matters: who is hurt, how often, how badly, what it costs
Scale:          numbers
Evidence:       links - incidents, dashboards, tickets, the actual log line
```

**No solution words. Not one.** The moment "because we don't have a cache"
appears, this has stopped describing a problem and started defending an answer. If
a reviewer disagrees with the problem, everything downstream is wasted, so keep it
arguable on its own terms.

**3. A numbered `Scope` list** - each item one concrete capability the design must
deliver, product-facing, with a nested sub-bullet per case where needed.

**Requirements describe what ships now, with no phase headers.** Phasing is a
delivery detail; it lives in Tasks & Phases and nowhere else. Do not organize the
Scope list or the goals around "phase 1 / phase 2" - a reviewer arguing about
requirements should not have to argue about sequencing at the same time. Mention
a future extension in one sentence, in the place where it justifies a design
choice ("the table keeps a `kind` column so alert rules can join later"), and
nowhere else.

**Respect explicit scope statements.** When the user narrows the scope ("only
manual policies migrate"), the doc says so plainly - in the Scope list or as a
non-goal - and describes no work outside it. A doc that quietly designs beyond a
stated boundary reads as not having listened.

**4. Goals and Non-Goals.** Tests for both are in `SKILL.md` Phase 5. Group goals
as reviewers read them: functional, operational (latency, reliability, cost),
security, explicit SLA/SLO commitments. Every non-goal is labelled *not now* (with
the trigger) / *not ever* (with the reason) / *someone else's* (with who).

**5. Optionally a "Tech approach (high level)" bullet block** - 3-5 bullets naming
the mechanism you're building on, so a reviewer sees the shape before the detail.

For larger designs, nest PRD-style subsections here, using only the ones that
apply: `Background`, `Problem Statement`, `Proposed Solution`, `Extendibility`,
`Monitoring & Alerts`, `Potential Side Effects`.

Keep requirements outcome-shaped: what the user or system gets, not how every
piece is built. Implementation constraints and test-design details belong in the
Design Summary.

**Ask:** how often, how many, since when, what's the evidence, what happens if we
do nothing.

**Goes wrong, three ways:** the problem stated as the absence of the solution
("the problem is we have no rate limiting" is a missing feature, not a problem -
the problem is what goes wrong because of it, to whom); goals no design could fail
("should be maintainable") - delete them; and non-goals nobody would have assumed,
which pad the list and bury the two that matter.

---

## 🏛️ Current Architecture

**Include when:** anything already exists that this design changes. Skip only for
genuine greenfield, and then replace it with two paragraphs on where this will sit
and what it will touch.

**Contains:** main components one line each; the data flow (what calls what, what
reads and writes where); known limits and bottlenecks with numbers; links to
repos, runbooks, dashboards. This is Phase 1's surface map, written up.

**Say which parts you read and which you were told.** A current-architecture
section built from someone's memory of the system is the most quietly wrong part
of most design docs. Diagram rules in `conventions.md` - never render one from
inference.

**Ask:** is anything here out of date? What did I miss?

**Goes wrong:** describes the system as designed rather than as running. The gap
between the two is usually where the problem lives.

---

## 💻 Technical Overview

**Include when:** the design is large enough that a reviewer wants the shape by
concern before the detail. A bulleted breakdown: data storage, processing, API,
access. Delete it when the Design Summary already covers it - two summaries of
the same thing is worse than one.

---

## 🧑‍🎨 Design Summary

**For:** getting the whole idea into the reader's head before any one part is
detailed. The core section.

It opens **high level**: it names the new pieces and shows how work moves between
them. It does not contain a schema, a query, or a payload - those live in the
per-component subsections that follow.

**Contains, in this order:**

**1. What we are going to do.** Two or three paragraphs in ordinary words, from
the approach picked in Phase 6. What changes, what's new, what goes away.

**2. The pieces, one line each.** A list, not a description: `The state table -
one row per commit; the handover point between the two processes.`

**3. A sketch of the flow.** A rendered Mermaid diagram for a flow you designed
(recipe in `conventions.md`), or a plain-text box-and-arrow block, which is cheap,
editable, and reviewable in a diff:

```
PRODUCER  (runs inside the policy, every cycle)
  1. ask the database which items changed
  2. build the artifact, store it
  3. write a row saying "this is what should exist downstream"
      -> makes ZERO external API calls

                      state table
                           |
                           v

UPLOADER  (its own schedule, every 15 minutes)
  1. ask the table what's built but not sent
  2. send it
  3. write back "sent"
      -> owns ALL external calls, and therefore all rate limiting
```

**4. Why it's split this way.** A short list of what the structure buys, one line
each: what stops being a problem, what becomes ordinary, what becomes visible.

**5. Then the fixed menu of subsections**, in this order, dropping the ones that
do not apply:

**🗄️ Data model.** Name each table and say what it means - one sentence of
meaning per table, then only the columns that carry a decision (the state column
the engine reads, the foreign key that fixes ownership, the timestamp that drives
the schedule). Say **which** database when the system has more than one. **Omit
indexes, primary-key mechanics, and constraint internals - they belong in the PR,
not the design.** A constraint earns a line only when it enforces an invariant
the design depends on ("one active rule per tenant - a uniqueness rule enforces
this"). Schema changes to an existing table go as **Removed / New / Renamed /
Unchanged** field tables.

**🔌 API.** The real mutations, queries, or endpoints as short code blocks, not
prose descriptions of them. A reviewer reads `POST /exports/{format}` with a
five-line body faster than a paragraph about it. For a schema change, show **old
query vs new query** as two code blocks with `# will be deprecated` /
`# new-field` comments.

**⚙️ Core engine behavior.** What the rule, automation, or engine does, and the
lifecycle table (below). This is where the six-part component template earns its
keep.

**🛡️ Access control.** Who can reach the new surface and which mechanism
enforces it. One paragraph when the answer is "the existing permission model,
unchanged" - see Security & Access below for when it grows.

**⚡ Performance.** Only for a path with a real load, latency, or volume
question, and with numbers. Skip silently when there is none - this slot is not
⚠️-guarded.

**🔍 Filtering & query surfaces.** How users or systems search, filter, sort, and
list the new data - the surfaces, not the index strategy behind them.

**🚚 Migration & backfill.** ⚠️ What happens to the rows that already exist - see
the Migration & Backfill entry below.

New components slot into the menu entry they belong to: a state table under Data
model, a job under Core engine behavior. A component big enough for its own
numbered subsection (see below) still lives inside its slot.

House idioms, wherever they fit:

- **Location.** The exact directory or file the component lives in.
- **"Reuses:" list.** The existing utilities, models, services, and hooks it
  builds on. Reusing existing code over building new is a first-class value in
  review - make it visible. A **Reuse vs Build** two-column table is the idiom
  when a change spans many pieces.
- **Config** as real JSON or YAML blocks.

**The lifecycle table.** For any rule, automation, or engine, enumerate the
lifecycle edge cases as an action → effect table - it beats prose here, and it is
the part readers actually argue about. Keep it short:

| Action | Effect |
|---|---|
| Rule created | ... |
| Rule edited | What happens to work already produced by the old version? |
| Rule disabled | Does existing output stay, close, or freeze? |
| Rule deleted | ... |
| Manual override | Does the engine respect it, revert it, or skip the item? |

**What good looks like:** someone reads only the high-level part of this section
and can argue with the design. If they'd need the schema to disagree, it's too
thin.

**Goes wrong:** it jumps straight to the schema. The reader then has to infer the
architecture from a `CREATE TABLE`, which they will do incorrectly.

---

## One subsection per new component

**Include when:** the design introduces new pieces, which is most designs. One
subsection each, numbered, inside the menu slot the component belongs to - a
state table under 🗄️ Data model, a job under ⚙️ Core engine behavior. **Never
describe two components in one subsection:** the reviewer has to hold both in
their head to check either.

A component is anything with its own responsibility and its own failure mode. A
table. A store. A job. A service. A queue. A new API surface.

**The template - six things, in this order:**

```markdown
### <N>. <Component name> - `POST /exports/{format}`

<One or two sentences: what it is and what job it does in the system.>

**Why it exists.** <What breaks without it. One short paragraph.>

**Why this way, and not <the local alternative>.** <The design choice inside this
piece, and the reason. Not the global approach - that's Possible Solutions. This
is "why a table and not a status column", "why store the file and not rebuild it",
"why this runs in Postgres not Iceberg".>

**What it owns.** <The data, decisions, or calls only this piece makes - and,
explicitly, what it does not own. A table of which writer owns which columns, or
which process makes which external calls.>

**The detail.** <The substance. Location, Reuses list, schema with comments, the
query, the key layout, the contract, the config. This is where jargon earns its
place.>

**How it fails.** <Errors, retries, ordering constraints, what a crash halfway
through leaves behind. If two orderings are possible, say which one is correct and
what the wrong one does.>

**Traps.** <The specific way an implementer gets this wrong. Usually the thing you
only saw because you thought it through properly. Write it as an STE warning:
start with the command, put the condition before the instruction, one instruction
per sentence, and say what happens if the reader gets it wrong. See `ste.md`.>
```

Not every component needs all six as separate labels - a small one might be four
short paragraphs. But **"Why this way" and "Traps" are never optional.** Without
them the subsection is a schema dump, and the next person to touch it breaks an
invariant nobody wrote down.

Use **bold run-in labels** as their own paragraph rather than a fourth heading
level - see *Style rules* in `conventions.md`.

**What good looks like** - the moves that make these subsections worth reading:

| Move | Example of it |
|---|---|
| Name the trick | "The two hashes are the whole trick", then a two-row table explaining each and the one-line question each process asks. |
| Single writer per field | A table of owner → columns, plus "neither process ever writes the other's columns", plus what goes wrong if one does. Active voice does the work here: "only the uploader writes `sent_at`" names the actor that a passive sentence would hide. |
| Say why *not* the obvious thing | "Why not just a payload column on the table" - because that table is joined against 121,000 rows every run and has to stay narrow. |
| Make ordering explicit | A two-row table: *store first, then row* → self-healing; *row first, then store* → permanently stuck. |
| Record the accepted downside | "The staleness window - a trade-off we are accepting." It self-heals, but it's real, and it didn't exist before. |
| Show the termination | A four-row table walking the state machine to a stop, proving the loop can't repeat forever. |
| Point at prior art | "Copy `issue_tracker_sync` - it runs `*/15` with per-tenant tasks and is exactly this shape of job." With the file path. |
| Leave a decision open, on purpose | "Either drop the batch to ~200 or add a shared token bucket - decide when implementing." Better than a fake answer. |
| Inline **Why X?** block | A bolded mini-header (**Why a queue here?**) plus a short technical justification, whenever a component choice is non-obvious. |

**Ask, per component:** what's already decided here versus still open? What must
this stay compatible with? What would a reviewer challenge?

**Goes wrong, three ways:** a schema with no reasoning; a component whose failure
behaviour is "we'll retry"; and two components merged into one subsection because
they arrived at the same time.

---

## Possible Solutions

**Include when:** more than one credible approach existed, which is nearly always.
Skip only if you can state in one line why there was genuinely one way.

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

For an approach that was rejected rather than weighed, one block each:

```
Approach: <plain name>
What it would have done: <2-3 sentences>
Why not: <the specific reason - cost, risk, time, a constraint it violates>
Would reconsider if: <what would change the answer>
```

**"Would reconsider if" is the line that pays off.** It turns a rejection into a
decision with a shelf life.

**What good looks like:** each rejected option is one a reasonable person could
have picked. If they all have obvious fatal flaws, you wrote them to lose and the
reviewer can tell.

**Goes wrong:** written after the fact to justify a decision already made. It
reads differently and it damages the rest of the doc.

---

## 🖥️ Frontend

**Include when:** the change has a UI. A separate top-level section, after the
Design Summary - frontend work reviewed as an afterthought inside a backend
subsection gets afterthought review.

**Contains:**

- **The end-to-end user flow**, numbered, screen by screen: what the user sees,
  what they do, what each action calls, and what changes on screen as a result.
  This is the frontend counterpart of the backend End-to-End Flow section.
- **Field-mapping tables** per page or table: "UI column → backend source", with
  a source legend.
- The states that are easy to forget: empty, loading, error, and permission-
  denied.
- New components or pages, one line each, with where they live and what they
  reuse.

**When a prototype exists** (Figma, a spike branch), the flow follows the
prototype, and every capability visible in it - extra columns, bulk actions,
validation rules, cross-navigation - appears here or is named as out of scope.
The diff against the prototype is part of the pre-handover review; see
`review.md`.

**Ask:** is there a prototype or mock? Which existing components does this build
from? What does the user see while the backend works?

**Goes wrong:** describes the happy-path screen and none of the states around it;
or restates the prototype in prose instead of adding what the prototype cannot
show - sources, permissions, and error behavior.

---

## 🔄 End-to-End Flow

**Include when:** the runtime path is non-trivial. Goes near the end, before Open
questions. This is the narrative complement to the structural Design Summary, and
it is **the most-read part of most design docs.**

A **numbered walkthrough of one full run** - what the user does, then what each
system does in order, with the concrete records and values produced at each step
inlined. Ends with an **End state** paragraph describing the observable result.

Then the variations, each a short labelled block:

- **Nothing changed since last time.** Should usually be: almost nothing happens.
  If a quiet run is expensive, the design has a problem.
- **The item changed.**
- **The item went away entirely.** Who closes, deletes, or cleans up?
- **A dependency rejected us or was down.**
- **The process died halfway through.** What does a rerun do?

**If a variation can't be narrated, the design is missing something.** Go and fix
the design, not the sentence. Full sweep in `review.md`.

---

## 🚚 Migration & Backfill ⚠️

**Include when:** existing data, existing traffic, or existing clients have to
move. Anything that adds a field, a state, or a rule to something that already has
rows. It is the last slot of the Design Summary menu; promote it to its own
top-level section only when the migration is staged enough that a reviewer would
scroll to find it.

**Contains:**

- What existing data looks like, and how much of it there is
- The choice, made out loud: **backfill / default / migrate lazily / leave old
  rows exempt**
- How long the backfill takes, and what load it puts on what
- The period where both old and new exist - what reads which
- Whether the change is backward compatible, and for how long the old path stays
- How to stop halfway and be in a valid state

The standard move for reshaping a hot table is to build the new one, expose it
through a view with the old shape so readers are untouched, dual-write, switch
reads, then drop the old columns:

```
UI V1 → API V1 → back-compat view (V2→V1) → Table V2 ← Writer V2
```

**Ask:** how many existing rows? Can old and new coexist, or is there a cutover?
Who's still on the old path, and do they know? Is the migration reversible?

**Goes wrong:** the design is correct for new data and undefined for the millions
of rows that already exist. This is the single most common way a reviewed design
fails in production.

---

## 🚦 Rollout & Rollback ⚠️

**Include when:** it reaches production. Skip for a spike or prototype doc, and
say so.

**Contains:**

- Stages: environments, regions, tenant cohorts, with ranged estimates
- The feature flag or toggle - what it controls, its default, who flips it, and
  what happens when it's off
- Gradual exposure: canary, percentage, internal-first
- **Rollback** - what the button is, how long it takes, and what becomes
  unrecoverable once it has shipped. If there is no rollback, say that in bold; it
  changes the risk level
- Who needs to know, and when

**Ask:** who can turn it off, and how fast? Is there anything here that can't be
undone?

**Goes wrong:** "deploy to staging, then prod", which is not a plan, it's the
definition of deploying. And the rollback line says "revert the PR" for a change
that has already written data.

---

## 🧪 Testing Strategy

**Include when:** correctness is hard to eyeball, the change spans services, or
there's a data migration involved. Skip when ordinary unit tests plainly cover it.

**Contains:** what's covered by unit versus integration versus manual; what you'll
test against real data and how you'll get it; what you deliberately won't test and
why; how you'll know it works in production, not just in CI.

**Ask:** is there existing test infrastructure for this path? Can we test against
a copy of real data?

**Goes wrong:** lists test types rather than what would actually catch this design
being wrong.

---

## 📊 Monitoring & Observability

**Include when:** it runs in production.

**Contains:** the few metrics that matter, each tied to an operational goal; what
gets logged, where, and for how long; the alerts - **only the ones someone should
be woken for**, because an alert nobody acts on trains people to ignore alerts;
how you'd detect customer impact specifically as opposed to system health; the
dashboard and runbook.

**What good looks like:** for each operational goal from Requirements, one line
saying which metric proves it. A goal with no metric is not going to be checked.

**Ask:** who's on call for this? Is there an existing dashboard to extend rather
than a new one to build?

**Goes wrong:** ten metrics and no answer to "how would we know a customer is
affected?"

---

## 🛡️ Security & Access ⚠️

**Include when:** new data is stored, a new external surface appears, an auth path
changes, credentials or secrets are involved, or data crosses a trust boundary.
Its home is the 🛡️ Access control slot of the Design Summary menu; promote it to
its own top-level section when there is this much to say.

**Contains:** what new data is stored or moved and how sensitive it is; who can
reach the new surface and how they're authenticated and authorised; data at rest
and in transit; where secrets live and how they rotate; tenant isolation, if the
system is multi-tenant - **the specific mechanism, not the intent**; what an
attacker would go for here and what stops them; audit and logging requirements.

**Ask:** does this touch customer data? Does it cross a tenant boundary? Any
compliance requirement in play?

**Goes wrong:** asserts a property ("data is isolated per tenant") without saying
which mechanism enforces it. Named mechanisms can be reviewed; intentions cannot.

---

## 💰 Cost ⚠️

**Include when:** new infrastructure, a per-event or per-tenant cost driver, or
third-party spend. Skip with a one-line reason when it's code on machines you're
already paying for.

**Contains:** new infrastructure costs; what drives cost as things grow (per
event, per tenant, per GB); the worst case - what the bill looks like at 10x
volume or if something retries in a loop; guardrails (limits, budgets, rate caps,
spend alerts); the expected delta against today.

**Ask:** what's the biggest tenant, and what's the growth expectation? Is there a
spend alert on this account already?

**Goes wrong:** costs the steady state and not the failure mode. The expensive
scenario is almost always a retry storm or an unbounded fan-out, not normal
traffic.

---

## ✅ Tasks & Phases

**Include when:** anything multi-step. Each phase gets:

- **Definition of Done** - bullets stating the observable end conditions.
- **Tasks** - a numbered list of concrete work items.
- **Tasks Dependencies** - the ordering as arrows: `1 → 2 → [3,4,5] → 6`
  (brackets mean parallelizable).

For migration and rollout designs, interleave explicit deploy steps between phases
wherever a deploy has to land before the next step is safe. Make them their own
line, in caps, so nobody reorders them by accident.

When tickets exist, render the breakdown as a checkbox list with each task linked
to its ticket, grouped by the teams that own them.

**Phases list deliverables only.** No "verify by hand: …" walkthrough bullets and
no narration bullets ("Submit. Then …") - every phase bullet is a deliverable, a
Definition-of-Done condition, or a concrete task.

Two ordering rules that are easy to get wrong:

- **The first phase is the riskiest unknown, not the easiest setup.** The wrong
  order is scaffolding first, hard part last, discovering on day three that the
  hard part doesn't work.
- **Every "must handle" case from the sweep in `review.md` appears in some phase's
  Definition of Done.** A case that isn't in a done condition isn't handled, it's
  remembered.

**Goes wrong:** estimates with no range, and a phase whose done condition is "the
code is written".

---

## ⚠️ Risks and ❓ Open questions

**For:** showing the reviewer that you know where the soft ground is. Always
included, always short.

**Risks** - the top three technical risks. Three, not eleven; a list of eleven is
a way of not prioritising. Operational, security and product risks if they're
real. A mitigation for each:

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|

**Open questions** hold concrete unresolved tensions, not vague "TBDs". Each names
the decision and its options or tradeoff, and each gets an **owner** and **what it
blocks**:

| Question | Owner | Blocks |
|---|---|---|

Tag decisions owned by someone outside engineering *(product)*, *(design)*,
*(legal)*.

**Open questions are a running record, not a snapshot.** Keep every question ever
raised, including across doc updates. A resolved one is never deleted: strike it
through and attach its resolution in place ("~~Batch size?~~ ✅ resolved - 200,
matches the provider rate limit"). The review history then shows what was already
addressed, and nobody re-raises a settled question in the next review round. The
section is always the **last** one in the doc, so reviewers know where the live
end of the conversation is.

**Build this list as you go, from Phase 1.** Reconstructed at the end it contains
the ones you remember and none of the ones you quietly assumed away.

**Goes wrong:** risks written to be survivable so the doc looks safe. A doc with
no scary risk in it has either a trivial design or an author who hasn't looked
hard enough, and reviewers read it the second way.

---

## 🔗 References

Related design docs, tickets and epics, incidents and postmortems, external specs,
the prior art found in Phase 1.

**Include what you read and rejected**, not just what you used. It stops the next
person repeating the search.
