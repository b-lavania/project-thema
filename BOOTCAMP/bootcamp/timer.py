"""Countdown timer with start/stop/reset for Streamlit."""

from __future__ import annotations

import time

import streamlit as st


def render_timer(
    duration_minutes: int,
    key: str = "drill_timer",
    label: str | None = None,
) -> None:
    """Render a countdown timer in Streamlit.

    Stores state under ``st.session_state[f"{key}_*"]``.

    Args:
        duration_minutes: Total timer duration.
        key: Session state key prefix.
        label: Optional display label above the timer.
    """
    state_key = f"{key}_start"
    running_key = f"{key}_running"
    done_key = f"{key}_done"

    if state_key not in st.session_state:
        st.session_state[state_key] = 0.0
    if running_key not in st.session_state:
        st.session_state[running_key] = False
    if done_key not in st.session_state:
        st.session_state[done_key] = False

    duration_sec = duration_minutes * 60

    # ── Compute elapsed ──────────────────────────────────────
    if st.session_state[running_key] and st.session_state[state_key] > 0:
        elapsed = time.time() - st.session_state[state_key]
        if elapsed >= duration_sec:
            elapsed = duration_sec
            st.session_state[running_key] = False
            st.session_state[done_key] = True
    else:
        elapsed = 0.0

    remaining = max(0, duration_sec - elapsed)
    mins, secs = divmod(int(remaining), 60)
    display = f"{mins}:{secs:02d}"

    # ── Display ──────────────────────────────────────────────
    if label:
        st.markdown(f"**{label}** — {duration_minutes} min")

    st.markdown(
        f"<div style='font-size:3rem;text-align:center;"
        f"font-family:monospace;padding:0.5rem;"
        f"background:#f0f2f6;border-radius:8px;'>{display}</div>",
        unsafe_allow_html=True,
    )

    if st.session_state[done_key]:
        st.success("⏰ Time's up!")  # noqa: RUF001 — incorrect unicode but intentional for emoji

    cols = st.columns(3)
    with cols[0]:
        if st.button("▶ Start", key=f"{key}_start_btn", disabled=st.session_state[running_key]):
            st.session_state[state_key] = time.time()
            st.session_state[running_key] = True
            st.session_state[done_key] = False
            st.rerun()

    with cols[1]:
        if st.button("⏸ Stop", key=f"{key}_stop_btn", disabled=not st.session_state[running_key]):
            st.session_state[running_key] = False
            st.session_state[done_key] = False
            st.rerun()

    with cols[2]:
        if st.button("↺ Reset", key=f"{key}_reset_btn"):
            st.session_state[state_key] = 0.0
            st.session_state[running_key] = False
            st.session_state[done_key] = False
            st.rerun()

    # ── Auto-refresh while running ───────────────────────────
    if st.session_state[running_key] and remaining > 0:
        time.sleep(0.5)
        st.rerun()
