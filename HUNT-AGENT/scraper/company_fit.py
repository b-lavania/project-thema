"""Company-level fit scoring for ops-AI lane."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

from .filter import PM_LANE_TITLE
from .leads import Lead

BASE = Path(__file__).resolve().parents[1]
CANDIDATES_PATH = BASE / "company_candidates.json"
DENYLIST_PATH = BASE / "denylist_companies.txt"

DOMAIN_COMPANY = re.compile(
    r"\b(freight|logistics|trucking|dispatch|tms|broker|carrier|"
    r"field\s+service|supply\s+chain|quoting|last\s+mile)\b",
    re.I,
)
AI_NATIVE = re.compile(
    r"\b(agent|llm|machine\s+learning|computer\s+vision|voice\s+ai|"
    r"automation|or\b|optimization)\b",
    re.I,
)
OPS_WORKFLOW = re.compile(
    r"\b(quoting|dispatch|routing|fill\s+rate|broker|carrier|"
    r"onboarding|tender|load|shipment)\b",
    re.I,
)
RECRUITER = re.compile(
    r"\b(insight\s+global|jobgether|randstad|adecco|robert\s+half|"
    r"teksystems|staffing|recruiting)\b",
    re.I,
)

FIT_GATE = 40
HIGH_PRIORITY = 70


@lru_cache(maxsize=1)
def load_denylist() -> set[str]:
    if not DENYLIST_PATH.exists():
        return set()
    items: set[str] = set()
    for line in DENYLIST_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip().lower()
        if line and not line.startswith("#"):
            items.add(line)
    return items


@lru_cache(maxsize=1)
def load_candidates() -> list[dict]:
    if not CANDIDATES_PATH.exists():
        return []
    with open(CANDIDATES_PATH, encoding="utf-8") as f:
        return json.load(f)


def _normalize(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (name or "").lower()).strip()


def find_candidate(company: str) -> dict | None:
    norm = _normalize(company)
    if not norm:
        return None
    for c in load_candidates():
        c_norm = _normalize(c.get("name", ""))
        if c_norm == norm or c_norm in norm or norm in c_norm:
            return c
    return None


def score_lead(lead: Lead) -> int:
    """Return fit_score 0-100 for a lead."""
    score = 0
    company = lead.company or ""
    norm = _normalize(company)
    haystack = f"{lead.title} {lead.description_snippet}"

    candidate = find_candidate(company)
    if candidate:
        score += 50
        if candidate.get("verified"):
            score += 10
        stage = (candidate.get("stage") or "").lower()
        if stage in ("series_c", "series_d", "late_stage"):
            score -= 30

    if DOMAIN_COMPANY.search(company):
        score += 15
    if AI_NATIVE.search(haystack):
        score += 15
    if OPS_WORKFLOW.search(haystack):
        score += 15
    if PM_LANE_TITLE.search(lead.title):
        score += 10

    denylist = load_denylist()
    for token in denylist:
        if token in norm or norm in token:
            score -= 100
            break

    if RECRUITER.search(company) or RECRUITER.search(haystack):
        score -= 50

    return max(0, min(100, score))


def passes_fit_gate(lead: Lead, min_score: int = FIT_GATE) -> bool:
    return score_lead(lead) >= min_score


def allowlist_only_pass(lead: Lead) -> bool:
    """True if company is on verified allowlist."""
    candidate = find_candidate(lead.company)
    return bool(candidate and candidate.get("verified"))


def filter_by_fit(
    leads: list[Lead],
    *,
    min_score: int = FIT_GATE,
    allowlist_only: bool = False,
) -> tuple[list[Lead], list[Lead]]:
    """Return (passed, rejected) leads."""
    passed: list[Lead] = []
    rejected: list[Lead] = []
    for lead in leads:
        if allowlist_only and not allowlist_only_pass(lead):
            rejected.append(lead)
            continue
        if score_lead(lead) >= min_score:
            passed.append(lead)
        else:
            rejected.append(lead)
    return passed, rejected


def hypothesis_for_company(company: str) -> str:
    candidate = find_candidate(company)
    if candidate:
        return candidate.get("hypothesis", "") or ""
    return ""
