"""Search-based job discovery via Google Jobs.

Three modes:
  api    — SerpAPI primary, SearchAPI.io fallback
  scrape — headless-browser scrape of Google Jobs via Playwright
  auto   — try api first, fall back to scrape
"""

from __future__ import annotations

import json
import re

import requests
from bs4 import BeautifulSoup

from .env import SERPAPI_KEY, SEARCHAPI_KEY
from .leads import Lead

SERPAPI_BASE = "https://serpapi.com/search.json"
SEARCHAPI_BASE = "https://www.searchapi.io/api/v1/search"
GOOGLE_JOBS_URL = "https://www.google.com/search"


def _parse_jobs_response(data: dict, source_label: str, max_results: int = 10) -> list[Lead]:
    """Parse Google Jobs results dict into Lead objects."""
    jobs = data.get("jobs_results", [])
    leads = []
    for job in jobs[:max_results]:
        title = job.get("title", "")
        company = (job.get("company_name") or "").strip()
        location = (job.get("location") or "").strip()
        snippet = (job.get("description") or "")[:400].strip()
        via = job.get("via", "")

        link = job.get("source_link", "") or ""
        if not link:
            opts = job.get("apply_options", [])
            for o in opts:
                lnk = o.get("link", "")
                if lnk:
                    link = lnk
                    break
        if not link:
            link = job.get("share_link", "")

        if title and company:
            leads.append(Lead(
                title=title,
                company=company,
                url=link,
                source=f"search/{via}" if via else f"search/{source_label}",
                location=location,
                description_snippet=snippet,
            ))
    return leads


def _extract_lead_from_card(card, source_label: str) -> Lead | None:
    """Extract a Lead from a Google Jobs HTML card element."""
    title = None
    company = None
    location = None
    link = None
    via = None
    html = str(card)

    for sel in ("h3", "[role='heading']"):
        el = card.select_one(sel)
        if el:
            title = el.get_text(strip=True)
            break
    if not title:
        m = re.search(r'"title"\s*:\s*"([^"]+)"', html)
        if m:
            title = m.group(1)
    if not title:
        return None

    for cls in ("CompanyName", "company"):
        el = card.select_one(f"[class*='{cls}']")
        if el:
            company = el.get_text(strip=True)
            break
    if not company:
        m = re.search(r'"company_name"\s*:\s*"([^"]+)"', html)
        if m:
            company = m.group(1)
    if not company:
        company = ""

    for cls in ("location", "Location", "remote"):
        el = card.select_one(f"[class*='{cls}']")
        if el:
            location = el.get_text(strip=True)
            break
    if not location:
        m = re.search(r'"location"\s*:\s*"([^"]+)"', html)
        if m:
            location = m.group(1)
    if not location:
        location = ""

    a = card.select_one("a[href]")
    if a:
        href = a.get("href", "")
        if href.startswith("/"):
            href = "https://www.google.com" + href
        link = href
    if not link:
        m = re.search(r'"link"\s*:\s*"([^"]+)"', html)
        if m:
            link = m.group(1)
    if not link:
        link = ""

    for cls in ("via", "source"):
        el = card.select_one(f"[class*='{cls}']")
        if el:
            via = el.get_text(strip=True)
            break
    if not via:
        m = re.search(r'"via"\s*:\s*"([^"]+)"', html)
        if m:
            via = m.group(1)

    src = f"scrape/{via}" if via else f"scrape/{source_label}"
    return Lead(title=title, company=company, url=link, source=src, location=location)


def fetch_via_direct_scrape(query: str, location: str = "United States", max_results: int = 10) -> list[Lead]:
    """Attempt direct scrape of Google Jobs via Playwright headless browser.

    NOTE: Google blocks automated scraping (CAPTCHA / sorry page) even from
    headless Chromium. This function will rarely succeed without additional
    evasions (proxies, stealth plugins, etc.). The `api` and `auto` modes
    are the reliable path.
    """
    search_query = f"{query} {location}" if location else query
    url = f"{GOOGLE_JOBS_URL}?q={requests.utils.quote(search_query)}&udm=8&hl=en"

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  [search/scrape] playwright not installed")
        return []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=30000)
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(5000)
            html = page.content()
            final_url = page.url
            browser.close()
    except Exception as e:
        print(f"  [search/scrape] Browser error: {e}")
        return []

    # Google redirected to CAPTCHA
    if "/sorry/" in final_url:
        print("  [search/scrape] Blocked by Google CAPTCHA — try --mode api")
        return []

    soup = BeautifulSoup(html, "html.parser")

    # LD+JSON
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
        except (json.JSONDecodeError, TypeError):
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            if not isinstance(item, dict):
                continue
            if item.get("@type") != "JobPosting":
                continue
            title = (item.get("title") or "").strip()
            company = ""
            h_name = item.get("hiringOrganization") or {}
            if isinstance(h_name, dict):
                company = (h_name.get("name") or "").strip()
            loc = ""
            j_loc = item.get("jobLocation") or {}
            if isinstance(j_loc, dict):
                addr = j_loc.get("address") or {}
                if isinstance(addr, dict):
                    loc = (addr.get("addressLocality") or "")
            link = (item.get("url") or item.get("directApply") or "")
            if title and company:
                leads.append(Lead(
                    title=title, company=company, url=link, source="scrape/ldjson",
                    location=loc,
                ))
    if leads:
        return leads[:max_results]

    # HTML card parsing
    cards = soup.select("[role='listitem']")
    if not cards:
        cards = soup.select("[class*='job'], [class*='card'], [class*='result']")
    for card in cards[:max_results]:
        l = _extract_lead_from_card(card, "scrape")
        if l:
            leads.append(l)

    return leads[:max_results]


def fetch_via_serpapi(query: str, location: str = "United States", max_results: int = 10) -> list[Lead]:
    """Try SerpAPI Google Jobs engine."""
    params = {
        "engine": "google_jobs",
        "q": query,
        "api_key": SERPAPI_KEY,
        "hl": "en",
        "location": location,
    }
    if max_results > 10:
        params["count"] = max_results
    try:
        resp = requests.get(SERPAPI_BASE, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if data.get("error"):
            print(f"  [search/serpapi] API error: {data['error']}")
            return []
        return _parse_jobs_response(data, "serpapi", max_results)
    except requests.RequestException as e:
        print(f"  [search/serpapi] Request failed: {e}")
        return []


def fetch_via_searchapi(query: str, location: str = "United States", max_results: int = 10) -> list[Lead]:
    """Fallback: SearchAPI.io Google Jobs engine."""
    if not SEARCHAPI_KEY:
        return []
    params = {
        "engine": "google_jobs",
        "q": query,
        "api_key": SEARCHAPI_KEY,
        "location": location,
    }
    try:
        resp = requests.get(SEARCHAPI_BASE, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if data.get("error"):
            print(f"  [search/searchapi] API error: {data['error']}")
            return []
        return _parse_jobs_response(data, "searchapi", max_results)
    except requests.RequestException as e:
        print(f"  [search/searchapi] Request failed: {e}")
        return []


def search_jobs(query: str, location: str = "United States", max_results: int = 10, mode: str = "auto") -> list[Lead]:
    """Search for jobs using the selected mode.

    Modes:
      api    — SerpAPI primary, SearchAPI.io fallback
      scrape — direct HTTP scrape of Google Jobs
      auto   — try api first, fall back to scrape
    """
    if mode == "scrape":
        return fetch_via_direct_scrape(query, location, max_results)

    # api or auto: try SerpAPI first
    leads = []
    if SERPAPI_KEY:
        leads = fetch_via_serpapi(query, location, max_results)
        if leads:
            return leads
        print("  [search] SerpAPI returned 0 results", end="")
    else:
        print("  [search] No SERPAPI_KEY", end="")

    if SEARCHAPI_KEY:
        print(" — trying SearchAPI.io")
        leads = fetch_via_searchapi(query, location, max_results)
        if leads:
            return leads
    else:
        print(" — no SEARCHAPI_KEY", end="")

    # auto: fall back to direct scrape if APIs failed
    if mode == "auto":
        print(" — falling back to direct scrape")
        return fetch_via_direct_scrape(query, location, max_results)

    print(" — skipping query")
    return leads


def run_search_queries(queries: list[str], location: str = "United States", max_results: int = 10, mode: str = "auto") -> list[Lead]:
    """Run multiple search queries and return deduplicated leads."""
    seen = set()
    all_leads = []
    for q in queries:
        print(f"  [search] query: {q} (max {max_results}, mode={mode})")
        leads = search_jobs(q, location, max_results, mode)
        for l in leads:
            key = f"{l.company}|{l.title}"
            if key in seen:
                continue
            seen.add(key)
            all_leads.append(l)
    return all_leads
