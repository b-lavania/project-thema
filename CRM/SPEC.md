# CRM Fugit — Job-Hunt OS SPEC

Single-user Streamlit operating system for a focused 30/90/12-month job-hunt cycle.
Extends the existing RES + HUNT-AGENT stack into a CRM, content engine, and scoreboard
for one specific lane: founding product lead for operational AI in logistics / field service.

## Core thesis

Turn the personal GTM plan (`REPENTANCE/crmfugit.md`) into a repeatable system:
pipeline visibility, bottleneck memos, outreach tracking, weekly artifacts, and a scoreboard
that makes avoidance visible.

## Architecture

```
project-thema/
├── app.py                          # Streamlit entry (already at root)
├── RES/                            # Resume generation (unchanged)
├── HUNT-AGENT/                     # Scraper → leads.json (unchanged)
├── CRM/                         # NEW: Job-hunt OS
│   ├── SPEC.md                     # This file
│   ├── crm/                     # Python package
│   │   ├── __init__.py
│   │   ├── models.py               # SQLAlchemy ORM models
│   │   ├── db.py                   # SQLite engine + session factory
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── companies.py        # CRUD for target companies
│   │   │   ├── pipeline.py         # Stage transitions, SLA alerts
│   │   │   ├── outreach.py         # Log manual outreach actions
│   │   │   ├── memos.py            # LLM bottleneck memo generation
│   │   │   ├── artifacts.py        # Weekly content → markdown files
│   │   │   ├── scoreboard.py       # Metric aggregations + streaks
│   │   │   └── evidence.py         # Evidence ledger for positioning claims
│   │   ├── prompts/
│   │   │   ├── bottleneck_memo.md  # LLM prompt for company memos
│   │   │   ├── outbound_note.md    # LLM prompt for outreach drafts
│   │   │   └── artifact_draft.md   # LLM prompt for weekly artifact
│   │   └── ui/
│   │       ├── __init__.py
│   │       ├── crm_tab.py       # Streamlit tab renderer
│   │       └── components/
│   │           ├── __init__.py
│   │           ├── company_card.py # Company detail card
│   │           ├── pipeline_board.py  # Kanban board
│   │           └── scoreboard_view.py # Metrics + streaks
│   ├── data/
│   │   ├── companies.yaml          # Curated target list (source of truth)
│   │   └── published/              # Weekly artifacts (markdown → served by Streamlit)
│   └── crm.db                   # SQLite database (gitignored)
```

## Data model

### Company

Target company in the pipeline.

```sql
CREATE TABLE companies (
    id            TEXT PRIMARY KEY,    -- uuid
    name          TEXT NOT NULL,
    url           TEXT,
    linkedin_url  TEXT,
    careers_url   TEXT,
    industry      TEXT,                -- logistics, field-service, marketplace, etc.
    segment       TEXT NOT NULL,       -- dream | realistic | consulting
    stage         TEXT NOT NULL DEFAULT 'sourced',  -- sourced | researching | contacted | conversation | applied | interview | onsite | offer | rejected | ghosted
    hypothesis    TEXT,                -- bottleneck hypothesis (LLM-generated or manual)
    notes         TEXT,
    key_people    TEXT,                -- JSON array of {name, role, linkedin}
    date_added    TEXT NOT NULL,
    date_updated  TEXT NOT NULL,
    date_stage_changed TEXT
);
```

### Outreach

Log of every manual outreach action.

```sql
CREATE TABLE outreach (
    id            TEXT PRIMARY KEY,
    company_id    TEXT NOT NULL REFERENCES companies(id),
    channel       TEXT NOT NULL,       -- email | linkedin | warm_intro | application
    action        TEXT NOT NULL,       -- sent | replied | booked | follow_up
    subject       TEXT,                -- email subject or LinkedIn connection note preview
    body          TEXT,                -- full text of the outreach
    contact_name  TEXT,                -- who was contacted
    contact_role  TEXT,
    date          TEXT NOT NULL,
    response      TEXT,                -- reply text if any
    response_date TEXT,
    notes         TEXT
);
```

### Memo

Generated bottleneck hypotheses for target companies.

```sql
CREATE TABLE memos (
    id            TEXT PRIMARY KEY,
    company_id    TEXT NOT NULL REFERENCES companies(id),
    stated_problem TEXT,               -- what the company says they need
    real_bottleneck TEXT,              -- what the company actually needs
    wrong_solution TEXT,               -- what they're probably building or buying
    metric_to_move TEXT,               -- the business lever
    full_memo     TEXT,                -- complete rendered memo (markdown)
    date_created  TEXT NOT NULL,
    version       INTEGER NOT NULL DEFAULT 1
);
```

### Artifact

Weekly proof content published for distribution.

```sql
CREATE TABLE artifacts (
    id            TEXT PRIMARY KEY,
    title         TEXT NOT NULL,
    topic         TEXT NOT NULL,       -- bottleneck | dispatch | ai-in-ops | pricing | etc.
    body          TEXT NOT NULL,       -- markdown content
    file_path     TEXT,                -- path in data/published/
    date_created  TEXT NOT NULL,
    published     INTEGER NOT NULL DEFAULT 0,
    published_to  TEXT                 -- linkedin | github | internal
);
```

### Evidence

Ledger of positioning claims and supporting evidence.

```sql
CREATE TABLE evidence (
    id            TEXT PRIMARY KEY,
    claim         TEXT NOT NULL,       -- positioning statement
    evidence      TEXT NOT NULL,       -- proof / case study / metric
    source        TEXT,                -- where this evidence came from
    date_added    TEXT NOT NULL
);
```

### Metric

Daily leading/lagging metric snapshots.

```sql
CREATE TABLE metrics (
    id            TEXT PRIMARY KEY,
    date          TEXT NOT NULL,
    outbound_touches  INTEGER DEFAULT 0,
    warm_intro_requests INTEGER DEFAULT 0,
    conversations      INTEGER DEFAULT 0,
    applications       INTEGER DEFAULT 0,
    replies_received   INTEGER DEFAULT 0,
    interviews_booked  INTEGER DEFAULT 0,
    onsites            INTEGER DEFAULT 0,
    artifacts_published INTEGER DEFAULT 0,
    wip_count          INTEGER DEFAULT 0,
    notes         TEXT
);
```

## Pipeline stages

```
sourced → researching → contacted → conversation → applied → interview → onsite → offer
                                                          ↘ rejected
                                                          ↘ ghosted
```

SLA rules:
- **sourced → researching**: 24h (you should know enough to write a hypothesis)
- **researching → contacted**: 72h (memo done, outreach sent)
- **contacted → conversation**: 7 days (if no reply → follow_up → 7 more days → ghosted)
- **conversation → applied**: 3 days
- **applied → interview**: 14 days

## LLM prompts

### bottleneck_memo.md

Input: company name, URL, industry, hypothesis (if any), any scraped job descriptions.
Output: structured memo with stated problem, real bottleneck, wrong solution, metric to move.
Uses existing `llm_client.py` — same provider/model selection as resume generation.

### outbound_note.md

Input: company name, bottleneck hypothesis, proof pillars (reframe/build/commercialize).
Output: 3 variants of a 2-3 sentence outreach note (cold email, LinkedIn connection, warm intro ask).
Tone: hypothesis-led, not generic. "I noticed X about your ops — the real bottleneck might be Y."

### artifact_draft.md

Input: topic, target audience (ops leaders, founders), key insight.
Output: 400-600 word proof artifact (markdown) suitable for LinkedIn or internal publishing.

## UI: Streamlit tab

Add a 6th tab to `app.py`: **🎯 CRM**

### Section 1: Pipeline Board (default view)

Kanban columns: Sourced | Researching | Contacted | Conversation | Applied | Interview | Onsite

Each card shows: company name, segment badge (dream/realistic/consulting), days in stage, last action.

Click a card → expands to Company Detail Card (below).

### Section 2: Company Detail (inline or modal)

When a company is selected:

```
Company: [name]  Segment: [badge]  Stage: [dropdown]
URL: [link]      LinkedIn: [link]   Careers: [link]

─── Bottleneck Memo ───
[generated or manual memo, editable]
[button: Generate Memo (LLM)]

─── Outreach History ───
[timeline of outreach actions, newest first]
[button: Log Outreach → form for channel, action, subject, body, contact]

─── Resume Link ───
[button: "Generate Resume" → pre-fills Job Details tab with company info]
```

### Section 3: Outreach Queue

Weekly view:
- Mon: companies needing action (stage SLA about to expire)
- Tue-Thu: outreach log form (batch entry)
- Fri: review week — mark conversations, update pipeline

### Section 4: Content Studio

- List of artifacts (drafts + published)
- [button: Generate Artifact] → pick topic → LLM drafts → edit → mark published
- File saved to `CRM/data/published/YYYY-MM-DD_topic.md`
- Preview rendered inline

### Section 5: Scoreboard

Leading metrics (this week vs last):
- Outbound touches
- Warm intro requests
- Conversations
- Artifacts published
- WIP count

Lagging metrics (rolling 4 weeks):
- Replies received
- Interviews booked
- Onsites

Streak counter:
- Days with at least 1 outbound action
- Weeks with at least 1 artifact published

### Section 6: Weekly Review

Friday view:
- Checklist: pipeline reviewed? outreach done? artifact published? scoreboard updated?
- [button: Generate Weekly Summary] → LLM reads metrics + pipeline state → produces 3-line summary
- Parking lot: new ideas that came up this week (recorded, not activated)

## Integration points

### HUNT-AGENT → CRM

- `leads.json` companies can be "promoted" to CRM companies via a button in `hunt_tab.py`
- Lead data (title, company, url, source) maps to Company fields
- Duplicate detection by normalized company name

### CRM → RES (Job Details tab)

- "Generate Resume" button on a company pre-fills `company_name`, `target_role`, `jd_url` in `st.session_state`
- Triggers resume generation pipeline for that specific company

### RES → CRM

- After resume generation, log to `outreach` table: action=application, company=generated company
- Auto-advance company stage to `applied`

## Weekly cadence automation

The UI enforces the weekly cadence from the GTM plan:

| Day | View | Action |
|-----|------|--------|
| Mon | Pipeline Board | Review all companies in stage, check SLA expiry, prioritize |
| Tue-Thu | Outreach Queue | Log outreach actions, follow up on stale contacts |
| Fri | Content Studio + Scoreboard | Publish artifact, update metrics, run weekly review |

Streamlit sidebar shows current day-of-week and suggests the appropriate view.

## File paths

| Path | Purpose |
|------|---------|
| `CRM/crm.db` | SQLite database (gitignored) |
| `CRM/data/companies.yaml` | Curated target list — seed data |
| `CRM/data/published/*.md` | Weekly artifacts (markdown) |
| `CRM/prompts/*.md` | LLM prompt templates |

## Dependencies

No new pip packages. Uses existing stack:
- `streamlit` — UI
- `sqlalchemy` — ORM (already in requirements.txt or add)
- `pyyaml` — load seed companies
- `llm_client.py` — LLM calls (existing)
- `generator.py` — shared prompt infrastructure (existing)

## MVP scope (3 weeks)

### Week 1: Data + CLI
- SQLAlchemy models + SQLite setup
- `companies.yaml` seed data (30-50 target companies)
- CLI commands: `crm add`, `crm memo <company>`, `crm outreach`, `crm metrics`

### Week 2: Streamlit tab
- Pipeline board (kanban)
- Company detail card + memo generation
- Outreach logging form
- Scoreboard (leading + lagging metrics)

### Week 3: Content + integration
- Artifact generator (LLM prompt → markdown → save)
- Weekly review view
- HUNT-AGENT → CRM promotion button
- RES → CRM stage advancement on resume generation

## Not in MVP (future)

- Accountability partner read-only share link
- LinkedIn API integration (manual log for now)
- Email send tracking (manual log for now)
- Scheduled daily metrics snapshot (cron or Streamlit rerun)
- Mobile-responsive layout
- Data export (CSV/JSON)
