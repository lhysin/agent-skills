# Cleanup Playbook

Use this reference when: the repo has 50+ packages, the user asks for an audit-first pass, or you need an end-to-end cleanup sequence across a large codebase.

## Large-repo specifics

### Skip the full boundary map for small targets

If the user pointed at a specific module or folder, skip step 1 (Map safety boundary) and go straight to evidence gathering. Only do the full boundary map when you're doing a repo-wide audit.

### Batch sizing for large codebases

- 5-10 high-confidence candidates per batch in repos under 20 packages
- 10-20 high-confidence candidates per batch in repos 20+ packages
- Always include coupled items (tests, barrel exports, configs) in the same batch as the symbol they serve

### Audit-first sequence for large repos

When doing a full repo audit without user-specified scope:

1. Run repo-wide diagnostics first (linters, type checkers, dead code detectors)
2. Collect all compiler/linter warnings about unused items
3. For each candidate, apply the confidence classification
4. Delete high-confidence batch
5. Run verification
6. Report medium/low candidates for user decision
7. Repeat until no high-confidence candidates remain

### When to stop

- Stop after the first batch where verification fails
- Stop when fewer than 3 high-confidence candidates remain per pass
- Do not attempt to clean everything in one session
