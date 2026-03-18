# Dynamic Risk Checklist

Dead-code cleanup often fails when the repo uses indirect references.

## Check for these before deleting

- file-based routing or auto-loaded pages
- dependency injection containers or service registries
- plugin systems or event handler registration
- background jobs, schedulers, or task discovery by filename
- template engines, CMS blocks, or email templates referenced by string key
- feature flags, environment switches, or A/B test variants
- analytics, monitoring, or tracing hooks with runtime-only references
- assets loaded from manifests, theme configuration, or bundler conventions

## If any of these are present

- downgrade confidence unless you can prove the candidate is still unused
- prefer a report-first approach for ambiguous files or exports
- mention the specific dynamic pattern that made the candidate risky
