# HUNT-AGENT

Personal job-hunt automation agent. Scrapes job listings from public APIs and
Google Jobs, filters to product-adjacent non-senior roles, and stores leads for
the RES resume generation pipeline.

## Architecture

Two parallel paths, each fetching independently:

```
                  ┌── Google Jobs ──→ SerpAPI ──→ SearchAPI.io (fallback)
                  │                   (──mode api)
User runs ────────┤
                  └── Direct ATS  ──→ Greenhouse API
                                      Lever API
                                      Ashby API
                                      SmartRecruiters API
```

Results merge → dedup → filter pipeline (keywords → senior exclusion → product-adjacent)
→ persist to `leads.json` + `job_leads.md`.

## Files

| File | Purpose |
|------|---------|
| `search_profile.json` | Roles × locations + keywords + exclusion rules (drives Google Jobs queries) |
| `target_companies.json` | Company board tokens for direct ATS scraping |
| `scraper/` | Python scraping package |
| `leads.json` | Structured lead storage (auto-appended) |
| `job_leads.md` | Human-readable lead table (auto-regenerated from JSON) |
| `.env` | API keys for SerpAPI + SearchAPI.io (gitignored) |
| `docs/optimization_plan.md` | Planned dedup & token-economy improvements |
| `job_search_profile.md` | Human-readable profile reference |
| `weekly_job_hunt_workflow.md` | Step-by-step weekly workflow |
| `weekly_run_prompt.md` | Reusable session prompt |

## Quick start

```bash
cd HUNT-AGENT

# Create .env with API keys:
echo 'SERPAPI_KEY=your_key_here' >> .env
echo 'SEARCHAPI_KEY=your_key_here' >> .env   # optional fallback

# Full run (Google Jobs + ATS):
python -m scraper.run --dry-run

# Save leads:
python -m scraper.run
```

## How the agent searches

### Path 1: Google Jobs (`--mode api` — default)

1. Reads 6 roles × 5 locations from `search_profile.json` → generates 30 search
   queries (one per role × location combo)
2. For each query, calls **SerpAPI** `google_jobs` engine with your `SERPAPI_KEY`
3. SerpAPI returns structured JSON aggregated from LinkedIn, Indeed, Glassdoor,
   ZipRecruiter, and company career pages
4. If SerpAPI fails or returns 0 results, falls back to **SearchAPI.io** with the
   same query using `SEARCHAPI_KEY`
5. Each result parsed into a `Lead` (title, company, URL, location, snippet)

Three modes via `--mode`:

| Mode | Behavior |
|------|----------|
| `api` | SerpAPI → SearchAPI.io fallback |
| `auto` | Try `api` first, fall back to `scrape` |
| `scrape` | Headless Chromium via Playwright (Google blocks with CAPTCHA — experimental) |

### Path 2: Direct ATS

1. Reads company board tokens from `target_companies.json`
2. Hits each company's **public API** directly — no auth, no aggregator:
   - **Greenhouse**: `GET https://boards-api.greenhouse.io/v1/boards/{token}/jobs`
   - **Lever**: `GET https://api.lever.co/v0/postings/{company}?mode=json`
   - **Ashby**: GraphQL POST to `https://jobs.ashbyhq.com/api/non-user-graphql`
   - **SmartRecruiters**: `GET https://api.smartrecruiters.com/v1/companies/{company}/postings`
3. Gets every open job at the company — zero aggregation lag

### Post-processing: filter pipeline

Runs in order (cheapest gate first):

1. **Profile keyword match** — regex on `title + description_snippet` against
   `search_profile.json` keywords (product, ai, platform, growth, etc.)
2. **Senior-title exclusion** — drops titles containing senior/sr/lead/staff/
   principal/head of/director/vp/chief (except "Chief of Staff" — allowed)
3. **Product-adjacent requirement** — title must match product/program/growth/
   platform/operations/monetization/ai/ml/hris/marketplace/pricing, or be
   Chief of Staff / BizOps / TPM
4. **Within-run dedup** — by normalized `company|title` key (normalizes
   "Sr" → "Senior", strips punctuation)
5. **Historical dedup** — against saved leads by URL

## CLI reference

```bash
python -m scraper.run [--source SOURCE] [--dry-run] [--discover]
                      [--max-results N] [--mode MODE]
```

| Flag | Default | Description |
|------|---------|-------------|
| `--source` | `all` | `search`, `greenhouse`, `lever`, `ashby`, `smartrecruiters`, `career_pages`, or `all` |
| `--dry-run` | off | Print filtered leads without saving |
| `--discover` | off | Extract board tokens from search result URLs → scrape newly found boards |
| `--max-results` / `-n` | 10 | Results per Google Jobs query |
| `--mode` | `auto` | `api` (SerpAPI/SearchAPI), `scrape` (Playwright), `auto` (api→scrape) |

### Examples

```bash
# Full run — Google Jobs + all ATS boards
python -m scraper.run

# Preview only (ideally pipe to less since output can be long)
python -m scraper.run --dry-run

# Google Jobs only, 20 results per query, API mode
python -m scraper.run --source search --mode api --max-results 20

# Single Greenhouse board
python -m scraper.run --source greenhouse --dry-run

# Search + discover new boards from results
python -m scraper.run --discover --mode api
```

## Configuration

### search_profile.json

Controls what the Google Jobs path searches for:

```json
{
  "roles": ["Product Manager", "Technical Product Manager", ...],
  "locations": ["Remote US Canada", "San Francisco", "Calgary", ...],
  "keywords": ["product", "ai", "ml", "platform", "growth", ...],
  "exclude_titles": ["senior", "sr", "lead", "staff", ...],
  "exclude_industries": ["gambling", "crypto", "defense"]
}
```

Every role × location becomes a search query (6 × 5 = 30 queries). Add/remove
roles and locations to control query count and breadth.

### target_companies.json

Lists companies to scrape via their ATS board APIs:

```json
{
  "greenhouse": ["stripe", "gitlab", "airtable", ...],
  "lever": [],
  "ashby": [],
  "smartrecruiters": [],
  "career_pages": []
}
```

Board token location by ATS:

| ATS | Board token location |
|-----|---------------------|
| Greenhouse | `https://boards.greenhouse.io/{board_token}` |
| Lever | `https://jobs.lever.co/{company}` |
| Ashby | Board token in career page URL (e.g. `jobs.ashbyhq.com/{token}`) |
| SmartRecruiters | Company slug from career page URL |

### .env

```
# Required: SerpAPI key (primary search provider)
SERPAPI_KEY=your_serpapi_key_here

# Optional: SearchAPI.io key (fallback if SerpAPI fails)
SEARCHAPI_KEY=your_searchapi_key_here
```

## Supported data sources

| Source | Provider | Coverage |
|--------|----------|----------|
| Google Jobs (via SerpAPI) | LinkedIn, Indeed, Glassdoor, ZipRecruiter, company career pages, etc. | Any job indexed by Google |
| Greenhouse API | Stripe, GitLab, Airtable, Vercel, Elastic, Plaid, Gusto, Deel, Rippling, Brex, Zillow, DoorDash | Company's complete open listings |
| Lever API | (configurable — add company slugs) | Company's complete open listings |
| Ashby API | (configurable — add board tokens) | Company's complete open listings |
| SmartRecruiters API | (configurable — add company slugs) | Company's complete open listings |
| Career page scrape | Any public career page URL | Whatever CSS selectors extract |

## Dependencies

```bash
pip install requests beautifulsoup4
# Optional (for --mode scrape):
pip install playwright && python -m playwright install chromium
```

Already in `RES/requirements.txt` if using that venv.

## Discovery mode

`--discover` runs after Google Jobs search. It:
1. Parses every search result URL for board tokens (Greenhouse, Lever, Ashby patterns)
2. Skips tokens already in `target_companies.json`
3. Scrapes newly discovered boards

Useful for finding companies you haven't configured yet.

## Optimizations

See `docs/optimization_plan.md` for planned improvements including:
- Progressive query expansion (tiered API calls)
- ATS-first ordering to reduce SerpAPI calls
- ETag-based staleness for Greenhouse
- Adaptive query width
- Budget caps via `--budget N`

## Integration with RES

After scraping, use the RES pipeline (`../RES/`) to generate tailored resumes and
cover letters for high-priority leads:

```bash
cd ../RES
streamlit run app.py
```

Paste a JD, select the lead, and generate.
