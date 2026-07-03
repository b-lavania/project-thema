# Option A workflow — Ops-AI lane

**Default path:** CRM direct outreach (primary) + HUNT for posted roles (secondary).

## Daily apply path

```
Pipeline (outreach)  →  Job Search (if role posted)  →  Job Details  →  Generate  →  Outcomes
```

| Step | Tab | What happens |
|------|-----|----------------|
| 1 | 🎯 Pipeline | Batch-1 filter → memo → draft outreach → log → stage contacted |
| 2 | 🔍 Job Search | Tuesday ATS scrape; **+ CRM** or **Gen** on high-fit leads |
| 3 | 📋 Job Details | Company/role/JD pre-filled from HUNT or CRM |
| 4 | 🚀 Generate | Resume + cover letter; auto `applications.csv` + CRM `applied` if matched |
| 5 | 📊 Outcomes | Application funnel (sent → interview → offer) |

## Pipeline CRM modes

| Mode | Sidebar setting | What's visible |
|------|-----------------|----------------|
| **Outreach** (default) | Full CRM OS **off** | Pipeline + memo + draft + log on cards |
| **Full OS** | Full CRM OS **on** | + Content Studio, Scoreboard, Weekly Review, Evidence |

Pipeline tab is **on by default**. Outreach mode hides admin surfaces unless you need Friday review.

## Trackers (don't duplicate)

| Tracker | Owns |
|---------|------|
| **Outcomes** | Application funnel after generate |
| **CRM Outreach log** | Founder messages, intros, conversations |
| **HUNT leads.json** | Scraped role stages before/without generate |

## BOOTCAMP

Separate app (`streamlit run BOOTCAMP/app.py`). PM skill sprint only — not part of daily apply loop.

## See also

- [HUNT-AGENT/weekly_job_hunt_workflow.md](../../HUNT-AGENT/weekly_job_hunt_workflow.md) — Tuesday ATS + monthly discovery
- [REPENTANCE/90-day-scoreboard.md](../../REPENTANCE/90-day-scoreboard.md) — metrics and cadence
