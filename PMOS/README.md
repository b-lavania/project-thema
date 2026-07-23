# PMOS — Product Manager Operating System

A personal toolkit for PM work: templates, context files, and decision logs you can run from day one in a new role.

**Seed framework:** [Rick Jarrell's PMOS thread](https://x.com/heyrickjarrell/status/1498365404435075080) (Feb 2022) — nine templates adopted from Basecamp, Amazon, and others. Unrolled at [Thread Reader](https://threadreaderapp.com/thread/1498365404435075080.html). Full spec: [SOURCE.md](SOURCE.md).

## What this is

| Layer | Path | Purpose |
|-------|------|---------|
| **Templates** | `templates/` | Fillable frameworks — BMC, roadmap, PRD, PR/FAQ, story map, KPI tree, timeline, JTBD, ICE, DACI |
| **Context** | `context/` | Company, product, and stakeholder truth for a new role |
| **Products** | `products/` | One folder per product or initiative you own |
| **Decisions** | `decisions/` | DACI-backed decision log |
| **Workspace** | `workspace/` | Meeting notes, user research, weekly plans, scratch |
| **Guides** | `guides/` | Situational playbooks (e.g. feature-factory mode) |

Not wired into Streamlit. Markdown-first, like `BOOTCAMP/` — open files, fill them in, point Cursor at the folder when you want AI help. Export to Notion/Figma/Miro when stakeholders need collaboration — see [references.md](references.md).

## Five-bucket organization

From Jarrell's thread updates — see [ORGANIZATION.md](ORGANIZATION.md) for the full map:

| Bucket | What lives here |
|--------|-----------------|
| **Strategy** | BMC, roadmap, mock PR/FAQ, company context |
| **Discovery** | JTBD, story map, user research log |
| **Execution** | PRD, planning timeline, ICE, DACI, meeting notes |
| **Analytics** | KPI tree, product metrics, `products/<name>/metrics.md` |
| **Career development** | Decision log, weekly plan, context portability |

## Goals of a PMOS

From Jarrell's thread:

- Toolkit that applies to any PM role (with situational tweaks)
- Fast orientation to product, business model, and stakeholders
- Collaborative artifacts — short, legible, easy to share (Notion/Figma/Slides as needed)

## Quick start (new role)

1. Copy `context/_template/` → `context/<company-slug>/`
2. Fill `company.md` and `product.md` in week one
3. Run `templates/01-business-model-canvas.md` before your first strategy conversation
4. Copy `products/_template/` → `products/<product-slug>/` and maintain `roadmap.md`
5. Log every non-trivial call in `decisions/` with DACI fields

See [onboarding/first-30-days.md](onboarding/first-30-days.md) for a day-by-day checklist.

## The ten templates

| # | Template | Bucket | When to use |
|---|----------|--------|-------------|
| 1 | [Business Model Canvas](templates/01-business-model-canvas.md) | Strategy | New company, new segment, or "how does this business work?" |
| 2 | [Roadmap](templates/02-roadmap.md) | Strategy · Execution | Now / next / later + 6-week cycles |
| 3 | [PRD](templates/03-prd.md) | Execution | Alignment before build — short, execution-focused |
| 4 | [Mock press release](templates/04-mock-press-release.md) | Strategy · Discovery | Amazon-style working backwards |
| 5 | [Story map](templates/05-story-map.md) | Discovery | User-journey view of the roadmap |
| 6 | [KPI tree](templates/06-kpi-tree.md) | Analytics | Connect features to business impact |
| 7 | [Planning timeline](templates/07-planning-timeline.md) | Execution | Deadlines without Gantt hell |
| 8 | [JTBD](templates/08-jtbd.md) | Discovery | Why customers actually buy |
| 9 | [ICE prioritization](templates/09-ice-prioritization.md) | Execution | Rank backlog fast |
| 10 | [DACI](templates/10-daci.md) | Execution · Strategy | Clear roles for decisions |

Jarrell's thread title says "9 templates"; the unroll includes planning timeline and DACI as distinct tools (10 total in `templates/`).

## Feature factory / slop-shop mode

When the org ships features without outcomes, PMOS still works as a **personal** operating system — minimum viable rigor, decision receipts, metrics you own. See [guides/feature-factory.md](guides/feature-factory.md).

## Using with Cursor

When working in this repo, reference `PMOS/context/<company>/` and the relevant template so the model starts from your written truth instead of inventing company facts.

```
Read PMOS/context/acme/product.md and PMOS/templates/03-prd.md.
Draft a PRD for [initiative] using only facts from context/.
```

## Related docs

| Doc | Purpose |
|-----|---------|
| [SOURCE.md](SOURCE.md) | Jarrell thread spec + attribution |
| [ORGANIZATION.md](ORGANIZATION.md) | Five buckets + template map |
| [references.md](references.md) | Thiago Brum metrics, Notion templates, external sources |
| [guides/feature-factory.md](guides/feature-factory.md) | PM work when output > outcomes |

## Related folders

| Path | Relationship |
|------|----------------|
| `BOOTCAMP/` | PM skill sprint (30-day shock cycle) — practice, not day job |
| `CRM/` | Job-hunt pipeline OS |
| `RES/` | Resume/cover letter generation |
