# Verification Checklist

## Preferred order

1. Run the narrowest local check that exercises the changed area.
2. Run repo-standard static checks such as lint, type check, or compile.
3. Run targeted tests for the affected package, app, or module.
4. Run a broader build or integration check if the repo normally relies on it.

## What to verify after deletion

- imports and exports still resolve
- route, registry, or config wiring still works
- tests and builds do not fail from missing symbols
- generated artifacts are not expected to be edited manually

## If verification is limited

- say exactly which commands were run
- say which commands could not be run
- call the result partially verified rather than fully verified
