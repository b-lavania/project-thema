# First 30 days — PMOS onboarding checklist

Use when starting a new PM role. One pass through context + templates beats a month of passive meetings.

## Week 1 — Map the terrain

- [ ] Copy `context/_template/` → `context/<company-slug>/`
- [ ] Fill `company.md`: mission, revenue model, org chart, your mandate
- [ ] Fill `product.md`: users, core workflow, stack, known pain
- [ ] Complete [Business Model Canvas](../templates/01-business-model-canvas.md)
- [ ] Identify DACI for your first big decision (even if informal)
- [ ] Schedule 1:1s: manager, eng lead, design, sales/CS, one power user

**Output:** One-page "how this business works" you could explain to a friend.

## Week 2 — Learn why customers stay

- [ ] Run [JTBD](../templates/08-jtbd.md) on 3–5 customer conversations or support themes
- [ ] Build a rough [story map](../templates/05-story-map.md) of the current product
- [ ] Draft [KPI tree](../templates/06-kpi-tree.md) — what metrics leadership actually watches
- [ ] Read last two quarters of roadmap / OKR docs; note gaps vs. reality

**Output:** Spreadsheet or doc: jobs, pains, current solutions, your product's role.

## Week 3 — Earn a small win

- [ ] ICE-score the backlog (or your slice of it) with eng + design
- [ ] Pick one item you can ship or unstick in 2 weeks
- [ ] Write a lightweight [PRD](../templates/03-prd.md) for that item only
- [ ] Align timeline with [planning timeline](../templates/07-planning-timeline.md)

**Output:** One shipped or unblocked thing + written alignment artifact.

## Week 4 — Show your operating system

- [ ] Publish [roadmap](../templates/02-roadmap.md) draft (now / next / later) to core stakeholders
- [ ] Run one [mock press release](../templates/04-mock-press-release.md) on the next bet-sized initiative
- [ ] Log 2–3 [decisions](../decisions/_template.md) with DACI
- [ ] 30-day retro: what was wrong in week-1 assumptions?

**Output:** Stakeholders know how you think, prioritize, and communicate.

## Standing habits (after day 30)

| Cadence | Artifact |
|---------|----------|
| Weekly | Update `products/<name>/roadmap.md` + `workspace/weekly-plan.md` |
| Per initiative | PRD or one-pager before eng kickoff |
| Per decision | `decisions/YYYY-MM-DD-<slug>.md` |
| Per quarter | Refresh BMC + KPI tree if strategy shifted |
| Per research session | `workspace/user-research.md` → JTBD rows |

## Situational guides

- **Feature factory / output-heavy org:** [guides/feature-factory.md](../guides/feature-factory.md)
- **Five-bucket map:** [ORGANIZATION.md](../ORGANIZATION.md)
- **External deep dives:** [references.md](../references.md)
