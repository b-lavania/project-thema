"""Best-effort company career page scraper.

Each company entry specifies a URL and CSS selectors for job listing links.
This is inherently fragile — use board APIs where available."""

from __future__ import annotations

import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from .leads import Lead


def scrape_career_page(entry: dict) -> list[Lead]:
    """Scrape one company career page for job listings.

    ``entry`` format:
        {"company": "Acme", "url": "https://acme.com/careers",
         "link_selector": "a[href*=job], a[href*=career]",
         "title_selector": "h2, h3, .title"}

    Returns best-effort Lead list. Empty on failure.
    """
    url = entry.get("url", "")
    company = entry.get("company", url)
    link_sel = entry.get("link_selector", "a[href]")

    try:
        resp = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
    except requests.RequestException:
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    links = soup.select(link_sel) if link_sel else soup.find_all("a", href=True)

    title_sel = entry.get("title_selector", "")
    leads = []
    seen_urls = set()

    for a in links:
        href = a.get("href", "")
        if not href or href.startswith("#") or href.startswith("javascript"):
            continue
        full_url = urljoin(url, href)

        if full_url in seen_urls:
            continue
        # Heuristic: skip non-job paths
        job_pattern = re.compile(r"(job|career|position|open(ing)?|role)", re.I)
        if not job_pattern.search(full_url) and not job_pattern.search(a.get_text()):
            continue
        seen_urls.add(full_url)

        # Extract title from selector or link text
        if title_sel and soup.select_one(title_sel):
            title = soup.select_one(title_sel).get_text(strip=True)
        else:
            title = a.get_text(strip=True)
        if not title:
            continue
        # Simple heuristic: skip short link texts
        if len(title) < 5:
            continue

        leads.append(Lead(
            title=title[:200],
            company=company,
            url=full_url,
            source="career_page",
        ))

    return leads


def scrape_career_pages(entries: list[dict]) -> list[Lead]:
    """Scrape multiple career page entries. Returns all leads found."""
    all_leads = []
    for entry in entries:
        if not entry.get("enabled", True):
            continue
        all_leads.extend(scrape_career_page(entry))
    return all_leads
