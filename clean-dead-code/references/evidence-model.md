# Evidence Model

## Signal taxonomy

Use this as a lookup when evaluating a specific candidate, not as a checklist.

### Strong signals

- Compiler, linter, or type checker marks a symbol as unused
- Repo-wide search shows no non-definition references
- The symbol is private or clearly internal
- No config, registry, route, manifest, or string-based lookup points to it
- Build, test, or type check still passes after removal

### Medium signals

- An export appears unconsumed inside the repo
- A file has no direct imports but lives in a convention-heavy directory
- A dependency appears unused but may be consumed by scripts or tooling
- Tests do not cover the affected area well

### Weak signals (do not act on these alone)

- A single text search shows zero matches
- A file "looks old"
- A component is not mentioned in nearby code

## Reporting pattern

When deleting code, explain the evidence in plain language:

- why it looked unused
- what you checked to rule out indirect consumers
- what verification still passed after removal
