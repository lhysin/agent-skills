# Confluence CLI Recipes

Use this file when you already know which operation you need and just want the exact command shape.

## Read current state

```bash
confluence read <pageId>
confluence edit <pageId>
confluence children <pageId>
confluence attachments <pageId>
confluence info <pageId>
```

Use `read` when you want the rendered body, and use `edit` when you need the storage-format source or raw editable content.

## Create and update pages

```bash
confluence create-child 'Document title' <parentId> -c 'Initial body'
confluence update <pageId> -t 'New title'
confluence update <pageId> -f /tmp/page.storage --format storage
```

Prefer a title-only update when the body does not need to change. It lowers the risk of accidental formatting drift.

## Move and back up content

```bash
confluence move <pageId> <newParentId>
confluence copy-tree <sourcePageId> <targetParentId> 'Backup title'
```

Before moving a populated page tree, capture a backup path so the user can recover quickly if numbering or page order becomes messy.

## Attach files

```bash
confluence attachment-upload <pageId> /path/to/file.png
confluence attachments <pageId>
```

Keep attachment names stable when replacing a diagram so existing references remain valid.

## Verify after changes

- Re-run `confluence read <pageId>` for the final body.
- Re-run `confluence children <parentId>` after move or rename work.
- Re-run `confluence attachments <pageId>` after image uploads.
