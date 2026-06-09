# Weekly Job Hunt Workflow

## 1. Scrape new leads

Run the scraper against all configured sources:

```bash
python -m scraper.run
```

Or target a single source:

```bash
python -m scraper.run --source greenhouse
```

Dry-run to preview without saving:

```bash
python -m scraper.run --dry-run
```

New leads are appended to `job_leads.md` and `leads.json` automatically.

## 2. Review & prioritize

- Read new entries in `job_leads.md`
- Check fit against `job_search_profile.md`
- Update stage for existing leads

## 3. Tailor materials

- Use the RES pipeline to generate tailored resume + cover letter per high-priority lead

## 4. Track outcomes

- Update stage (`sent`, `replied`, `screen`, etc.) in `job_leads.md` and `leads.json`
- Note interview prep, rejections, follow-ups

## 5. Weekly review

- Funnel summary: how many sent, replied, screened, interviewed
- What worked this week? What didn't?
- Update `job_search_profile.md` if targeting changes
