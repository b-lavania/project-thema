"""Pipeline stage transitions + SLA tracking."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Optional

from ..db import get_session, init_db
from ..models import PIPELINE_STAGES, TERMINAL_STAGES, Company

# SLA days per stage transition
SLA = {
    "sourced": 1,       # → researching within 24h
    "researching": 3,   # → contacted within 72h
    "contacted": 7,     # → conversation within 7 days
    "conversation": 3,  # → applied within 3 days
    "applied": 14,      # → interview within 14 days
    "interview": 14,    # → onsite within 14 days
    "onsite": 7,        # → offer within 7 days
    "offer": 14,        # → decision within 14 days
}


def _days_in_stage(company: Company) -> Optional[int]:
    if not company.date_stage_changed:
        return None
    try:
        changed = date.fromisoformat(company.date_stage_changed)
        return (date.today() - changed).days
    except (ValueError, TypeError):
        return None


def stage_status(company: dict) -> dict:
    """Return stage + days in stage + SLA breach info."""
    stage = company["stage"]
    changed = company.get("date_stage_changed")
    if not changed:
        return {"stage": stage, "days": None, "breached": False, "sla_days": None}

    try:
        d = (date.today() - date.fromisoformat(changed)).days
    except (ValueError, TypeError):
        return {"stage": stage, "days": None, "breached": False, "sla_days": None}

    sla_days = SLA.get(stage)
    breached = sla_days is not None and d > sla_days
    return {"stage": stage, "days": d, "breached": breached, "sla_days": sla_days}


def move_stage(company_id: str, new_stage: str) -> Optional[dict]:
    init_db()
    from .companies import _to_dict, get_company
    with get_session() as sess:
        c = sess.get(Company, company_id)
        if not c:
            return None
        c.stage = new_stage
        from ..models import _today_iso
        c.date_stage_changed = _today_iso()
        c.date_updated = _today_iso()
        sess.commit()
        return _to_dict(c)


def get_pipeline_summary() -> dict:
    """Return stage counts + breached companies."""
    init_db()
    with get_session() as sess:
        companies = sess.query(Company).all()
        summary = {}
        breached = []
        for stage in PIPELINE_STAGES:
            batch = [c for c in companies if c.stage == stage]
            summary[stage] = len(batch)
            for c in batch:
                d = _days_in_stage(c)
                sla = SLA.get(stage)
                if d is not None and sla is not None and d > sla:
                    breached.append({
                        "id": c.id,
                        "name": c.name,
                        "stage": stage,
                        "days": d,
                        "sla": sla,
                    })
        summary["_breached"] = breached
        summary["_total"] = len(companies)
        return summary


def get_action_queue() -> list[dict]:
    """Companies that need action this week (SLA approaching or breached)."""
    init_db()
    from .companies import _to_dict
    with get_session() as sess:
        companies = sess.query(Company).filter(
            Company.stage.notin_(TERMINAL_STAGES)
        ).all()
        result = []
        for c in companies:
            d = _days_in_stage(c)
            sla = SLA.get(c.stage)
            if d is None or sla is None:
                continue
            if d >= sla - 2:  # within 2 days of breach
                result.append({**_to_dict(c), "_days": d, "_sla": sla})
        result.sort(key=lambda x: x["_days"], reverse=True)
        return result
