"""Calendar View — 30-day grid with completion status per day."""

from __future__ import annotations

import streamlit as st

from bootcamp.calendar import get_calendar


def render_calendar_view_tab() -> None:
    cal = get_calendar()
    from bootcamp.state import EDITING_DAY, PROGRESS, navigate_to_day

    progress = st.session_state.get(PROGRESS)

    st.subheader("30-Day Calendar")
    st.caption("Click any day to navigate to its scorecard.")

    # ── Legend ─────────────────────────────────────────────
    legend_cols = st.columns(4)
    with legend_cols[0]:
        st.markdown("🟢 Completed")
    with legend_cols[1]:
        st.markdown("🟡 In Progress")
    with legend_cols[2]:
        st.markdown("⬜ Not Started")
    with legend_cols[3]:
        st.markdown("📢 PA day")

    # ── Build the grid — 7 columns (Mon-Sun) per week ──────
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    weeks_data: list[list[dict]] = []  # each is 7 slots for a week row
    current_week: list[dict] = []

    for day in cal:
        dp = progress.days.get(day.number) if progress else None
        status = "completed" if (dp and dp.completed) else "pending"
        if dp and dp.completed:
            label = f"**Day {day.number}**\n{dp.grade or '—'}"
        else:
            label = f"Day {day.number}"

        is_pa = day.has_pa

        current_week.append({
            "day": day,
            "status": status,
            "label": label,
            "has_pa": is_pa,
        })

        if day.day_of_week == "Sunday" or day.number == 30:
            # Pad incomplete weeks
            while len(current_week) < 7:
                current_week.append(None)
            weeks_data.append(current_week)
            current_week = []

    # ── Render grid ────────────────────────────────────────
    for week_idx, week in enumerate(weeks_data):
        st.markdown(f"**Week {week_idx + 1}**")
        cols = st.columns(7)

        # Column headers
        for ci, name in enumerate(day_names):
            cols[ci].markdown(f"**{name}**")

        # Column content
        cols2 = st.columns(7)
        for ci, cell in enumerate(week):
            with cols2[ci]:
                if cell is None:
                    st.markdown("&nbsp;")
                    continue

                day = cell["day"]
                status = cell["status"]
                has_pa = cell["has_pa"]

                bg = (
                    "#d4edda" if status == "completed" else
                    "#fff3cd" if status == "in_progress" else
                    "#f8f9fa"
                )

                btn_label = (
                    f"**Day {day.number}**\n{progress.days[day.number].grade if progress and progress.days.get(day.number) and progress.days[day.number].completed else ''}"
                )

                clicked = st.button(
                    f"Day {day.number}",
                    key=f"cal_day_{day.number}",
                    use_container_width=True,
                    type="secondary",
                )

                if progress and progress.days.get(day.number) and progress.days[day.number].completed:
                    st.caption(f"Grade: {progress.days[day.number].grade}")
                elif has_pa:
                    st.caption("📢")

                if clicked:
                    navigate_to_day(day.number)
                    st.session_state[EDITING_DAY] = day.number
                    st.info(f"Navigated to Day {day.number}. Switch to 'Today's Focus' tab.")
