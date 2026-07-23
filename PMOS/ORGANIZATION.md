# PMOS organization

How this folder maps to Jarrell's five buckets from [SOURCE.md](SOURCE.md).

## The five buckets

| Bucket | Purpose | Primary paths |
|--------|---------|---------------|
| **Strategy** | How the business works and where it's going | `templates/01`, `02`, `04`; `context/`; `products/<name>/brief.md` |
| **Discovery** | Why customers buy; user journey truth | `templates/05`, `08`; `workspace/user-research.md` |
| **Execution** | Ship with alignment; decide fast | `templates/03`, `07`, `09`, `10`; `products/<name>/roadmap.md`; `decisions/` |
| **Analytics** | Connect work to outcomes | `templates/06`; `products/<name>/metrics.md`; [references.md](references.md) |
| **Career development** | Portable artifacts, learning, interview ammo | `context/`; `decisions/`; `workspace/weekly-plan.md`; `onboarding/` |

## Template → bucket map

| Template | Bucket(s) |
|----------|-----------|
| 01 Business Model Canvas | Strategy |
| 02 Roadmap | Strategy, Execution |
| 03 PRD | Execution |
| 04 Mock press release | Strategy, Discovery |
| 05 Story map | Discovery |
| 06 KPI tree | Analytics |
| 07 Planning timeline | Execution |
| 08 JTBD | Discovery |
| 09 ICE prioritization | Execution |
| 10 DACI | Execution, Strategy |

## Workspace → bucket map

| File | Bucket |
|------|--------|
| `workspace/meeting-notes.md` | Execution, Discovery |
| `workspace/user-research.md` | Discovery |
| `workspace/weekly-plan.md` | Execution, Career development |
| `workspace/scratch.md` | Any |

## Recommended flow (combine tools fluidly)

```
Strategy          Discovery         Execution         Analytics
   │                  │                  │                 │
   BMC ──────────► JTBD ──────────► PRD ──────────► KPI tree
   │                  │                  │                 │
   Roadmap ◄──── Story map      ICE / DACI ◄──── Metrics review
   │                  │                  │
   PR/FAQ             │            Planning timeline
```

**Examples from SOURCE.md:**
- JTBD insights → PRD problem section
- Story map slices → Roadmap now/next/later
- KPI tree gaps → ICE scoring inputs
- DACI decision → `decisions/YYYY-MM-DD-<slug>.md`

## Folder layout (full stack)

```
PMOS/
├── SOURCE.md              # Spec + attribution
├── README.md              # Quick start
├── ORGANIZATION.md        # This file
├── references.md          # External deep dives
├── guides/
│   └── feature-factory.md # Operating in output-heavy orgs
├── templates/             # 10 frameworks (01–10)
├── context/_template/     # Company + product truth
├── products/_template/    # Per-product dossier
├── decisions/             # DACI audit trail
├── workspace/             # Scratch, notes, weekly rhythm
└── onboarding/            # First 30 days
```

---

*Adapted from Rick Jarrell's PMOS thread (Feb 2022). See [SOURCE.md](SOURCE.md).*
