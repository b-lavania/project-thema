"""Board APIs Watcher: fetch, normalize, filter, and store job postings.

Stores data in JSONL (RES/data/jobs.jsonl) for Git-friendly persistence.
Supports Greenhouse, Lever, and Ashby public job board APIs.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup

RES_ROOT = Path(__file__).resolve().parent
JOBS_JSONL_PATH = RES_ROOT / "data" / "jobs.jsonl"

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MIN_JD_LENGTH = 200

CANADA_PATTERNS = [
    "canada",
    "canadian",
    "toronto", "vancouver", "montreal", "calgary", "edmonton",
    "ottawa", "waterloo", "kitchener", "hamilton", "winnipeg",
    "saskatoon", "regina", "halifax", "quebec", "bc", "ab", "on", "qc",
    "sk", "mb", "ns", "nb", "nl", "pe", "yt", "nt", "nu",
]

REMOTE_PATTERNS = ["remote", "work from home", "wfh", "anywhere", "distributed"]
NA_PATTERNS = ["north america", "na", "us", "usa", "united states", "americas"]

INCLUDE_TITLE_PATTERNS = [
    r"product\s*manager",
    r"senior\s+product\s+manager",
    r"staff\s+product\s+manager",
    r"group\s+product\s+manager",
    r"principal\s+product\s+manager",
    r"technical\s+product\s+manager",
    r"tpm\b",
    r"product\s+owner",
]

EXCLUDE_TITLE_PATTERNS = [
    r"program\s+manager",
    r"project\s+manager",
    r"implementation",
    r"coordinator",
    r"head\s+of\s+product",
    r"vp\s+product",
    r"chief\s+product\s+officer",
    r"cpo\b",
    r"director\s+of\s+product",
]

DEFAULT_SEED = [
    {"company": "Turvo", "platform": "lever", "slug": "turvo"},
    {"company": "ShipBob", "platform": "greenhouse", "slug": "shipbobinc"},
    {"company": "Bringg", "platform": "greenhouse", "slug": "bringg"},
    {"company": "Recharge", "platform": "greenhouse", "slug": "recharge"},
    {"company": "Instabase", "platform": "greenhouse", "slug": "instabase"},
    {"company": "Paddle", "platform": "ashby", "slug": "paddle"},
    {"company": "Cohere", "platform": "ashby", "slug": "cohere"},
]


# ---------------------------------------------------------------------------
# JSONL helpers
# ---------------------------------------------------------------------------
@dataclass
class JobRecord:
    id: str
    source: str
    company: str
    title: str
    location: str
    url: str
    posted_at: str | None
    jd_raw: str
    jd_structured: dict[str, list[str]] = field(default_factory=lambda: {"duties": [], "requirements": [], "tools": []})
    taxonomy: dict[str, Any] = field(default_factory=dict)
    status: str = "discovered"
    status_history: list[dict[str, str]] = field(default_factory=list)
    fit: dict[str, Any] = field(default_factory=lambda: {"coverage": 0.0, "notes": "", "score": 0, "explanation": ""})
    generated: dict[str, Any] = field(default_factory=lambda: {"resume_path": None, "cover_letter_path": None, "generated_at": None, "tokens_used": 0})
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source,
            "company": self.company,
            "title": self.title,
            "location": self.location,
            "url": self.url,
            "posted_at": self.posted_at,
            "jd_raw": self.jd_raw,
            "jd_structured": self.jd_structured,
            "taxonomy": self.taxonomy,
            "status": self.status,
            "status_history": self.status_history,
            "fit": self.fit,
            "generated": self.generated,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "JobRecord":
        return cls(
            id=d["id"],
            source=d["source"],
            company=d["company"],
            title=d["title"],
            location=d["location"],
            url=d["url"],
            posted_at=d.get("posted_at"),
            jd_raw=d["jd_raw"],
            jd_structured=d.get("jd_structured", {"duties": [], "requirements": [], "tools": []}),
            taxonomy=d.get("taxonomy", {}),
            status=d.get("status", "discovered"),
            status_history=d.get("status_history", []),
            fit=d.get("fit", {"coverage": 0.0, "notes": "", "score": 0, "explanation": ""}),
            generated=d.get("generated", {"resume_path": None, "cover_letter_path": None, "generated_at": None, "tokens_used": 0}),
            created_at=d.get("created_at", ""),
            updated_at=d.get("updated_at", ""),
        )


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _job_id(source: str, url: str) -> str:
    return hashlib.sha1(f"{source}:{url}".encode()).hexdigest()[:16]


def html_to_text(html: str) -> str:
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    for script in soup(["script", "style"]):
        script.decompose()
    return soup.get_text(separator="\n\n", strip=True)


def load_jobs_index(path: Path | None = None) -> dict[str, JobRecord]:
    """Load all jobs from JSONL into memory index (id -> record)."""
    path = path or JOBS_JSONL_PATH
    index: dict[str, JobRecord] = {}
    if not path.exists():
        return index
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
                job = JobRecord.from_dict(d)
                index[job.id] = job
            except Exception:
                continue
    return index


def save_jobs(jobs: dict[str, JobRecord], path: Path | None = None) -> None:
    """Write jobs dict back to JSONL (atomic temp-file swap)."""
    path = path or JOBS_JSONL_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        for job in jobs.values():
            f.write(json.dumps(job.to_dict(), ensure_ascii=False) + "\n")
    os.replace(tmp, path)


def append_job(job: JobRecord, path: Path | None = None) -> None:
    """Append a single job to JSONL (no full rewrite)."""
    path = path or JOBS_JSONL_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(job.to_dict(), ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# Fetchers
# ---------------------------------------------------------------------------
def _http_get(url: str, timeout: int = 15) -> dict[str, Any]:
    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        return {"ok": True, "data": resp.json()}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def greenhouse_fetch(slug: str) -> list[JobRecord]:
    """Fetch jobs from Greenhouse board. List endpoint lacks content; fetch individual job pages for JD text."""
    list_url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
    result = _http_get(list_url)
    if not result["ok"]:
        return []
    payload = result["data"]
    company_name = payload.get("name", slug)
    jobs: list[JobRecord] = []
    for item in payload.get("jobs", []):
        title = item.get("title", "")
        location_str = ", ".join(
            str(v) for v in item.get("location", {}).values() if v
        )
        url = item.get("absolute_url", "")
        # Quick title pre-filter before fetching individual job content (saves API calls)
        if not title_matches(title):
            continue
        # Fetch individual job for content
        job_id = item.get("id", "")
        jd_text = ""
        if job_id:
            detail = _http_get(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs/{job_id}")
            if detail["ok"]:
                jd_html = detail["data"].get("content", "")
                jd_text = html_to_text(jd_html)
        job = JobRecord(
            id=_job_id("greenhouse", url),
            source="greenhouse",
            company=company_name,
            title=title,
            location=location_str,
            url=url,
            posted_at=item.get("first_published") or item.get("updated_at") or None,
            jd_raw=jd_text,
            created_at=_now_iso(),
            updated_at=_now_iso(),
        )
        jobs.append(job)
    return jobs


def lever_fetch(slug: str) -> list[JobRecord]:
    url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
    result = _http_get(url)
    if not result["ok"]:
        return []
    payload = result["data"]
    jobs: list[JobRecord] = []
    for item in payload:
        categories = item.get("categories", {})
        location_str = categories.get("location", "")
        team = categories.get("team", "")
        company_name = slug.replace("-", " ").title()
        jd_text = html_to_text(item.get("description", ""))
        job = JobRecord(
            id=_job_id("lever", item.get("hostedUrl", "")),
            source="lever",
            company=company_name,
            title=item.get("text", ""),
            location=location_str,
            url=item.get("hostedUrl", ""),
            posted_at=None,
            jd_raw=jd_text,
            created_at=_now_iso(),
            updated_at=_now_iso(),
        )
        jobs.append(job)
    return jobs


def ashby_fetch(slug: str) -> list[JobRecord]:
    url = f"https://api.ashbyhq.com/posting-api/job-board/{slug}?includeCompensation=true"
    result = _http_get(url)
    if not result["ok"]:
        return []
    payload = result["data"]
    jobs: list[JobRecord] = []
    for item in payload.get("jobs", []):
        title = item.get("title", "")
        location_str = item.get("location", "")
        job_url = item.get("jobUrl", "")
        jd_text = html_to_text(item.get("descriptionHtml", ""))
        company_name = slug.replace("-", " ").title()
        job = JobRecord(
            id=_job_id("ashby", job_url),
            source="ashby",
            company=company_name,
            title=title,
            location=location_str,
            url=job_url,
            posted_at=None,
            jd_raw=jd_text,
            created_at=_now_iso(),
            updated_at=_now_iso(),
        )
        jobs.append(job)
    return jobs


def scrape_url(url: str) -> dict[str, Any]:
    """Generic scrape for manual entry. Returns {ok, text, error}."""
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return {"ok": False, "text": "", "error": f"HTTP {resp.status_code}"}
        soup = BeautifulSoup(resp.content, "html.parser")
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text(separator="\n\n", strip=True)
        if len(text) < MIN_JD_LENGTH:
            return {"ok": False, "text": text, "error": f"Scraped text too short ({len(text)} chars)"}
        return {"ok": True, "text": text, "error": ""}
    except Exception as e:
        return {"ok": False, "text": "", "error": str(e)}


def manual_add(url_or_text: str, company: str = "", title: str = "") -> JobRecord | None:
    """Add a job from manual URL or raw text."""
    text = url_or_text
    url = ""
    if url_or_text.startswith("http://") or url_or_text.startswith("https://"):
        result = scrape_url(url_or_text)
        if not result["ok"]:
            return None
        text = result["text"]
        url = url_or_text
    if len(text) < MIN_JD_LENGTH:
        return None
    now = _now_iso()
    job = JobRecord(
        id=_job_id("manual", url or text[:200]),
        source="manual",
        company=company or "Unknown",
        title=title or "Unknown Role",
        location="",
        url=url,
        posted_at=None,
        jd_raw=text,
        created_at=now,
        updated_at=now,
    )
    return job


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------
def _matches_pattern(text: str, patterns: list[str]) -> bool:
    lower = text.lower()
    return any(p.lower() in lower for p in patterns)


def _matches_regex(text: str, patterns: list[str]) -> bool:
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def classify_title(title: str) -> dict[str, Any]:
    """Classify title into family and seniority."""
    lower = title.lower()
    family = "Other"
    seniority = "IC"

    if re.search(r"technical\s+product\s+manager", lower) or re.search(r"\btpm\b", lower):
        family = "TPM"
    elif re.search(r"group\s+product\s+manager", lower):
        family = "GPM"
    elif re.search(r"principal\s+product\s+manager", lower):
        family = "Principal"
    elif re.search(r"product\s+owner", lower):
        family = "ProductOwner"
    elif re.search(r"product\s*manager", lower):
        family = "PM"

    if re.search(r"\bsenior\b", lower) or re.search(r"\bsr\.?\b", lower):
        seniority = "Senior"
    elif re.search(r"\bstaff\b", lower):
        seniority = "Senior"
    elif re.search(r"\bprincipal\b", lower):
        seniority = "Principal"
    elif re.search(r"\bgroup\b", lower):
        seniority = "Group"
    elif re.search(r"\bmanager\b", lower) and not re.search(r"product\s+manager", lower):
        seniority = "Manager"

    return {"role_family": family, "seniority": seniority}


def location_matches(job: JobRecord, remote_policy: str = "canada_na_only") -> bool:
    """Return True if location matches Canada or Remote per policy."""
    loc = job.location.lower()
    is_canada = _matches_pattern(loc, CANADA_PATTERNS)
    is_remote = _matches_pattern(loc, REMOTE_PATTERNS)

    if is_canada:
        return True

    if is_remote:
        if remote_policy == "global_remote":
            return True
        # canada_na_only: require NA mention or absence of non-NA signals
        if _matches_pattern(loc, NA_PATTERNS + CANADA_PATTERNS):
            return True
        # If remote but no region specified, assume eligible
        if not any(x in loc for x in ["europe", "asia", "africa", "latam", "south america", "india", "china", "uk", "germany", "france"]):
            return True
    return False


def title_matches(title: str) -> bool:
    """Return True if title is a matching Product role."""
    if _matches_regex(title, EXCLUDE_TITLE_PATTERNS):
        return False
    return _matches_regex(title, INCLUDE_TITLE_PATTERNS)


def apply_filters(job: JobRecord, remote_policy: str = "canada_na_only") -> bool:
    """Return True if job passes all filters."""
    if not title_matches(job.title):
        return False
    if not location_matches(job, remote_policy):
        return False
    if len(job.jd_raw) < MIN_JD_LENGTH:
        return False
    return True


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
def run_fetch(companies: list[dict[str, str]], remote_policy: str = "canada_na_only") -> dict[str, Any]:
    """Fetch jobs from all configured companies, filter, dedupe, and return stats.

    Returns dict:
    {
        "new": int,
        "updated": int,
        "skipped": int,
        "errors": list[str],
        "log": list[str],
        "new_ids": list[str],
    }
    """
    existing = load_jobs_index()
    stats = {"new": 0, "updated": 0, "skipped": 0, "errors": [], "log": [], "new_ids": []}

    for cfg in companies:
        platform = cfg.get("platform", "").lower()
        slug = cfg.get("slug", "")
        name = cfg.get("company", slug)
        if not slug:
            continue

        try:
            if platform == "greenhouse":
                fetched = greenhouse_fetch(slug)
            elif platform == "lever":
                fetched = lever_fetch(slug)
            elif platform == "ashby":
                fetched = ashby_fetch(slug)
            else:
                stats["errors"].append(f"Unknown platform '{platform}' for {name}")
                continue
        except Exception as e:
            stats["errors"].append(f"{name} ({platform}): {e}")
            continue

        total_fetched = len(fetched)
        passed = 0
        for job in fetched:
            if not apply_filters(job, remote_policy):
                continue
            passed += 1
            if job.id in existing:
                # Update raw JD if changed (simple length comparison)
                old = existing[job.id]
                if len(job.jd_raw) > len(old.jd_raw):
                    old.jd_raw = job.jd_raw
                    old.updated_at = _now_iso()
                    existing[job.id] = old
                    stats["updated"] += 1
                else:
                    stats["skipped"] += 1
            else:
                job.status_history = [{"status": "discovered", "changed_at": _now_iso()}]
                existing[job.id] = job
                stats["new"] += 1
                stats["new_ids"].append(job.id)

        stats["log"].append(f"{name} ({platform}): {total_fetched} fetched, {passed} passed filters")

    save_jobs(existing)
    return stats


def validate_slug(slug: str, platform: str) -> dict[str, Any]:
    """Ping a board once to see if it responds."""
    platform = platform.lower()
    if platform == "greenhouse":
        url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
    elif platform == "lever":
        url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
    elif platform == "ashby":
        url = f"https://api.ashbyhq.com/posting-api/job-board/{slug}"
    else:
        return {"ok": False, "error": f"Unknown platform {platform}"}
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return {"ok": True, "error": ""}
        return {"ok": False, "error": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ---------------------------------------------------------------------------
# Fit (lightweight)
# ---------------------------------------------------------------------------
def compute_fit(job: JobRecord, master_context: str) -> dict[str, Any]:
    """Lightweight heuristic fit score. No LLM cost."""
    score = 0
    notes_parts = []
    title_lower = job.title.lower()
    loc_lower = job.location.lower()

    # Title match
    if re.search(r"senior|sr\.?|staff|principal|group", title_lower):
        score += 25
        notes_parts.append("Senior+ title match")
    elif re.search(r"product\s*manager", title_lower):
        score += 15
        notes_parts.append("PM title match")

    # Location match
    if _matches_pattern(loc_lower, CANADA_PATTERNS):
        score += 30
        notes_parts.append("Canada location")
    elif _matches_pattern(loc_lower, REMOTE_PATTERNS):
        if _matches_pattern(loc_lower, NA_PATTERNS + CANADA_PATTERNS):
            score += 25
            notes_parts.append("Remote NA")
        else:
            score += 10
            notes_parts.append("Remote (global)")

    # Tools overlap (simple keyword search in master context)
    mc_lower = master_context.lower()
    tools = job.jd_structured.get("tools", [])
    matched_tools = [t for t in tools if t.lower() in mc_lower]
    if tools:
        tool_ratio = len(matched_tools) / len(tools)
        score += int(tool_ratio * 30)
        notes_parts.append(f"{len(matched_tools)}/{len(tools)} tools in context")

    score = min(score, 100)
    explanation = "; ".join(notes_parts) if notes_parts else "Baseline"
    return {
        "score": score,
        "notes": explanation,
        "explanation": explanation,
        "coverage": round(len(matched_tools) / len(tools), 2) if tools else 0.0,
    }


# ---------------------------------------------------------------------------
# Import / Export
# ---------------------------------------------------------------------------
def export_jsonl(path: Path | None = None) -> bytes:
    path = path or JOBS_JSONL_PATH
    if not path.exists():
        return b""
    return path.read_bytes()


def import_jsonl(data: bytes, merge: bool = True) -> tuple[int, int]:
    """Import jobs from JSONL bytes. Returns (added, skipped_duplicates)."""
    existing = load_jobs_index()
    added = 0
    skipped = 0
    for line in data.decode("utf-8", errors="ignore").strip().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
            job = JobRecord.from_dict(d)
            if job.id in existing:
                if merge:
                    # Keep the newer one by updated_at
                    old = existing[job.id]
                    if (job.updated_at or "") > (old.updated_at or ""):
                        existing[job.id] = job
                skipped += 1
            else:
                existing[job.id] = job
                added += 1
        except Exception:
            continue
    save_jobs(existing)
    return added, skipped
