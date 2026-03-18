# Common Failure Patterns

Use this file when you need to diagnose why a skill underperforms or how to rewrite it.

## 1. The Tutorial

- Symptom: explains basic concepts, common tools, or standard coding patterns
- Root cause: author tries to teach the model instead of extending it
- Fix: delete basics; keep only expert choices, trade-offs, and edge cases

## 2. The Dump

- Symptom: huge `SKILL.md`, everything in one place
- Root cause: no progressive disclosure design
- Fix: keep routing and core guidance in `SKILL.md`; move detail into `references/`

## 3. Orphan References

- Symptom: `references/` exists but the model is never told when to read specific files
- Root cause: references are listed, not routed
- Fix: add explicit loading guidance at the workflow point where each file matters

## 4. Checkbox Procedure

- Symptom: mechanical steps with no decision logic
- Root cause: author encodes process without expert judgment
- Fix: add "before doing X, ask..." frameworks and branch points

## 5. Vague Warning

- Symptom: "be careful", "avoid mistakes", "consider edge cases"
- Root cause: author knows failure exists but has not named it precisely
- Fix: replace with concrete anti-patterns and consequences

## 6. Invisible Skill

- Symptom: good body, poor activation in practice
- Root cause: weak description
- Fix: make the description carry WHAT, WHEN, and trigger keywords in realistic phrasing

## 7. Wrong Location

- Symptom: trigger guidance lives in the body instead of metadata
- Root cause: misunderstanding of skill loading order
- Fix: move all activation logic into the frontmatter description

## 8. Over-Engineered Package

- Symptom: README, changelog, installation notes, and other docs that do not improve runtime behavior
- Root cause: treated the skill like a software project instead of an agent package
- Fix: remove auxiliary files unless the agent must read them to do the job

## 9. Freedom Mismatch

- Symptom: rigid instructions for creative work, vague instructions for fragile work
- Root cause: task fragility was never considered
- Fix: increase freedom for creative skills; increase precision for fragile operations

## Rewrite priorities

When multiple failure patterns are present, fix them in this order:
1. invisible skill or wrong-location description issues
2. dump/orphan-reference packaging issues
3. tutorial and vague-warning content issues
4. freedom mismatch and pattern mismatch

This order usually improves both trigger rate and output quality fastest.
