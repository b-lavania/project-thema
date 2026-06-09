"""Discover company board tokens from search result URLs.

After a search run, parse job posting URLs for known board patterns
and return board tokens that can be fed back into the board scrapers."""

from __future__ import annotations

import re
from urllib.parse import urlparse

from .board_apis import scrape_greenhouse, scrape_lever, scrape_ashby
from .leads import Lead

# Known board URL patterns → (source_name, extractor_fn, scrape_fn)
BOARD_PATTERNS: list[tuple[re.Pattern, str, callable]] = [
    # boards.greenhouse.io/{board_token}/jobs/...
    (re.compile(r"boards\.greenhouse\.io/([^/]+)"), "greenhouse", scrape_greenhouse),
    # boards-api.greenhouse.io/v1/boards/{board_token}
    (re.compile(r"boards-api\.greenhouse\.io/v1/boards/([^/]+)"), "greenhouse", scrape_greenhouse),
    # jobs.lever.co/{company}
    (re.compile(r"jobs\.lever\.co/([^/]+)"), "lever", scrape_lever),
    # jobs.ashbyhq.com/{board_token}
    (re.compile(r"jobs\.ashbyhq\.com/([^/]+)"), "ashby", scrape_ashby),
]


def extract_board_tokens(leads: list[Lead]) -> dict[str, set[str]]:
    """Scan lead URLs for known board tokens.

    Returns {source_name: {set of tokens}}, e.g.
    {"greenhouse": {"intercom", "figma"}, "lever": {"company-a"}}
    """
    found: dict[str, set[str]] = {}
    for l in leads:
        if not l.url:
            continue
        for pattern, source, _ in BOARD_PATTERNS:
            m = pattern.search(l.url)
            if m:
                token = m.group(1)
                found.setdefault(source, set()).add(token)
    return found


def scrape_discovered_boards(
    discovered: dict[str, set[str]],
    known_tokens: set[str],
) -> list[Lead]:
    """Scrape boards for discovered tokens not already in known_tokens.

    Returns new leads (not yet filtered or deduplicated against existing leads).
    """
    all_leads = []
    for source, tokens in discovered.items():
        scrapers = {
            "greenhouse": scrape_greenhouse,
            "lever": scrape_lever,
            "ashby": scrape_ashby,
        }
        scrape_fn = scrapers.get(source)
        if not scrape_fn:
            continue
        for token in sorted(tokens):
            if token in known_tokens:
                continue
            print(f"  discover/{source}: new board '{token}' — scraping...")
            try:
                leads = scrape_fn(token)
                for l in leads:
                    l.notes = f"Discovered via {source} board search"
                all_leads.extend(leads)
                print(f"    -> {len(leads)} jobs")
            except Exception as e:
                print(f"    -> error: {e}")
    return all_leads
