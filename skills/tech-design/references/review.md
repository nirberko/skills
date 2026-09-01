# Reviewing the design before anyone else does

Two passes, in this order. The **sweep** finds holes in the design. The
**self-check** finds holes in the document. Run the sweep at Phase 7a, while the
design is still cheap to change; run the self-check before handing anything over.

## Table of Contents
- [The sweep](#the-sweep)
- [Rating what the sweep finds](#rating-what-the-sweep-finds)
- [Two questions after the sweep](#two-questions-after-the-sweep)
- [The prototype diff](#the-prototype-diff)
- [The self-check](#the-self-check)
- [The hostile reviewer](#the-hostile-reviewer)

## The sweep

Walk one item through the system, then walk these. Not from memory - from the
list. Guessing from the ticket alone produces generic cases ("what if the input is
empty") and misses every real one.

Skip a category **out loud** ("no money involved here") rather than silently.

| # | Category | What to check |
|---|---|---|
| 1 | **None** | First run, empty account, empty batch. Does a job with nothing to do succeed, or fail on an empty set? Does the sum of nothing return 0, null, or an error? |
| 2 | **One** | A list of one. Off-by-one at the first and last element. Delete the only one - is the parent now invalid? |
| 3 | **Many** | 1M rows in an export, 10k in a dropdown. Does the count query scan the whole table? Does the request time out at the load balancer before the query finishes? |
| 4 | **Malformed** | Wrong type, missing required field, null where the type says non-null, truncated upload. **Who sees the error, and can they act on it?** |
| 5 | **Duplicate** | Double-click submit. A client retry after a timeout where the first call actually succeeded. A webhook delivered twice - most providers guarantee *at least* once. Is the operation idempotent, and if not, what key would make it so? |
| 6 | **Concurrent** | Two writers on the same row - last write silently wins, is that acceptable? Read-then-write without a lock. Two requests both pass the "does this exist?" check, then both insert. |
| 7 | **Out of order** | The update arrives before the create. A retry lands after a newer correct value was already written. |
| 8 | **Mid-way failure** | Crash after the write but before the send. Third-party charge succeeded, local write failed. Half a batch processed, then the process dies - does a rerun redo the first half? **Walk the state of the world at each step.** |
| 9 | **Dependency trouble** | Down, slow, rate-limiting, or returning 200 with an error body. What's the timeout? Do you retry, how many times, with what backoff, and does retrying create duplicates? |
| 10 | **Permissions** | Not logged in, session expired mid-action, permission revoked between page load and submit. Does it say "not allowed" or "not found" - leaking existence is a real leak. Can user A read user B's data by changing an ID? |
| 11 | **State transitions** | Already done, cancelled, refunded, archived, deleted while a form for it was open. Write the list of legal transitions; the illegal ones are the cases. |
| 12 | **Time** | Timezones - the user's, the server's, and the one in the database. DST: the hour that happens twice. Expiry exactly at the boundary, `<` or `<=`. Clock skew. A scheduled job that didn't run yesterday - does today's run catch up? |
| 13 | **Money** | Rounding in integers, not floats. Negative and zero amounts. A refund larger than the charge, then a second partial refund. |
| 14 | **Text** | Unicode and emoji - does the length limit count bytes or characters? RTL in an LTR layout. Very long input with no spaces. Whitespace only. Where is this rendered, and is it escaped there? |
| 15 | **Boundaries** | Zero, one, max, max+1, negative. Exactly at the limit - limits are usually written with the wrong comparison operator. The last page of pagination, and a page beyond it. |
| 16 | **Existing data** | **The one most often missed.** Rows created before this feature existed. Is null a valid state or a broken one? Records that would fail the new validation rule. **Pick one out loud: backfill, default, migrate lazily, or exempt.** Not deciding is deciding. |
| 17 | **After** | Undo - can this be reversed, and by whom? Delete the parent: cascade, orphan, or block? Is this new data covered by export and deletion requests? What does an old client do with the new response? |
| 18 | **Knowing it broke** | How would you find out this failed in production? Is there a log line with enough context to identify the affected tenant? Does it alert someone, or fail silently in a queue? Can you tell "nobody used it" from "it's broken"? **If the honest answer is "we'd hear from a customer", say so**, then decide whether that's acceptable. |

**Don't run all 18 blindly.** Match them to the change:

| Change kind | Categories that matter most |
|---|---|
| New table or model | 1, 2, 4, 6, 11, **16** |
| Change to an existing model | **16, always**, plus 4, 11, 17 |
| List, search, or export | 1, 2, 3, 15 |
| New API surface | 4, 5, 10, 15, 17 |
| Integration or webhook | 5, 7, 8, 9, 18 |
| Background job or pipeline | 1, 3, 5, 7, 8, 9, 12, 18 |
| Migration | 8, **16**, 17 |
| Anything with money | 5, 8, 13 |
| Anything with dates | 12 |

## Rating what the sweep finds

Rating is the part people skip, and it's what stops the list becoming a wall of
paranoia. One line per hit:

```
<what happens> | likely: H/M/L | damage: H/M/L | handling: <one line>
```

| Verdict | Meaning | Where it goes in the doc |
|---|---|---|
| **Must handle** | Likely, or damaging enough that once is too many | A component's "How it fails", and a phase's Definition of Done |
| **Should handle** | Real but survivable | Open questions, with the cost of handling it and the cost of skipping it |
| **Accept and document** | Will happen, we'll live with it | A "Record the accepted downside" line in the relevant component, or Did Not Address |
| **Out of scope, because** | Can't happen given the constraints | Did Not Address, **with why it can't**, so a future reader can check whether that's still true |

**"Accept and document" is a legitimate and common answer.** Most cases should not
be handled. A design that turns every edge case into work is worse than useless -
it makes people stop running the sweep. But an accepted case is a decision; an
unnoticed one is a bug. Write it down either way.

**Every "must handle" appears in a Definition of Done.** A case that isn't in a
done condition isn't handled, it's remembered.

## Two questions after the sweep

1. **What does this design make harder?** Every design narrows what's easy next.
   Name the future thing that just got more expensive, and put it in the doc.
2. **What are we committing to forever?** New API surface, a new URL, a new state,
   a new user-visible promise. These don't get removed. Name them before agreeing
   to them.

## The prototype diff

When a prototype exists - a Figma file, a spike branch, a clickable mock - **diff
the doc against it before calling the doc done.** The prototype is a requirements
source, and it is usually ahead of the written spec.

Walk every screen and interaction in the prototype and check each against the
doc. The things the text most often misses:

- extra columns in a table or list
- bulk actions (select-all, multi-delete, export)
- validation rules visible in the forms
- cross-navigation - links from this feature into others, and back

Each miss is one of two findings, and both go to the user:

1. **The doc missed a requirement the prototype shows.** Add it, or record it as
   explicitly out of scope.
2. **The prototype and the written spec conflict.** This is a finding to
   **escalate, not to silently resolve.** Name the conflict, show both versions,
   and let the user pick. Picking quietly bakes one side's mistake into the
   design.

## The self-check

Run all of it before handing the doc over.

**The problem and the boundary**

- [ ] Could someone who reads only Requirements disagree with the decision? If
      they'd have to read further to disagree, it's too vague.
- [ ] Does the problem statement contain any solution words? Remove them.
- [ ] Are there phase headers anywhere in Requirements? Move the phasing to
      Tasks & Phases; Requirements describe what ships now.
- [ ] Did the user state an explicit scope boundary ("only X migrates")? The doc
      says it plainly and describes no work outside it.
- [ ] Is there a goal that no reasonable design could fail? Delete it.
- [ ] Does every non-goal trace to something that actually came up?

**The design**

- [ ] Does every new component have its own subsection, and does every one have
      "why this way" and "traps"?
- [ ] For anything with two writers or two steps, is it stated who owns what and
      which order is correct?
- [ ] Does the design say what happens when each dependency is down or slow?
- [ ] Is there an answer for data that already exists?
- [ ] Can this be turned off, and how fast?
- [ ] Does the walk-through cover the boring case, the deletion case, and the
      failure case, not just the first-time case?
- [ ] Is every operational goal matched by a metric in Monitoring?
- [ ] Are the four ⚠️ sections either present, or skipped with a stated reason?
- [ ] Does every rule, automation, or engine have its lifecycle table - on
      create, on edit, on disable, on delete, on manual override?
- [ ] If a prototype exists, was the prototype diff run, and is every conflict
      escalated rather than silently resolved?

**The altitude**

- [ ] Do the Design Summary slots appear in the fixed menu order - data model,
      API, core engine, access control, performance, filtering, migration?
- [ ] Any indexes, primary-key mechanics, or constraint internals in the data
      model? Move them to the PR, unless one enforces a design invariant.
- [ ] Is any API described in prose where a short code block would do? Replace
      it.
- [ ] Pick the simplest mechanism in the doc. Is its section one paragraph? If
      it's longer, it was padded to look thorough - cut it.
- [ ] For each remaining detail: does it change what a reviewer approves or what
      an implementer builds first? If not, cut it.
- [ ] Count the diagrams. More than three, or one for a trivial flow? Cut the
      weakest.

**The writing**

Run the full STE self-check in `ste.md` as well. These are the ones that catch the
most in a design doc:

- [ ] Is any sentence longer than 25 words, or any paragraph longer than six
      sentences? Split it.
- [ ] Is there a passive sentence with a known actor? Name the actor.
- [ ] Is there an `-ing` word used as a verb or a noun, or a perfect tense ("has
      been", "will have")? Rewrite it.
- [ ] Are more than three nouns stacked anywhere? Break the cluster.
- [ ] Is one thing called by two names across two sections? Pick one.
- [ ] Is any word from the substitution table in `ste.md` still in the doc -
      utilize, ensure, perform, prior to, in order to, however, therefore?
- [ ] Does each Traps paragraph start with a command, with its condition first?
- [ ] Is every internal term and acronym glossed inline where it first appears?
- [ ] Is there a Vocabulary / Terminology / Definitions / Glossary section
      anywhere? Delete it and fold each definition into the sentence that first
      uses the term. The glossary pass is the approved Technical Names list, not a
      section.
- [ ] Does every file path, class, table, and service have a clause saying what it
      does?
- [ ] Pick three sentences at random. Does any need insider knowledge the doc
      never gave? Rewrite them.
- [ ] Is there a single fuzzy word left - scalable, real-time, robust, seamless,
      just? Chase it.
- [ ] Any em dash (`—`)? Replace with `-`.
- [ ] Any revision history or "changed from the previous version" narrative?
      Delete it.
- [ ] Does every open question have an owner and something it blocks?
- [ ] Is Open questions the last section, and is every resolved question still
      there - struck through with its resolution attached, never deleted?
- [ ] Does every rendered diagram URL return `200`? Check it - a Mermaid syntax
      error returns an error image that silently ships as a broken diagram.

**The last one**

- [ ] Would a hostile reviewer find something you already know and didn't write
      down?

## The hostile reviewer

That last check is the whole test. Read the doc once as the reviewer who wants it
to fail: the person on the team that owns the table you're changing, or the one
who was on call last time something like this shipped.

Ask their three questions:

1. **"What happens to the rows that already exist?"**
2. **"What breaks for me, and when will I find out?"**
3. **"What did you already know was a problem and leave out?"**

The risk you leave out is the one that gets found in the meeting. Writing it down
costs a line and buys you the room.
