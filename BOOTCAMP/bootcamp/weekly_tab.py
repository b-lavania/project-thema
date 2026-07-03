"""Weekly Audit — auto-populated weekly review with grade assignment."""

from __future__ import annotations

from typing import Any

import streamlit as st

from bootcamp.calendar import get_calendar


def _week_days(week: int) -> list[int]:
    """Return the day numbers for a given week (1-4)."""
    if week == 4:
        return [22, 23, 24, 25, 26, 27, 28, 29, 30]
    return list(range((week - 1) * 7 + 1, week * 7 + 1))


def render_weekly_tab() -> None:
    from bootcamp.state import PROGRESS

    progress = st.session_state.get(PROGRESS)
    if progress is None:
        st.info("Start the bootcamp to begin weekly audits.")
        return

    st.subheader("Weekly Audit")
    st.caption("Auto-populated from daily scorecards. Fill in qualitative review.")

    week = st.selectbox("Select Week", [1, 2, 3, 4], format_func=lambda w: f"Week {w}")
    day_numbers = _week_days(week)

    # ── Scoreboard Summary ─────────────────────────────────
    st.markdown("### Scoreboard Summary")

    daily_rows: list[dict[str, Any]] = []
    total = 0
    misses = 0
    days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    for i, dnum in enumerate(day_numbers):
        dp = progress.days.get(dnum)
        if dp and dp.completed:
            total += dp.score or 0
            if dp.quotas_hit < 6:
                misses += 1
            daily_rows.append(
                {
                    "Day": days_of_week[i] if i < 7 else f"Day {dnum}",
                    "Score": f"{dp.score:.0f}" if dp.score else "—",
                    "Grade": dp.grade or "—",
                    "Misses": 6 - dp.quotas_hit,
                }
            )
        else:
            daily_rows.append(
                {
                    "Day": days_of_week[i] if i < 7 else f"Day {dnum}",
                    "Score": "—",
                    "Grade": "—",
                    "Misses": "—",
                }
            )

    if daily_rows:
        import pandas as pd
        st.dataframe(pd.DataFrame(daily_rows), use_container_width=True, hide_index=True)

    # ── Weekly total ───────────────────────────────────────
    st.markdown(f"**Raw weekly total:** {total:.0f} points")
    if misses == 0:
        st.markdown("**Misses:** 0 — Perfect week! 🎉")
    else:
        st.markdown(f"**Misses:** {misses} day(s) with incomplete quotas")

    artifact_shipped = st.checkbox(
        "Public artifact shipped this week",
        value=progress.weeks.get(week, Any).artifact_shipped  # type: ignore[truthy-function]
        if progress.weeks.get(week)
        else False,
        key=f"wa_art_{week}",
    )

    # ── Quantified Review ──────────────────────────────────
    st.markdown("### Quantified Review")
    qcols = st.columns(3)
    with qcols[0]:
        decisions = st.number_input("Decisions made", 0, 50, 0, key=f"qr_dec_{week}")
        artifacts = st.number_input("Artifacts shipped", 0, 50, 0, key=f"qr_art_{week}")
    with qcols[1]:
        verbal_reps = st.number_input("Stakeholder reps", 0, 50, 0, key=f"qr_vr_{week}")
        tasks_cut = st.number_input("Tasks cut", 0, 100, 0, key=f"qr_cut_{week}")
    with qcols[2]:
        pub_art = st.checkbox("Public artifact shipped", value=artifact_shipped, key=f"qr_pa_{week}")

    # ── Qualitative Review ─────────────────────────────────
    st.markdown("### Qualitative Review")
    qual_review = {}
    qual_fields = [
        "Where did I make a real decision instead of analyzing forever?",
        "Where did I hide behind cleverness?",
        "Where did I optimize for elegance instead of outcome?",
        "Which conversation or artifact showed stronger executive presence?",
        "What did I cut that the old version of me would have kept?",
    ]
    for i, field in enumerate(qual_fields):
        qual_review[f"q{i}"] = st.text_area(
            field,
            height=80,
            key=f"qual_{i}_{week}",
        )

    # ── Anti-Pattern Detection ─────────────────────────────
    st.markdown("### Anti-Pattern Detection")
    anti_patterns = [
        "Open-option addiction: kept multiple paths open instead of committing",
        "Defensive language: over-justified claims or hedged recommendations",
        "Backlog sprawl: added tasks without cutting others",
        "Distribution avoidance: skipped outreach, publishing, or stakeholder conversations",
        "Novelty chase: started something new to avoid the boring middle",
        "Insight hoarding: had good ideas but didn't connect them to numbers",
        "Perfectionism delay: polished instead of shipping",
    ]
    detected = []
    for ap in anti_patterns:
        if st.checkbox(ap, key=f"ap_{week}_{anti_patterns.index(ap)}"):
            detected.append(ap)

    # ── Lagging muscle ─────────────────────────────────────
    st.markdown("### Lagging Muscle")
    muscles = [
        "Judgment",
        "Communication",
        "Commercial ownership",
        "Execution discipline",
        "Leadership under load",
    ]
    lagging = st.selectbox(
        "Which muscle is lagging hardest?",
        [""] + muscles,
        key=f"lagging_{week}",
    )

    # ── Next Week Focus ────────────────────────────────────
    st.markdown("### Next Week Focus")
    nwf_cols = st.columns(2)
    with nwf_cols[0]:
        double_down = st.text_input("One thing to double down on", key=f"nwf_dd_{week}")
        one_fix = st.text_input("One thing to fix", key=f"nwf_fix_{week}")
    with nwf_cols[1]:
        one_cut = st.text_input("One thing to cut", key=f"nwf_cut_{week}")
        day1_priority = st.text_input("Day 1 priority", key=f"nwf_d1_{week}")

    # ── Relapse check ──────────────────────────────────────
    st.markdown("### Relapse Check")
    rc_cols = st.columns(3)
    relapse_checks = {
        "no_new_project": "No new side project started",
        "no_new_identity": "No new identity experiment",
        "no_hidden_misses": "No hidden misses",
        "no_phone_rule": "No phone rule broken",
        "no_passive": "No passive consumption before quotas",
        "accountability": "Accountability partner check-in completed",
    }
    for i, (rckey, rclabel) in enumerate(relapse_checks.items()):
        col_idx = i % 3
        with rc_cols[col_idx]:
            st.checkbox(rclabel, key=f"rc_{rckey}_{week}")

    # ── Grade Assignment ──────────────────────────────────
    st.markdown("---")
    st.markdown("### Grade Assignment")

    a_eligible = total >= 400 and misses <= 1 and artifact_shipped
    b_eligible = total >= 320
    c_eligible = total >= 240

    suggested = "A" if a_eligible else "B" if b_eligible else "C" if c_eligible else "F"
    final_grade = st.selectbox(
        f"Suggested grade based on rubric: **{suggested}**",
        ["A", "B", "C", "F"],
        index=["A", "B", "C", "F"].index(suggested),
        key=f"final_grade_{week}",
    )

    if st.button("💾 Save Weekly Audit", type="primary", key=f"save_wa_{week}"):
        from bootcamp.data import WeekProgress, save_progress

        wp = WeekProgress(
            total=total,
            grade=final_grade,
            misses=misses,
            artifact_shipped=artifact_shipped,
        )
        progress.weeks[week] = wp
        save_progress(progress)
        st.session_state[PROGRESS] = progress
        st.success(f"Week {week} audit saved — Grade: {final_grade}")
