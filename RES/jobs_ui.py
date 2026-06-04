"""Streamlit UI components for the Board APIs Watcher Jobs tab."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import streamlit as st

from jobs_watcher import (
    DEFAULT_SEED,
    JOBS_JSONL_PATH,
    JobRecord,
    apply_filters,
    classify_title,
    compute_fit,
    export_jsonl,
    html_to_text,
    import_jsonl,
    load_jobs_index,
    location_matches,
    manual_add,
    run_fetch,
    save_jobs,
    title_matches,
    validate_slug,
)

# ---------------------------------------------------------------------------
# Session state helpers
# ---------------------------------------------------------------------------
_JOBS_PAGE_KEY = "jobs_page"
_JOBS_PER_PAGE = 25


def _init_state():
    """Seed session state keys once."""
    if "watcher_companies" not in st.session_state:
        st.session_state.watcher_companies = json.loads(json.dumps(DEFAULT_SEED))
    if "watcher_last_run" not in st.session_state:
        st.session_state.watcher_last_run = "Never"
    if "watcher_filter_company" not in st.session_state:
        st.session_state.watcher_filter_company = []
    if "watcher_filter_keyword" not in st.session_state:
        st.session_state.watcher_filter_keyword = ""
    if "watcher_filter_status" not in st.session_state:
        st.session_state.watcher_filter_status = []
    if "watcher_filter_location" not in st.session_state:
        st.session_state.watcher_filter_location = []
    if "watcher_filter_seniority" not in st.session_state:
        st.session_state.watcher_filter_seniority = []
    if "watcher_remote_policy" not in st.session_state:
        st.session_state.watcher_remote_policy = "canada_na_only"
    if "watcher_show_hidden" not in st.session_state:
        st.session_state.watcher_show_hidden = False
    if "watcher_sort_by" not in st.session_state:
        st.session_state.watcher_sort_by = "Posted Date (newest)"
    if "watcher_view_mode" not in st.session_state:
        st.session_state.watcher_view_mode = "table"
    if _JOBS_PAGE_KEY not in st.session_state:
        st.session_state[_JOBS_PAGE_KEY] = 1
    if "watcher_selected_ids" not in st.session_state:
        st.session_state.watcher_selected_ids = []
    if "watcher_fit_job_id" not in st.session_state:
        st.session_state.watcher_fit_job_id = None
    if "watcher_generate_job_id" not in st.session_state:
        st.session_state.watcher_generate_job_id = None
    if "watcher_new_since_run" not in st.session_state:
        st.session_state.watcher_new_since_run = []
    if "watcher_run_log" not in st.session_state:
        st.session_state.watcher_run_log = []


# ---------------------------------------------------------------------------
# Filter / sort logic
# ---------------------------------------------------------------------------
def _filter_jobs(jobs: dict[str, JobRecord]) -> list[JobRecord]:
    out: list[JobRecord] = []
    for job in jobs.values():
        if not st.session_state.watcher_show_hidden:
            if not title_matches(job.title):
                continue
            if not location_matches(job, st.session_state.watcher_remote_policy):
                continue

        company_filter = st.session_state.watcher_filter_company
        if company_filter and job.company not in company_filter:
            continue

        kw = st.session_state.watcher_filter_keyword.strip().lower()
        if kw and kw not in job.title.lower() and kw not in job.company.lower():
            continue

        status_filter = st.session_state.watcher_filter_status
        if status_filter and job.status not in status_filter:
            continue

        loc_filter = st.session_state.watcher_filter_location
        if loc_filter:
            loc_lower = job.location.lower()
            matched = False
            for f in loc_filter:
                if f == "Canada" and any(p in loc_lower for p in ["canada", "toronto", "vancouver", "montreal", "calgary", "edmonton", "ottawa", "waterloo", "kitchener", "bc", "ab", "on", "qc"]):
                    matched = True
                elif f == "Remote" and "remote" in loc_lower:
                    matched = True
                elif f == "North America" and any(p in loc_lower for p in ["north america", "na", "us", "usa", "united states"]):
                    matched = True
                elif f == "Global" and any(p in loc_lower for p in ["remote", "anywhere", "global", "worldwide"]):
                    matched = True
            if not matched:
                continue

        seniority_filter = st.session_state.watcher_filter_seniority
        if seniority_filter:
            tax = classify_title(job.title)
            if tax.get("seniority", "IC") not in seniority_filter:
                continue

        out.append(job)

    sort = st.session_state.watcher_sort_by
    if sort == "Posted Date (newest)":
        out.sort(key=lambda j: j.created_at or "", reverse=True)
    elif sort == "Posted Date (oldest)":
        out.sort(key=lambda j: j.created_at or "")
    elif sort == "Fit Score (high)":
        out.sort(key=lambda j: j.fit.get("score", 0), reverse=True)
    elif sort == "Fit Score (low)":
        out.sort(key=lambda j: j.fit.get("score", 0))
    elif sort == "Company (A-Z)":
        out.sort(key=lambda j: j.company.lower())
    return out


# ---------------------------------------------------------------------------
# Badges
# ---------------------------------------------------------------------------
def _render_badges(job: JobRecord) -> str:
    badges = []
    loc_lower = job.location.lower()
    if any(p in loc_lower for p in ["canada", "toronto", "vancouver", "montreal", "calgary", "edmonton", "ottawa", "bc", "ab", "on", "qc"]):
        badges.append("🇨🇦 Canada")
    if "remote" in loc_lower:
        badges.append("🌐 Remote")
    if any(p in loc_lower for p in ["north america", "na", "us", "usa"]):
        badges.append("🇺🇸 NA")
    jd_lower = job.jd_raw.lower()
    if any(p in jd_lower for p in ["ai", "machine learning", "ml", "llm", "genai", "artificial intelligence"]):
        badges.append("🤖 AI")
    if any(p in jd_lower for p in ["marketplace", "platform", "network"]):
        badges.append("🏪 Marketplace")
    if job.id in st.session_state.get("watcher_new_since_run", []):
        badges.append("🆕 New")
    return " · ".join(badges) if badges else ""


# ---------------------------------------------------------------------------
# Status helpers
# ---------------------------------------------------------------------------
_STATUS_ORDER = ["discovered", "shortlisted", "applied", "followup", "archived"]
_STATUS_COLORS = {
    "discovered": "#6B7280",
    "shortlisted": "#3B82F6",
    "applied": "#10B981",
    "followup": "#F59E0B",
    "archived": "#9CA3AF",
}

_STATUS_LABELS = {
    "discovered": "🔍 Discovered",
    "shortlisted": "⭐ Shortlisted",
    "applied": "📤 Applied",
    "followup": "⏰ Follow-up",
    "archived": "🗑️ Archived",
}


def _next_action_badge(job: JobRecord) -> str | None:
    """Return reminder text if a follow-up is due."""
    if job.status != "applied":
        return None
    # Find last applied transition
    for entry in reversed(job.status_history):
        if entry.get("status") == "applied":
            try:
                dt = datetime.fromisoformat(entry["changed_at"].replace("Z", "+00:00"))
                days = (datetime.now(timezone.utc) - dt).days
                if days >= 7:
                    return f"⏰ {days}d since applied"
            except Exception:
                pass
            break
    return None


# ---------------------------------------------------------------------------
# Companies config UI
# ---------------------------------------------------------------------------
def _render_companies_config():
    st.markdown("### Companies Config")
    st.caption("One slug per line. Select platform for each.")

    companies = st.session_state.watcher_companies
    cols = st.columns([3, 2, 1])
    with cols[0]:
        st.markdown("**Company**")
    with cols[1]:
        st.markdown("**Platform**")
    with cols[2]:
        st.markdown("**Slug**")

    edited = []
    for i, cfg in enumerate(companies):
        c1, c2, c3 = st.columns([3, 2, 1])
        with c1:
            name = st.text_input("Name", value=cfg.get("company", ""), key=f"wc_name_{i}", label_visibility="collapsed")
        with c2:
            plat = st.selectbox("Platform", ["greenhouse", "lever", "ashby"], index=["greenhouse", "lever", "ashby"].index(cfg.get("platform", "greenhouse")), key=f"wc_plat_{i}", label_visibility="collapsed")
        with c3:
            slug = st.text_input("Slug", value=cfg.get("slug", ""), key=f"wc_slug_{i}", label_visibility="collapsed")
        edited.append({"company": name, "platform": plat, "slug": slug})

    st.session_state.watcher_companies = edited

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("➕ Add Company", use_container_width=True):
            st.session_state.watcher_companies.append({"company": "", "platform": "greenhouse", "slug": ""})
            st.rerun()
    with c2:
        if st.button("🔄 Reset to Defaults", use_container_width=True):
            st.session_state.watcher_companies = json.loads(json.dumps(DEFAULT_SEED))
            st.rerun()
    with c3:
        if st.button("✅ Validate All", use_container_width=True):
            results = []
            for cfg in edited:
                if not cfg["slug"]:
                    continue
                res = validate_slug(cfg["slug"], cfg["platform"])
                icon = "✅" if res["ok"] else "❌"
                results.append(f"{icon} {cfg['company'] or cfg['slug']}: {res['error'] or 'OK'}")
            st.session_state.watcher_validation_results = results
            st.rerun()

    if "watcher_validation_results" in st.session_state:
        for r in st.session_state.watcher_validation_results:
            st.markdown(r)


# ---------------------------------------------------------------------------
# Run Now
# ---------------------------------------------------------------------------
def _render_run_now(master_context: str):
    st.markdown("### Run Now")
    st.caption(f"Last run: {st.session_state.watcher_last_run}")

    if st.button("🚀 Fetch Jobs", type="primary", use_container_width=True):
        active = [c for c in st.session_state.watcher_companies if c.get("slug")]
        with st.spinner("Fetching jobs..."):
            stats = run_fetch(active, remote_policy=st.session_state.watcher_remote_policy)
        st.session_state.watcher_last_run = datetime.now().strftime("%Y-%m-%d %H:%M")
        st.session_state.watcher_run_log = stats["log"]
        st.session_state.watcher_new_since_run = stats["new_ids"]
        st.success(
            f"Done: {stats['new']} new, {stats['updated']} updated, {stats['skipped']} skipped"
        )
        if stats["errors"]:
            for err in stats["errors"]:
                st.error(err)
        st.rerun()

    if st.session_state.get("watcher_run_log"):
        with st.expander("Run log"):
            for entry in st.session_state.watcher_run_log:
                st.markdown(f"- {entry}")


# ---------------------------------------------------------------------------
# Filter bar
# ---------------------------------------------------------------------------
def _render_filter_bar(all_jobs: dict[str, JobRecord]):
    with st.expander("🔍 Filters & Sort", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            companies = sorted({j.company for j in all_jobs.values()})
            st.multiselect("Company", companies, key="watcher_filter_company")
        with c2:
            st.text_input("Keyword", key="watcher_filter_keyword", placeholder="Title or company...")
        with c3:
            statuses = list(_STATUS_LABELS.keys())
            st.multiselect("Status", statuses, format_func=lambda x: _STATUS_LABELS[x], key="watcher_filter_status")

        c1, c2, c3 = st.columns(3)
        with c1:
            st.multiselect("Location", ["Canada", "Remote", "North America", "Global"], key="watcher_filter_location")
        with c2:
            st.multiselect("Seniority", ["IC", "Senior", "Principal", "Group", "Manager"], key="watcher_filter_seniority")
        with c3:
            st.selectbox("Sort", [
                "Posted Date (newest)", "Posted Date (oldest)",
                "Fit Score (high)", "Fit Score (low)", "Company (A-Z)"
            ], key="watcher_sort_by")

        c1, c2 = st.columns(2)
        with c1:
            st.radio("Remote Policy", ["canada_na_only", "global_remote"], format_func=lambda x: "Canada/NA Only" if x == "canada_na_only" else "Global Remote", key="watcher_remote_policy")
        with c2:
            st.checkbox("Show hidden (excluded by filters)", key="watcher_show_hidden")

        if st.button("Clear All Filters", use_container_width=True):
            st.session_state.watcher_filter_company = []
            st.session_state.watcher_filter_keyword = ""
            st.session_state.watcher_filter_status = []
            st.session_state.watcher_filter_location = []
            st.session_state.watcher_filter_seniority = []
            st.session_state.watcher_show_hidden = False
            st.rerun()


# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------
def _paginate_jobs(jobs: list[JobRecord]) -> list[JobRecord]:
    total = len(jobs)
    page = st.session_state.get(_JOBS_PAGE_KEY, 1)
    pages = max(1, (total + _JOBS_PER_PAGE - 1) // _JOBS_PER_PAGE)
    page = max(1, min(page, pages))
    st.session_state[_JOBS_PAGE_KEY] = page
    start = (page - 1) * _JOBS_PER_PAGE
    end = start + _JOBS_PER_PAGE
    return jobs[start:end]


def _render_pagination(total: int):
    pages = max(1, (total + _JOBS_PER_PAGE - 1) // _JOBS_PER_PAGE)
    page = st.session_state.get(_JOBS_PAGE_KEY, 1)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        if st.button("◀ Prev", disabled=page <= 1, use_container_width=True):
            st.session_state[_JOBS_PAGE_KEY] = page - 1
            st.rerun()
    with c2:
        st.markdown(f"<div style='text-align:center; padding-top: 8px;'>Page {page} of {pages} ({total} jobs)</div>", unsafe_allow_html=True)
    with c3:
        if st.button("Next ▶", disabled=page >= pages, use_container_width=True):
            st.session_state[_JOBS_PAGE_KEY] = page + 1
            st.rerun()


# ---------------------------------------------------------------------------
# Table view
# ---------------------------------------------------------------------------
def _render_table(jobs: list[JobRecord], all_jobs: dict[str, JobRecord], master_context: str):
    if not jobs:
        st.info("No jobs match current filters.")
        return

    # Bulk actions
    selected = st.session_state.get("watcher_selected_ids", [])
    if selected:
        st.markdown(f"**{len(selected)} selected**")
        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("⭐ Shortlist Selected", use_container_width=True):
                for jid in selected:
                    if jid in all_jobs:
                        _transition_status(all_jobs[jid], "shortlisted")
                save_jobs(all_jobs)
                st.session_state.watcher_selected_ids = []
                st.rerun()
        with b2:
            if st.button("🗑️ Archive Selected", use_container_width=True):
                for jid in selected:
                    if jid in all_jobs:
                        _transition_status(all_jobs[jid], "archived")
                save_jobs(all_jobs)
                st.session_state.watcher_selected_ids = []
                st.rerun()
        with b3:
            if st.button("Clear Selection", use_container_width=True):
                st.session_state.watcher_selected_ids = []
                st.rerun()

    # Header
    header = st.columns([0.5, 2.5, 1.5, 1.5, 1, 1.5, 2])
    with header[0]:
        st.markdown("**Sel**")
    with header[1]:
        st.markdown("**Title**")
    with header[2]:
        st.markdown("**Company**")
    with header[3]:
        st.markdown("**Location**")
    with header[4]:
        st.markdown("**Fit**")
    with header[5]:
        st.markdown("**Status**")
    with header[6]:
        st.markdown("**Actions**")

    for job in jobs:
        row = st.columns([0.5, 2.5, 1.5, 1.5, 1, 1.5, 2])
        with row[0]:
            is_sel = job.id in selected
            if st.checkbox("", value=is_sel, key=f"sel_{job.id}", label_visibility="collapsed"):
                if job.id not in selected:
                    selected.append(job.id)
            else:
                if job.id in selected:
                    selected.remove(job.id)
            st.session_state.watcher_selected_ids = selected

        with row[1]:
            is_new = job.id in st.session_state.get("watcher_new_since_run", [])
            prefix = "**🆕** " if is_new else ""
            st.markdown(f"{prefix}{job.title}")
            badges = _render_badges(job)
            if badges:
                st.caption(badges)
        with row[2]:
            st.markdown(job.company)
        with row[3]:
            st.markdown(job.location or "—")
        with row[4]:
            score = job.fit.get("score", 0)
            color = "#10B981" if score >= 70 else "#F59E0B" if score >= 40 else "#EF4444"
            st.markdown(f"<span style='color:{color}; font-weight:600;'>{score}</span>", unsafe_allow_html=True)
        with row[5]:
            new_status = st.selectbox(
                "",
                _STATUS_ORDER,
                index=_STATUS_ORDER.index(job.status) if job.status in _STATUS_ORDER else 0,
                format_func=lambda x: _STATUS_LABELS[x],
                key=f"status_{job.id}",
                label_visibility="collapsed",
            )
            if new_status != job.status:
                _transition_status(job, new_status)
                save_jobs(all_jobs)
                st.rerun()
            reminder = _next_action_badge(job)
            if reminder:
                st.caption(reminder)
        with row[6]:
            a1, a2, a3 = st.columns(3)
            with a1:
                if st.button("👁", key=f"view_{job.id}", use_container_width=True, help="View JD"):
                    st.session_state.watcher_view_job_id = job.id
                    st.rerun()
            with a2:
                if st.button("⚡", key=f"fit_{job.id}", use_container_width=True, help="Preview Fit"):
                    st.session_state.watcher_fit_job_id = job.id
                    st.rerun()
            with a3:
                if st.button("🚀", key=f"gen_{job.id}", use_container_width=True, help="Generate"):
                    st.session_state.watcher_generate_job_id = job.id
                    st.rerun()


# ---------------------------------------------------------------------------
# Kanban view
# ---------------------------------------------------------------------------
def _render_kanban(jobs: list[JobRecord], all_jobs: dict[str, JobRecord]):
    cols = st.columns(len(_STATUS_ORDER))
    for i, status in enumerate(_STATUS_ORDER):
        with cols[i]:
            st.markdown(f"<div style='background:{_STATUS_COLORS[status]}; color:white; padding:8px; border-radius:8px; text-align:center; font-weight:600;'>{_STATUS_LABELS[status]}</div>", unsafe_allow_html=True)
            status_jobs = [j for j in jobs if j.status == status]
            for job in status_jobs[:20]:  # Cap per column
                st.markdown(
                    f"<div style='border:1px solid #E5E7EB; border-radius:8px; padding:10px; margin-bottom:8px;'>"
                    f"<strong>{job.title}</strong><br>"
                    f"<span style='color:#6B7280; font-size:0.85em;'>{job.company} · {job.location or '—'}</span><br>"
                    f"<span style='color:{_STATUS_COLORS[status]}; font-weight:600;'>Fit: {job.fit.get('score', 0)}</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("View", key=f"kview_{job.id}", use_container_width=True):
                        st.session_state.watcher_view_job_id = job.id
                        st.rerun()
                with c2:
                    if st.button("Gen", key=f"kgen_{job.id}", use_container_width=True):
                        st.session_state.watcher_generate_job_id = job.id
                        st.rerun()


# ---------------------------------------------------------------------------
# JD Panel
# ---------------------------------------------------------------------------
def _render_jd_panel(job: JobRecord, all_jobs: dict[str, JobRecord], master_context: str):
    st.markdown("---")
    st.markdown(f"### {job.title} at {job.company}")
    st.caption(f"{job.location or '—'} · {job.url}")

    tabs = st.tabs(["Structured", "Raw JD", "Notes"])
    with tabs[0]:
        structured = job.jd_structured or {}
        with st.expander("DUTIES", expanded=True):
            for item in structured.get("duties", []):
                st.markdown(f"- {item}")
        with st.expander("REQUIREMENTS"):
            for item in structured.get("requirements", []):
                st.markdown(f"- {item}")
        with st.expander("TOOLS & KEYWORDS"):
            for item in structured.get("tools", []):
                st.markdown(f"- {item}")
    with tabs[1]:
        if st.button("📋 Copy JD", key=f"copy_jd_{job.id}"):
            st.write(job.jd_raw)  # Simple display; copy manually
        st.text_area("Raw text", value=job.jd_raw, height=400, key=f"raw_{job.id}", disabled=True)
    with tabs[2]:
        notes = st.text_area("Your notes", value=job.fit.get("notes", ""), key=f"notes_{job.id}", height=150)
        if st.button("Save Notes", key=f"save_notes_{job.id}"):
            job.fit["notes"] = notes
            job.updated_at = datetime.now(timezone.utc).isoformat()
            save_jobs(all_jobs)
            st.success("Notes saved")


# ---------------------------------------------------------------------------
# Fit Preview
# ---------------------------------------------------------------------------
def _render_fit_preview(job: JobRecord, all_jobs: dict[str, JobRecord], master_context: str):
    st.markdown("---")
    st.markdown(f"### Fit Preview: {job.title} at {job.company}")

    # Compute if missing or stale
    if job.fit.get("score", 0) == 0 and job.jd_structured:
        job.fit = compute_fit(job, master_context)
        job.updated_at = datetime.now(timezone.utc).isoformat()
        save_jobs(all_jobs)

    fit = job.fit
    score = fit.get("score", 0)
    col1, col2 = st.columns([1, 3])
    with col1:
        st.metric("Fit Score", f"{score}/100")
        st.progress(score / 100.0)
    with col2:
        st.markdown(f"**Explanation:** {fit.get('explanation', '—')}")
        cov = fit.get("coverage", 0.0)
        st.markdown(f"**Tool Coverage:** {cov:.0%}")
        st.progress(cov)

    if st.button("🚀 Generate Resume for this Role", key=f"fit_gen_{job.id}", type="primary"):
        st.session_state.watcher_generate_job_id = job.id
        st.rerun()


# ---------------------------------------------------------------------------
# Generate pre-flight
# ---------------------------------------------------------------------------
def _render_generate_preflight(job: JobRecord, all_jobs: dict[str, JobRecord]):
    st.markdown("---")
    st.markdown(f"### Generate: {job.title} at {job.company}")

    # Duplicate guard
    gen = job.generated or {}
    if gen.get("resume_path"):
        st.warning(f"⚠️ Resume already generated on {gen.get('generated_at', 'unknown')}")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Regenerate", key=f"regen_{job.id}", type="primary"):
                _do_populate_and_generate(job)
        with c2:
            if st.button("Cancel", key=f"cancel_gen_{job.id}"):
                st.session_state.watcher_generate_job_id = None
                st.rerun()
        return

    # Pre-flight form
    with st.form(key=f"preflight_{job.id}"):
        company = st.text_input("Company", value=job.company)
        role = st.text_input("Role", value=job.title)
        track = st.selectbox("Track", [
            "Product/AI", "Pricing/Ops", "Growth",
            "Logistics/Marketplace", "BizOps", "Chief of Staff", "HR/HRIS"
        ])
        voice = st.selectbox("Voice", [
            "Sharp Product PM", "Technical Product PM",
            "Growth / GTM PM", "Chief of Staff / BizOps"
        ])
        submitted = st.form_submit_button("🚀 Populate & Go to Generate", type="primary")
        if submitted:
            job.generated["resume_path"] = None  # Reset so we know it's in-flight
            job.generated["generated_at"] = None
            save_jobs(all_jobs)
            _do_populate_and_generate(job, company=company, role=role, track=track, voice=voice)


def _do_populate_and_generate(job: JobRecord, company: str | None = None, role: str | None = None, track: str | None = None, voice: str | None = None):
    st.session_state["company_name"] = company or job.company
    st.session_state["target_role"] = role or job.title
    st.session_state["jd_text"] = job.jd_raw
    st.session_state["jd_url"] = job.url
    if track:
        st.session_state["selected_track"] = track
    if voice:
        st.session_state["selected_voice"] = voice
    st.session_state.watcher_generate_job_id = None
    st.success("✅ Job details populated. Switch to the **Generate & Output** tab to generate.")
    st.balloons()


# ---------------------------------------------------------------------------
# Manual entry
# ---------------------------------------------------------------------------
def _render_manual_entry(all_jobs: dict[str, JobRecord]):
    st.markdown("### Manual Entry")
    st.caption("Paste a JD URL or raw text for boards not yet supported.")
    with st.form(key="manual_entry_form"):
        url_or_text = st.text_area("JD URL or raw text", height=150, placeholder="https://... or paste JD text here")
        company = st.text_input("Company (optional)")
        title = st.text_input("Role title (optional)")
        submitted = st.form_submit_button("Add Job")
        if submitted and url_or_text.strip():
            job = manual_add(url_or_text.strip(), company=company or "", title=title or "")
            if job:
                existing = load_jobs_index()
                if job.id not in existing:
                    job.status_history = [{"status": "discovered", "changed_at": datetime.now(timezone.utc).isoformat()}]
                    existing[job.id] = job
                    save_jobs(existing)
                    st.success(f"Added: {job.title} at {job.company}")
                    st.rerun()
                else:
                    st.warning("This job already exists.")
            else:
                st.error("Failed to parse or scrape. Check URL/text length (min 200 chars).")


# ---------------------------------------------------------------------------
# Import / Export
# ---------------------------------------------------------------------------
def _render_import_export():
    st.markdown("### Backup & Restore")
    c1, c2 = st.columns(2)
    with c1:
        data = export_jsonl()
        if data:
            st.download_button("📥 Download jobs.jsonl", data=data, file_name="jobs.jsonl", mime="application/jsonlines+json", use_container_width=True)
    with c2:
        uploaded = st.file_uploader("Upload jobs.jsonl", type=["jsonl", "json"], key="jobs_upload")
        if uploaded is not None:
            added, skipped = import_jsonl(uploaded.read())
            st.success(f"Imported: {added} new, {skipped} duplicates")
            st.rerun()


# ---------------------------------------------------------------------------
# Status transition
# ---------------------------------------------------------------------------
def _transition_status(job: JobRecord, new_status: str):
    old = job.status
    if old == new_status:
        return
    job.status = new_status
    now = datetime.now(timezone.utc).isoformat()
    job.status_history.append({"status": new_status, "changed_at": now})
    job.updated_at = now


# ---------------------------------------------------------------------------
# Main render
# ---------------------------------------------------------------------------
def render_jobs_tab(master_context: str):
    """Main entry point for the Jobs tab."""
    _init_state()
    all_jobs = load_jobs_index()

    st.markdown("## 🎯 Jobs Watcher")

    # Top controls
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        with st.expander("Companies Config"):
            _render_companies_config()
    with col2:
        _render_run_now(master_context)
    with col3:
        _render_import_export()

    # Manual entry
    with st.expander("➕ Manual Entry"):
        _render_manual_entry(all_jobs)

    # Filters
    _render_filter_bar(all_jobs)

    # View toggle
    view_mode = st.radio("View", ["table", "kanban"], format_func=lambda x: "📋 Table" if x == "table" else "📊 Kanban", key="watcher_view_mode", horizontal=True)

    # Filtered list
    filtered = _filter_jobs(all_jobs)

    # Modal / panel state handling
    view_job_id = st.session_state.get("watcher_view_job_id")
    fit_job_id = st.session_state.get("watcher_fit_job_id")
    gen_job_id = st.session_state.get("watcher_generate_job_id")

    # If a generate is requested, show pre-flight
    if gen_job_id and gen_job_id in all_jobs:
        _render_generate_preflight(all_jobs[gen_job_id], all_jobs)
        return

    # If a fit preview is requested, show it
    if fit_job_id and fit_job_id in all_jobs:
        _render_fit_preview(all_jobs[fit_job_id], all_jobs, master_context)
        if st.button("Back to list", key="back_fit"):
            st.session_state.watcher_fit_job_id = None
            st.rerun()
        return

    # If a view is requested, show JD panel
    if view_job_id and view_job_id in all_jobs:
        _render_jd_panel(all_jobs[view_job_id], all_jobs, master_context)
        if st.button("Back to list", key="back_view"):
            st.session_state.watcher_view_job_id = None
            st.rerun()
        return

    # Main view
    if view_mode == "kanban":
        _render_kanban(filtered, all_jobs)
    else:
        _render_pagination(len(filtered))
        page_jobs = _paginate_jobs(filtered)
        _render_table(page_jobs, all_jobs, master_context)
        _render_pagination(len(filtered))
