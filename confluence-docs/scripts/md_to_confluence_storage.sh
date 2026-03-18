#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  printf 'usage: %s <input.md> <output.storage>\n' "$0" >&2
  exit 1
fi

input_md=$1
output_storage=$2

if [[ ! -f "$input_md" ]]; then
  printf 'input markdown not found: %s\n' "$input_md" >&2
  exit 1
fi

if ! command -v pandoc >/dev/null 2>&1; then
  printf 'pandoc is required but not installed\n' >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  printf 'python3 is required but not installed\n' >&2
  exit 1
fi

tmp_html=$(mktemp -t confluence_html.XXXXXX)
trap 'rm -f "$tmp_html"' EXIT

pandoc "$input_md" \
  -f gfm \
  -t html5 \
  --wrap=none \
  --no-highlight \
  -o "$tmp_html"

python3 - "$tmp_html" "$output_storage" <<'PY'
from html import unescape
from pathlib import Path
import re
import sys

input_html = Path(sys.argv[1])
output_storage = Path(sys.argv[2])

html = input_html.read_text(encoding="utf-8")

pattern = re.compile(r'<pre><code(?: class="language-([^"]+)")?>(.*?)</code></pre>', re.DOTALL)


def replace_code_block(match):
    language = match.group(1) or "text"
    body = unescape(match.group(2)).replace("]]>", "]]]]><![CDATA[>")
    return (
        '<ac:structured-macro ac:name="code">\n'
        f'  <ac:parameter ac:name="language">{language}</ac:parameter>\n'
        f'  <ac:plain-text-body><![CDATA[{body}]]></ac:plain-text-body>\n'
        '</ac:structured-macro>'
    )


html = pattern.sub(replace_code_block, html)
html = html.replace("<hr />", "<hr/>")
html = html.replace("<br />", "<br/>")

output_storage.write_text(html, encoding="utf-8")
PY
