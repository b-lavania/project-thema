# Optimization Plan: Dedup & Intelligent Search

## 1. Don't Crawl Duplicate Postings

### 1a. Robust within-session dedup
**Problem**: Same job appears across multiple role×location queries (e.g. Stripe PM
shows up under "Product Manager Remote US Canada" AND "Product Manager San Francisco").
Current dedup key `company|title` is fragile — same title with "Sr" vs "Senior" sneaks
dupes through.

**Fix**: Normalize title + company before dedup:

```python
import re
def _dedup_key(l: Lead) -> str:
    t = re.sub(r"\bsr\.?\b", "senior", l.title, flags=re.I)
    t = re.sub(r"[^\w\s]", "", t).strip().lower()
    c = re.sub(r"[^\w\s]", "", l.company).strip().lower()
    return f"{c}|{t}"
```

Store as `leads.DEDUP_KEYS` set alongside `existing_urls`. Apply in both
`run_search_queries` and `append_leads`.

### 1b. Cross-source dedup (Google Jobs vs Direct ATS)
**Problem**: Same posting can appear via Google Jobs AND the company's direct ATS feed.
Currently these are separate paths that don't compare results.

**Fix**: After both paths finish, run a cross-source pass:
1. Parse every `url` for a normalised job-id (Greenhouse `?gh_jid=`, Lever `?lever-`, Ashby path).
2. If two leads share a job-id, keep the one from Direct ATS (more reliable, richer data).
3. The same normalised URL pattern applies to `append_leads` when checking against historicals.

### 1c. Staleness-aware re-scrape
**Problem**: Every full run rescrapes all 12+ company boards regardless of whether
anything changed. Wasteful.

**Fix**: Before scraping a company board:
1. Read a `scraper_state.json` that stores `{board_token: last_etag_or_hash}`.
2. For Greenhouse: send `If-None-Match` with the cached ETag from last response.
   If server returns `304 Not Modified`, skip the board — zero jobs processed.
3. For others without ETag support: store a content hash of the previous API response
   and compare before parsing.

### 1d. URL dedup at persistence layer
**Problem**: `append_leads` in `leads.py` dedups only by exact `url` string.
Same job with different tracking params (`?gh_jid=123` vs `?gh_jid=123&source=linkedin`)
counts as two leads.

**Fix**: Normalise URLs when storing the dedup set:
```python
from urllib.parse import urlparse, urlencode, parse_qs
def _normalise_url(url: str) -> str:
    p = urlparse(url)
    qs = parse_qs(p.query)
    # Keep only job-id params, drop tracking
    keep = {k: qs[k] for k in ("gh_jid", "lever-") if k in qs}
    return f"{p.scheme}://{p.netloc}{p.path}?" + urlencode(keep, doseq=True) if keep else f"{p.scheme}://{p.netloc}{p.path}"
```

---

## 2. Token Economics & Smarter Searching

### 2a. Progressive query expansion
**Problem**: 30 role×location queries × 2-3 API calls each = 60-90 SerpAPI calls per
run. Most return overlapping results.

**Fix**: Run queries in tiers:

```
Tier 1 (high-signal) — 6 queries:
  [PM, TPM] × [Remote US Canada, San Francisco]
  These are the highest-yield combos. Run first.

Tier 2 (medium-signal) — 6 queries:
  [Platform PM, Technical PM] × [United States, Remote]
  Only run if Tier 1 yielded <max_results per query (signal that supply exists).

Tier 3 (low-signal) — remaining 18 combos:
  [Chief of Staff, BizOps] × [Calgary, Canada, United States]
  Only run if Tier 1+2 combined yielded fewer than (2 × max_results × queries_run).
```

Each tier feeds its results into the shared dedup set so later tiers don't waste
calls on already-seen postings.

### 2b. Adaptive query width
**Problem**: All queries request `max_results=10` regardless of whether the market
for that combo has 3 jobs or 300.

**Fix**: Start each query at `max_results=5`. If the API returns exactly 5
(hit the cap, there are more), ask `count=10` on the same query. Stop after
two rounds or once you have enough.

```python
for cap in (5, 10, 20):
    leads = search_jobs(q, location, max_results=cap)
    if len(leads) < cap:
        break  # market exhausted
```

### 2c. ATS-first ordering
**Problem**: Run order is search → ATS. Search (Google Jobs) burns SerpAPI credits
on postings the ATS scrapers will find cheaper.

**Fix**: Run Direct ATS first. Collect `(company, title)` pairs. Then when running
Google Jobs queries, skip any result whose `(company, title)` already exists in the
ATS set. This eliminates redundant API calls for the same posting.

### 2d. Tiered filter pipeline
**Problem**: Filter passes (`profile_keywords`, `product_adjacent`, `senior_exclude`)
run sequentially on ALL leads. The expensive passes (regex against body text, LLM
classification) touch every row.

**Fix**: Chain filters so the cheapest gate runs first and drops rows early:

```
1. URL dedup (O(1) hash lookup) — drops 0%
2. Profile keyword on title (fast regex) — drops ~60%
3. Senior exclusion on title (fast regex) — drops ~30% of remainder
4. Product-adjacent on title (fast regex) — drops ~10% of remainder
5. Description keyword match (heavier regex) — drops ~15% of remainder
6. LLM classification (expensive) — last resort, only if still >threshold
```

Currently steps 2-4 run in `filter_leads` but on all leads at once.
Move to pipelined generator with early exit:

```python
def filter_pipeline(leads, profile):
    seen = set()
    kw_re = _build_keyword_regex(profile["keywords"])
    for l in leads:
        if _dedup_key(l) in seen:
            continue
        seen.add(_dedup_key(l))
        haystack = f"{l.title} {l.description_snippet}"
        if profile_keywords and not kw_re.search(haystack):
            yield "skip", "no keyword match"
        if not is_product_adjacent(l.title):
            yield "skip", "not product-adjacent"
        if is_senior_title(l.title):
            yield "skip", "senior title"
        yield "keep", l
```

Count skip reasons for a weekly "why leads are dropping" dashboard.

### 2e. SerpAPI budget control
**Problem**: SerpAPI charges per search. 30 queries / run = real cost.

**Fix**: Add `--budget N` flag (default 15 searches). Once the search counter hits
N across all tiers + fallbacks, stop making new API calls for that run. Remaining
queries get the fallback path only (SearchAPI.io or scrape, which may or may not
have their own budgets).

### 2f. Cached query results
**Problem**: Running the same query back-to-back (or across consecutive daily runs)
re-fetches identical results from SerpAPI.

**Fix**: Short-lived query cache in `/tmp/`:
```python
_CACHE: dict[str, tuple[float, list[Lead]]] = {}
CACHE_TTL = 3600  # 1 hour

def _cached_search(q, location, max_results, mode):
    key = f"{q}|{location}|{max_results}|{mode}"
    now = time.time()
    if key in _CACHE and now - _CACHE[key][0] < CACHE_TTL:
        return _CACHE[key][1]
    leads = search_jobs(q, location, max_results, mode)
    _CACHE[key] = (now, leads)
    return leads
```

---

## Implementation priority

| # | Item | Effort | Impact |
|---|------|--------|--------|
| 1 | Normalized dedup key (title+company) | 1h | High — catches ~20% more dupes |
| 2 | ATS-first ordering | 30m | High — reduces SerpAPI calls ~40% |
| 3 | Tiered query expansion | 2h | High — cuts API calls 50%+ in most runs |
| 4 | URL normalization at persistence | 1h | Medium — prevents dupes across sessions |
| 5 | ETag-based staleness for Greenhouse | 2h | Medium — skips ~60% of ATS boards on re-scrape |
| 6 | Adaptive query width | 1h | Medium — saves results on sparse markets |
| 7 | Tiered filter pipeline with counters | 2h | Medium — minor perf gain, major debugging win |
| 8 | In-memory query cache | 30m | Low — saves calls on re-runs within an hour |
| 9 | `--budget N` flag | 30m | Low — safety valve |
