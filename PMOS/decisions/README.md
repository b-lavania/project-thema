# Decision log

DACI-backed audit trail. One file per non-trivial call.

## Naming

```
decisions/YYYY-MM-DD-<short-slug>.md
```

Example: `decisions/2026-07-22-pricing-tier-change.md`

## Workflow

1. Draft in [templates/10-daci.md](../templates/10-daci.md) or [workspace/meeting-notes.md](../workspace/meeting-notes.md)
2. Copy [\_template.md](_template.md) → dated file
3. Link from `products/<name>/decisions.md` index

## When to log

- Prioritization overrides (especially in feature-factory mode)
- Scope cuts with stakeholder sign-off
- Launch / no-launch calls
- Anything you'd need to explain in an interview or postmortem

See [guides/feature-factory.md](../guides/feature-factory.md) for why this matters when the org doesn't keep records.
