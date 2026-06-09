"""Scrape job listings from public job board APIs."""

from __future__ import annotations

import requests

from .leads import Lead

GREENHOUSE_BASE = "https://boards-api.greenhouse.io/v1/boards/{board}/jobs"
LEVER_BASE = "https://api.lever.co/v0/postings/{company}?mode=json"
ASHBY_BASE = "https://api.ashbyhq.com/posting-api/job-board/{board_token}"
SMARTR_BASE = "https://api.smartrecruiters.com/v1/companies/{company}/postings"


def scrape_greenhouse(board_token: str) -> list[Lead]:
    """Fetch all active jobs from a Greenhouse board.

    Handles two response formats:
      - Structured (offices as list of dicts with name/location)
      - Flat (location as string, company_name at root)
    """
    url = GREENHOUSE_BASE.format(board=board_token)
    resp = requests.get(url, params={"content": "true", "per_page": 100}, timeout=30)
    if resp.status_code == 404:
        return []
    resp.raise_for_status()
    data = resp.json()
    leads = []
    for job in data.get("jobs", []):
        title = job.get("title", "")
        company = job.get("company_name", board_token.capitalize())

        # Location: structured offices array or flat string
        raw_locs = job.get("offices", "")
        if isinstance(raw_locs, list):
            location = "; ".join(
                f"{o.get('name', '')}, {o.get('location', '')}" for o in raw_locs
            ) if raw_locs else ""
        else:
            location = job.get("location", raw_locs) or ""

        # Description if available
        raw_content = job.get("content", "")
        if isinstance(raw_content, dict):
            snippet = (raw_content.get("description", "") or "")[:400].strip()
        elif isinstance(raw_content, str):
            snippet = raw_content[:400].strip()
        else:
            snippet = ""

        url = job.get("absolute_url", "")
        if title and url:
            leads.append(Lead(
                title=title,
                company=company,
                url=url,
                source="greenhouse",
                location=location,
                description_snippet=snippet,
            ))
    return leads


def scrape_lever(company: str) -> list[Lead]:
    """Fetch all postings from a Lever company page."""
    url = LEVER_BASE.format(company=company.lower())
    resp = requests.get(url, timeout=30)
    if resp.status_code == 404:
        return []
    resp.raise_for_status()
    data = resp.json()
    if not isinstance(data, list):
        return []
    leads = []
    for job in data:
        title = job.get("text", "")
        location = job.get("categories", {}).get("location", "")
        desc = job.get("description", "") or ""
        snippet = desc[:400].strip() if desc else ""
        url = job.get("hostedUrl", "")
        if title and url:
            leads.append(Lead(
                title=title,
                company=job.get("country", company).capitalize(),
                url=url,
                source="lever",
                location=location,
                description_snippet=snippet,
            ))
    return leads


def scrape_ashby(board_token: str) -> list[Lead]:
    """Fetch all jobs from an Ashby job board (GET, not POST)."""
    url = ASHBY_BASE.format(board_token=board_token)
    resp = requests.get(url, params={"maxResults": 100}, timeout=30)
    if resp.status_code in (404, 400, 401):
        return []
    resp.raise_for_status()
    data = resp.json()
    jobs = data.get("jobs", [])
    leads = []
    for job in jobs:
        title = job.get("title", "")
        loc = job.get("location", "") or ""
        secondary = job.get("secondaryLocations", [])
        if secondary:
            locs = [s.get("location", "") for s in secondary if s.get("location")]
            if locs:
                loc = f"{loc}; {'; '.join(locs)}" if loc else "; ".join(locs)
        snippet = (job.get("descriptionPlain") or job.get("descriptionHtml") or "")[:400].strip()
        url = job.get("jobUrl", "")
        if title and url:
            leads.append(Lead(
                title=title,
                company=board_token.capitalize(),
                url=url,
                source="ashby",
                location=loc,
                description_snippet=snippet,
            ))
    return leads


def scrape_smartrecruiters(company: str) -> list[Lead]:
    """Fetch all postings from a SmartRecruiters company page."""
    url = SMARTR_BASE.format(company=company.lower())
    resp = requests.get(url, timeout=30)
    if resp.status_code == 404:
        return []
    resp.raise_for_status()
    data = resp.json()
    content = data.get("content", [])
    leads = []
    for job in content:
        title = job.get("name", "")
        location = job.get("location", "") or ""
        desc = (job.get("jobDescription", {}).get("text", "") or "")[:400]
        url = job.get("applyUrl", "") or job.get("url", "")
        if title and url:
            leads.append(Lead(
                title=title,
                company=company.capitalize(),
                url=url,
                source="smartrecruiters",
                location=location,
                description_snippet=desc,
            ))
    return leads
