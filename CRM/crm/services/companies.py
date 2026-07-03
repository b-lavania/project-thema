"""Company CRUD + seed from YAML."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import yaml

from ..db import get_session, init_db
from ..models import PIPELINE_STAGES, SEGMENTS, Company

SEED_PATH = Path(__file__).resolve().parents[2] / "data" / "companies.yaml"


def _to_dict(c: Company) -> dict:
    return {
        "id": c.id,
        "name": c.name,
        "url": c.url,
        "linkedin_url": c.linkedin_url,
        "careers_url": c.careers_url,
        "industry": c.industry,
        "segment": c.segment,
        "stage": c.stage,
        "hypothesis": c.hypothesis,
        "notes": c.notes,
        "key_people": json.loads(c.key_people) if c.key_people else [],
        "date_added": c.date_added,
        "date_updated": c.date_updated,
        "date_stage_changed": c.date_stage_changed,
    }


def list_companies(
    segment: Optional[str] = None,
    stage: Optional[str] = None,
) -> list[dict]:
    init_db()
    with get_session() as sess:
        q = sess.query(Company)
        if segment:
            q = q.filter(Company.segment == segment)
        if stage:
            q = q.filter(Company.stage == stage)
        return [_to_dict(c) for c in q.order_by(Company.date_added.desc()).all()]


def get_company(company_id: str) -> Optional[dict]:
    init_db()
    with get_session() as sess:
        c = sess.get(Company, company_id)
        return _to_dict(c) if c else None


def add_company(
    name: str,
    url: str = "",
    linkedin_url: str = "",
    careers_url: str = "",
    industry: str = "",
    segment: str = "realistic",
    hypothesis: str = "",
    notes: str = "",
) -> dict:
    init_db()
    with get_session() as sess:
        c = Company(
            name=name,
            url=url,
            linkedin_url=linkedin_url,
            careers_url=careers_url,
            industry=industry,
            segment=segment,
            hypothesis=hypothesis,
            notes=notes,
        )
        sess.add(c)
        sess.commit()
        return _to_dict(c)


def update_company(company_id: str, **fields) -> Optional[dict]:
    init_db()
    with get_session() as sess:
        c = sess.get(Company, company_id)
        if not c:
            return None
        for k, v in fields.items():
            if k == "key_people" and isinstance(v, list):
                setattr(c, k, json.dumps(v))
            elif hasattr(c, k):
                setattr(c, k, v)
        from ..models import _now_iso
        c.date_updated = _now_iso()
        sess.commit()
        return _to_dict(c)


def delete_company(company_id: str) -> bool:
    init_db()
    with get_session() as sess:
        c = sess.get(Company, company_id)
        if not c:
            return False
        sess.delete(c)
        sess.commit()
        return True


def load_seed_companies() -> int:
    """Load companies from data/companies.yaml. Returns count added."""
    if not SEED_PATH.exists():
        return 0
    init_db()
    with open(SEED_PATH) as f:
        data = yaml.safe_load(f) or []
    count = 0
    with get_session() as sess:
        existing = {c.name.lower() for c in sess.query(Company.name).all()}
        for item in data:
            if item.get("name", "").lower() in existing:
                continue
            c = Company(
                name=item["name"],
                url=item.get("url", ""),
                linkedin_url=item.get("linkedin_url", ""),
                careers_url=item.get("careers_url", ""),
                industry=item.get("industry", ""),
                segment=item.get("segment", "realistic"),
                hypothesis=item.get("hypothesis", ""),
                notes=item.get("notes", ""),
            )
            sess.add(c)
            count += 1
        sess.commit()
    return count


def find_company_by_name(name: str) -> Optional[dict]:
    """Fuzzy match company by name."""
    if not name or not name.strip():
        return None
    init_db()
    norm = name.strip().lower()
    with get_session() as sess:
        for c in sess.query(Company).all():
            c_norm = c.name.lower()
            if c_norm == norm or norm in c_norm or c_norm in norm:
                return _to_dict(c)
    return None


def import_from_leads(lead, *, hypothesis: str = "") -> Optional[dict]:
    """Import a HUNT-AGENT Lead as a Tempus company. Returns None if duplicate."""
    init_db()
    with get_session() as sess:
        existing = sess.query(Company).filter(
            Company.name.ilike(f"%{lead.company}%")
        ).first()
        if existing:
            return None
        c = Company(
            name=lead.company,
            url=lead.url or "",
            industry=lead.source or "",
            segment="realistic",
            hypothesis=hypothesis or "",
            notes=lead.description_snippet or "",
        )
        sess.add(c)
        sess.commit()
        return _to_dict(c)


def advance_on_application(company_name: str) -> Optional[dict]:
    """On resume generate: move CRM stage to applied + log application outreach."""
    from .pipeline import move_stage
    from .outreach import log_outreach

    co = find_company_by_name(company_name)
    if not co:
        return None
    if co["stage"] not in ("applied", "interview", "onsite", "offer"):
        move_stage(co["id"], "applied")
        co = get_company(co["id"]) or co
    log_outreach(
        co["id"],
        channel="application",
        action="sent",
        notes="Auto-logged on resume generate",
    )
    return co
