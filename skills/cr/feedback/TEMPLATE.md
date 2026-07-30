# <repo> review ruleset

> **This is a format template, not a ruleset.** Copy it to
> `~/.claude/cr/feedback/<repo>.md` and let `/cr update` fill it in from your repo's
> real review comments — that's what makes `/cr` say what *your* reviewers say
> instead of generic best practice. Writing rows by hand is fine too; anything you
> add survives future syncs.
>
> Every placeholder below is marked `<…>`. Delete the ones you don't fill in — an
> unedited placeholder row will produce a nonsense finding.

Derived from **<N> review comments across <M> PRs** (all authors).
Most review comments are not deep — they're the same recurring mechanical issues.

**Last updated: <YYYY-MM-DD> · synced through PR #<N>** (see `~/.claude/cr/state.json`).

## Mechanical checks (RUN answers every applicable row)

Binary, surface-routed checks RUN *executes* — one verdict per row whose surface
matches a changed file/construct in the diff (a failing answer is a finding; the
quote is its TLDR). Populated and maintained by UPDATE's routing + migrate pass
(see the skill's UPDATE mode); every row should trace to a real reviewer quote.

A row earns its place only if all three hold: a reviewer would **always** raise it,
it's phrasable as a **yes/no**, and it's bound to a **recognizable surface** (file
glob, import, or code construct you can match in a diff). Everything else belongs in
the prose categories below.

| surface (glob / import / construct) | binary question | sev | reviewer quote |
|---|---|---|---|
| `<glob, e.g. *Table.tsx>` | `<yes/no question about the changed code>` | 🟡 | "`<what the reviewer actually wrote>`" |
| `<construct, e.g. any new API endpoint>` | `<is the auth guard present?>` | 🔴 | "`<verbatim quote>`" |
| `<import, e.g. files importing the logger>` | `<yes/no>` | 🔵 | "`<verbatim quote>`" |

## Severity examples (<repo>)

The repo-specific triggers that map onto the engine's severity scale:

- 🔴 **blocker** — `<the hard rules this repo blocks merge on, e.g. a specific cast,
  a missing migration guard, a mutating command in a script>`
- 🟡 **should-fix** — `<the recurring requests-changes comments: duplication, magic
  value, missing test, missing null path, convention violation>`
- 🔵 **nit** — `<style/polish your reviewers leave but don't block on>`

## RUN sweep (<repo>-specific)

As part of the review, also sweep the diff for: magic values, duplicated blocks,
missing null/error guards, `<plus the repo-specific things reviewers keep catching —
unparameterized SQL, unstable refs, broad excepts, whatever applies here>`. Merge
anything found into the same findings list (dedupe by line).

## The categories (ranked by frequency across team PRs)

Judgment/contextual guidance RUN *reasons with* — not yes/no against a surface.
Rank by how often it actually comes up; put the top one first. Keep each category
under **~12 triggers or ~25 lines** — split it into sub-categories when it grows
past that, because dense prose gets read but not applied.

### 1. `<category name — e.g. DRY: reuse, don't recreate>` (~<N>)
`<What reviewers keep saying here, with the concrete examples they flagged. Quote
them: a real "we already have X, use it" beats an abstract principle. Name the
actual helpers/components/utils in this repo that get pointed at.>`

### 2. `<category name — e.g. Correctness / regressions>` (~<N>)
`<The lenses to apply on every change: null/empty/loading paths, contract
preservation on deletes and renames, guards at parity. Add the failure modes this
repo has actually shipped.>`

### 3. `<category name — e.g. Magic values → named consts/enums>` (~<N>)
`<…>`

### 4. `<category name — e.g. Tests ship WITH the change>` (~<N>)
`<…>`

`<Add categories as UPDATE discovers them. A new category needs ≥3 occurrences from
≥2 reviewers — otherwise fold it into the closest existing one.>`

## Final gate (report as a checklist)

One row per category, in the same order. RUN reports ✓ / ~ / ✗ with one-line
evidence — a secondary summary under the inline comments, never a replacement
for them.

```
□ <category 1 restated as a check>
□ <category 2 restated as a check>
□ <category 3 restated as a check>
□ <category 4 restated as a check>
□ Swept diff for magic values, dupes, missing guards, <repo-specific sweep items>
```
