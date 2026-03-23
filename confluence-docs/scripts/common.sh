#!/usr/bin/env bash
# common.sh — shared utilities for confluence-docs scripts
# Source this file: source "$(dirname "$0")/common.sh"

set -euo pipefail

require_cmd() {
  local cmd=$1
  command -v "$cmd" >/dev/null 2>&1 || {
    printf 'required command not found: %s\n' "$cmd" >&2
    exit 1
  }
}

make_tmpfile() {
  local f
  f=$(mktemp "${TMPDIR:-/tmp}/confluence.XXXXXX")
  trap "rm -f '$f'" EXIT
  printf '%s' "$f"
}

die() {
  printf 'error: %s\n' "$*" >&2
  exit 1
}