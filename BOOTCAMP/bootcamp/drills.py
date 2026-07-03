"""Render all 8 bootcamp drill forms."""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd
import streamlit as st

# ── Drill configuration ──────────────────────────────────────────


@dataclass
class DrillConfig:
    number: int
    name: str
    duration_minutes: int
    instructions: list[str]
    field_labels: list[str]  # text_area labels
    field_heights: list[int] = field(default_factory=lambda: [100] * 8)
    self_checks: list[str] = field(default_factory=list)


DRILLS: dict[int, DrillConfig] = {
    1: DrillConfig(
        number=1,
        name="15-Minute Product Teardown",
        duration_minutes=15,
        instructions=[
            "No research, no browsing, no 'let me check'",
            "Use what you already know or can infer",
            "15 minutes, hard stop",
        ],
        field_labels=[
            "1. Who is it for? (2 min) — One sentence, be specific",
            "2. What core behavior matters? (2 min) — Single action that indicates success",
            "3. Where is the friction? (3 min) — Where do users stall/drop/complain?",
            "4. What metric would I inspect first? (2 min) — One metric, why this one?",
            "5. What would I cut? (3 min) — One feature or flow, why?",
            "6a. Stated problem (3 min)",
            "6b. Actual problem (3 min)",
        ],
        self_checks=[
            "Completed in 15 minutes or less",
            "No hedging language",
            "One clear recommendation implied",
            "Would a CEO understand this in 30 seconds?",
        ],
    ),
    2: DrillConfig(
        number=2,
        name="Recommendation Under Constraint",
        duration_minutes=10,
        instructions=[
            "You have incomplete information. That's the point.",
            "Decide anyway.",
        ],
        field_labels=[
            "Context (2 min) — Write what you know. Don't research.",
            "The Decision (3 min) — What do you recommend? One sentence.",
            "Rationale bullet 1 (3 min)",
            "Rationale bullet 2 (3 min)",
            "Rationale bullet 3 (3 min)",
            "Risk (2 min) — What's the biggest risk if you're wrong?",
            "Rollback (2 min) — How would you know it's wrong? What would you do?",
        ],
        self_checks=[
            "Completed in 10 minutes",
            "One clear recommendation stated",
            "Risk acknowledged, not dwelled on",
            "Rollback plan exists",
        ],
    ),
    3: DrillConfig(
        number=3,
        name="Anti-Defensiveness Rewrite",
        duration_minutes=7,
        instructions=[
            "Find something you wrote that feels important but soft",
            "Could be a resume bullet, positioning, case study, or recommendation",
        ],
        field_labels=[
            "Original text (paste what you're rewriting)",
            "Hedge found 1 — e.g. 'I think', 'might', 'relatively'",
            "Hedge found 2",
            "Hedge found 3",
            "The brutal rewrite — Same claim, no hedges, no throat-clearing",
        ],
        self_checks=[
            "Original had hedges",
            "Rewrite has zero hedges",
            "Meaning preserved",
            "Sounds stronger, not just louder",
        ],
    ),
    4: DrillConfig(
        number=4,
        name="Operator Translation",
        duration_minutes=10,
        instructions=[
            "Pick a real product decision or problem",
            "Explain it three ways to three different audiences",
        ],
        field_labels=[
            "Topic / decision you're translating",
            "Version 1: PM Language (3 min) — Frameworks, users, journeys, hypotheses",
            "Version 2: Executive / Commercial (3 min) — Revenue, cost, risk, timeline, ROI",
            "Version 3: Operator / Frontline (3 min) — Actions, pain, workarounds, trust",
            "The synthesis (1 min) — Which version is truest? Which moves the decision?",
        ],
        field_heights=[80, 150, 150, 150, 100],
        self_checks=[
            "All three versions completed",
            "Each version sounds natural to its audience",
            "No version is just the others with jargon swapped",
            "Synthesis identifies the leverage point",
        ],
    ),
    5: DrillConfig(
        number=5,
        name="Backlog Triage Sprint",
        duration_minutes=10,
        instructions=[
            "Gather 10 real or hypothetical tasks",
            "Defend every cut",
        ],
        field_labels=[
            "The 2 that survive — Item 1",
            "Why keep item 1?",
            "The 2 that survive — Item 2",
            "Why keep item 2?",
            "The hardest cut — Which task was hardest to kill? Why?",
        ],
        field_heights=[80, 120, 80, 120, 120],
        self_checks=[
            "Completed in 10 minutes",
            "Every cut has a reason",
            "Every keep has a metric",
            "Hardest cut acknowledged",
        ],
    ),
    6: DrillConfig(
        number=6,
        name="Executive Compression Under Pressure",
        duration_minutes=8,
        instructions=[
            "Take any messy page of notes, a long email, or a complex document",
            "Compress to 3 bullets + recommendation + ask",
        ],
        field_labels=[
            "Source material — What are you compressing?",
            "Original length (e.g. '500 words, 4 pages')",
            "Bullet 1 — The context",
            "Bullet 2 — The problem",
            "Bullet 3 — The opportunity",
            "The recommendation",
            "The ask",
            "Total compressed length (words)",
        ],
        self_checks=[
            "Completed in 8 minutes",
            "Exactly 3 bullets",
            "Exactly 1 recommendation",
            "Exactly 1 ask",
            "A CEO could read it in 30 seconds and know what to do",
        ],
    ),
    7: DrillConfig(
        number=7,
        name="Hostile Stakeholder Response",
        duration_minutes=10,
        instructions=[
            "No hedging, no apologizing, no over-explaining",
            "One explicit recommendation",
        ],
        field_labels=[
            "Your decision / bet",
            "The stakeholder",
            "Their objection",
            "Your response (10 min)",
        ],
        self_checks=[
            "Completed in 10 minutes",
            "Zero hedging",
            "Acknowledges the concern without folding",
            "One explicit recommendation stated",
            "Would you trust this person with a hard decision?",
        ],
    ),
    8: DrillConfig(
        number=8,
        name="Five-Minute Spoken Diagnosis",
        duration_minutes=5,
        instructions=[
            "No notes, no slides, no prep beyond 30 seconds",
            "Record yourself or present to a peer",
        ],
        field_labels=[
            "Product being diagnosed",
            "Transcript or summary of your spoken diagnosis",
            "What broke down?",
            "What would I do differently?",
        ],
        field_heights=[80, 200, 120, 120],
        self_checks=[
            "Spoke for 4-5 minutes (not 2, not 10)",
            "No notes used",
            "One clear problem identified",
            "One clear recommendation implied or stated",
            "No 'ums' or throat-clearing at the start",
            "Sounded confident, not tentative",
        ],
    ),
}


# ── Shared drill result helpers ──────────────────────────────────


def _drill_state_key(drill_num: int, suffix: str = "") -> str:
    return f"drill_{drill_num}_result{suffix}"


def get_drill_result(drill_num: int) -> dict:
    """Get saved drill result from session state."""
    key = _drill_state_key(drill_num)
    return st.session_state.get(key, {})


def save_drill_result(drill_num: int, data: dict) -> None:
    """Save drill result to session state."""
    key = _drill_state_key(drill_num)
    st.session_state[key] = data


# ── Triage data editor helper ────────────────────────────────────


def _render_triage_table() -> pd.DataFrame:
    """Render the backlog triage data editor and return the edited df."""
    default_tasks = [
        {"Task": "", "Metric it moves": "", "Effort": "Medium", "Cut?": False, "Why": ""}
        for _ in range(10)
    ]
    df = pd.DataFrame(default_tasks)
    edited = st.data_editor(
        df,
        column_config={
            "Task": st.column_config.TextColumn("Task", width="medium"),
            "Metric it moves": st.column_config.TextColumn("Metric", width="medium"),
            "Effort": st.column_config.SelectColumn("Effort", options=["Low", "Medium", "High", "Critical"]),
            "Cut?": st.column_config.CheckboxColumn("Cut?"),
            "Why": st.column_config.TextColumn("Why cut/keep", width="medium"),
        },
        num_rows="fixed",
        hide_index=True,
        key="triage_editor",
    )
    return edited


# ── Main drill renderer ──────────────────────────────────────────


def _render_grade_and_self_checks(cfg: DrillConfig, key_suffix: str) -> tuple[int, list[bool]]:
    """Render self-check checkboxes and grade slider."""
    self_check_results: list[bool] = []
    for i, check_text in enumerate(cfg.self_checks):
        checked = st.checkbox(check_text, key=f"drill_{cfg.number}_chk_{i}_{key_suffix}")
        self_check_results.append(checked)

    st.markdown("---")
    grade = st.slider(
        "Grade /10",
        0, 10, 0, 1,
        key=f"drill_{cfg.number}_grade_{key_suffix}",
    )
    return grade, self_check_results


def render_drill(drill_number: int, key_suffix: str = "") -> dict | None:
    """Render the drill form for the given drill number.

    Returns the saved result dict if the user clicks Save, else None.
    """
    cfg = DRILLS.get(drill_number)
    if cfg is None:
        st.error(f"Unknown drill #{drill_number}")
        return None

    # ── Header ──────────────────────────────────────────────
    st.subheader(f"Drill {cfg.number}: {cfg.name}")
    st.caption(f"⏱ {cfg.duration_minutes} minutes — hard stop")

    for inst in cfg.instructions:
        st.info(inst)

    saved = get_drill_result(drill_number)
    if saved:
        st.success(f"✅ Saved — Grade: {saved.get('grade', '—')}/10")

    # ── Drill 5 has a data editor table ─────────────────────
    if drill_number == 5:
        st.markdown("### The 10 tasks")
        st.caption("Fill in your backlog. Cut anything that doesn't move a metric.")
        triage_df = _render_triage_table()

        st.markdown("### Survivors & hardest cut")
        field_values: list[str] = []
        for i, label in enumerate(cfg.field_labels):
            val = st.text_area(
                label,
                value=saved.get("fields", [""] * len(cfg.field_labels))[i]
                if i < len(saved.get("fields", []))
                else "",
                height=cfg.field_heights[i] if i < len(cfg.field_heights) else 100,
                key=f"drill_{drill_number}_f_{i}_{key_suffix}",
            )
            field_values.append(val)

        grade, self_checks = _render_grade_and_self_checks(cfg, key_suffix)

        if st.button("💾 Save Drill Result", key=f"drill_{drill_number}_save_{key_suffix}"):
            result = {
                "drill_number": drill_number,
                "duration_minutes": cfg.duration_minutes,
                "completed": True,
                "fields": field_values,
                "triage_table": triage_df.to_dict(orient="records"),
                "self_checks": self_checks,
                "grade": grade,
            }
            save_drill_result(drill_number, result)
            st.rerun()
            return result
        return saved if saved else None

    # ── Standard text-area drill forms ──────────────────────
    field_values: list[str] = []
    for i, label in enumerate(cfg.field_labels):
        val = st.text_area(
            label,
            value=saved.get("fields", [""] * len(cfg.field_labels))[i]
            if i < len(saved.get("fields", []))
            else "",
            height=cfg.field_heights[i] if i < len(cfg.field_heights) else 100,
            key=f"drill_{drill_number}_f_{i}_{key_suffix}",
        )
        field_values.append(val)

    grade, self_checks = _render_grade_and_self_checks(cfg, key_suffix)

    if st.button("💾 Save Drill Result", key=f"drill_{drill_number}_save_{key_suffix}"):
        result = {
            "drill_number": drill_number,
            "duration_minutes": cfg.duration_minutes,
            "completed": True,
            "fields": field_values,
            "self_checks": self_checks,
            "grade": grade,
        }
        save_drill_result(drill_number, result)
        st.rerun()
        return result

    return saved if saved else None


# ── Standalone drill library view ────────────────────────────────


def render_drill_library() -> None:
    """Render drill library tab — browse and practice any drill."""
    st.subheader("Drill Library")
    st.caption("Practice any drill outside the daily flow. Results are saved per session.")

    selected = st.selectbox(
        "Choose a drill to practice",
        options=list(DRILLS.keys()),
        format_func=lambda n: f"Drill {n}: {DRILLS[n].name} ({DRILLS[n].duration_minutes} min)",
        key="drill_library_select",
    )

    st.markdown("---")
    # Unique key_suffix so it doesn't conflict with today tab state
    render_drill(selected, key_suffix="_lib")

    # Reset button
    if st.button("🧹 Clear saved result for this drill", key="drill_lib_clear"):
        key = _drill_state_key(selected)
        if key in st.session_state:
            del st.session_state[key]
            st.rerun()
