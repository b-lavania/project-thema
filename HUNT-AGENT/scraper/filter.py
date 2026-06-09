"""Filter job leads by title seniority, relevance, and profile keywords."""

from __future__ import annotations

import re
from typing import Sequence

from .leads import Lead

# Titles to exclude — these indicate senior/leadership IC or management
SENIOR_KEYWORDS = re.compile(
    r"\b(senior|sr\.?|lead|staff|principal|head\s+of|director|vp\s*\.?|"
    r"vice\s+president|manager\s+of|group\s+product)\b",
    re.I,
)

# Product-adjacent keyword signals — at least one must match
PRODUCT_KEYWORDS = re.compile(
    r"\b(product|program|growth|platform|operations?|"
    r"monetization|ai|ml|hris|marketplace|pricing)\b",
    re.I,
)

# Roles that pass even without PRODUCT_KEYWORDS match
ALLOWED_NON_PRODUCT = re.compile(
    r"\b(chief\s+of\s+staff|bizops|biz\s+ops|program\s+manager|tpm)\b",
    re.I,
)

CHIEF_PRODUCT = re.compile(
    r"\bchief\b.*\b(product|ai|ml|growth|platform|technology|digital|revenue|data|operating)", re.I,
)


def is_senior_title(title: str) -> bool:
    title_lower = title.lower()
    if "chief of staff" in title_lower:
        return False
    if bool(SENIOR_KEYWORDS.search(title)):
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
    require_product_adjacent: bool = True,
) -> list[Lead]:
    """Filter leads through up to three stages:

    1. Profile-keyword pre-filter (cheap pass over title+description).
    2. Product-adjacent requirement.
    3. Senior-title exclusion.
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
        if exclude_senior and is_senior_title(l.title):
            continue
        filtered.append(l)
    return filtered
