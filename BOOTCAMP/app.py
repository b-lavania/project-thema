"""PM Shock Cycle Bootcamp — 30-Day Interactive Web App."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# Ensure this directory's parent is on sys.path so bootcamp/ resolves
_BOOTCAMP_ROOT = Path(__file__).resolve().parent
if str(_BOOTCAMP_ROOT) not in sys.path:
    sys.path.insert(0, str(_BOOTCAMP_ROOT))

st.set_page_config(
    page_title="PM Shock Cycle Bootcamp",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

from bootcamp.state import init_bootcamp_state, PROGRESS, CURRENT_DAY
from bootcamp.calendar import get_calendar

# ── Session state initialisation ────────────────────────────────
init_bootcamp_state()

# ── Sidebar ─────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚡ Bootcamp")
    st.caption("30-Day PM Shock Cycle")

    progress = st.session_state.get(PROGRESS)
    if progress:
        completed = sum(1 for d in progress.days.values() if d.completed)
        st.metric("Days Completed", f"{completed} / 30", delta=f"Day {progress.current_day}")

    st.markdown("---")

    tab_options = [
        "Today's Focus",
        "Progress Dashboard",
        "Weekly Audit",
        "Drill Library",
        "Calendar View",
        "Artifacts",
        "Export",
    ]
    selected_tab = st.radio(
        "Navigate",
        tab_options,
        key="bc_sidebar_tab",
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.caption("Built from BOOTCAMP/ source docs")

# ── Tab routing ─────────────────────────────────────────────────
if selected_tab == "Today's Focus":
    from bootcamp.today_tab import render_today_tab
    render_today_tab()
elif selected_tab == "Progress Dashboard":
    from bootcamp.progress_tab import render_progress_tab
    render_progress_tab()
elif selected_tab == "Weekly Audit":
    from bootcamp.weekly_tab import render_weekly_tab
    render_weekly_tab()
elif selected_tab == "Drill Library":
    from bootcamp.drills import render_drill_library
    render_drill_library()
elif selected_tab == "Calendar View":
    from bootcamp.calendar_view_tab import render_calendar_view_tab
    render_calendar_view_tab()
elif selected_tab == "Artifacts":
    from bootcamp.artifacts_tab import render_artifacts_tab
    render_artifacts_tab()
elif selected_tab == "Export":
    from bootcamp.export_tab import render_export_tab
    render_export_tab()
