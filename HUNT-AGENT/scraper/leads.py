"""Lead data model + JSON/markdown persistence."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from datetime import date
from pathlib import Path

LEADS_DIR = Path(__file__).resolve().parents[1]
LEADS_JSON = LEADS_DIR / "leads.json"
LEADS_MD = LEADS_DIR / "job_leads.md"

TABLE_HEADER = """\
# Job Leads

| Source | Role | Company | Location | Link | MatchReason | Notes | OutreachStatus |
|--------|------|---------|----------|------|-------------|-------|----------------|
"""


def _lead_id(company: str, title: str, url: str) -> str:
    raw = f"{company}|{title}|{url}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]


@dataclass
class Lead:
    title: str
    company: str
    url: str
    source: str  # greenhouse, lever, ashby, smartrecruiters, career_page, search, manual
    date_found: str = ""
    location: str = ""
    description_snippet: str = ""
    match_reason: str = ""
    stage: str = "sent"  # sent, replied, screen, interview, final, offer, accepted, rejected, ghosted
    notes: str = ""
    id: str = ""

    def __post_init__(self):
        if not self.date_found:
            self.date_found = date.today().isoformat()
        if not self.id:
            self.id = _lead_id(self.company, self.title, self.url)


def load_leads() -> list[Lead]:
    if not LEADS_JSON.exists():
        return []
    with open(LEADS_JSON) as f:
        return [Lead(**d) for d in json.load(f)]


def save_leads(leads: list[Lead]):
    LEADS_JSON.write_text(
        json.dumps([asdict(l) for l in leads], indent=2, default=str)
    )
    _regenerate_markdown(leads)


def get_lead(lead_id: str) -> Lead | None:
    """Look up a single lead by its id."""
    for l in load_leads():
        if l.id == lead_id:
            return l
    return None


def update_lead_stage(lead_id: str, new_stage: str) -> bool:
    """Update the stage of a lead. Returns True if found and updated."""
    leads = load_leads()
    for l in leads:
        if l.id == lead_id:
            l.stage = new_stage
            save_leads(leads)
            return True
    return False


def append_leads(new_leads: list[Lead]) -> int:
    existing = load_leads()
    existing_urls = {l.url for l in existing if l.url}
    merged = list(existing)
    appended_count = 0
    for l in new_leads:
        if l.url and l.url in existing_urls:
            continue
        if l.url:
            existing_urls.add(l.url)
        merged.append(l)
        appended_count += 1
    save_leads(merged)
    return appended_count


def _md_cell(text: str, max_len: int = 80) -> str:
    """Format a markdown table cell: escape pipes, truncate, strip newlines."""
    if not text:
        return ""
    cleaned = text.replace("|", "\\|").replace("\n", " ").replace("\r", "").strip()
    if len(cleaned) > max_len:
        cleaned = cleaned[: max_len - 3] + "..."
    return cleaned


def _md_link(url: str, text: str = "") -> str:
    if not url:
        return ""
    label = text or url
    return f"[{_md_cell(label, 50)}]({url})"


def _regenerate_markdown(leads: list[Lead]):
    """Regenerate job_leads.md as a table from the leads list."""
    LEADS_MD.parent.mkdir(parents=True, exist_ok=True)
    lines = [TABLE_HEADER]
    for l in leads:
        source = _md_cell(l.source, 16)
        role = _md_cell(l.title, 60)
        company = _md_cell(l.company, 40)
        location = _md_cell(l.location, 40)
        link = _md_link(l.url)
        match_reason = _md_cell(l.match_reason or l.description_snippet, 80)
        notes = _md_cell(l.notes, 80)
        lines.append(
            f"| {source} | {role} | {company} | {location} | {link} | "
            f"{match_reason} | {notes} | {l.stage} |\n"
        )
    LEADS_MD.write_text("".join(lines))
