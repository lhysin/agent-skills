# Dimension Rubric

Use this file for actual scoring. The core skill only routes the evaluation.

## D1: Knowledge Delta (20)

Question: does the skill add expert knowledge, or does it mostly restate what the model already knows?

Score bands:
- `0-5`: basics, tutorials, generic best practices, standard library explanations
- `6-10`: mixed bag; some useful insight, too much obvious material
- `11-15`: mostly expert content with limited redundancy
- `16-20`: almost every paragraph earns its tokens

Evidence that supports a high score:
- decision trees for non-obvious choices
- trade-offs an expert would care about
- real failure modes and edge cases
- explicit reasons to prefer one approach over another

Evidence that forces deductions:
- "what is X" sections for common concepts
- standard step-by-step tutorials for ordinary tasks
- repeated summaries of the same idea in different words
- definitions the model clearly already knows

## D2: Mindset + Appropriate Procedures (15)

Question: does the skill teach the model how to think, and when needed how to execute domain-specific workflows?

Score bands:
- `0-3`: only generic procedures
- `4-7`: has procedures, lacks decision mindset
- `8-11`: solid balance of mindset and domain workflows
- `12-15`: expert thinking patterns plus procedures the model would not infer reliably

Reward:
- "before doing X, ask..." frameworks
- correct ordering that matters in the domain
- non-obvious checkpoints or failure-prevention steps

Deduct for:
- open/read/write/save procedures
- generic coding advice with no domain angle
- checklist mechanics with no decision logic

## D3: Anti-Pattern Quality (15)

Question: does the skill clearly say what not to do, with reasons that come from experience?

Score bands:
- `0-3`: no anti-pattern guidance
- `4-7`: vague warnings only
- `8-11`: specific NEVER list with partial reasoning
- `12-15`: concrete expert anti-patterns with clear why

Reward:
- specific mistakes the model is prone to making
- reasons tied to real consequences
- anti-patterns that help the model avoid generic AI output

Deduct for:
- "be careful"
- "avoid mistakes"
- any warning that could apply to everything

## D4: Specification Compliance (15)

Question: does the skill follow spec, especially in the frontmatter?

Score bands:
- `0-5`: missing or invalid frontmatter
- `6-10`: valid format but vague description
- `11-13`: description has WHAT but weak WHEN
- `14-15`: description clearly covers WHAT, WHEN, and trigger keywords

Check:
- `name` is lowercase and uses hyphens only
- `description` tells the agent when to load the skill
- trigger phrases live in metadata, not hidden in the body

Deduct when:
- description is generic
- description omits realistic trigger contexts
- the body contains critical activation guidance that the description lacks

## D5: Progressive Disclosure (15)

Question: does the package keep the always-loaded body lean and push detail into on-demand resources?

Score bands:
- `0-5`: everything dumped in one body, or extra docs with no loading guidance
- `6-10`: some layering, but triggers are weak or unclear
- `11-13`: good layering with explicit loading guidance
- `14-15`: excellent layering with scenario-based triggers and explicit non-loading guidance

Reward:
- `SKILL.md` stays focused
- detailed material moves into `references/`
- workflow points tell the model exactly when to read which file
- unnecessary docs are absent

Deduct for:
- `SKILL.md` far beyond what the task needs
- references that are never routed to
- README-heavy packages where runtime guidance is split for humans, not the agent

## D6: Freedom Calibration (15)

Question: is the level of specificity appropriate for the risk of getting the task wrong?

Score bands:
- `0-5`: strong mismatch between freedom and fragility
- `6-10`: partly aligned, some sections too rigid or too vague
- `11-13`: mostly well calibrated
- `14-15`: consistently matched to task risk

Use this rule:
- creative/taste tasks -> higher freedom
- judgment tasks -> medium freedom
- fragile operations -> lower freedom and clearer steps

Deduct when:
- a creative skill reads like a rigid script
- a fragile operational skill gives only vibes and no exact procedure

## D7: Pattern Recognition (10)

Question: does the skill follow a clear official pattern and use the right one?

Score bands:
- `0-3`: chaotic, no recognizable pattern
- `4-6`: partial pattern with visible mismatch
- `7-8`: clear pattern with minor drift
- `9-10`: strong execution of the right pattern

See `references/patterns.md` when pattern choice is unclear.

## D8: Practical Usability (15)

Question: can an agent use this skill immediately and reliably?

Score bands:
- `0-5`: confusing, incomplete, or contradictory
- `6-10`: usable but gaps are obvious
- `11-13`: works well for normal cases
- `14-15`: strong actionability, fallbacks, and edge-case handling

Reward:
- decision trees or clear branch points
- usable examples, not decorative examples
- fallback paths when the main approach fails
- explicit handling of realistic edge cases

Deduct for:
- broad advice with no decision path
- examples that look nice but do not change what the agent should do
- no fallback when the primary path is likely to fail

## Grade Scale

Total score:
- `108-120`: A
- `96-107`: B
- `84-95`: C
- `72-83`: D
- `<72`: F

## Evidence Standard

For each dimension:
- quote the lines or sections that matter
- say why they help or hurt the score
- name the concrete change that would raise the score

Do not give full credit because a skill is long, formal, or confident.
