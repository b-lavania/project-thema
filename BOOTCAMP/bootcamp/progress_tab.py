"""Progress Dashboard — score visualization, streaks, camp progress."""

from __future__ import annotations

import streamlit as st

from bootcamp.calendar import get_calendar
from bootcamp.scoring import CAMP_TARGET, compute_camp_score


def render_progress_tab() -> None:
    from bootcamp.state import PROGRESS

    progress = st.session_state.get(PROGRESS)
    if progress is None:
        st.info("Start the bootcamp to see progress.")
        return

    cal = get_calendar()
    if not progress.days:
        st.info("No scorecards saved yet. Complete a day to see progress.")
        return

    # ── Overview cards ──────────────────────────────────────
    completed = [d for d in progress.days.values() if d.completed]
    total_scores = [d.score or 0 for d in completed]
    avg_score = sum(total_scores) / len(total_scores) if total_scores else 0

    kpi_cols = st.columns(4)
    with kpi_cols[0]:
        st.metric("Days Completed", f"{len(completed)} / 30")
    with kpi_cols[1]:
        st.metric("Average Score", f"{avg_score:.0f}/80")
    with kpi_cols[2]:
        st.metric("Total Points", f"{progress.total_score:.0f}")
    with kpi_cols[3]:
        st.metric("Review Streak", f"{progress.review_streak} days")

    # ── Score chart ─────────────────────────────────────────
    st.subheader("Daily Scores")
    chart_data = {
        "Score": [d.score or 0 for d in progress.days.values()],
        "Day": list(range(1, len(progress.days) + 1)),
    }
    if chart_data["Score"]:
        import pandas as pd

        df = pd.DataFrame(chart_data)
        df.set_index("Day", inplace=True)

        c1, c2 = st.columns([3, 1])
        with c1:
            st.line_chart(df, y="Score", height=250)
        with c2:
            st.caption("80 = max daily")
            st.caption("60 = all quotas")
            st.caption("40 = 2/3 quotas")

    # ── Weekly breakdown ────────────────────────────────────
    st.subheader("Weekly Scores")
    week_data = []
    for wk in range(1, 5):
        w = progress.weeks.get(wk)
        if w:
            week_data.append(
                {
                    "Week": f"Week {wk}",
                    "Total": w.total,
                    "Grade": w.grade or "—",
                    "Misses": w.misses,
                    "Artifact": "✅" if w.artifact_shipped else "❌",
                }
            )

    if week_data:
        import pandas as pd

        st.dataframe(
            pd.DataFrame(week_data),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.caption("Complete weekly audits to show weekly breakdown.")

    # ── Camp progress bar ───────────────────────────────────
    st.subheader("Camp Progress")
    camp_pct = min(100, int(progress.total_score / CAMP_TARGET * 100))
    st.progress(camp_pct / 100)
    st.caption(
        f"{progress.total_score:.0f} / {CAMP_TARGET} points ({camp_pct}%) "
        f"— need 8,000+ to pass camp"
    )

    # ── Camp status preview ─────────────────────────────────
    if len(completed) >= 7:
        week_grades = [
            w.grade or "—"
            for wk in range(1, 5)
            for w in [progress.weeks.get(wk)]
            if w
        ]
        artifacts = sum(1 for w in progress.weeks.values() if w.artifact_shipped)

        camp = compute_camp_score(
            total_points=progress.total_score,
            week_grades=week_grades,
            public_artifacts=artifacts,
            portfolio_assets=0,
            review_streak=progress.review_streak,
        )

        if camp["passed"]:
            st.success(f"🎉 On track for camp **{camp['grade']}**!")
        else:
            for f in camp["failures"]:
                st.warning(f"⚠️ {f}")

    # ── Grade distribution ──────────────────────────────────
    st.subheader("Grade Distribution")
    grades = {"A": 0, "B": 0, "C": 0, "F": 0}
    for d in completed:
        g = d.grade or ""
        if g in grades:
            grades[g] += 1

    if sum(grades.values()) > 0:
        import pandas as pd

        gdf = pd.DataFrame(
            {"Grade": list(grades.keys()), "Count": list(grades.values())}
        )
        st.bar_chart(gdf.set_index("Grade"), height=200)
    else:
        st.caption("No graded days yet.")
