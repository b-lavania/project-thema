"""Scoreboard: metric snapshots + aggregations + streaks."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Optional

from ..db import get_session, init_db
from ..models import Metric, Outreach, _today_iso


def _to_dict(m: Metric) -> dict:
    return {
        "id": m.id,
        "date": m.date,
        "outbound_touches": m.outbound_touches,
        "warm_intro_requests": m.warm_intro_requests,
        "conversations": m.conversations,
        "applications": m.applications,
        "replies_received": m.replies_received,
        "interviews_booked": m.interviews_booked,
        "onsites": m.onsites,
        "artifacts_published": m.artifacts_published,
        "wip_count": m.wip_count,
        "notes": m.notes,
    }


def get_metric(date_str: str) -> Optional[dict]:
    init_db()
    with get_session() as sess:
        m = sess.query(Metric).filter(Metric.date == date_str).first()
        return _to_dict(m) if m else None


def upsert_metric(date_str: str, **kwargs) -> dict:
    init_db()
    with get_session() as sess:
        m = sess.query(Metric).filter(Metric.date == date_str).first()
        if m:
            for k, v in kwargs.items():
                if hasattr(m, k):
                    setattr(m, k, v)
        else:
            m = Metric(date=date_str, **kwargs)
            sess.add(m)
        sess.commit()
        return _to_dict(m)


def auto_compute_outreach_metrics(target_date: str) -> dict:
    """Compute today's leading metrics from outreach table."""
    init_db()
    with get_session() as sess:
        outbound = sess.query(Outreach).filter(
            Outreach.date == target_date
        ).count()
        warm_intros = sess.query(Outreach).filter(
            Outreach.date == target_date,
            Outreach.channel == "warm_intro",
        ).count()
        replies = sess.query(Outreach).filter(
            Outreach.date == target_date,
            Outreach.action == "replied",
        ).count()
        booked = sess.query(Outreach).filter(
            Outreach.date == target_date,
            Outreach.action == "booked",
        ).count()

    return upsert_metric(
        target_date,
        outbound_touches=outbound,
        warm_intro_requests=warm_intros,
        replies_received=replies,
        conversations=booked,
    )


def weekly_summary(weeks_back: int = 0) -> dict:
    """Aggregate metrics for a week ending on a given date."""
    init_db()
    today = date.today()
    start = today - timedelta(days=today.weekday() + 7 * weeks_back)
    end = start + timedelta(days=6)
    start_s, end_s = start.isoformat(), end.isoformat()

    with get_session() as sess:
        metrics = sess.query(Metric).filter(
            Metric.date >= start_s, Metric.date <= end_s
        ).all()

    if not metrics:
        return {
            "week": f"{start_s} to {end_s}",
            "outbound_touches": 0,
            "warm_intro_requests": 0,
            "conversations": 0,
            "applications": 0,
            "replies_received": 0,
            "interviews_booked": 0,
            "onsites": 0,
            "artifacts_published": 0,
            "wip_count": 0,
        }

    return {
        "week": f"{start_s} to {end_s}",
        "outbound_touches": sum(m.outbound_touches for m in metrics),
        "warm_intro_requests": sum(m.warm_intro_requests for m in metrics),
        "conversations": sum(m.conversations for m in metrics),
        "applications": sum(m.applications for m in metrics),
        "replies_received": sum(m.replies_received for m in metrics),
        "interviews_booked": sum(m.interviews_booked for m in metrics),
        "onsites": sum(m.onsites for m in metrics),
        "artifacts_published": sum(m.artifacts_published for m in metrics),
        "wip_count": max((m.wip_count for m in metrics), default=0),
    }


def outbound_streak() -> int:
    """Count consecutive days (back from today) with outbound_touches > 0."""
    init_db()
    streak = 0
    d = date.today()
    with get_session() as sess:
        while True:
            m = sess.query(Metric).filter(Metric.date == d.isoformat()).first()
            if m and m.outbound_touches > 0:
                streak += 1
                d -= timedelta(days=1)
            else:
                break
    return streak


def artifact_streak() -> int:
    """Count consecutive weeks with artifacts_published > 0."""
    init_db()
    streak = 0
    today = date.today()
    with get_session() as sess:
        for week_offset in range(52):
            start = today - timedelta(days=today.weekday() + 7 * week_offset)
            end = start + timedelta(days=6)
            count = sess.query(Metric).filter(
                Metric.date >= start.isoformat(),
                Metric.date <= end.isoformat(),
            ).with_entities(Metric.artifacts_published).all()
            total = sum(c[0] for c in count)
            if total > 0:
                streak += 1
            else:
                break
    return streak
