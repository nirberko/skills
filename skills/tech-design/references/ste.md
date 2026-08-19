# ASD-STE100 Simplified Technical English

The design document is written in **ASD-STE100 Simplified Technical English**
(STE). STE is a controlled English standard: a set of writing rules plus a
dictionary of approved words, each with one approved meaning.

It fits this document for the same reason the skill exists. The reader is an
engineer from another team who has never opened this code, and often reads English
as a second language. STE removes the two things that stop that reader: long
sentences with several ideas in them, and one thing called by three names.

The specification and its Dictionary are the authority. Get them from
`asd-ste100.org`. This file holds the rules that apply to a design document, the
substitutions that come up most, and the parts of the document where STE gives
way.

## Table of Contents
- [What STE applies to](#what-ste-applies-to)
- [The writing rules](#the-writing-rules)
- [Approved verb forms](#approved-verb-forms)
- [Word substitutions](#word-substitutions)
- [Technical Names and Technical Verbs](#technical-names-and-technical-verbs)
- [Where STE gives way](#where-ste-gives-way)
- [Traps and warnings](#traps-and-warnings)
- [Worked examples](#worked-examples)
- [STE self-check](#ste-self-check)

## What STE applies to

**It applies to the document.** Every sentence of prose in every section.

**It does not apply to the conversation.** Questions to the user, checkpoints, and
the messages that show your work stay natural English. Interrogating someone in
controlled English is stilted and slows the exchange down.

**These are exempt inside the document:**

| Exempt | Why |
|---|---|
| Code, file paths, commands, schemas, queries, config | They are what they are. Never reword them. |
| Identifiers: class, table, column, endpoint, service, metric names | Same. `AlertRunner` stays `AlertRunner`. |
| Section headings and table headers | Titles, not sentences. `📊 Monitoring & Observability` is fine. |
| Technical Names and Technical Verbs | See below. This is the main carve-out. |
| Error strings and log lines quoted as evidence | Quote them exactly. |
| A ticket title or an incident name quoted verbatim | Same. |

## The writing rules

These are the same rules the `Plain` output style uses, so the two agree.

- **Write one instruction in one sentence.** Keep procedural sentences to 20 words
  or fewer. Keep descriptive sentences to 25 words or fewer.
- **Use the active voice.** Write "the job reads the checkpoint", not "the
  checkpoint is read". Use the passive only when the doer is unknown or does not
  matter, and only in descriptive text.
- **Use one word for one meaning.** Do not call the same thing a "job", a "run",
  and a "task" in one document. Pick one word and keep it, in every section.
- **Use simple verb tenses.** Prefer the present tense. Use the simple past for
  what happened. Do not use the perfect or the progressive tenses.
- **Do not remove articles.** Write "the query fails", not "query fails".
- **Do not stack more than three nouns together.** Break the cluster with a
  preposition.
- **Keep paragraphs to six sentences or fewer.** One topic per paragraph. Start
  the paragraph with its topic.
- **Use a vertical list** for a sequence of steps or a set of conditions.
- **Write short, common words.** No idiom, no metaphor, no jargon the reader did
  not use first.
- **Do not use a word to mean two things.** Define an internal term once, inline,
  where it first appears, then reuse it unchanged.
- **Do not drop words to make a sentence shorter.** Write the full sentence.
- **Put the condition before the instruction.** Write "If the batch is empty, the
  job stops", not "The job stops if the batch is empty".

Two rules from the base conventions get stronger under STE, not weaker:

- **Numbers, not adjectives.** "3 seconds", not "slow". STE has no approved word
  that means "slow enough to matter".
- **Tables and lists over paragraphs.** STE limits a sentence to one idea, so a
  set of related facts becomes a table. This is not a workaround. It is the
  intended result.

## Approved verb forms

STE allows four forms of a verb. Nothing else.

| Form | Example |
|---|---|
| Infinitive | to read, to write |
| Imperative | Read the row. Set the flag. |
| Simple present | The job reads the row. |
| Simple past, and the past participle **as an adjective** | The job read the row. The **stored** file. |

So:

- **No `-ing` as a verb.** "The job is reading the table" → "The job reads the
  table". "Reusing existing code is preferred" → "Use existing code where it
  exists".
- **No `-ing` as a noun (gerund).** "Handling of retries happens here" → "This
  component retries the call".
- **No perfect tenses.** "The row has been written" → "The row is in the table".
- **Prefer the verb to the noun built from it.** "Do the validation of the input"
  → "Check the input". "Perform a migration of the rows" → "Move the rows".

`-ing` survives only inside an approved Technical Name: `Monitoring` in a heading,
`rate limiting` if the house file approves it as a Technical Name.

## Word substitutions

The ones that come up most in a design document. The ASD-STE100 Dictionary is the
authority and holds about 900 approved words; this is a working subset, not a
replacement for it.

| Do not write | Write |
|---|---|
| utilize, leverage, employ | use |
| initiate, commence, kick off | start |
| terminate, cease | stop |
| ensure, guarantee | make sure that |
| verify | check, or make sure that |
| perform, execute, carry out, accomplish | do |
| implement | build, or do, or the specific verb |
| facilitate, assist | help |
| permit | let |
| shall, is required to, is to be | must |
| attempt | try |
| obtain, acquire | get |
| provide | give |
| require | need |
| indicate | show |
| locate | find |
| ascertain, determine | find out |
| maintain, retain | keep |
| modify, alter | change |
| approximately | about |
| sufficient | enough |
| additional | more, other |
| multiple, numerous, a large number of | many, more than one |
| currently, presently | now |
| prior to | before |
| subsequent to, following | after |
| due to the fact that, inasmuch as | because |
| in the event that | if |
| in order to | to |
| in addition, furthermore, moreover | also |
| however, nevertheless | but |
| therefore, thus, hence, consequently | so |
| via | by, through, with |
| per (as in "per tenant") | for each |
| regarding, with respect to, in terms of | about |
| utilization | use |
| functionality | function, or the specific thing it does |
| methodology | method |
| in the same way as, analogous to | like |
| a number of | some, or the number |

Two habits to break that are not single words:

- **"There is" / "there are" openings.** "There is a risk that the job fails" →
  "The job can fail". Name the subject.
- **"It should be noted that" and every other empty opening.** Delete it and start
  with the fact.

## Technical Names and Technical Verbs

STE cannot describe a real system with 900 words alone, and it does not try to.
The specification lets a project approve its own **Technical Names** (things: a
table, a service, a domain concept) and **Technical Verbs** (actions specific to
the technology). Once approved, they are used freely.

**The Phase 2 glossary pass is this list.** That is its second job. Every term you
rated `known` or confirmed from `assumed` is an approved Technical Name for this
document. Every term still `unknown` is not approved, and it does not go in the
doc - which is already the hard rule in `SKILL.md` Phase 2.

Rules for using them:

- **Gloss each one inline, once, where it first appears.** STE requires that a
  Technical Name is defined for the reader; the base conventions require the same
  thing and forbid a glossary section. They are the same rule.
- **One name per thing.** If the code calls it a `tenant` and the ticket calls it
  an `org`, pick one for the whole document and say once that they are the same
  thing.
- **Record the project's list in the house file.** `docs/tech-design.md` or
  `~/.claude/tech-design/<repo>.md` - see *House patterns* in `conventions.md`. A
  project that writes many designs approves `backfill`, `dual-write`, `shard`,
  `idempotent` and its own domain nouns once, and the next design does not argue
  about them.
- **Do not approve a word to avoid rewriting a sentence.** A Technical Name names
  a thing in the system. It is not a licence to keep `leverage`.

## Where STE gives way

STE was built for procedural and descriptive technical documentation. A design
document also **argues**: it weighs options, recommends one, records a trade-off,
and warns the next engineer. The dictionary is thin there, and forcing it makes
the argument mushy.

So:

| Part of the doc | STE writing rules | STE dictionary |
|---|---|---|
| Requirements, Current Architecture, the detail of each component, End-to-End Flow, Migration, Rollout, Monitoring, Security, Cost, Tasks & Phases | Apply in full | Apply in full |
| **Why this way**, **Traps**, Possible Solutions rationale, Risks, the first-person recommendation | Apply in full | Relax where the argument needs a word the dictionary lacks |

The **writing rules never relax.** Short sentences, active voice, one word for one
meaning, and no `-ing` verbs apply to every sentence in the document. Only the
word list gives way, and only in a sentence that makes a judgement.

The first-person recommendation stays exactly as the conventions require it: **"In
my opinion, Option 1 is better and recommended because …"**. It is short, active,
and its subject is named. It already passes.

## Traps and warnings

STE has a section of rules for warnings and cautions, and they map onto the
**Traps** part of a component section better than anything else in this skill.

- **Start with a clear command.** Not a description of the danger.
- **Put the condition first**, then the instruction.
- **One instruction per sentence.**
- **Say what happens if the reader gets it wrong.**

```
Do not add a payload column to this table. The table is joined against 121,000
rows in each run, and it must stay narrow. A wide row makes each run slower.

Write the file to the object store first, then write the row. In the other order,
a crash between the two steps leaves a row that points at nothing, and the job
cannot recover.
```

This is the correct register for a trap. It survives being read quickly by a tired
person, which is when traps are read.

## Worked examples

**A component, described**

> Before: The uploader is responsible for the handling of all outbound GitHub API
> calls, and is therefore the component in which rate limiting is implemented,
> having been separated from the producer in order to ensure that a quiet run does
> not consume quota.

> After: The uploader makes every call to the GitHub API. It also does all the
> rate limiting. The producer is a separate process, so a run with no changes uses
> no quota.

72 words to 33. Three ideas, three sentences. No `-ing` verb, no passive.

**A failure path**

> Before: In the event that the process is terminated prior to the completion of
> the batch, the previously processed records will have already been persisted.

> After: If the process stops before the batch is complete, the rows it already
> wrote stay in the table. A rerun finds them and does not write them again.

The rewrite is longer and says more. STE is short per sentence, not short overall.

**A noun cluster**

> Before: the tenant sync job retry backoff configuration value

> After: the config value for the retry backoff in the tenant sync job

Six nouns become three, with prepositions between them.

**An ownership statement**

> Before: Writes to the `sent_at` column are performed exclusively by the uploader.

> After: Only the uploader writes the `sent_at` column. The producer never writes
> it. If the producer writes it, the uploader sends the file twice.

Active voice names the actor, and the rewrite adds the consequence the passive
sentence hid.

## STE self-check

Run this with the rest of the self-check in `review.md`.

- [ ] Is any sentence longer than 25 words? Split it.
- [ ] Is any paragraph longer than six sentences? Split it.
- [ ] Is there a passive sentence with a known actor? Name the actor.
- [ ] Is there an `-ing` word used as a verb or a noun? Rewrite it.
- [ ] Is there a perfect tense ("has been", "had been", "will have")? Rewrite it.
- [ ] Are more than three nouns stacked anywhere? Break the cluster.
- [ ] Is one thing called by two names across two sections? Pick one.
- [ ] Is any word from the left column of the substitution table still in the doc?
- [ ] Does any sentence open with "There is", "There are", or "It should be noted
      that"? Delete the opening.
- [ ] Is every Technical Name glossed inline at its first appearance, and nowhere
      else?
- [ ] Is there a Vocabulary / Terminology / Glossary section? Delete it. The
      glossary pass never becomes a section.
- [ ] Does each Traps paragraph start with a command and put the condition first?
