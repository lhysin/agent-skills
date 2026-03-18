# Mermaid CLI Recipes

## Basic render

```bash
scripts/render_mermaid_png.sh diagram.mmd out.png
```

## Render from standard input

```bash
cat <<'EOF' | scripts/render_mermaid_png.sh - out.png
flowchart TB
    A["Frontend"] --> B["BFF API"]
    B --> C["Domain API"]
EOF
```

## Recommended defaults

- theme: `dark`
- background: `#0b1220`
- width: `2400`

These defaults produce a crisp diagram for Confluence pages and large screenshots, but you can override them per page style.

## Publishing rule

- Show the PNG in the page body first so readers can scan it quickly.
- Keep the Mermaid source in an expand block or the page's existing equivalent.
- If the current document already uses a specific attachment naming pattern, keep it consistent.
