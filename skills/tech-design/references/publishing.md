# Publishing a Tech Design

Publish only when the user asks. It's an outward-facing write - confirm the
title, space, and parent page with the user first, then create.

## Where it goes

This skill ships no target. Ask the user once, then remember it for the session:

| Setting | What it is |
|---|---|
| `cloudId` | The Atlassian site, e.g. `yourcompany.atlassian.net` |
| `spaceId` | The space key the team keeps designs in, e.g. `RD`, `ENG`, `ARCH` |
| `parentId` | The numeric id of the parent page all designs hang off |

The fastest way to get `parentId` is to open the team's existing design index
page in Confluence - the number in the URL after `/pages/` is the id. If the user
has a house file (see `conventions.md` → *House patterns*), record these there so
the next design doesn't ask again.

If the team isn't on Confluence, skip all of this: write the design as markdown
into the repo (`docs/designs/<slug>.md`) and open a PR for it. Everything in
`conventions.md` applies unchanged except the HTML nodes below.

## Recipe

1. Load the tool:
   `ToolSearch` query `select:mcp__claude_ai_Atlassian__createConfluencePage`.
   (The exact tool name depends on how the Atlassian MCP server is connected -
   search for `createConfluencePage` if that name misses.)
2. Write the finished HTML to a local file first. It's the source of truth, and
   it lets the user review before anything goes up.
3. Call `createConfluencePage`:
   ```
   cloudId="<site>.atlassian.net"
   spaceId="<SPACE>"          # space key is accepted, resolved to a numeric id
   parentId="<parent page id>"
   title="<Feature Name> - Technical Design"
   contentFormat="html"
   body=<the full HTML document body - no <html>/<head>/<body> wrappers>
   status="draft"             # stage privately; use "current" to publish live
   ```
4. Return the page URL (from the result's `_links.webui`, prefixed with
   `https://<site>.atlassian.net/wiki`) to the user.

## Why HTML (not markdown)

`contentFormat="html"` unlocks native Confluence nodes that markdown can't
express: real @mention chips, the Status pill, info and warning panels, expands,
task lists. It is also round-trip safe - fetching a page as html and updating it
preserves inline comments and local ids, which markdown round-trips lose.

## HTML+ nodes to use

- **Status pill** (Overview table):
  `<span data-type="status" data-color="neutral">NOT STARTED</span>`
  - `neutral` = NOT STARTED, `blue` = IN PROGRESS, `green` = DONE.
- **@mentions** (Owner / Contributors):
  `<span data-type="mention" data-user-id="ACCOUNT_ID">@Name</span>`
  - Resolve ACCOUNT_ID with `lookupJiraAccountId` (load via ToolSearch), or copy
    it from an existing page fetched as html. **Never invent an id** - if you
    can't resolve it, leave the name as plain text.
- **Code blocks:** `<pre><code class="language-python">...</code></pre>`
  (ASCII diagrams: plain `<pre><code>` with no language class).
- **Panels** (sparingly, e.g. a scope warning):
  `<div data-type="panel-info"><p>...</p></div>`
- Tables, headings, lists: standard HTML (`<table>`, `<h2>`, `<ul><li><p>`). Wrap
  cell and list-item text in `<p>`.

## Formatting rules (rejected otherwise)

- No `<html>`, `<head>`, or `<body>` wrappers - body content only.
- Follow ADF nesting: no nested tables, panels can't contain tables or expands,
  list items can't contain headings.
- Escape `<` / `>` inside code blocks (`&lt;vendor&gt;`).
- Omit `data-local-id` on new nodes. When editing a fetched page, preserve the
  existing `data-local-id` attributes so inline comments keep their anchors.

## Notes

- **Never overwrite a shared template page.** Many spaces keep a
  `Design Document Template` page that says "make a copy, don't edit". Publishing
  always creates a **new child page** under the parent - it never updates a
  template. If the user hands you a page id, confirm it isn't the template before
  writing to it.
- **If the Atlassian tools aren't available** (no auth, headless run), say so
  plainly and leave the local file. Don't work around it.
- **Default to `status="draft"`** unless the user says publish or live. A draft is
  private to the author and safe to iterate on. Switch to `"current"` to make it
  visible in the space.
## Updating a published page

Use `updateConfluencePage` (load via ToolSearch) with the page id, not a second
create. Four rules, all of them about not destroying other people's work:

1. **Always fetch the current version first and edit on top of it.** Call
   `getConfluencePage` with `contentFormat="html"` and apply your changes to
   *that* body. Never resend a full body built from your local file or from
   memory of what you published - a full-body resend silently overwrites every
   edit anyone made on the page between versions, and nobody finds out until
   they look for their change.
2. **Preserve existing `data-local-id` attributes** on every node you keep or
   move. Inline comments anchor to them; a rewritten id orphans the comment
   thread. (New nodes still omit `data-local-id` - Confluence assigns them.)
3. **Treat comment-anchored text as near-immutable.** A sentence with an inline
   comment on it is part of a conversation. Rewriting it detaches the thread and
   erases the context the reply was written against. If the sentence must
   change, prefer adding the correction next to it; reword the anchored text
   itself only when it is plainly wrong, and say so to the user.
4. **Edit surgically.** Change the sections that changed and leave the rest of
   the fetched body byte-for-byte. The smaller the diff, the less there is to
   destroy.
