# Draft: CRM Integration Tighten

## Requirements (confirmed)

1. **tab_tempus → tab_crm rename** — Rename variable in app.py (declaration + usage)
2. **RES → CRM auto-advance** — On successful resume generation, if `company_name` exactly matches a CRM company name, auto-advance stage to `applied` and log outreach entry
3. **CRM "Generate Resume" tab auto-switch** — Use `st.session_state.active_tab` index (0=Job Details) to redirect user
4. **Sidebar cadence widget** — Move day-of-week hint from crm_tab.py info bar to sidebar in app.py, visible on every tab
5. **HUNT-AGENT → CRM promotion button** — Add "Promote to CRM" button in lead card in hunt_tab.py

## Technical Decisions

- **Company matching**: Exact name match (case-insensitive)
- **Tab switching**: Session state tab index pattern
- **Sidebar placement**: Every tab (not Pipeline-only)
- **Artifact file saving**: Already implemented — no work needed

## Scope Boundaries

- **IN**: 5 changes above
- **OUT**: Polish items (collapsible cards, one-number callout, REPENTANCE references in app), artifact file saving (already done)

## Research Findings

- `mark_published()` in CRM/crm/services/artifacts.py:56 already writes to disk — item #5 is DONE
- `import_from_leads()` in CRM/crm/services/companies.py:138 exists but is not wired into hunt_tab.py
- `tab_tempus` used in 2 places: declaration at line 852, usage block at line 1837
- Generate section ends at line 1308 with `status.update(label="Generation complete!")` — ideal hook point for auto-advance
- HUNT-AGENT leads from `HUNT-AGENT/leads.json`, loaded via `from scraper.leads import load_leads`
