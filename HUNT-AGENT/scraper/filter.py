"""Filter job leads by title seniority, relevance, and profile keywords."""

from __future__ import annotations

import re
from typing import Sequence

from .leads import Lead

# Lane-target titles — always pass senior exclusion (too-greedy ops-AI PM lane)
LANE_ALLOWED = re.compile(
    r"\b(founding|principal|head\s+of\s+(ai\s+)?product|lead\s+product)\b",
    re.I,
)

# Generic senior IC signals (after lane allowlist)
GENERIC_SENIOR = re.compile(
    r"\b(senior|sr\.?|staff)\b",
    re.I,
)

# Leadership / management titles
LEADERSHIP = re.compile(
    r"\b(director|vp\s*\.?|vice\s+president|manager\s+of|group\s+product)\b",
    re.I,
)

# Product-adjacent keyword signals — at least one must match
PRODUCT_KEYWORDS = re.compile(
    r"\b(product|program|growth|platform|operations?|"
    r"monetization|ai|ml|hris|marketplace|pricing|"
    r"logistics|freight|dispatch|field\s+service|supply\s+chain|quoting|tms)\b",
    re.I,
)

# Roles that pass even without PRODUCT_KEYWORDS match
ALLOWED_NON_PRODUCT = re.compile(
    r"\b(chief\s+of\s+staff|bizops|biz\s+ops|program\s+manager|tpm)\b",
    re.I,
)

CHIEF_PRODUCT = re.compile(
    r"\bchief\b.*\b(product|ai|ml|growth|platform|technology|digital|revenue|data|operating)",
    re.I,
)

PM_LANE_TITLE = re.compile(
    r"\b(founding|principal|head\s+of\s+(ai\s+)?product|lead\s+product|product\s+manager)\b",
    re.I,
)


def is_senior_title(title: str, exclude_titles: Sequence[str] | None = None) -> bool:
    """Return True if title should be excluded as too senior / out of lane."""
    title_lower = title.lower()
    if "chief of staff" in title_lower:
        return False
    if LANE_ALLOWED.search(title):
        return False
    if exclude_titles:
        for ex in exclude_titles:
            if ex.strip().lower() in title_lower:
                return True
    if bool(GENERIC_SENIOR.search(title)):
        return True
    if bool(LEADERSHIP.search(title)):
        return True
    if bool(CHIEF_PRODUCT.search(title)):
        return True
    return False


def is_product_adjacent(title: str) -> bool:
    if bool(PRODUCT_KEYWORDS.search(title)):
        return True
    if bool(ALLOWED_NON_PRODUCT.search(title)):
        return True
    return False


def _build_keyword_regex(keywords: Sequence[str]) -> re.Pattern:
    """Build a case-insensitive regex matching any of the given keywords as whole words."""
    if not keywords:
        return re.compile(r"(?!)")  # never match
    escaped = [re.escape(k) for k in keywords]
    return re.compile(r"\b(" + "|".join(escaped) + r")\b", re.I)


def filter_leads(
    leads: list[Lead],
    exclude_senior: bool = True,
    profile_keywords: Sequence[str] | None = None,
    exclude_titles: Sequence[str] | None = None,
    require_product_adjacent: bool = True,
) -> list[Lead]:
    """Filter leads through up to three stages:

    1. Profile-keyword pre-filter (cheap pass over title+description).
    2. Product-adjacent requirement.
    3. Senior-title exclusion (reads exclude_titles from search_profile when provided).
    """
    keyword_re = _build_keyword_regex(profile_keywords or [])

    filtered = []
    for l in leads:
        if profile_keywords:
            haystack = f"{l.title} {l.description_snippet}"
            if not keyword_re.search(haystack):
                continue
        if require_product_adjacent and not is_product_adjacent(l.title):
            continue
        if exclude_senior and is_senior_title(l.title, exclude_titles=exclude_titles):
            continue
        filtered.append(l)
    return filtered
