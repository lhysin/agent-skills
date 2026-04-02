---
name: clean-dead-code
description: Find, verify, and remove dead code in any codebase with a conservative, evidence-driven workflow. Use this skill for multi-step dead-code cleanup work when the user wants to audit unused files, stale exports, orphaned helpers, or dependency cleanup safely across a repository.
metadata:
  short-description: Clean dead code safely
---

# Clean Dead Code

Use this skill when the user wants dead code removed without turning the cleanup into a risky guessing game. The goal is not to delete the most code. The goal is to remove high-confidence unused code while avoiding false positives caused by dynamic loading, public APIs, framework conventions, or reflection.

Do not read every reference file up front. Start with the main workflow, then load only the reference that matches the risk you discovered.

## Compatibility

- Requires normal codebase tools: file search, file reads, edits, and terminal commands.
- Prefer the repository's own diagnostics first: compiler errors, linter warnings, type checks, test suites, build commands, and framework analyzers.
- Works best when you can inspect the whole repository, not just a single file.

## Default outcome

When you finish, use this compact report structure:

| Item | Action | Evidence | Verification | Result |
|---|---|---|---|---|
| `path/or/symbol` | removed or kept | short reason | command or check | passed, failed, or not run |

After the table, add one short note listing any medium- or low-confidence candidates you intentionally left alone.

## Working approach

### 1. Map the safety boundary first

Before deleting anything, identify what counts as internal implementation detail versus public or externally consumed surface area.

- Identify entrypoints, packages, apps, libraries, CLI commands, routes, and integration boundaries.
- Check obvious metadata first, such as package manifests, workspace config, exports fields, route folders, and app entry files.
- Use quick repo searches to locate likely entrypoints and public surfaces before judging a file as private.
- Note generated code, vendored code, migrations, snapshots, fixtures, and build outputs that should not be cleaned up casually.
- Notice whether the repo uses conventions such as file-based routing, plugin auto-discovery, dependency injection, or string-based lookups.

Useful first-pass checks include:

- reading `package.json`, workspace config, or equivalent project manifests
- searching for exports, entry files, route folders, or registry modules
- checking whether the candidate lives under directories commonly treated as public or convention-driven

Do not delete anything in this step. The goal here is only to separate likely private implementation code from possible public or convention-loaded code.

If the user asked to delete code immediately, still do this first. It prevents easy mistakes.

### 2. Gather evidence from more than one signal

Unused code is often obvious only after you combine several signals. A text search alone is rarely enough.

Use the strongest signals available in the repo:

- compiler, linter, or type-checker warnings about unused imports, locals, parameters, exports, or files
- whole-repo reference searches for symbols, filenames, routes, CSS classes, assets, and config keys
- entrypoint and registry checks for manual wiring, reflection, plugin loading, dependency injection, or naming conventions
- package and workspace boundaries to see whether a symbol is consumed outside the current folder
- test, build, or runtime verification after a candidate is removed

Read `references/evidence-model.md` only if a candidate has one strong signal, crosses package boundaries, or might still be used indirectly.

### 3. Classify candidates by confidence

Treat cleanup as a triage problem, not a binary yes-or-no judgment.

Use this decision tree to classify:

```
Is the candidate flagged by compiler/linter/type-checker as unused?
├─ YES → Is it private (not exported, no public API surface)?
│       ├─ YES → Are there zero cross-package or dynamic references?
│       │       ├─ YES → HIGH confidence → safe to delete in next batch
│       │       └─ NO  → MEDIUM confidence → report to user
│       └─ NO  → MEDIUM confidence → check external consumers before deleting
└─ NO  → Is it clearly internal with zero repo-wide references?
        ├─ YES → Is there a dynamic loading pattern nearby?
        │       ├─ YES → LOW confidence → do not delete automatically
        │       └─ NO  → HIGH confidence → safe to delete in next batch
        └─ NO  → MEDIUM confidence → gather more signals
```

#### High confidence

Usually safe to remove when most of these are true:

- the symbol or file is private or clearly internal
- repo-wide searches show no real consumers
- no config, registry, route, or string-based reference points to it
- diagnostics already flag it as unused, unreachable, or dead
- a relevant test, build, or type check still passes after removal

#### Medium confidence

Often worth reporting or removing only in small batches:

- exported code appears unused but may be part of a shared surface
- a file has no direct references but sits inside a framework-driven directory
- there are indirect references through config, templates, or generated code
- tests do not cover the affected area well

#### Low confidence

Do not delete automatically when clues suggest dynamic behavior:

- reflection, dependency injection, plugin systems, event names, or string-based registries
- file-system conventions such as routes, jobs, templates, migrations, or loaders
- assets or code referenced only from documentation, generated manifests, or deployment config

In medium or low confidence cases, prefer reporting the candidate list and the uncertainty rather than forcing a deletion.

### 4. Delete in small coherent batches

When you do remove code, keep each batch understandable and easy to verify.

- Remove the symbol and its obviously coupled imports, tests, stories, snapshots, and barrel exports together.
- Avoid broad sweep edits across the whole repo unless the evidence is extremely strong.
- Keep naming, exports, and file structure coherent after each batch.

If multiple unrelated dead-code candidates exist, handle the safest ones first.

Read `references/cleanup-playbook.md` only when the repo is large, the user asked for an audit-first pass, or you need an end-to-end cleanup sequence.

### 5. Verify the cleanup

A deletion is only finished when the remaining code still works.

- Run the narrowest meaningful verification first, then broader checks if available.
- Prefer project-native commands such as lint, type-check, unit tests, integration tests, or build steps.
- If verification cannot be run, say so clearly and mark the result as partially verified.

Read `references/verification-checklist.md` only when the repo has multiple available checks and you need help choosing the verification order.

## Candidate types this skill should consider

- unused imports, locals, parameters, and private helpers
- unreachable branches and obsolete feature-flag paths
- unreferenced internal functions, classes, components, hooks, or modules
- stale exports and barrel exports with no consumers
- orphaned files, tests, stories, styles, assets, or docs that no longer connect to active code
- dependencies that became unused only if the repo evidence clearly supports package cleanup

## Anti-patterns (NEVER do these)

- **NEVER delete a migration file** just because it appears unused — frameworks auto-run them in order, and removing one can corrupt the DB schema state for other developers or production.
- **NEVER delete a fixture or snapshot file** based on zero direct imports — test runners or storybooks often load them by glob pattern or filename convention.
- **NEVER delete routes, pages, or job files** because a text search finds no callers — frameworks like Next.js, Rails, or Celery discover them by filename or directory structure.
- **NEVER delete code exported from a shared package** (SDK, utils, ui) based only on zero references in the producing repo — consumers outside the repo may depend on it.
- **NEVER delete generated files, vendor code, or lock files** — these are not dead code even when they appear orphaned.
- **NEVER delete feature-flagged code** where the flag is a string key checked at runtime — the linter cannot see that the branch is live in production.

Read `references/dynamic-risk-checklist.md` only when you see route conventions, registries, string-based lookups, reflection, or other runtime discovery patterns.

## Reference map

- `references/cleanup-playbook.md`: load for large repos or audit-first cleanup passes
- `references/evidence-model.md`: load when evidence is incomplete or mixed
- `references/dynamic-risk-checklist.md`: load when runtime discovery or conventions are involved
- `references/verification-checklist.md`: load when multiple verification options exist

## Quality rules

- Prefer evidence over intuition.
- Do not remove externally consumed or framework-discovered code unless the evidence is unusually strong.
- Make uncertainty visible instead of pretending the answer is certain.
- Leave the repo in a passing or clearly explained state after each cleanup batch.
