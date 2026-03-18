# Official Skill Patterns

Use this file only when pattern choice affects the score or the rewrite plan.

## Mindset

- Typical size: about 50 lines
- Best for: creative tasks, taste, style, and judgment
- Shape: compact principles, strong anti-patterns, high freedom
- Failure mode: becomes generic self-help instead of domain taste

## Navigation

- Typical size: about 30 lines
- Best for: skills with multiple distinct sub-scenarios
- Shape: short router that sends the model to the right reference file
- Failure mode: references exist but routing is vague, so they never load

## Philosophy

- Typical size: about 150 lines
- Best for: art, writing, or creation where originality matters
- Shape: point of view first, then practical expression
- Failure mode: manifesto without actionable guidance

## Process

- Typical size: about 200 lines
- Best for: multi-step projects with checkpoints
- Shape: phases, decision points, verification steps
- Failure mode: turns into checklist theater without real judgment

## Tool

- Typical size: about 300 lines
- Best for: precise operations on a format or domain
- Shape: decision trees, fallbacks, examples, low-to-medium freedom
- Failure mode: giant manual or library tutorial instead of a decision harness

## Choosing the right pattern

Pick based on task shape, not author preference:
- if taste and differentiation matter most -> Mindset
- if routing across variants matters most -> Navigation
- if creative point of view matters most -> Philosophy
- if phased execution matters most -> Process
- if precise operational guidance matters most -> Tool

## Scoring pattern fit

High score signals:
- one dominant pattern is obvious
- structure matches the job the skill needs to do
- examples and references support the chosen pattern

Low score signals:
- pattern shifts halfway through the file
- the task calls for routing but everything sits in one body
- the task calls for freedom but the skill over-specifies outputs
- the task calls for precision but the skill only states principles
