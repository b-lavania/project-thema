"""Evidence ledger for positioning claims."""

from __future__ import annotations

from typing import Optional

from ..db import get_session, init_db
from ..models import Evidence, _today_iso


def _to_dict(e: Evidence) -> dict:
    return {
        "id": e.id,
        "claim": e.claim,
        "evidence": e.evidence,
        "source": e.source,
        "date_added": e.date_added,
    }


def list_evidence() -> list[dict]:
    init_db()
    with get_session() as sess:
        items = sess.query(Evidence).order_by(Evidence.date_added.desc()).all()
        return [_to_dict(e) for e in items]


def add_evidence(claim: str, evidence: str, source: str = "") -> dict:
    init_db()
    with get_session() as sess:
        e = Evidence(claim=claim, evidence=evidence, source=source)
        sess.add(e)
        sess.commit()
        return _to_dict(e)


def delete_evidence(evidence_id: str) -> bool:
    init_db()
    with get_session() as sess:
        e = sess.get(Evidence, evidence_id)
        if not e:
            return False
        sess.delete(e)
        sess.commit()
        return True
