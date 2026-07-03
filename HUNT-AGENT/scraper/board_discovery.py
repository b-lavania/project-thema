"""Discover board tokens by searching Google for ATS URL patterns.

Uses SerpAPI with domain-scoped queries for ops-AI lane discovery.
"""

from __future__ import annotations

import re
from urllib.parse import urlparse

import requests

from .company_fit import load_denylist
from .env import SERPAPI_KEY
from .config import load_target_companies, save_target_companies

SERPAPI_BASE = "https://serpapi.com/search.json"
PAGES_PER_ATS = 3
RESULTS_PER_PAGE = 10

# Generic discovery (legacy)
ATS_PATTERNS_GENERIC = [
    {
        "name": "greenhouse",
        "query": 'site:boards.greenhouse.io "jobs"',
        "regex": re.compile(r"boards\.greenhouse\.io/([^/]+)"),
    },
    {
        "name": "lever",
        "query": "site:jobs.lever.co",
        "regex": re.compile(r"jobs\.lever\.co/([^/]+)"),
    },
    {
        "name": "ashby",
        "query": "site:jobs.ashbyhq.com",
        "regex": re.compile(r"jobs\.ashbyhq\.com/([^/]+)"),
    },
    {
        "name": "smartrecruiters",
        "query": 'site:careers.smartrecruiters.com "Careers"',
        "regex": re.compile(r"careers\.smartrecruiters\.com/([^/]+)"),
    },
]

# Ops-AI scoped discovery (too-greedy lane)
ATS_PATTERNS_SCOPED = [
    {
        "name": "greenhouse",
        "query": "site:boards.greenhouse.io logistics AI freight product",
        "regex": re.compile(r"boards\.greenhouse\.io/([^/]+)"),
    },
    {
        "name": "lever",
        "query": 'site:jobs.lever.co dispatch "product manager" AI',
        "regex": re.compile(r"jobs\.lever\.co/([^/]+)"),
    },
    {
        "name": "ashby",
        "query": 'site:jobs.ashbyhq.com freight dispatch "product manager"',
        "regex": re.compile(r"jobs\.ashbyhq\.com/([^/]+)"),
    },
    {
        "name": "smartrecruiters",
        "query": 'site:careers.smartrecruiters.com logistics freight AI',
        "regex": re.compile(r"careers\.smartrecruiters\.com/([^/]+)"),
    },
]

SKIP_TOKENS = frozenset({"jobs", "assets", "api", "v1", "_next", "careers"})


def _search_serpapi(query: str, page: int = 0) -> list[dict]:
    """Run a Google search via SerpAPI and return organic results."""
    if not SERPAPI_KEY:
        return []
    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": RESULTS_PER_PAGE,
    }
    if page > 0:
        params["start"] = page * RESULTS_PER_PAGE
    try:
        resp = requests.get(SERPAPI_BASE, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if data.get("error"):
            print(f"    [discover] SerpAPI error: {data['error']}")
            return []
        return data.get("organic_results", [])
    except requests.RequestException as e:
        print(f"    [discover] SerpAPI request failed: {e}")
        return []


def _extract_tokens(results: list[dict], pattern: re.Pattern) -> set[str]:
    """Extract board tokens from organic result URLs matching the regex."""
    tokens: set[str] = set()
    denylist = load_denylist()
    for r in results:
        link = r.get("link", "") or ""
        title_snippet = f"{r.get('title', '')} {r.get('snippet', '')}".lower()
        m = pattern.search(link)
        if m:
            token = m.group(1).strip().lower().split("?")[0].split("#")[0]
            if not token or token in SKIP_TOKENS:
                continue
            if token in denylist:
                continue
            # Reject giant company tokens appearing in title
            if any(d in title_snippet for d in denylist if len(d) > 4):
                continue
            tokens.add(token)
    return tokens


def discover_boards(*, scoped: bool = True) -> dict[str, set[str]]:
    """Search Google for each ATS pattern and return discovered board tokens."""
    patterns = ATS_PATTERNS_SCOPED if scoped else ATS_PATTERNS_GENERIC
    discovered: dict[str, set[str]] = {}

    for ats in patterns:
        name = ats["name"]
        q = ats["query"]
        regex = ats["regex"]
        print(f"  [discover] {name}: searching \"{q}\"")

        all_tokens: set[str] = set()
        for page in range(PAGES_PER_ATS):
            results = _search_serpapi(q, page)
            if not results:
                if page == 0:
                    print(f"    [discover] {name}: no results")
                break
            tokens = _extract_tokens(results, regex)
            before = len(all_tokens)
            all_tokens.update(tokens)
            if len(all_tokens) == before:
                break
        discovered[name] = all_tokens
        print(f"    [discover] {name}: {len(all_tokens)} tokens")

    return discovered


def merge_into_targets(discovered: dict[str, set[str]], show_new_only: bool = True):
    """Merge discovered tokens into target_companies.json, skipping denylist + existing."""
    existing = load_target_companies()
    denylist = load_denylist()
    added_any = False

    for source, new_tokens in discovered.items():
        known = set(existing.get(source, []))
        fresh = {t for t in new_tokens - known if t.lower() not in denylist}
        if not fresh:
            continue
        added_any = True
        existing.setdefault(source, []).extend(sorted(fresh))
        for t in sorted(fresh):
            print(f"    [discover] +{source}/{t}")

    if added_any:
        save_target_companies(existing)
        print("  [discover] Updated target_companies.json")
    else:
        print("  [discover] No new tokens — already up to date")
