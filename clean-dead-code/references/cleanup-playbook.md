# Cleanup Playbook

## Goal

Remove high-confidence unused code without breaking runtime behavior or accidentally deleting framework-managed files.

## Recommended sequence

1. Identify the stack and repo boundaries.
2. Find candidate dead code from diagnostics and repo-wide searches.
3. Cross-check each candidate against public APIs, config, conventions, and dynamic wiring.
4. Classify each candidate as high, medium, or low confidence.
5. Delete only the high-confidence batch first.
6. Run the narrowest meaningful validation, then broader validation if available.
7. Report what was removed and what remains uncertain.

## What good cleanup looks like

- Small, understandable diffs
- Evidence attached to each deletion decision
- Verification after removal
- Explicit notes for risky candidates left untouched

## What bad cleanup looks like

- Deleting exported or framework-discovered files based only on zero text matches
- Sweeping removals without build or test verification
- Treating generated files or migrations as ordinary dead code
- Removing code from shared packages without checking cross-package consumers
