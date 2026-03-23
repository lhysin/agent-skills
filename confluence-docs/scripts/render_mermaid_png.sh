#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 || $# -gt 4 ]]; then
  printf 'usage: %s <input.mmd|-> <output.png> [background] [width]\n' "$0" >&2
  exit 1
fi

if ! command -v npx >/dev/null 2>&1; then
  printf 'npx is required but not installed\n' >&2
  exit 1
fi

input=$1
output=$2
background=${3:-#0b1220}
width=${4:-2400}

tmp_input=""
cleanup() {
  if [[ -n "$tmp_input" && -f "$tmp_input" ]]; then
    rm -f "$tmp_input"
  fi
}
trap cleanup EXIT

if [[ "$input" == "-" ]]; then
  tmp_input=$(mktemp "${TMPDIR:-/tmp}/mermaid.XXXXXX")
  cat > "$tmp_input"
  input=$tmp_input
fi

npx -y @mermaid-js/mermaid-cli \
  -i "$input" \
  -o "$output" \
  -t RDark \
  -b "$background" \
  -w "$width"
