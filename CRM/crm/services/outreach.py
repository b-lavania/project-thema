"""Outreach logging + history."""

from __future__ import annotations

from typing import Optional

from ..db import get_session, init_db
from ..models import Outreach, _today_iso, _now_iso


def _to_dict(o: Outreach) -> dict:
    return {
        "id": o.id,
        "company_id": o.company_id,
        "channel": o.channel,
        "action": o.action,
        "subject": o.subject,
        "body": o.body,
        "contact_name": o.contact_name,
        "contact_role": o.contact_role,
        "date": o.date,
        "response": o.response,
        "response_date": o.response_date,
        "notes": o.notes,
    }


def log_outreach(
    company_id: str,
    channel: str,
    action: str,
    subject: str = "",
    body: str = "",
    contact_name: str = "",
    contact_role: str = "",
    response: str = "",
    notes: str = "",
) -> dict:
    init_db()
    with get_session() as sess:
        o = Outreach(
            company_id=company_id,
            channel=channel,
            action=action,
            subject=subject,
            body=body,
            contact_name=contact_name,
            contact_role=contact_role,
            response=response,
            response_date=_today_iso() if response else None,
            notes=notes,
        )
        sess.add(o)
        sess.commit()
        return _to_dict(o)


def list_outreach(company_id: Optional[str] = None, limit: int = 50) -> list[dict]:
    init_db()
    with get_session() as sess:
        q = sess.query(Outreach)
        if company_id:
            q = q.filter(Outreach.company_id == company_id)
        q = q.order_by(Outreach.date.desc()).limit(limit)
        return [_to_dict(o) for o in q.all()]


def generate_outreach_llm(llm, company: dict) -> str:
    """Generate 3-variant outreach note using outbound_note.md prompt."""
    from pathlib import Path

    prompt_path = Path(__file__).resolve().parents[2] / "prompts" / "outbound_note.md"
    if not prompt_path.exists():
        return "(outbound_note.md prompt not found)"

    prompt_template = prompt_path.read_text(encoding="utf-8")
    memo_hypothesis = company.get("hypothesis", "") or ""
    from crm.services.memos import get_memo
    memo = get_memo(company["id"])
    if memo and memo.get("real_bottleneck"):
        memo_hypothesis = memo_hypothesis or memo["real_bottleneck"]

    prompt = prompt_template.format(
        company_name=company.get("name", ""),
        hypothesis=memo_hypothesis or "operational bottleneck not yet documented",
    )

    from llm_client import call_llm
    result = call_llm(
        llm,
        system_prompt="You write concise, hypothesis-led outreach for ops-AI PM roles.",
        user_prompt=prompt,
        max_tokens=600,
        temperature=0.4,
        tier="default",
        require_nonempty=True,
        step_label="Outreach draft generation",
    )
    text, _usage = result if isinstance(result, tuple) else (result, {})
    return text


def outreach_stats() -> dict:
    """Aggregate outreach counts for scoreboard."""
    init_db()
    from sqlalchemy import func
    with get_session() as sess:
        total = sess.query(Outreach).count()
        by_channel = {}
        for channel, count in sess.query(
            Outreach.channel, func.count(Outreach.id)
        ).group_by(Outreach.channel).all():
            by_channel[channel] = count
        by_action = {}
        for action, count in sess.query(
            Outreach.action, func.count(Outreach.id)
        ).group_by(Outreach.action).all():
            by_action[action] = count
        return {"total": total, "by_channel": by_channel, "by_action": by_action}
