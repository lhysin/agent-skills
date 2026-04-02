---
name: confluence-docs
description: Create, update, back up, move, and verify Confluence pages from local Markdown and Mermaid assets using Confluence CLI, Pandoc, and Mermaid CLI. Use this skill when the user is doing multi-step Confluence publishing work such as page updates from local files, page tree changes, attachment handling, Markdown-to-Confluence conversion, Mermaid publishing, or explicit `confluence` CLI workflows.
metadata:
  short-description: Publish Markdown and Mermaid docs to Confluence
---

# Confluence Docs

Use this skill for repeatable Confluence documentation work where the user wants reliable page updates, hierarchy changes, backup steps, or verification after publishing.

## Decision tree

Before diving into steps, route by task type:

- **Single page content update** → steps 1 → 4 → 6
- **Page hierarchy / move / rename** → steps 1 → 2 → 5 → 6
- **Mermaid diagram publish** → steps 1 → 3 → 6
- **Multi-page restructure** → steps 1 → 2 → 5 → 6, then re-verify hierarchy
- **Any step fails** → step 7 before continuing

## Compatibility

- Use [confluence-cli](https://github.com/pchuri/confluence-cli) for all Confluence operations.
- Use `pandoc` for Markdown to HTML conversion.
- Use `python3` inside bundled scripts for deterministic HTML cleanup.
- Use `npx -y @mermaid-js/mermaid-cli` for Mermaid rendering.

## Working approach

### 1. Inspect first

Read the target page before editing so you preserve the existing structure, numbering, and tone unless the user asks to change them.

- Start with the smallest relevant inspection command, usually `confluence read <pageId>`.
- Read parent pages too when numbering, placement, or sibling order may change.
- Use the full command set in `references/confluence-cli-recipes.md` when you need a concrete command pattern.

If the user is changing a page tree or renumbering a section, inspect both the source page and the parent pages that will be affected.

### 2. Back up before risky structure changes

Large page moves, parent changes, and title reshuffles are easy to get wrong and harder to undo later. Create a backup path first when the user is reorganizing an existing document tree.

Create a backup before making the change if any of these are true:

- 3 or more existing pages will move
- a page's parent will change
- sibling titles may temporarily collide during renaming
- numbering will be reordered across an existing section

When backup is needed:

- Prefer a dedicated backup parent page for larger restructures.
- Try `copy-tree` when a clean snapshot is useful.
- If `copy-tree` is not viable, create a backup page and move or duplicate content in a reversible order.

Read `references/publishing-checklist.md` when you need a quick go/no-go checklist before changing hierarchy.

### 3. Handle Mermaid as rendered media plus source

Confluence page readability is usually better when readers see a rendered diagram first, while editors still have access to the Mermaid source.

- Render Mermaid to PNG with `scripts/render_mermaid_png.sh`.
- Upload the PNG as an attachment.
- Keep the Mermaid source in an expand block or other existing pattern if the page already uses one.
- Match the current document's publishing style instead of imposing a new layout without a reason.

Read `references/mermaid-cli-recipes.md` when you need rendering options or examples.

### 4. Convert Markdown through the storage pipeline

Direct Confluence Markdown updates are less reliable than storage-format updates, especially when code blocks and richer formatting are involved.

- Convert Markdown with `scripts/md_to_confluence_storage.sh`.
- Treat the resulting storage file as the publishable source.
- Preserve code block languages so Confluence renders them with the right macro.

Read `references/pandoc-confluence-pipeline.md` when handling larger pages or format edge cases.

### 5. Apply updates in a safe order

Use the smallest operation that solves the task, and order structural changes so temporary naming collisions are less likely.

- Prefer title-only updates when only the title changes.
- Prefer body-only updates when structure is stable and only content changes.
- Create child pages before large reorder work when that reduces churn.
- Move pages only after you understand the target parent's current child order.

Use `references/confluence-cli-recipes.md` for exact command patterns.

If two sibling pages would briefly share a conflicting title, use an intermediate temporary title and then finalize the rename.

### 6. Verify after publishing

Never stop at the write step. Re-read the affected pages so the user can trust the result.

- Re-read the page body.
- Confirm attachments if any file was uploaded or replaced.
- Confirm child order and parent placement if any move, rename, or renumbering happened.

If numbering or hierarchy matters, explicitly mention that you checked it.

### 7. Handle errors and fallbacks

If a step fails, use this decision path:

- **Auth failure**: re-run `confluence login --local` or re-confirm credentials before retrying.
- **Page locked or conflict**: read the current page state and decide whether to merge changes or ask the user to resolve the conflict.
- **Network or timeout error**: retry once, then report the page ID and the exact command that failed so the user can recover manually.
- **Mermaid render failure**: fall back to uploading the raw `.mmd` file as a text attachment and noting it in the report.
- **Pandoc conversion failure**: check that the input Markdown is valid and try with `--standalone` removed if the pipeline errors out.

## Default outcome

When you finish, give the user a short operational report that includes:

- which page IDs or titles were touched
- whether a backup page was created and why
- which attachments were uploaded or updated
- what verification you performed after the change

## Anti-patterns

**Never use Confluence Markdown format as the primary publish path.**
Why: The Confluence Markdown parser diverges from standard parsers in subtle but painful ways. Table column alignment silently breaks, code block language tags disappear after Confluence upgrades, and heading IDs get reassigned unpredictably. The storage format via Pandoc is longer but deterministic — what you preview is what you get.

**Never update a body-only operation when a title-only update would suffice.**
Why: A body update rewrites the entire storage payload and can accidentally drop formatting that the editor preserves but the storage format does not track (e.g. inline comments, embedded widgets). A title-only update touches only the title field and carries zero formatting risk.

**Never skip the read step before any write.**
Why: Confluence page state is not in your local repo. Without reading first you will not know if the page has existing Mermaid attachments, expand blocks, or numbered sections that your update would overwrite or duplicate. A 30-second read prevents a 30-minute cleanup.

**Never publish Mermaid without the source in an expand block.**
Why: Rendered PNG alone leaves editors with no way to edit the diagram later without reverse-engineering it from the image. The PNG is for readers; the source is for maintainers.

## Reference map

Load a reference file only when the decision tree routes to it. Do not pre-load reference files.

- `references/confluence-cli-recipes.md`: exact command patterns when you need CLI syntax
- `references/mermaid-cli-recipes.md`: Mermaid rendering defaults and publishing conventions
- `references/pandoc-confluence-pipeline.md`: Markdown to storage conversion flow and rules
- `references/publishing-checklist.md`: quick decision checklist for backup and verification scope

## Quality rules

- Preserve the page's existing structure when the user asks to keep the current Confluence style.
- Prefer reversible operations when changing page hierarchy.
- Explain risky assumptions before applying them if page identity or placement is uncertain.
- Re-verify parent-child ordering after any move, rename, or renumbering work.
