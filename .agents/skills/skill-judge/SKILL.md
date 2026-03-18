---
name: skill-judge
description: Evaluate Agent Skill quality against official specifications and expert patterns. Use this whenever reviewing, auditing, scoring, comparing, or rewriting a `SKILL.md`, skill package, or skill description, especially for requests like "evaluate this skill", "review my SKILL.md", "audit this skill", "compare these skills", or "how can I improve this skill?"
---

# Skill Judge

Judge a skill by its knowledge delta, not by markdown polish.

## Core standard

A strong skill compresses expert judgment the model would not reliably infer.

First pass:
- read `SKILL.md` completely
- note frontmatter quality, line count, and package shape
- mark each major section `[E] Expert`, `[A] Activation`, or `[R] Redundant`
- identify the dominant pattern and whether it fits task fragility
- note contradictions: long body with no layering, trigger logic hidden in body, generic NEVER list, or docs that do not help runtime use

Target ratio:
- strong: `E > 70%`, `A < 20%`, `R < 10%`
- weak: `E < 40%`, or obvious repetition even if it sounds smart

## Loading guidance

- **MANDATORY - READ ENTIRE FILE**: `references/dimensions.md`
- Read `references/patterns.md` when pattern choice or structure is unclear.
- Read `references/failure-patterns.md` when diagnosing weaknesses or planning a rewrite.
- Do not load every reference by default.

## Evaluation mindset

Before scoring, ask:
- what here would an expert say took years to learn?
- what only restates what the model already knows?
- if the skill fails, is the problem judgment, procedure, packaging, or triggering?
- would the description alone make the agent load this skill at the right time?

## Eight dimensions

Use `references/dimensions.md` for scoring details and evidence standards.

| Dimension | Max | Focus |
|-----------|-----|-------|
| D1: Knowledge Delta | 20 | Expert-only knowledge vs redundancy |
| D2: Mindset + Procedures | 15 | Thinking patterns plus domain-specific workflows |
| D3: Anti-Pattern Quality | 15 | Specific NEVER list with non-obvious reasons |
| D4: Specification Compliance | 15 | Valid frontmatter, especially description quality |
| D5: Progressive Disclosure | 15 | Good layering across metadata, body, and references |
| D6: Freedom Calibration | 15 | Constraint level matches task fragility |
| D7: Pattern Recognition | 10 | Clear fit to an official skill pattern |
| D8: Practical Usability | 15 | Clear decisions, fallbacks, and actionable guidance |

Fast deductions:
- invalid frontmatter -> `D4 <= 5`
- description has WHAT but not WHEN -> `D4 <= 13`
- generic or missing anti-patterns -> `D3 <= 7`
- dumpy single-file body with weak layering -> `D5 <= 5`
- no clear pattern -> `D7 <= 6`

Always capture:
- total `SKILL.md` lines
- whether `references/`, `scripts/`, or `assets/` exist
- whether loading triggers appear at the decision point
- whether auxiliary docs improve runtime use or only explain the skill
- whether the description carries the trigger burden the body cannot carry pre-load

## NEVER do this when evaluating

- Never reward polish over knowledge delta; pretty markdown is not expertise.
- Never excuse tutorials as "helpful context"; that is token waste.
- Never ignore the description field; the body cannot trigger before load.
- Never score progressive disclosure highly when everything sits in one long file.
- Never count README-like docs as value unless the agent must read them to do the job.
- Never mismatch freedom to fragility; creative work needs room, fragile work needs precision.

## Report format

Use this structure:

```markdown
# Skill Evaluation Report: [Skill Name]

## Summary
- **Total Score**: X/120 (X%)
- **Grade**: [A/B/C/D/F]
- **Pattern**: [Mindset/Navigation/Philosophy/Process/Tool]
- **Knowledge Ratio**: E:A:R = X:Y:Z
- **Verdict**: [One sentence]

## Dimension Scores
| Dimension | Score | Max | Notes |
|-----------|-------|-----|-------|
| D1: Knowledge Delta | X | 20 | |
| D2: Mindset + Procedures | X | 15 | |
| D3: Anti-Pattern Quality | X | 15 | |
| D4: Specification Compliance | X | 15 | |
| D5: Progressive Disclosure | X | 15 | |
| D6: Freedom Calibration | X | 15 | |
| D7: Pattern Recognition | X | 10 | |
| D8: Practical Usability | X | 15 | |

## Critical Issues
[Must-fix issues]

## Top 3 Improvements
1. [Highest-impact change]
2. [Second priority]
3. [Third priority]

## Detailed Analysis
[Explain every dimension below 80% of max with evidence and concrete fixes]
```

## Reporting rules

- Quote evidence and cite file paths.
- Give a one-line justification for every dimension.
- For every dimension below 80% of max, explain the flaw and the specific fix.
- Separate must-fix issues from nice-to-have improvements.
- For comparisons, hold the task constant and judge trigger quality, body quality, and package design separately before naming a winner.
- Prefer structural fixes before cosmetic rewrites.

## Final checks

- Shorter is better if expert content survives.
- Description quality matters more than body polish.
- Repetition across `SKILL.md` and auxiliary docs is usually waste.
- Penalize redundancy rather than praising effort.
- Judge metadata as metadata, not as body content.
- Catch orphan references, invisible triggers, and unnecessary docs.
- Give concrete next edits, not vague advice.
