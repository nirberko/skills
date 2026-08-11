---
name: tech-design
description: Write a technical design document (TDR / design doc / RFC) that a reviewer from another team can follow without prior knowledge of the code. Produces Confluence-ready HTML+ (native @mention chips, status pills, panels) or plain markdown. Use when the user asks to create, draft, or write a tech design, technical design, design doc, TDR, RFC, or design review.
---

# Tech Design

Produce a technical design document that an engineer from **another team** can
read end to end without asking anyone a question, and that a reviewer can map
line by line to the eventual diff.

Default output is Confluence HTML+ rather than markdown, because it unlocks
native Confluence nodes: real @mention chips, the Status pill, info panels, and
round-trip-safe updates that preserve inline comments. Write plain markdown
instead when the user isn't on Confluence.

## Workflow

1. **Read the conventions.** Load `references/conventions.md` - section order,
   the Overview table, how to write Requirements and the Design Summary, and the
   rules for making the doc legible to an outsider.

2. **Load the house patterns, if any.** Every org has recurring things a design
   is expected to address - which database a new table belongs in, whether a
   change has to work on two engines, how migrations are staged, how a feature is
   flagged and monitored. These are org-specific, so this skill ships none. Check
   for a house file, in this order, and use the first that exists:

   - `docs/tech-design.md` or `.github/tech-design.md` in the current repo
   - `~/.claude/tech-design/<repo>.md`

   If none exists and the change touches infrastructure, say so once and offer to
   derive one - see *House patterns* in `references/conventions.md`. Do not block
   on it, and never invent house rules you can't point at.

3. **Find a precedent.** A design that mirrors an accepted one gets reviewed
   faster. If the user has a corpus of past designs - a Confluence space, a
   `docs/designs/` directory - grep it for the closest prior design of the same
   shape (a schema change, a new API, a migration) and mirror its structure. If
   there's no corpus, follow the conventions file alone.

4. **Gather what you don't know.** A design needs: the change, the goal, the hard
   requirements, and the affected surface (new table? API? migration? background
   job?). If the user hasn't given enough to write a concrete Design Summary, ask
   - briefly, only the blocking gaps. Then read the codebase (models, routes,
   jobs, schemas) so the design cites real file paths and existing patterns
   instead of inventing them.

5. **Draft from the template.** Copy `assets/tech-design-template.html` as the
   starting structure. Fill the Overview table, Requirements, and Design Summary.
   Drop sections that don't apply - a small change is just Overview →
   Requirements → Design Summary → Open questions. Add `Possible Solutions`
   (Option 1 / Option 2 with Pros/Cons and a first-person recommendation) only
   when genuinely weighing alternatives.

6. **Make the Design Summary concrete.** Real model classes, schemas, queries,
   YAML/SQL, phased steps with exact file paths. Draw pipelines and service flows
   as **Mermaid diagrams rendered through mermaid.ink and embedded as `<img>`**
   (Confluence can't render a mermaid fence) - exact recipe, and the curl check
   that the URL returns 200, in `references/conventions.md` → *Diagrams, tables,
   code*. In markdown output, use a plain ```mermaid fence instead.

7. **Make it readable by an outsider.** Short sentences. Every internal term and
   acronym glossed **inline where it first appears**. Every file, table, and
   service given a clause saying what it does. One "why this piece exists"
   sentence per subsection. **Never add a Vocabulary / Terminology / Definitions /
   Glossary section** - definitions live in the sentence that uses the term.
   Explanatory, not longer. Rules and self-check: `references/conventions.md` →
   *Write so an outsider understands*.

8. **Write the file** where the user wants it (default: the repo, or a scratch
   directory, as `<name>-tech-design.html`).

9. **Publish** - only when the user asks. This is an outward-facing write:
   confirm the title, space, and parent page first, then follow
   `references/publishing.md`. Default to a draft unless they say publish live,
   and return the page URL.

## Scope note

The template is shaped for a backend or full-stack change, which is the common
case. Trim the Data Model and API sections for a pure frontend or infrastructure
design, and keep Requirements → Design Summary → Tasks & Phases.
