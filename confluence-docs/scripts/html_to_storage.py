#!/usr/bin/env python3
import re
import sys
from html import unescape
from pathlib import Path


def convert_code_blocks(html: str) -> str:
    pattern = re.compile(
        r'<pre class="([^"]+)"><code>(.*?)</code></pre>', re.DOTALL
    )

    def replace(match: re.Match) -> str:
        language = match.group(1) or "text"
        body = unescape(match.group(2)).replace("]]>", "]]]]><![CDATA[>")
        return (
            '<ac:structured-macro ac:name="code">\n'
            f'  <ac:parameter ac:name="language">{language}</ac:parameter>\n'
            '  <ac:parameter ac:name="theme">RDark</ac:parameter>\n'
            f'  <ac:plain-text-body><![CDATA[{body}]]></ac:plain-text-body>\n'
            '</ac:structured-macro>'
        )

    return pattern.sub(replace, html)


def normalize_self_closing(html: str) -> str:
    html = html.replace("<hr />", "<hr/>")
    html = html.replace("<br />", "<br/>")
    return html


def convert(input_path: Path, output_path: Path) -> None:
    html = input_path.read_text(encoding="utf-8")
    html = convert_code_blocks(html)
    html = normalize_self_closing(html)
    output_path.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: html_to_storage.py <input.html> <output.storage>", file=sys.stderr)
        sys.exit(1)

    convert(Path(sys.argv[1]), Path(sys.argv[2]))