"""Streamlit tab: PM behavioral interview prep (ported from pm-behavioral-interview canvas)."""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

_DATA_PATH = Path(__file__).resolve().parent / "data" / "interview_prep.json"
_STATE_PATH = Path(__file__).resolve().parent / "data" / "interview_prep_state.json"

_TONE_LABEL = {"danger": "High risk", "warning": "Reframe", "info": "Standard"}
_TODO_CYCLE = ("pending", "in_progress", "completed")


@st.cache_data
def load_interview_prep_data(mtime: float) -> dict:
    with _DATA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def _load_state() -> dict:
    if _STATE_PATH.exists():
        try:
            return json.loads(_STATE_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _save_state(state: dict) -> None:
    _STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _init_session_state(data: dict) -> None:
    if "interview_prep_initialized" not in st.session_state:
        saved = _load_state()
        st.session_state.interview_prep_initialized = True
        st.session_state.interview_prep_notes = saved.get("practice_notes", "")
        todo_status = saved.get("todo_status", {})
        st.session_state.interview_prep_todos = {
            item["id"]: todo_status.get(item["id"], "pending")
            for item in data["prep_todos"]
        }

    if "interview_prep_roleplay_id" not in st.session_state:
        st.session_state.interview_prep_roleplay_id = data["roleplay"][0]["id"]


def _persist_state() -> None:
    _save_state(
        {
            "practice_notes": st.session_state.get("interview_prep_notes", ""),
            "todo_status": st.session_state.get("interview_prep_todos", {}),
        }
    )


def _render_opening(data: dict) -> None:
    spine = data["opening_spine"]
    cols = st.columns(len(data["stats"]))
    for col, stat in zip(cols, data["stats"]):
        col.metric(stat["value"], stat["label"])

    st.warning(f"**HR screen** — {data['hr_screen_note']}")

    with st.expander("Opening spine — say first", expanded=True):
        st.markdown("**Positioning thesis**")
        st.write(spine["positioning_thesis"])
        st.markdown("**60-second HR intro (~75 words)**")
        st.write(spine["hr_intro"])
        st.markdown("**One-sentence hire-me**")
        st.write(spine["hire_me_one_liner"])


def _render_psych_tricks(data: dict) -> None:
    st.caption("Expand each trick for do / say / avoid scripts.")
    for trick in data["psych_tricks"]:
        tone = trick["tone"]
        with st.expander(f"[{_TONE_LABEL.get(tone, tone)}] {trick['trick']}"):
            st.markdown("**What they're testing**")
            st.write(trick["test"])
            st.markdown("**Say this**")
            st.info(trick["counter"]["say"])
            col_do, col_avoid = st.columns(2)
            with col_do:
                st.markdown("**Do**")
                for i, line in enumerate(trick["counter"]["do"], 1):
                    st.write(f"{i}. {line}")
            with col_avoid:
                st.markdown("**Avoid**")
                for line in trick["counter"]["avoid"]:
                    st.caption(line)


def _render_roleplay(data: dict) -> None:
    options = {r["id"]: f"{r['category']}: {r['question'][:52]}…" for r in data["roleplay"]}
    selected_id = st.selectbox(
        "Scenario",
        options=list(options.keys()),
        format_func=lambda k: options[k],
        key="interview_prep_roleplay_select",
    )
    st.session_state.interview_prep_roleplay_id = selected_id
    scenario = next(r for r in data["roleplay"] if r["id"] == selected_id)

    st.markdown(f"### {scenario['category']}")
    st.caption(f"Lead story: **{scenario['leadStory']}**")

    st.markdown("**Interviewer asks**")
    st.write(scenario["question"])
    st.error(f"**Trap:** {scenario['trap']}")

    col_want, col_dont = st.columns(2)
    with col_want:
        st.markdown("**What they want**")
        st.write(scenario["whatTheyWant"])
    with col_dont:
        st.markdown("**Don't say**")
        st.caption(scenario["dontSay"])

    st.markdown("**Your opening line**")
    st.success(scenario["openingLine"])

    st.markdown("**Likely probe**")
    st.write(f"*{scenario['probe']}*")

    st.markdown("**Your probe answer**")
    st.write(scenario["probeAnswer"])

    notes = st.text_area(
        "Practice notes",
        key="interview_prep_notes",
        placeholder="What sounded defensive? Too technical? Where did you ramble?",
        height=100,
    )
    if st.button("Save practice notes", key="interview_prep_save_notes"):
        _persist_state()
        st.toast("Notes saved.")


def _render_story_bank(data: dict) -> None:
    stories = data["story_bank"]
    st.caption(
        "Full STAR bank from master_context — all 14 stories. Pick one, read S→T→A→R, "
        "then the 90-second spoken version. Do not merge metrics across stories."
    )

    roles = sorted({s.get("role", "") for s in stories if s.get("role")})
    col_f1, col_f2 = st.columns([1, 2])
    with col_f1:
        role_filter = st.selectbox("Role", ["All"] + roles, key="interview_prep_story_role")
    filtered = [s for s in stories if role_filter == "All" or s.get("role") == role_filter]
    with col_f2:
        options = {s["id"]: f"{s['id']} — {s['title']}" for s in filtered}
        ids = list(options.keys())
        if st.session_state.get("interview_prep_story_id") not in ids:
            st.session_state.interview_prep_story_id = ids[0]
        selected_id = st.selectbox(
            "Story",
            ids,
            format_func=lambda k: options[k],
            key="interview_prep_story_id",
        )
    story = next((s for s in filtered if s["id"] == selected_id), filtered[0])

    tags = story.get("tags") or []
    tag_label = tags if isinstance(tags, str) else " · ".join(tags)

    st.markdown(f"### {story['id']}: {story['title']}")
    st.caption(f"{story.get('role', '')}  ·  {story.get('headline_metrics', '')}")
    if tag_label:
        st.caption(tag_label)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Use for**")
        st.write(story.get("useFor", ""))
    with c2:
        st.markdown("**JD match**")
        st.write(story.get("jd_match", ""))

    st.markdown("**Situation**")
    st.write(story.get("situation", ""))
    st.markdown("**Task**")
    st.write(story.get("task", ""))
    st.markdown("**Action**")
    st.write(story.get("action", ""))
    st.markdown("**Result**")
    st.write(story.get("result", ""))

    spoken = story.get("spoken_90s")
    if spoken:
        st.markdown("**90-second spoken version (HR default)**")
        st.success(spoken)

    probe = story.get("if_they_probe")
    if probe:
        st.markdown("**If they probe**")
        st.write(probe)

    d1, d2 = st.columns(2)
    with d1:
        st.markdown("**HR depth**")
        st.caption(story.get("hr_depth", ""))
    with d2:
        st.markdown("**HM depth**")
        st.caption(story.get("hm_depth", ""))

    guardrail = story.get("guardrail")
    if guardrail:
        st.warning(f"**Guardrail:** {guardrail}")
    dont = story.get("dont_say")
    if dont:
        st.caption(f"Don't say: {dont}")

    st.markdown("#### All stories (index)")
    st.dataframe(
        [
            {
                "ID": s["id"],
                "Title": s["title"],
                "Role": s.get("role", ""),
                "Metrics": s.get("headline_metrics", ""),
                "Use for": s.get("useFor", ""),
            }
            for s in stories
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("### Question → story assignment")
    st.dataframe(
        data["story_assignments"],
        use_container_width=True,
        hide_index=True,
    )


def _render_slop(data: dict) -> None:
    for item in data["slop_antipatterns"]:
        with st.expander(item["slop"]):
            st.markdown("**Why it fails**")
            st.write(item["whyItFails"])
            st.markdown("**Say instead**")
            st.write(item["instead"])
            st.markdown("**Your story / script**")
            st.info(item["story"])
            if item.get("badExample") and item.get("goodExample"):
                col_bad, col_good = st.columns(2)
                with col_bad:
                    st.markdown("**Bad**")
                    st.caption(item["badExample"])
                with col_good:
                    st.markdown("**Good**")
                    st.write(item["goodExample"])


def _render_star_scripts(data: dict) -> None:
    for i, script in enumerate(data["star_scripts"]):
        with st.expander(script["title"], expanded=(i == 0)):
            st.write(f"**S:** {script['situation']}")
            st.write(f"**T:** {script['task']}")
            st.write(f"**A:** {script['action']}")
            st.write(f"**R:** {script['result']}")


def _render_hr_vs_hm(data: dict) -> None:
    st.dataframe(data["hr_vs_hm"], use_container_width=True, hide_index=True)


def _render_questions(data: dict) -> None:
    for i, q in enumerate(data["questions_to_ask"], 1):
        st.write(f"{i}. {q}")


def _render_checklist(data: dict) -> None:
    todos = st.session_state.interview_prep_todos
    done = sum(1 for s in todos.values() if s == "completed")
    st.caption(f"{done} of {len(todos)} done — click to cycle pending → in progress → done")

    for item in data["prep_todos"]:
        tid = item["id"]
        status = todos.get(tid, "pending")
        prefix = {"pending": "⬜", "in_progress": "🔄", "completed": "✅"}.get(status, "⬜")
        if st.button(f"{prefix} {item['content']}", key=f"interview_prep_todo_{tid}"):
            idx = _TODO_CYCLE.index(status) if status in _TODO_CYCLE else 0
            todos[tid] = _TODO_CYCLE[(idx + 1) % len(_TODO_CYCLE)]
            st.session_state.interview_prep_todos = todos
            _persist_state()
            st.rerun()


def render_interview_prep_tab() -> None:
    """Main render function for the Interview Prep tab."""
    data = load_interview_prep_data(_DATA_PATH.stat().st_mtime)
    _init_session_state(data)

    st.markdown("### PM behavioral interview prep")
    st.caption(
        "HR cheatsheet + roleplay drill. Source: master_context.md, CONCEPT3/CONCEPT1 portfolio, "
        "STAR story bank. Data: RES/data/interview_prep.json"
    )

    sections = st.tabs(
        [
            "Opening",
            "Psych tricks",
            "Roleplay",
            "Stories",
            "Slop flags",
            "STAR scripts",
            "HR vs HM",
            "Checklist",
        ]
    )

    with sections[0]:
        _render_opening(data)
    with sections[1]:
        _render_psych_tricks(data)
    with sections[2]:
        _render_roleplay(data)
    with sections[3]:
        _render_story_bank(data)
    with sections[4]:
        _render_slop(data)
    with sections[5]:
        _render_star_scripts(data)
    with sections[6]:
        _render_hr_vs_hm(data)
        st.markdown("### Questions to ask them")
        _render_questions(data)
        st.info(data["honest_gap_note"])
    with sections[7]:
        _render_checklist(data)
