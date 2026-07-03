# Weekly Job Hunt Workflow — Ops-AI Lane

**Dual-path model:** CRM direct outreach is primary. HUNT-AGENT catches posted roles at target companies.

## Three trackers

| Tracker | Location | Purpose |
|---------|----------|---------|
| CRM Scoreboard | `CRM/tempus.db` | Outbound touches, conversations, artifacts |
| HUNT leads | `HUNT-AGENT/leads.json` | Scraped role pipeline |
| Outcomes | `RES/data/applications.csv` | Post-generation application funnel |

---

## Weekly cadence

| Day | Action |
|-----|--------|
| **Monday** | CRM Pipeline review — Batch-1 filter, SLA breaches |
| **Tuesday** | **HUNT ATS Only** — check PM roles at verified board slugs |
| **Wed–Thu** | CRM outreach — 5 touches/day, log every action |
| **Friday** | Optional artifact + weekly review (enable Full CRM OS) |
| **Monthly** | Scoped board discovery + `scripts/discover_candidates.py` |

---

## Tuesday: ATS scrape (secondary motion)

From project root:

```bash
cd HUNT-AGENT
python3 -m scraper.run --lane ops_ai --allowlist-only --dry-run
python3 -m scraper.run --lane ops_ai --allowlist-only
```

Or in Streamlit: **Job Search** tab → **ATS Only** (primary button).

- **Ops-AI lane only** toggle ON (default) — only verified `company_candidates.json` companies
- Review leads with fit score ≥ 70 (high priority)
- **+ CRM** to add company to Pipeline with hypothesis
- **Gen** → Job Details → Generate → Outcomes

---

## Monthly: discovery mode

Google Jobs + domain queries (higher SerpAPI cost):

```bash
python3 -m scraper.run --lane ops_ai --source search --max-results 8
```

Scoped board discovery:

```bash
python3 -m scraper.run --discover-boards
```

Grow candidate list:

```bash
python3 scripts/discover_candidates.py --yc yc_export.csv --crunch crunch_export.csv
# Review candidates_review.md → merge verified into company_candidates.json
# Sync target_companies.json slugs from verified candidates only
```

---

## End-to-end flow

```
CRM Pipeline → memo + draft outreach → send → log → stage contacted
     ↓
HUNT finds posted role → + CRM or Gen → Outcomes
     ↓
Generate resume → CRM auto-advances to applied (if company in pipeline)
```

---

## Configuration files

| File | Role |
|------|------|
| `search_profile.json` | Roles, domain_queries, exclude_titles, lane=ops_ai |
| `company_candidates.json` | Master company registry (verified = scrape allowlist) |
| `target_companies.json` | ATS board slugs (derived from verified candidates) |
| `denylist_companies.txt` | Giants + recruiters to screen out |

**Rule:** Never edit `target_companies.json` independently — flow from verified candidates → slugs.
