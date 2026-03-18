# Pandoc to Confluence Storage

## Standard path

```text
Markdown
-> pandoc HTML
-> code block macro conversion
-> Confluence storage update
```

This path is more predictable than direct Confluence Markdown publishing because it gives you a stable storage-format payload before upload.

## Command sequence

```bash
scripts/md_to_confluence_storage.sh docs/example.md /tmp/example.storage
confluence update <pageId> -f /tmp/example.storage --format storage
```

## Rules

- Do not rely on Confluence markdown format as the primary publish path.
- Convert fenced code blocks into Confluence `code` macros.
- Let Pandoc handle headings, tables, and lists unless the page needs a hand-tuned storage fragment.
- For larger pages, compare the old and new rendered body before and after publishing.
