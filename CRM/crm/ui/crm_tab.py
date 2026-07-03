"""Streamlit tab: Pipeline CRM — job-hunt operating system.

Six sections:
  1. Pipeline Board — Kanban view of companies by stage
  2. Company Detail — memo, outreach history, resume link
  3. Outreach Queue — weekly action queue + log form
  4. Content Studio — weekly artifact generation + publish
  5. Scoreboard — leading/lagging metrics + streaks
  6. Weekly Review — checklist + summary
"""

from __future__ import annotations

import json
from datetime import date

import streamlit as st

# ---------------------------------------------------------------------------
# Path setup — CRM already on sys.path from app.py
# ---------------------------------------------------------------------------
from crm.db import init_db
from crm.models import (
    ACTIONS,
    CHANNELS,
    PIPELINE_STAGES,
    SEGMENTS,
    TERMINAL_STAGES,
)
from crm.services.companies import (
    add_company,
    delete_company,
    get_company,
    import_from_leads,
    list_companies,
    load_seed_companies,
    update_company,
)
from crm.services.pipeline import (
    get_action_queue,
    get_pipeline_summary,
    move_stage,
    stage_status,
)
from crm.services.outreach import list_outreach, log_outreach, generate_outreach_llm
from crm.services.memos import (
    generate_memo_llm,
    get_all_memos,
    get_memo,
    save_memo,
)
from crm.services.artifacts import (
    generate_artifact_llm,
    list_artifacts,
    mark_published,
)
from crm.services.scoreboard import (
    auto_compute_outreach_metrics,
    artifact_streak,
    outbound_streak,
    upsert_metric,
    weekly_summary,
)
from crm.services.evidence import add_evidence, list_evidence

STAGE_ICONS = {
    "sourced": "🔍",
    "researching": "📝",
    "contacted": "📧",
    "conversation": "💬",
    "applied": "📄",
    "interview": "🎯",
    "onsite": "🏢",
    "offer": "🎉",
    "rejected": "❌",
    "ghosted": "👻",
}


def render_crm_tab(*, mode: str = "outreach"):
    """Main render function for the Pipeline CRM tab.

    mode="outreach" (default): Pipeline + memo + draft + log on company cards.
    mode="full": all sections including Content Studio, Scoreboard, Weekly Review.
    """
    init_db()

    # Seed data if empty
    companies = list_companies()
    if not companies:
        count = load_seed_companies()
        if count:
            st.success(f"Seeded {count} companies from data/companies.yaml")
            st.rerun()

    # --- Section tabs ---
    if mode == "outreach":
        st.caption(
            "Outreach mode: pipeline + memo + draft + log. "
            "Enable **Full CRM OS** in sidebar for scoreboard, content, and weekly review."
        )
        sec_board, sec_outreach = st.tabs([
            "📋 Pipeline Board",
            "📧 Outreach",
        ])
        with sec_board:
            _render_pipeline_board(card_mode="outreach")
        with sec_outreach:
            _render_outreach_section()
        return

    sec_board, sec_outreach, sec_content, sec_scoreboard, sec_review = st.tabs([
        "📋 Pipeline Board",
        "📧 Outreach",
        "✍️ Content Studio",
        "📊 Scoreboard",
        "📝 Weekly Review",
    ])

    # ==================================================================
    # Section 1: Pipeline Board
    # ==================================================================
    with sec_board:
        _render_pipeline_board(card_mode="full")

    # ==================================================================
    # Section 2: Outreach
    # ==================================================================
    with sec_outreach:
        _render_outreach_section()

    # ==================================================================
    # Section 3: Content Studio
    # ==================================================================
    with sec_content:
        _render_content_section()

    # ==================================================================
    # Section 4: Scoreboard
    # ==================================================================
    with sec_scoreboard:
        _render_scoreboard_section()

    # ==================================================================
    # Section 5: Weekly Review
    # ==================================================================
    with sec_review:
        _render_review_section()


# ------------------------------------------------------------------ helpers


def _needs_outreach(co: dict, days: int = 7) -> bool:
    """True if no outreach logged in the last N days."""
    from datetime import timedelta
    actions = list_outreach(company_id=co["id"], limit=20)
    if not actions:
        return True
    cutoff = date.today() - timedelta(days=days)
    for o in actions:
        try:
            if date.fromisoformat(o["date"]) >= cutoff:
                return False
        except (ValueError, TypeError):
            continue
    return True


def _batch1_filter(companies: list[dict]) -> list[dict]:
    """Batch-1: dream/realistic + sourced/researching + stale outreach."""
    result = []
    for co in companies:
        if co.get("segment") not in ("dream", "realistic"):
            continue
        if co.get("stage") not in ("sourced", "researching"):
            continue
        if not _needs_outreach(co):
            continue
        result.append(co)
    return result


def _render_pipeline_board(*, card_mode: str = "outreach"):
    companies = list_companies()
    summary = get_pipeline_summary()

    batch1_only = st.checkbox(
        "Batch-1 filter (dream/realistic, needs outreach)",
        key="crm_batch1_filter",
    )
    if batch1_only:
        companies = _batch1_filter(companies)
        if not companies:
            st.info("No Batch-1 companies need outreach right now.")
            return

    # Summary bar
    cols = st.columns(len(PIPELINE_STAGES) + 1)
    for i, stage in enumerate(PIPELINE_STAGES):
        count = summary.get(stage, 0)
        icon = STAGE_ICONS.get(stage, "📌")
        with cols[i]:
            st.metric(label=f"{icon} {stage.title()}", value=count)
    with cols[len(PIPELINE_STAGES)]:
        total = summary.get("_total", 0)
        breached = len(summary.get("_breached", []))
        st.metric(label="Total", value=total)
        if breached:
            st.caption(f"⚠️ {breached} SLA breach{'es' if breached > 1 else ''}")

    # SLA breach alerts
    breached = summary.get("_breached", [])
    if breached:
        with st.expander(f"⚠️ {len(breached)} SLA breach{'es' if len(breached) > 1 else ''}", expanded=True):
            for b in breached:
                st.markdown(
                    f"**{b['name']}** — {STAGE_ICONS.get(b['stage'], '')} {b['stage']} for "
                    f"**{b['days']}d** (SLA: {b['sla']}d)"
                )

    # Company cards by stage
    st.divider()
    for stage in PIPELINE_STAGES:
        stage_cos = [c for c in companies if c["stage"] == stage]
        if not stage_cos:
            continue
        with st.expander(f"{STAGE_ICONS.get(stage, '')} {stage.title()} ({len(stage_cos)})", expanded=False):
            for co in stage_cos:
                _render_company_card(co, card_mode=card_mode)

    # Add new company form
    st.divider()
    with st.expander("➕ Add Company", expanded=False):
        _render_add_company_form()


def _render_company_card(co: dict, *, card_mode: str = "outreach"):
    status = stage_status(co)
    days_str = f"{status['days']}d" if status["days"] is not None else "—"
    sla_warn = " ⚠️" if status["breached"] else ""

    col1, col2, col3 = st.columns([4, 1, 1])
    with col1:
        st.markdown(f"**{co['name']}** `[{co['segment']}]` — {co.get('industry', '')}")
        if co.get("url"):
            st.caption(f"🔗 {co['url']}")
        if co.get("hypothesis"):
            st.caption(f"💡 {co['hypothesis'][:120]}...")
    with col2:
        st.caption(f"⏱️ {days_str}{sla_warn}")
    with col3:
        # Stage selector
        current_idx = PIPELINE_STAGES.index(co["stage"]) if co["stage"] in PIPELINE_STAGES else 0
        new_stage = st.selectbox(
            "Stage",
            options=PIPELINE_STAGES + list(TERMINAL_STAGES),
            index=current_idx,
            key=f"stage_{co['id']}",
            label_visibility="collapsed",
        )
        if new_stage != co["stage"]:
            move_stage(co["id"], new_stage)
            st.rerun()

    # Detail sub-tabs
    if card_mode == "outreach":
        detail_tabs = st.tabs(["Memo", "Draft", "Log", "Contacts"])
        with detail_tabs[0]:
            _render_company_memo(co)
        with detail_tabs[1]:
            _render_company_draft(co)
        with detail_tabs[2]:
            _render_company_log(co)
        with detail_tabs[3]:
            _render_key_people(co)
    else:
        detail_tabs = st.tabs(["Memo", "Outreach", "Actions", "Contacts"])
        with detail_tabs[0]:
            _render_company_memo(co)
        with detail_tabs[1]:
            _render_company_outreach(co)
        with detail_tabs[2]:
            _render_company_actions(co)
        with detail_tabs[3]:
            _render_key_people(co)

    st.divider()


def _render_company_memo(co: dict):
    memo = get_memo(co["id"])
    if memo:
        st.markdown("**Stated Problem:** " + (memo.get("stated_problem") or "—"))
        st.markdown("**Real Bottleneck:** " + (memo.get("real_bottleneck") or "—"))
        st.markdown("**Wrong Solution:** " + (memo.get("wrong_solution") or "—"))
        st.markdown("**Metric to Move:** " + (memo.get("metric_to_move") or "—"))
        with st.expander("Full memo", expanded=False):
            st.text(memo.get("full_memo", ""))
    else:
        st.caption("No memo yet.")

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🤖 Generate Memo (LLM)", key=f"gen_memo_{co['id']}"):
            if st.session_state.get("_llm_client"):
                with st.spinner("Generating bottleneck memo..."):
                    result = generate_memo_llm(st.session_state._llm_client, co)
                    st.success("Memo generated")
                    st.rerun()
            else:
                st.warning("No LLM client — generate a resume first to initialize.")
    with col_b:
        # Manual memo entry
        with st.expander("✏️ Edit Memo", expanded=False):
            hypothesis = st.text_area(
                "Hypothesis / Notes",
                value=co.get("hypothesis", ""),
                key=f"memo_hypothesis_{co['id']}",
                height=100,
            )
            if st.button("Save Hypothesis", key=f"save_hyp_{co['id']}"):
                update_company(co["id"], hypothesis=hypothesis)
                st.success("Saved")
                st.rerun()


def _render_company_outreach(co: dict):
    actions = list_outreach(company_id=co["id"], limit=10)
    if actions:
        for o in actions:
            icon = "📨" if o["action"] == "sent" else "💬" if o["action"] == "replied" else "📅"
            st.markdown(
                f"{icon} **{o['channel']}** — {o['action']} | {o['date']}"
                + (f" | {o['contact_name']}" if o.get("contact_name") else "")
            )
    else:
        st.caption("No outreach logged yet.")


def _render_company_draft(co: dict):
    draft_key = f"outreach_draft_{co['id']}"
    if draft_key not in st.session_state:
        st.session_state[draft_key] = ""

    if st.button("🤖 Draft outreach (3 variants)", key=f"gen_draft_{co['id']}"):
        if st.session_state.get("_llm_client"):
            with st.spinner("Generating outreach drafts…"):
                text = generate_outreach_llm(st.session_state._llm_client, co)
                st.session_state[draft_key] = text
                st.rerun()
        else:
            st.warning("No LLM client — generate a resume first to initialize.")

    draft = st.text_area(
        "Outreach draft (cold email / LinkedIn / warm intro)",
        value=st.session_state.get(draft_key, ""),
        height=220,
        key=f"draft_text_{co['id']}",
    )
    if draft != st.session_state.get(draft_key):
        st.session_state[draft_key] = draft


def _render_company_log(co: dict):
    _render_company_outreach(co)
    with st.form(key=f"log_form_{co['id']}", clear_on_submit=True):
        st.caption("Log outreach")
        cols = st.columns(3)
        with cols[0]:
            channel = st.selectbox("Channel", CHANNELS, key=f"log_ch_{co['id']}")
        with cols[1]:
            action = st.selectbox("Action", ACTIONS, key=f"log_act_{co['id']}")
        with cols[2]:
            contact = st.text_input("Contact name", key=f"log_contact_{co['id']}")
        body = st.text_area("Note / subject", key=f"log_body_{co['id']}", height=80)
        if st.form_submit_button("Log"):
            log_outreach(co["id"], channel, action, contact_name=contact, body=body)
            st.success("Logged")
            st.rerun()

    if st.button("📝 Generate Resume", key=f"gen_resume_log_{co['id']}", use_container_width=True):
        st.session_state.company_name = co["name"]
        if co.get("url"):
            st.session_state.jd_url = co["url"]
            st.session_state._auto_scrape_from_url = True
        st.session_state["_prefill_from_crm"] = True
        st.info("Open **Job Details** → paste or confirm JD → **Generate**.")


def _render_key_people(co: dict):
    people = co.get("key_people") or []
    if not people:
        people = [{"name": "", "role": "", "linkedin": ""}]

    st.caption("Founder / key contact for Series-A outreach")
    updated: list[dict] = []
    for i, person in enumerate(people):
        cols = st.columns(3)
        with cols[0]:
            name = st.text_input("Name", value=person.get("name", ""), key=f"kp_name_{co['id']}_{i}")
        with cols[1]:
            role = st.text_input("Role", value=person.get("role", ""), key=f"kp_role_{co['id']}_{i}")
        with cols[2]:
            linkedin = st.text_input("LinkedIn", value=person.get("linkedin", ""), key=f"kp_li_{co['id']}_{i}")
        if name.strip() or role.strip() or linkedin.strip():
            updated.append({"name": name.strip(), "role": role.strip(), "linkedin": linkedin.strip()})

    if st.button("Save contacts", key=f"save_kp_{co['id']}"):
        update_company(co["id"], key_people=updated)
        st.success("Contacts saved")
        st.rerun()


def _render_company_actions(co: dict):
    # Log outreach
    with st.form(key=f"outreach_form_{co['id']}", clear_on_submit=True):
        st.caption("Log outreach")
        cols = st.columns(3)
        with cols[0]:
            channel = st.selectbox("Channel", CHANNELS, key=f"ch_{co['id']}")
        with cols[1]:
            action = st.selectbox("Action", ACTIONS, key=f"act_{co['id']}")
        with cols[2]:
            contact = st.text_input("Contact name", key=f"contact_{co['id']}")
        body = st.text_area("Note / subject", key=f"body_{co['id']}", height=80)
        if st.form_submit_button("Log"):
            log_outreach(co["id"], channel, action, contact_name=contact, body=body)
            st.success("Logged")
            st.rerun()

    # Generate resume button
    if st.button("📝 Generate Resume", key=f"gen_resume_{co['id']}", use_container_width=True):
        st.session_state.company_name = co["name"]
        if co.get("url"):
            st.session_state.jd_url = co["url"]
            st.session_state._auto_scrape_from_url = True
        st.session_state["_prefill_from_crm"] = True
        st.info("Open **Job Details** → paste or confirm JD → **Generate**. Track stage in **Outcomes**.")


def _render_add_company_form():
    with st.form("add_company_form", clear_on_submit=True):
        cols = st.columns(2)
        with cols[0]:
            name = st.text_input("Company name *")
            url = st.text_input("URL")
            industry = st.text_input("Industry")
        with cols[1]:
            segment = st.selectbox("Segment", SEGMENTS)
            linkedin = st.text_input("LinkedIn URL")
            careers = st.text_input("Careers URL")
        notes = st.text_area("Notes / hypothesis", height=80)
        if st.form_submit_button("Add Company", type="primary"):
            if name.strip():
                add_company(
                    name=name.strip(),
                    url=url.strip(),
                    linkedin_url=linkedin.strip(),
                    careers_url=careers.strip(),
                    industry=industry.strip(),
                    segment=segment,
                    hypothesis=notes.strip(),
                    notes=notes.strip(),
                )
                st.success(f"Added {name}")
                st.rerun()
            else:
                st.warning("Company name is required")


def _render_outreach_section():
    st.markdown("### Outreach Queue")

    # Action queue (SLA approaching/breached)
    queue = get_action_queue()
    if queue:
        st.caption(f"**{len(queue)}** companies need action this week")
        for co in queue:
            days = co.get("_days", "?")
            sla = co.get("_sla", "?")
            st.markdown(
                f"- **{co['name']}** — {STAGE_ICONS.get(co['stage'], '')} {co['stage']} "
                f"({days}d / {sla}d SLA)"
            )
    else:
        st.success("All companies within SLA — no urgent action needed.")

    st.divider()

    # Log outreach (standalone)
    st.markdown("### Log Outreach")
    companies = list_companies()
    if not companies:
        st.info("Add companies first.")
        return

    company_names = {c["name"]: c["id"] for c in companies}
    with st.form("standalone_outreach", clear_on_submit=True):
        cols = st.columns(3)
        with cols[0]:
            selected = st.selectbox("Company", list(company_names.keys()))
        with cols[1]:
            channel = st.selectbox("Channel", CHANNELS, key="so_channel")
        with cols[2]:
            action = st.selectbox("Action", ACTIONS, key="so_action")
        contact = st.text_input("Contact name", key="so_contact")
        body = st.text_area("Note / subject", key="so_body", height=80)
        if st.form_submit_button("Log", type="primary"):
            cid = company_names[selected]
            log_outreach(cid, channel, action, contact_name=contact, body=body)
            st.success("Logged")
            st.rerun()

    # Recent outreach
    st.divider()
    st.markdown("### Recent Outreach")
    recent = list_outreach(limit=20)
    if recent:
        for o in recent:
            icon = "📨" if o["action"] == "sent" else "💬" if o["action"] == "replied" else "📅"
            st.markdown(
                f"{icon} **{o['channel']}** — {o['action']} | {o['date']}"
                + (f" | {o.get('contact_name', '')}" if o.get("contact_name") else "")
            )
    else:
        st.caption("No outreach logged yet.")


def _render_content_section():
    st.markdown("### ✍️ Content Studio")

    # New artifact
    with st.expander("Generate New Artifact", expanded=False):
        topic = st.selectbox(
            "Topic",
            ["bottleneck", "dispatch", "ai-in-ops", "pricing", "quoting", "marketplace", "field-service", "general"],
            key="artifact_topic",
        )
        insight = st.text_area(
            "Key insight or angle",
            height=100,
            key="artifact_insight",
            placeholder="What observation or pattern do you want to write about?",
        )
        if st.button("Generate Artifact", type="primary", key="gen_artifact"):
            if st.session_state.get("_llm_client"):
                with st.spinner("Generating artifact..."):
                    result = generate_artifact_llm(st.session_state._llm_client, topic, insight)
                    st.success(f"Artifact saved: {result.get('title', '')}")
                    st.rerun()
            else:
                st.warning("No LLM client — generate a resume first to initialize.")

    # List artifacts
    artifacts = list_artifacts()
    if artifacts:
        st.divider()
        st.markdown(f"### Artifacts ({len(artifacts)})")
        for a in artifacts:
            status = "✅ Published" if a["published"] else "📝 Draft"
            with st.expander(f"{status} — {a['title']} ({a['date_created']})", expanded=False):
                st.markdown(a["body"])
                if not a["published"]:
                    if st.button("Mark Published", key=f"pub_{a['id']}"):
                        mark_published(a["id"], published_to="linkedin")
                        st.success("Marked published + saved to data/published/")
                        st.rerun()
    else:
        st.info("No artifacts yet. Generate your first one above.")


def _render_scoreboard_section():
    st.markdown("### 📊 Scoreboard")

    # Auto-compute today's metrics from outreach
    today = date.today().isoformat()
    auto_compute_outreach_metrics(today)

    # This week vs last week
    this_week = weekly_summary(0)
    last_week = weekly_summary(1)

    st.markdown("**This Week**")
    cols = st.columns(4)
    metrics_this = [
        ("Outbound", this_week["outbound_touches"]),
        ("Intros", this_week["warm_intro_requests"]),
        ("Conversations", this_week["conversations"]),
        ("Replies", this_week["replies_received"]),
    ]
    for i, (label, val) in enumerate(metrics_this):
        prev = [last_week["outbound_touches"], last_week["warm_intro_requests"],
                last_week["conversations"], last_week["replies_received"]][i]
        delta = val - prev if prev else None
        with cols[i]:
            st.metric(label, value=val, delta=delta)

    cols2 = st.columns(4)
    metrics_this2 = [
        ("Applications", this_week["applications"]),
        ("Interviews", this_week["interviews_booked"]),
        ("Onsites", this_week["onsites"]),
        ("Artifacts", this_week["artifacts_published"]),
    ]
    for i, (label, val) in enumerate(metrics_this2):
        with cols2[i]:
            st.metric(label, value=val)

    # Streaks
    st.divider()
    st.markdown("**Streaks**")
    col_a, col_b = st.columns(2)
    with col_a:
        streak = outbound_streak()
        st.metric("Outbound Streak", value=f"{streak}d")
    with col_b:
        art_streak = artifact_streak()
        st.metric("Artifact Streak", value=f"{art_streak}w")

    # Manual metric entry
    st.divider()
    with st.expander("✏️ Update Manual Metrics", expanded=False):
        with st.form("manual_metrics", clear_on_submit=True):
            cols = st.columns(3)
            with cols[0]:
                applications = st.number_input("Applications", min_value=0, value=0)
                interviews = st.number_input("Interviews Booked", min_value=0, value=0)
            with cols[1]:
                onsites = st.number_input("Onsites", min_value=0, value=0)
                wip = st.number_input("WIP Count", min_value=0, value=0)
            with cols[2]:
                notes = st.text_input("Notes")
            if st.form_submit_button("Save"):
                upsert_metric(
                    today,
                    applications=applications,
                    interviews_booked=interviews,
                    onsites=onsites,
                    wip_count=wip,
                    notes=notes,
                )
                st.success("Saved")
                st.rerun()

    # Evidence ledger
    st.divider()
    st.markdown("### 📚 Evidence Ledger")
    evidence = list_evidence()
    with st.expander(f"View Evidence ({len(evidence)} items)", expanded=False):
        for e in evidence:
            st.markdown(f"- **{e['claim']}** — {e['evidence'][:100]}...")
    with st.expander("➕ Add Evidence", expanded=False):
        with st.form("add_evidence", clear_on_submit=True):
            claim = st.text_input("Claim")
            ev = st.text_area("Evidence", height=80)
            src = st.text_input("Source (optional)")
            if st.form_submit_button("Add"):
                if claim.strip() and ev.strip():
                    add_evidence(claim.strip(), ev.strip(), src.strip())
                    st.success("Added")
                    st.rerun()


def _render_review_section():
    st.markdown("### 📝 Weekly Review")

    # Checklist
    st.markdown("**Friday Checklist**")
    checklist = {
        "Pipeline reviewed": st.checkbox("Pipeline reviewed", key="review_pipeline"),
        "Outreach logged": st.checkbox("Outreach logged this week", key="review_outreach"),
        "Artifact published": st.checkbox("Artifact published", key="review_artifact"),
        "Metrics updated": st.checkbox("Metrics updated", key="review_metrics"),
    }
    completed = sum(1 for v in checklist.values() if v)
    total = len(checklist)
    st.progress(completed / total)
    st.caption(f"{completed}/{total} complete")

    # Weekly summary
    st.divider()
    this_week = weekly_summary(0)
    st.markdown("**Week Summary**")
    st.json({
        "outbound_touches": this_week["outbound_touches"],
        "warm_intro_requests": this_week["warm_intro_requests"],
        "conversations": this_week["conversations"],
        "replies_received": this_week["replies_received"],
        "applications": this_week["applications"],
        "interviews_booked": this_week["interviews_booked"],
        "onsites": this_week["onsites"],
        "artifacts_published": this_week["artifacts_published"],
    })

    # Review questions
    st.divider()
    st.markdown("**Review Questions** (from 90-day-scoreboard.md)")
    questions = [
        "Did I move the pipeline, or did I just think about it?",
        "Did I distribute externally and internally, or did I hide in building?",
        "Did every active task connect to interview generation, proof quality, or the one number?",
        "Did I try to escape into a new identity, domain, or elegant side path?",
    ]
    for q in questions:
        st.text_area(q, height=68, key=f"review_q_{q[:30]}")

    # Parking lot
    st.divider()
    st.markdown("**🅿️ Parking Lot** (recorded, not activated)")
    st.caption("New ideas go here — not onto the calendar.")
    st.text_area(
        "Parking lot (one idea per line)",
        height=120,
        key="parking_lot",
        placeholder="Logistics AI benchmarking tool...\nConsulting offer from X...",
    )
