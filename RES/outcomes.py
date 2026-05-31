"""Local application outcome tracker (CSV-backed)."""

from __future__ import annotations

import csv
import datetime
import hashlib
from pathlib import Path

import streamlit as st

RES_ROOT = Path(__file__).resolve().parent
APPLICATIONS_CSV = RES_ROOT / "data" / "applications.csv"

APPLICATION_COLUMNS = [
    "app_id",
    "date",
    "company",
    "role",
    "track",
    "voice",
    "ats_coverage",
    "stage",
]

STAGE_OPTIONS = [
    "sent",
    "replied",
    "screen",
    "interview",
    "final",
    "offer",
    "accepted",
    "rejected",
    "ghosted",
]

STAGE_WEIGHTS = {
    "sent": 0.0,
    "replied": 0.15,
    "screen": 0.35,
    "interview": 0.55,
    "final": 0.75,
    "offer": 0.90,
    "accepted": 1.0,
    "rejected": 0.0,
    "ghosted": 0.0,
}


def ensure_applications_file() -> None:
    APPLICATIONS_CSV.parent.mkdir(parents=True, exist_ok=True)
    if not APPLICATIONS_CSV.exists():
        with APPLICATIONS_CSV.open("w", encoding="utf-8", newline="") as f:
            csv.DictWriter(f, fieldnames=APPLICATION_COLUMNS).writeheader()


def load_applications() -> list[dict[str, str]]:
    ensure_applications_file()
    with APPLICATIONS_CSV.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def save_applications(rows: list[dict[str, str]]) -> None:
    ensure_applications_file()
    with APPLICATIONS_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=APPLICATION_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, "") for col in APPLICATION_COLUMNS})


def append_application_record(
    company: str,
    role: str,
    track: str,
    voice: str,
    ats_coverage: float,
) -> str:
    """Append one row after a successful generation. Returns app_id."""
    ensure_applications_file()
    date = datetime.date.today().isoformat()
    unique = f"{date}|{company}|{role}|{datetime.datetime.now().isoformat()}"
    app_id = hashlib.sha256(unique.encode()).hexdigest()[:10]
    row = {
        "app_id": app_id,
        "date": date,
        "company": company,
        "role": role,
        "track": track,
        "voice": voice,
        "ats_coverage": f"{ats_coverage:.4f}",
        "stage": "sent",
    }
    rows = load_applications()
    rows.append(row)
    save_applications(rows)
    return app_id


def compute_funnel(rows: list[dict[str, str]]) -> dict[str, int]:
    counts = {stage: 0 for stage in STAGE_OPTIONS}
    for row in rows:
        stage = (row.get("stage") or "sent").strip().lower()
        if stage in counts:
            counts[stage] += 1
    return counts


def compute_rates(rows: list[dict[str, str]]) -> dict[str, float | int]:
    n = len(rows)
    if n == 0:
        return {"total": 0, "reply_rate": 0.0, "screen_rate": 0.0, "offer_count": 0}

    replied = sum(
        1
        for r in rows
        if (r.get("stage") or "").lower()
        in ("replied", "screen", "interview", "final", "offer", "accepted")
    )
    screen_plus = sum(
        1
        for r in rows
        if (r.get("stage") or "").lower()
        in ("screen", "interview", "final", "offer", "accepted")
    )
    offers = sum(
        1
        for r in rows
        if (r.get("stage") or "").lower() in ("offer", "accepted")
    )
    return {
        "total": n,
        "reply_rate": replied / n,
        "screen_rate": screen_plus / n,
        "offer_count": offers,
    }


def render_outcomes_tab() -> None:
    """Streamlit shell for the Outcomes tab (Phase C)."""
    st.markdown("### Application outcomes")
    st.caption("Descriptive funnel stats from `data/applications.csv` (one row per generation).")

    rows = load_applications()
    if not rows:
        st.info(
            "No applications logged yet. Run **Generate Documents** on the Generate tab "
            "to create the first row."
        )
        return

    rates = compute_rates(rows)
    funnel = compute_funnel(rows)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Applications", rates["total"])
    c2.metric("Reply rate", f"{rates['reply_rate'] * 100:.0f}%")
    c3.metric("Screen rate", f"{rates['screen_rate'] * 100:.0f}%")
    c4.metric("Offers", rates["offer_count"])

    st.markdown("#### Funnel (stage counts)")
    funnel_active = [
        (s, funnel[s])
        for s in ("sent", "replied", "screen", "interview", "final", "offer", "accepted")
        if funnel[s] > 0
    ]
    if funnel_active:
        funnel_md = "| Stage | Count |\n| --- | ---: |\n"
        funnel_md += "\n".join(f"| {s} | {c} |" for s, c in funnel_active)
        st.markdown(funnel_md)
    else:
        st.caption("All applications are still at `sent`.")

    terminal = funnel.get("rejected", 0) + funnel.get("ghosted", 0)
    if terminal:
        st.caption(f"Terminal: {funnel.get('rejected', 0)} rejected, {funnel.get('ghosted', 0)} ghosted")

    st.markdown("#### Applications")
    st.caption("Descriptive stats only — small sample; not A/B significance.")

    for i, row in enumerate(rows):
        app_id = row.get("app_id", "")
        cols = st.columns([2, 2, 2, 1.5, 1.5, 1, 2])
        cols[0].write(row.get("date", ""))
        cols[1].write(row.get("company", ""))
        cols[2].write(row.get("role", ""))
        try:
            ats_pct = f"{float(row.get('ats_coverage', 0) or 0) * 100:.0f}%"
        except (TypeError, ValueError):
            ats_pct = "—"
        cols[3].write(row.get("track", ""))
        cols[4].write(ats_pct)
        current_stage = (row.get("stage") or "sent").lower()
        if current_stage not in STAGE_OPTIONS:
            current_stage = "sent"
        new_stage = cols[5].selectbox(
            "Stage",
            STAGE_OPTIONS,
            index=STAGE_OPTIONS.index(current_stage),
            key=f"outcome_stage_{app_id or i}",
            label_visibility="collapsed",
        )
        cols[6].caption(app_id[:8] if app_id else "")

        if new_stage != current_stage:
            rows[i] = {**row, "stage": new_stage}
            save_applications(rows)
            st.rerun()

    if st.button("Refresh", key="outcomes_refresh"):
        st.rerun()
