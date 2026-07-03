"""Today's Focus — main day-by-day interactive experience."""

from __future__ import annotations

import streamlit as st

from bootcamp.calendar import get_calendar
from bootcamp.drills import render_drill
from bootcamp.state import (
    EDITING_DAY,
    get_scorecard,
    is_completed,
    save_scorecard,
)


def _nav_col(delta: int, label: str, day_num: int) -> None:
    """Render a navigation button that changes the editing day."""
    target = day_num + delta
    disabled = target < 1 or target > 30
    if st.button(label, disabled=disabled, use_container_width=True):
        st.session_state[EDITING_DAY] = target
        st.rerun()


def render_today_tab() -> None:
    cal = get_calendar()
    day_num = st.session_state.get(EDITING_DAY, 1)
    day = cal[day_num - 1] if 1 <= day_num <= len(cal) else cal[0]

    # ── Header + Nav ────────────────────────────────────────
    hcols = st.columns([1, 3, 1])
    with hcols[0]:
        _nav_col(-1, "◀ Previous", day_num)
    with hcols[1]:
        status = "✅" if is_completed(day_num) else "⬜"
        st.subheader(f"{status} Day {day.number} — {day.day_of_week}")
        st.caption(f"Week {day.week}: {day.theme}")
        st.markdown(f"**Focus:** {day.focus}")
        if day.has_pa:
            st.markdown("📢 **Public Artifact Day** — PA quota required")
    with hcols[2]:
        _nav_col(1, "Next ▶", day_num)

    card = get_scorecard(day.number)

    # ── Morning Setup ──────────────────────────────────────
    with st.expander("🌅 Morning Setup", expanded=True):
        card["wake_time"] = st.text_input(
            "Wake time", card.get("wake_time", ""),
            key=f"wake_{day.number}",
            placeholder="e.g. 06:30",
        )
        card["phone_away"] = st.checkbox(
            "Phone left in another room during first block",
            card.get("phone_away", False),
            key=f"phone_{day.number}",
        )
        card["day_plan"] = st.text_area(
            "Day plan (3 bullets)",
            card.get("day_plan", ""),
            height=80,
            key=f"plan_{day.number}",
            placeholder="1. …\n2. …\n3. …",
        )

    # ── Daily Quotas ────────────────────────────────────────
    with st.expander("🎯 Daily Quotas (6)", expanded=True):
        quota_fields = [
            ("decision", "Hard product decision written down"),
            ("artifact", "Written artifact completed"),
            ("verbal", "Verbal communication rep completed"),
            ("cut", "Backlog cut made"),
            ("rewrite", "Anti-defensiveness rewrite completed"),
            ("scoreboard", "Scoreboard entry published"),
        ]
        quotas_hit = 0
        for key, label in quota_fields:
            done = st.checkbox(
                label,
                card.get(f"{key}_completed", False),
                key=f"q_{key}_{day.number}",
            )
            card[f"{key}_completed"] = done
            if done:
                quotas_hit += 1

        st.markdown(f"**Quotas hit: {quotas_hit} / 6**")
        card["quotas_hit"] = quotas_hit

    # ── Block Log ───────────────────────────────────────────
    with st.expander("📋 Block Log", expanded=True):
        block_labels = [
            ("a", "A: Cognitive brutality (07:00-08:30)"),
            ("b", "B: Communication rep (08:45-09:30)"),
            ("c", "C: Operator rep (09:45-11:15)"),
            ("hiit1", "HIIT Drill 1 (11:30-12:00)"),
            ("hiit2", "HIIT Drill 2 + Backlog (13:00-14:00)"),
            ("stakeholder", "Stakeholder simulation (14:15-15:00)"),
            ("compression", "Compression / rewrite (15:15-16:00)"),
        ]
        for blk_key, blk_label in block_labels:
            c1, c2 = st.columns([3, 1])
            with c1:
                activity_key = f"block_{blk_key}_activity"
                card[activity_key] = st.text_input(
                    blk_label,
                    card.get(activity_key, ""),
                    key=f"blk_{blk_key}_{day.number}",
                    placeholder="What did you do?",
                )
            with c2:
                done_key = f"block_{blk_key}_completed"
                card[done_key] = st.checkbox(
                    "Done",
                    card.get(done_key, False),
                    key=f"blk_done_{blk_key}_{day.number}",
                )

    # ── HIIT Drills ─────────────────────────────────────────
    if day.hiit1:
        with st.expander(
            f"🏋️ HIIT 1: Drill {day.hiit1.drill_number} — {day.hiit1.drill_name}",
            expanded=True,
        ):
            st.caption(day.hiit1.description)
            render_drill(
                day.hiit1.drill_number,
                key_suffix=f"_day{day.number}_h1",
            )

    if day.hiit2:
        with st.expander(
            f"🏋️ HIIT 2: Drill {day.hiit2.drill_number} — {day.hiit2.drill_name}",
            expanded=True,
        ):
            st.caption(day.hiit2.description)
            render_drill(
                day.hiit2.drill_number,
                key_suffix=f"_day{day.number}_h2",
            )

    # ── Punishment Log ──────────────────────────────────────
    with st.expander("⚠️ Punishment Log", expanded=False):
        pun_data = [
            ("missed_quota_drill", "Missed 1 quota → extra evening drill"),
            ("missed_2plus", "Missed 2+ quotas → weekend catch-up"),
            ("missed_artifact", "Missed public artifact deadline"),
            ("relapse", "Relapse into new identity/project"),
        ]
        for p_key, p_label in pun_data:
            card[p_key] = st.checkbox(
                p_label,
                card.get(p_key, False),
                key=f"pun_{p_key}_{day.number}",
            )

    # ── Daily Review ────────────────────────────────────────
    with st.expander("📝 Daily Review", expanded=True):
        grade_options = [
            "",
            "A: All quotas hit, no avoidance, strong output",
            "B: One miss, quickly corrected",
            "C: Multiple misses or visible drift",
            "F: Hidden miss, relapse, or skipped review",
        ]
        current_grade = card.get("self_grade", "")
        grade_idx = 0
        for i, opt in enumerate(grade_options):
            if opt.startswith(current_grade) and current_grade:
                grade_idx = i
                break

        card["self_grade"] = st.selectbox(
            "Self-grade for the day",
            grade_options,
            index=grade_idx,
            key=f"sg_{day.number}",
        )
        # Store just the letter
        card["self_grade_letter"] = card["self_grade"][0] if card["self_grade"] else ""

        avoidance_opts = [
            "Hiding behind nuance",
            "Chasing novelty",
            "Over-defending claims",
            "Avoiding stakeholder conversation",
            "Optimizing for elegance over outcome",
        ]
        card["avoidance_patterns"] = st.multiselect(
            "Which avoidance pattern showed up?",
            avoidance_opts,
            default=card.get("avoidance_patterns", []),
            key=f"avoid_{day.number}",
        )

        card["tomorrow_one_thing"] = st.text_area(
            "Tomorrow's one thing (the single most important quota)",
            card.get("tomorrow_one_thing", ""),
            height=80,
            key=f"tomorrow_{day.number}",
            placeholder="The one quota I absolutely must hit tomorrow",
        )

    # ── Save ─────────────────────────────────────────────────
    st.markdown("---")
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if st.button(
            "💾 Save Day",
            type="primary",
            use_container_width=True,
            key=f"save_{day.number}",
        ):
            save_scorecard(day.number)
            saved_card = get_scorecard(day.number)
            st.success(
                f"Day {day.number} saved! "
                f"Score: {saved_card.get('score', 0)}/80 — "
                f"Grade: {saved_card.get('grade', '—')}"
            )
            st.rerun()

    with c1:
        if st.button("📋 Today is done, advance to next day", use_container_width=True):
            save_scorecard(day.number)
            from bootcamp.state import advance_day

            advance_day()
            st.success(f"Advanced to Day {st.session_state[EDITING_DAY]}")
            st.rerun()
