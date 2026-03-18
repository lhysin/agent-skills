# Publishing Checklist

Use this file as a short decision checklist, not as a full workflow.

## Before publishing

- Confirm the target page ID and parent page ID.
- Read the current body with `confluence read` or `confluence edit`.
- Create a backup plan if 3 or more pages move, a parent changes, numbering is reordered, or sibling titles may collide.
- Decide whether attachment names should be preserved or replaced.

## During publishing

- Render Mermaid diagrams to PNG before updating the page body.
- Upload or replace PNG attachments.
- Convert Markdown to storage format.
- Apply title changes and moves in an order that avoids naming collisions.

## After publishing

- Run `confluence read <pageId>`.
- Run `confluence children <parentId>` only if hierarchy changed.
- Run `confluence attachments <pageId>` only if files changed.
- Confirm numbering, parent placement, and diagram references only where relevant.
