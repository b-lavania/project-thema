"""Load search profile + target companies from JSON files.

search_profile.json   — role×location combos + keywords + exclusions
target_companies.json — per-board-type company lists for ATS scraping
"""

from __future__ import annotations

import json
from itertools import product
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]

PROFILE_PATH = BASE / "search_profile.json"
COMPANIES_PATH = BASE / "target_companies.json"

DEFAULT_PROFILE = {
    "roles": ["Product Manager"],
    "locations": ["United States"],
    "keywords": ["product"],
    "exclude_titles": [],
    "exclude_industries": [],
    "lane": "ops_ai",
    "domain_queries": [],
}

DEFAULT_COMPANIES = {
    "greenhouse": [],
    "lever": [],
    "ashby": [],
    "smartrecruiters": [],
    "career_pages": [],
}


def load_profile() -> dict:
    if not PROFILE_PATH.exists():
        return dict(DEFAULT_PROFILE)
    with open(PROFILE_PATH) as f:
        data = json.load(f)
    merged = dict(DEFAULT_PROFILE)
    merged.update(data)
    return merged


def load_target_companies() -> dict:
    if not COMPANIES_PATH.exists():
        return dict(DEFAULT_COMPANIES)
    with open(COMPANIES_PATH) as f:
        return json.load(f)


def save_target_companies(companies: dict):
    """Write updated target companies back to JSON."""
    with open(COMPANIES_PATH, "w") as f:
        json.dump(companies, f, indent=2)
        f.write("\n")


def generate_search_queries(profile: dict) -> list[str]:
    """Generate search queries — domain_queries when lane=ops_ai, else role×location."""
    if profile.get("lane") == "ops_ai" and profile.get("domain_queries"):
        return list(profile["domain_queries"])
    roles = profile.get("roles", DEFAULT_PROFILE["roles"])
    locations = profile.get("locations", DEFAULT_PROFILE["locations"])
    queries = []
    for role, location in product(roles, locations):
        q = f"{role} {location}"
        if q not in queries:
            queries.append(q)
    return queries


def generate_domain_queries(profile: dict) -> list[str]:
    """Return domain_queries if set, else build from roles + keywords."""
    if profile.get("domain_queries"):
        return list(profile["domain_queries"])
    roles = profile.get("roles", ["Product Manager"])
    keywords = profile.get("keywords", ["logistics"])
    domain_kw = [k for k in keywords if k in (
        "logistics", "freight", "trucking", "dispatch", "field service",
        "supply chain", "quoting", "tms", "last mile", "brokerage",
    )][:3]
    if not domain_kw:
        domain_kw = ["logistics", "freight"]
    queries = []
    for role in roles[:3]:
        queries.append(f"{role} {' '.join(domain_kw)} remote")
    return queries
