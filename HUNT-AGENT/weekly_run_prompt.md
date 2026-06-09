# Weekly Run Prompt

You are my job-hunt agent. Follow the process below using the files in this directory.

## Context files

- `job_search_profile.md` — my target roles, locations, industries, constraints
- `weekly_job_hunt_workflow.md` — the workflow steps
- `job_leads.md` — current leads with stages and notes
- `leads.json` — structured leads data (same info as the markdown)

## Each session

1. **Read** all four context files to understand my current situation.
2. **Scrape** new leads by running the scraper:
   ```bash
   cd /path/to/HUNT-AGENT && python -m scraper.run
   ```
3. **Review** new leads against my search profile. For each promising lead:
   - Generate a tailored resume + cover letter using the RES pipeline (`../../RES/`)
   - Add notes to the lead entry
4. **Update** stages on existing leads based on my feedback.
5. **Summarize** the funnel: sent / replied / screened / interviewed / offers.
