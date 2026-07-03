"""Session state management + day progression."""

from __future__ import annotations

from datetime import date

import streamlit as st

from bootcamp.calendar import get_calendar
from bootcamp.data import CampProgress, load_progress, save_progress
from bootcamp.scoring import compute_daily_score

# ── State key constants ──────────────────────────────────────────

CURRENT_DAY = "bc_current_day"
START_DATE = "bc_start_date"
PROGRESS = "bc_progress"
ACTIVE_TAB = "bc_active_tab"
EDITING_DAY = "bc_editing_day"
SCORECARD_FORM = "bc_scorecard_form"


def init_bootcamp_state() -> None:
    """Ensure all bootcamp session state keys exist."""
    progress = load_progress()

    if CURRENT_DAY not in st.session_state:
        st.session_state[CURRENT_DAY] = progress.current_day
    if START_DATE not in st.session_state:
        st.session_state[START_DATE] = (
            progress.start_date or date.today().isoformat()
        )
    if PROGRESS not in st.session_state:
        st.session_state[PROGRESS] = progress
    if ACTIVE_TAB not in st.session_state:
        st.session_state[ACTIVE_TAB] = "Today's Focus"
    if EDITING_DAY not in st.session_state:
        st.session_state[EDITING_DAY] = progress.current_day

    # Initialize scorecard form for current day if not present
    _ensure_form(progress.current_day)


def _ensure_form(day: int) -> None:
    """Initialize scorecard form data for a given day."""
    key = f"{SCORECARD_FORM}_{day}"
    if key not in st.session_state:
        st.session_state[key] = _fresh_scorecard(day)


def _fresh_scorecard(day: int) -> dict:
    return {
        "day": day,
        # Morning
        "wake_time": "",
        "phone_away": False,
        "day_plan": "",
        # Quotas
        "decision_completed": False,
        "decision_time": "",
        "artifact_completed": False,
        "artifact_time": "",
        "verbal_completed": False,
        "verbal_time": "",
        "cut_completed": False,
        "cut_time": "",
        "rewrite_completed": False,
        "rewrite_time": "",
        "scoreboard_completed": False,
        "scoreboard_time": "",
        # Blocks
        "block_a_activity": "",
        "block_a_completed": False,
        "block_b_activity": "",
        "block_b_completed": False,
        "block_c_activity": "",
        "block_c_completed": False,
        "block_hiit1_activity": "",
        "block_hiit1_completed": False,
        "block_hiit2_activity": "",
        "block_hiit2_completed": False,
        "block_stakeholder_activity": "",
        "block_stakeholder_completed": False,
        "block_compression_activity": "",
        "block_compression_completed": False,
        # Drills
        "hiit1_grade": 0,
        "hiit2_grade": 0,
        # Punishments
        "missed_quota_drill": False,
        "missed_2plus": False,
        "missed_artifact": False,
        "relapse": False,
        # Review
        "self_grade": "",
        "tomorrow_one_thing": "",
        "avoidance_patterns": [],
        "score": 0,
        "grade": "",
        "quotas_hit": 0,
        # Bonuses/penalties for scoring
        "bonuses": [],
        "penalties": [],
    }


def get_scorecard(day: int | None = None) -> dict:
    """Return the current scorecard form data."""
    if day is None:
        day = st.session_state[CURRENT_DAY]
    key = f"{SCORECARD_FORM}_{day}"
    _ensure_form(day)
    return st.session_state[key]


def save_scorecard(day: int | None = None) -> None:
    """Compute score, save to progress, persist to disk."""
    if day is None:
        day = st.session_state[CURRENT_DAY]
    card = get_scorecard(day)
    progress: CampProgress = st.session_state[PROGRESS]

    # Count quotas hit
    quota_fields = [
        "decision_completed",
        "artifact_completed",
        "verbal_completed",
        "cut_completed",
        "rewrite_completed",
        "scoreboard_completed",
    ]
    quotas_hit = sum(1 for f in quota_fields if card.get(f, False))

    # Bonuses
    bonuses = card.get("bonuses", [])
    penalties = card.get("penalties", [])

    # Compute score
    result = compute_daily_score(quotas_hit, bonuses, penalties)

    # Update card
    card["quotas_hit"] = quotas_hit
    card["score"] = result["total"]
    card["grade"] = result["grade"]

    # Persist to progress
    from bootcamp.data import DayProgress

    progress.days[day] = DayProgress(
        completed=True,
        score=float(result["total"]),
        grade=result["grade"],
        quotas_hit=quotas_hit,
    )
    progress.current_day = min(day + 1, 30)
    progress.start_date = st.session_state.get(START_DATE, date.today().isoformat())
    st.session_state[CURRENT_DAY] = progress.current_day

    save_progress(progress)
    st.session_state[PROGRESS] = progress


def advance_day() -> None:
    """Move to the next bootcamp day."""
    progress: CampProgress = st.session_state[PROGRESS]
    if progress.current_day < 30:
        progress.current_day += 1
    st.session_state[CURRENT_DAY] = progress.current_day
    st.session_state[EDITING_DAY] = progress.current_day
    save_progress(progress)
    st.session_state[PROGRESS] = progress
    _ensure_form(progress.current_day)


def navigate_to_day(day: int) -> None:
    """Navigate to a specific day (for calendar view nav)."""
    if 1 <= day <= 30:
        st.session_state[EDITING_DAY] = day
        _ensure_form(day)


def is_completed(day: int) -> bool:
    """Check if a day's scorecard is completed."""
    progress: CampProgress = st.session_state.get(PROGRESS, CampProgress())
    d = progress.days.get(day)
    return d is not None and d.completed
