#!/usr/bin/env bash
source "$(dirname "$0")/common.sh"

[[ $# -ne 2 ]] && die "usage: $0 <input.md> <output.storage>"

input_md=$1
output_storage=$2

[[ -f "$input_md" ]] || die "input markdown not found: $input_md"

require_cmd pandoc
require_cmd python3

tmp_html=$(make_tmpfile)

pandoc "$input_md" \
  -f gfm \
  -t html5 \
  --wrap=none \
  --no-highlight \
  -o "$tmp_html"

python3 "$(dirname "$0")/html_to_storage.py" "$tmp_html" "$output_storage"