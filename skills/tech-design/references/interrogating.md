# Interrogating the request

Three things here: how to run the glossary pass, what to ask in each round, and
how to chase a fuzzy word.

The governing idea: **a question costs thirty seconds, a wrong assumption costs a
review meeting and a rewrite.** A design skill asks more than most on purpose.
What it must not do is ask lazily - questions the code already answered, questions
with the same answer as the last one, or questions with no default attached.

## Table of Contents
- [The glossary pass](#the-glossary-pass)
- [Terms that hide differences](#terms-that-hide-differences)
- [The rounds](#the-rounds)
- [Chasing fuzzy words](#chasing-fuzzy-words)
- [Question hygiene](#question-hygiene)

## The glossary pass

Run it in Phase 2, before any other question.

Take the request exactly as it arrived - the ticket, the sentence, the Slack
thread. Pull out every noun and every phrase that carries meaning, **including
the ones you feel you understand.** The dangerous terms are not the strange ones.
They are the ordinary-sounding ones that mean something specific here: "the
pipeline", "an asset", "sync", "the agent", "a finding", "onboarding".

For each, write a row:

```
term                 | status  | my definition
"tenant"             | known   | one customer org, models/tenant.py:14
"the sync path"      | assumed | the nightly job that pulls from the provider API
"near real-time"     | unknown | -
```

| Status | Means | What you do |
|---|---|---|
| **known** | Found it in the code or docs. Cite where. | Nothing. |
| **assumed** | You have a definition; nobody confirmed it. | Confirm before it reaches the doc. |
| **unknown** | You do not know what it refers to. | Ask. Never write it. |

**Show the whole table, including the `known` rows.** Two reasons: the user can
correct a `known` you got wrong, which is the most expensive kind, and it
demonstrates you read the code rather than skimmed the ticket.

**The table is a conversation artifact, not a document section.** It never gets
pasted into the design - see *Write so an outsider understands* in
`conventions.md`. What it produces is the inline gloss for each term in the
sentence that first uses it, and the confidence that the gloss is right. A doc
that opens with a definitions list makes the reader memorise a vocabulary before
the design starts; a doc built on this pass defines each term exactly once, where
it is needed.

## Terms that hide differences

Some words are understood by everyone, and by everyone differently. When one
shows up, don't ask "what does X mean?" - ask the question that separates the
readings:

| Term | The question that separates it |
|---|---|
| "user" | An end user, an admin, a service account, or a customer org? |
| "real-time" | Within a second, a minute, or "not overnight"? |
| "the API" | Which one - public, internal, or the provider's? |
| "sync" | Pull, push, or both? Full or incremental? |
| "event" | Something the system emits, or something it receives? |
| "job" | Scheduled, triggered, or on demand? |
| "cache" | For speed, cost, or availability? They lead to different designs. |
| "tenant" / "org" / "account" | Three names for one thing, or three things? |
| "the table" | Which database? Which engine? |
| "we" | Which team owns this after it ships? |

That last one matters more than it looks. "We'll handle retries" is not a design
decision until you know who "we" is.

## The rounds

Each question carries two things attached to it:

- **Why I'm asking** - one clause. It lets the user answer the real question
  instead of the literal one.
- **What I'll assume if you don't answer** - so no round can block. If the user
  skips it, the assumption goes into the doc in bold.

In Quick lane, collapse all of this into one batch of three to five questions:
the unknown terms, the deadline, and what "done" looks like.

### Round 1 - Gates and glossary

These change what the whole doc looks like, so they go first.

- Who reviews this, and what will they push back on? *(A doc for a staff engineer
  and a doc for a VP are different documents.)*
- Is there a deadline, or a reason this is being designed now rather than later?
- Is the approach already decided, or is this genuinely open? *(If it's decided,
  say so - the doc's job becomes justifying and de-risking, not choosing.)*
- Every `unknown` term from the glossary pass.
- If the system isn't in this repo: where is it?

**Ask the question that saves the most time:** *"What would make this document a
waste of everyone's time?"* People answer that one honestly, and it surfaces the
real constraint faster than any polite version.

### Round 2 - The problem

Feeds Phase 4 and the Problem part of Requirements.

- How often does this happen, and how many are affected? *(Numbers, not "a lot".)*
- Since when? Did it get worse, or has it always been like this?
- What's the evidence - an incident, a dashboard, a ticket, a customer complaint?
  Can I see it?
- Who feels it: customers, the platform, on-call, another team?
- **What happens if we do nothing for six months?** *(If the answer is "nothing
  much", that belongs in the doc. It changes the risk level and it's honest.)*
- Has anyone tried to fix this before? What happened?

### Round 3 - Boundaries

Feeds Goals and Non-Goals.

- What must this not change? Which behaviours, contracts, or interfaces are
  load-bearing for someone else?
- What are we explicitly not doing in this iteration?
- Hard constraints: how many people, how long, what tech is mandatory, what tech
  is off the table?
- Any SLA or SLO this must meet, or must not break?
- What's the tolerance for downtime during the change?
- Compliance, data residency, or audit requirements in play?

For every constraint that appears, ask the follow-up: **"who decided that, and can
it change?"** A surprising share of constraints in design docs are preferences
that were never re-examined. Knowing which are real is half the design space.

### Round 4 - Shape of the solution

Feeds Phase 6 and the Design Summary.

- What must this fit alongside - existing services, jobs, schemas, clients?
- Volume today, and what growth do you expect? *(Designs die at 10x, not 1.1x.)*
- How fast does it need to be, and what happens to the user if it's slower?
- Who operates this after it ships? Who gets paged?
- Is there existing data that has to keep working, or move?
- Are there external clients or integrations that would notice a change?

### Round 5+ - Per section

Asked inside Phase 8 as each section is written. The per-section question lists
are in `sections.md`.

## Chasing fuzzy words

Every one of these is a number, a behaviour, or a boundary that somebody hasn't
said yet. None of them may reach the doc unchased.

| Word | Ask |
|---|---|
| **scalable** | To what number, by when? What breaks first today? |
| **real-time** | What's the acceptable delay, in seconds? What happens at double that? |
| **robust** | Robust against what specifically - bad input, a dependency down, a restart? |
| **secure** | Against whom? What's the thing we'd hate to happen? |
| **seamless** | Seamless for whom - the user, the operator, or the other team? |
| **simple** | Simple to build, to operate, or to explain? Those pull in different directions. |
| **clean** | What's dirty about it now? Name one concrete thing. |
| **fast** | Faster than what, measured where, at which percentile? |
| **flexible** | Flexible in which direction? Name the change you expect to make later. |
| **reliable** | What uptime, and what's the current number? |
| **soon** | This sprint, this quarter, or this year? |
| **a lot of** | How many? Per what - day, tenant, request? |
| **best practice** | Whose, and what breaks here if we don't follow it? |
| **standard** | Standard where - this repo, this company, or the industry? |
| **temporary** | Until what event? Who removes it? |
| **just** | (In "we could just…") What does this make harder later? |

The last one is the sleeper. "We could just add a column" is where an hour of
design gets skipped.

## Question hygiene

- **Delete every question Phase 1 answered.** Sending them anyway tells the user
  you didn't read.
- **Merge questions with the same answer.** Three questions that all resolve on
  "is this per-tenant or global?" is one question.
- **Batch by theme.** Five questions in one message beats five messages.
- **Give a default, always.** A question with no default is a block, and blocks
  get abandoned.
- **Never re-ask an answered question.** If you need to check, quote their answer
  back and ask if it still holds.
- **Ask the dumb question.** "What is the sync path?" is cheap now and
  unaffordable at review.
