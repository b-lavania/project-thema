"""Streamlit tab: Job Search (HUNT-AGENT integration).

Secondary motion for posted roles at target companies.
Primary outreach is CRM direct (Pipeline tab).
"""

from __future__ import annotations

import contextlib
import io
import json
import sys
from pathlib import Path

import streamlit as st

# ---------------------------------------------------------------------------
# Path setup — add HUNT-AGENT to Python path
# ---------------------------------------------------------------------------
HUNT_ROOT = Path(__file__).resolve().parents[1] / "HUNT-AGENT"
if str(HUNT_ROOT) not in sys.path:
    sys.path.insert(0, str(HUNT_ROOT))

CRM_ROOT = Path(__file__).resolve().parents[1] / "CRM"
if str(CRM_ROOT) not in sys.path:
    sys.path.insert(0, str(CRM_ROOT))

from scraper.leads import load_leads, update_lead_stage
from scraper.config import load_profile, load_target_companies, save_target_companies
from scraper.board_discovery import discover_boards, merge_into_targets
from scraper.run import run_google_jobs, run_direct_ats, _make_args
from scraper.env import SERPAPI_KEY
from scraper.company_fit import score_lead, hypothesis_for_company, HIGH_PRIORITY

STAGE_OPTIONS = ["sent", "replied", "screen", "interview", "final", "offer", "accepted", "rejected", "ghosted"]


def _run_with_status(label: str, fn, **kwargs):
    """Run a function, capturing its print output into a st.status widget."""
    buf = io.StringIO()
    with st.status(label, expanded=True) as status:
        with contextlib.redirect_stdout(buf):
            result = fn(**kwargs)
        output = buf.getvalue()
        if output:
            st.code(output, language="text")
        else:
            st.caption("No output (completed).")
        status.update(label=f"✅ {label}", state="complete")
    return result


def render_hunt_tab():
    """Main render function for the Job Search tab."""
    profile = load_profile()
    is_ops_lane = profile.get("lane") == "ops_ai"

    st.caption(
        "**Secondary motion** — catches posted roles at target companies. "
        "**Primary outreach** is CRM Pipeline (direct founder messages)."
    )

    if "hunt_allowlist_only" not in st.session_state:
        st.session_state.hunt_allowlist_only = is_ops_lane

    # ------------------------------------------------------------------
    # Section 1: Run Controls
    # ------------------------------------------------------------------
    st.markdown("### 🎯 Run Scraper")
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    with col1:
        max_results = st.number_input("Max results/query", min_value=1, max_value=50, value=10, key="hunt_max_results")
    with col2:
        mode = st.selectbox("Search mode", ["auto", "api", "scrape"], key="hunt_mode")
    with col3:
        dry_run = st.checkbox("Dry run (preview only)", value=False, key="hunt_dry_run")
    with col4:
        st.caption(f"SerpAPI key: {'✅ set' if SERPAPI_KEY else '❌ missing'}")

    st.checkbox(
        "Ops-AI lane only (verified target list)",
        key="hunt_allowlist_only",
        help="Only save leads from verified companies in company_candidates.json",
    )

    col_a, col_b, col_c = st.columns(3)
    args = _make_args(max_results=max_results, mode=mode)

    def _full_scrape():
        companies = load_target_companies()
        all_leads = []
        if not st.session_state.hunt_allowlist_only:
            all_leads.extend(run_google_jobs(profile, args))
        all_leads.extend(run_direct_ats(companies))
        return all_leads

    def _search_only():
        return run_google_jobs(profile, args)

    def _ats_only():
        return run_direct_ats(load_target_companies())

    with col_c:
        if st.button("🏢 ATS Only", use_container_width=True, type="primary"):
            raw = _run_with_status("Scraping ATS boards…", _ats_only)
            if raw is not None:
                filtered = _filter_and_save(raw, dry_run)
                _show_result(filtered, raw, dry_run)
            if not dry_run:
                st.rerun()

    with col_b:
        if st.button("🔍 Google Jobs Only", use_container_width=True):
            raw = _run_with_status("Searching Google Jobs…", _search_only)
            if raw is not None:
                filtered = _filter_and_save(raw, dry_run)
                _show_result(filtered, raw, dry_run)
            if not dry_run:
                st.rerun()

    with col_a:
        if st.button("🔄 Full Scrape", use_container_width=True):
            raw = _run_with_status("Running full scrape…", _full_scrape)
            if raw is not None:
                filtered = _filter_and_save(raw, dry_run)
                _show_result(filtered, raw, dry_run)
            if not dry_run:
                st.rerun()

    # ------------------------------------------------------------------
    # Section 2: Board Discovery
    # ------------------------------------------------------------------
    st.divider()
    st.markdown("### 🌐 Board Discovery")
    st.caption("Scoped ops-AI discovery (logistics/freight/dispatch). Monthly cadence.")
    if st.button("🔍 Discover New Boards (scoped)", use_container_width=True):
        discovered = _run_with_status("Discovering board tokens…", lambda: discover_boards(scoped=True))
        if discovered:
            merge_into_targets(discovered)
            st.success("✅ target_companies.json updated")
            st.rerun()
        else:
            st.warning("No new tokens discovered.")

    if "hunt_last_result" in st.session_state:
        r = st.session_state.hunt_last_result
        st.info(f"Last scrape: {r.get('saved', 0)} saved, {r.get('skipped', 0)} skipped")
        if st.button("Clear result", key="hunt_clear_result"):
            del st.session_state.hunt_last_result
            st.rerun()

    # ------------------------------------------------------------------
    # Section 3: Leads Browser
    # ------------------------------------------------------------------
    st.divider()
    st.markdown("### 📋 Leads")
    leads = load_leads()

    if not leads:
        st.info("No leads yet — run **ATS Only** above (Tuesday weekly cadence).")
    else:
        _render_leads_table(leads)

    # ------------------------------------------------------------------
    # Section 4: Configuration
    # ------------------------------------------------------------------
    st.divider()
    with st.expander("⚙️ Configuration Files", expanded=False):
        _render_config()


def _filter_and_save(raw_leads: list, dry_run: bool):
    """Filter + optionally save leads. Returns filtered list."""
    from scraper.filter import filter_leads
    from scraper.company_fit import filter_by_fit

    profile = load_profile()
    title_filtered = filter_leads(
        raw_leads,
        exclude_senior=True,
        profile_keywords=profile.get("keywords"),
        exclude_titles=profile.get("exclude_titles"),
        require_product_adjacent=True,
    )
    allowlist = st.session_state.get("hunt_allowlist_only", False)
    filtered, fit_rejected = filter_by_fit(
        title_filtered,
        allowlist_only=allowlist,
    )
    skipped = len(raw_leads) - len(filtered)

    if not dry_run and filtered:
        from scraper.leads import append_leads
        count = append_leads(filtered)
        msg = f"Saved {count} new leads ({skipped} skipped)"
        st.session_state.hunt_last_result = {"saved": count, "skipped": skipped}
    else:
        msg = f"Total: {len(filtered)} / {len(raw_leads)} (skipped {skipped})"
        if dry_run:
            msg += " — dry run, not saved"

    st.info(msg)
    return filtered


def _show_result(filtered: list, raw: list, dry_run: bool):
    skipped = len(raw) - len(filtered)
    st.caption(f"{len(filtered)} filtered, {skipped} skipped")
    if filtered:
        for l in filtered[:20]:
            fit = score_lead(l)
            badge = "🔥" if fit >= HIGH_PRIORITY else ""
            st.markdown(f"- {badge} **{l.title}** @ {l.company} (fit {fit}) — `{l.source}`")
        if len(filtered) > 20:
            st.caption(f"… and {len(filtered) - 20} more")


def _promote_to_crm(lead):
    from crm.services.companies import import_from_leads, find_company_by_name

    existing = find_company_by_name(lead.company)
    if existing:
        st.warning("Already in pipeline")
        return
    hyp = hypothesis_for_company(lead.company)
    result = import_from_leads(lead, hypothesis=hyp)
    if result:
        st.success(f"Added **{lead.company}** to Pipeline")
    else:
        st.warning("Could not add — may already exist")


def _render_leads_table(leads):
    col_src, col_stage, col_q = st.columns(3)
    with col_src:
        sources = sorted({l.source for l in leads})
        src_filter = st.multiselect("Source", options=sources, default=[], key="hunt_src_filter")
    with col_stage:
        stage_filter = st.multiselect("Stage", options=STAGE_OPTIONS, default=[], key="hunt_stage_filter")
    with col_q:
        query = st.text_input("Search (company/role)", key="hunt_query")

    filtered = leads
    if src_filter:
        filtered = [l for l in filtered if l.source in src_filter]
    if stage_filter:
        filtered = [l for l in filtered if l.stage in stage_filter]
    if query:
        q = query.lower()
        filtered = [l for l in filtered if q in l.company.lower() or q in l.title.lower()]

    col_n, col_s = st.columns(2)
    with col_n:
        st.caption(f"**{len(filtered)}** leads (of {len(leads)} total)")
    with col_s:
        stage_counts = {s: sum(1 for l in filtered if l.stage == s) for s in STAGE_OPTIONS}
        summary = " | ".join(f"{s}: {c}" for s, c in stage_counts.items() if c)
        st.caption(summary)
    st.divider()

    for l in filtered:
        fit = score_lead(l)
        with st.container(border=True):
            cols = st.columns([4, 1, 1, 1])
            with cols[0]:
                priority = " 🔥 high fit" if fit >= HIGH_PRIORITY else ""
                st.markdown(f"**{l.title}** @ **{l.company}** · fit **{fit}**{priority}")
                st.caption(f"`{l.source}` · {l.location} · {l.date_found}")
                if l.description_snippet:
                    st.text(l.description_snippet[:200])
                if l.url:
                    st.markdown(f"[🔗 Apply]({l.url})")
            with cols[1]:
                new_stage = st.selectbox(
                    "Stage",
                    options=STAGE_OPTIONS,
                    index=STAGE_OPTIONS.index(l.stage),
                    key=f"hunt_stage_{l.id}",
                    label_visibility="collapsed",
                )
                if new_stage != l.stage and update_lead_stage(l.id, new_stage):
                    st.rerun()
            with cols[2]:
                if st.button("📝 Gen", key=f"hunt_use_{l.id}", help="Pre-fill Job Details"):
                    st.session_state.company_name = l.company
                    st.session_state.target_role = l.title
                    if l.url:
                        st.session_state.jd_url = l.url
                        st.session_state._auto_scrape_from_url = True
                    st.session_state["_prefill_from_hunt"] = True
                    st.success("→ **Job Details** → **Generate**")
                    st.rerun()
            with cols[3]:
                if st.button("+ CRM", key=f"hunt_crm_{l.id}", help="Add to Pipeline"):
                    _promote_to_crm(l)
                    st.rerun()


def _render_config():
    tab_p, tab_c, tab_d = st.tabs(["Search Profile", "Target Companies", "Candidate Review"])

    with tab_p:
        profile = load_profile()
        edited = {
            "roles": st.text_area("Roles (one per line)", "\n".join(profile["roles"]), key="hunt_profile_roles"),
            "locations": st.text_area("Locations (one per line)", "\n".join(profile["locations"]), key="hunt_profile_locs"),
            "keywords": st.text_input("Keywords (comma-separated)", ", ".join(profile["keywords"]), key="hunt_profile_kw"),
            "exclude_titles": st.text_area(
                "Exclude titles (one per line)",
                "\n".join(profile.get("exclude_titles", [])),
                key="hunt_profile_exclude",
            ),
            "domain_queries": st.text_area(
                "Domain queries (one per line, ops_ai lane)",
                "\n".join(profile.get("domain_queries", [])),
                key="hunt_profile_domain",
            ),
        }
        if st.button("💾 Save Profile", key="hunt_save_profile"):
            updated = {
                "roles": [r.strip() for r in edited["roles"].strip().split("\n") if r.strip()],
                "locations": [l.strip() for l in edited["locations"].strip().split("\n") if l.strip()],
                "keywords": [k.strip() for k in edited["keywords"].split(",") if k.strip()],
                "exclude_titles": [t.strip() for t in edited["exclude_titles"].strip().split("\n") if t.strip()],
                "exclude_industries": profile.get("exclude_industries", []),
                "lane": profile.get("lane", "ops_ai"),
                "domain_queries": [q.strip() for q in edited["domain_queries"].strip().split("\n") if q.strip()],
            }
            with open(HUNT_ROOT / "search_profile.json", "w") as f:
                json.dump(updated, f, indent=2)
                f.write("\n")
            st.success("Profile saved")
            st.rerun()

    with tab_c:
        companies = load_target_companies()
        for ats_name in ["greenhouse", "lever", "ashby", "smartrecruiters"]:
            tokens = companies.get(ats_name, [])
            edited = st.text_area(
                f"{ats_name.title()} (one per line)",
                "\n".join(tokens),
                key=f"hunt_companies_{ats_name}",
            )
            companies[ats_name] = [t.strip() for t in edited.strip().split("\n") if t.strip()]
        if st.button("💾 Save Companies", key="hunt_save_companies"):
            save_target_companies(companies)
            st.success("Companies saved")
            st.rerun()

    with tab_d:
        candidates_path = HUNT_ROOT / "company_candidates.json"
        if candidates_path.exists():
            candidates = json.loads(candidates_path.read_text())
            unverified = [c for c in candidates if not c.get("verified")]
            st.caption(f"{len(unverified)} unverified candidates (of {len(candidates)} total)")
            if unverified and st.session_state.get("_llm_client"):
                if st.button("🤖 Score unverified with LLM", key="hunt_llm_score"):
                    _llm_score_candidates(unverified[:10])
            for c in unverified[:15]:
                st.markdown(f"- **{c['name']}** — fit {c.get('fit_score', '?')} — {c.get('hypothesis', '')[:80]}")
        else:
            st.info("No company_candidates.json yet.")


def _llm_score_candidates(candidates: list):
    """Optional LLM batch scorer for candidate review."""
    llm = st.session_state.get("_llm_client")
    if not llm:
        st.warning("Generate a resume first to initialize LLM client.")
        return
    from llm_client import call_llm
    names = ", ".join(c["name"] for c in candidates)
    prompt = (
        f"Rate these ops-AI logistics/freight companies for a Founding PM candidate "
        f"(Series-A, AI-native ops): {names}. "
        "For each, reply one line: NAME | score 0-100 | one-line reason."
    )
    with st.spinner("Scoring candidates…"):
        result = call_llm(
            llm,
            system_prompt="You score company fit for ops-AI PM roles.",
            user_prompt=prompt,
            max_tokens=800,
            temperature=0.2,
            tier="default",
            require_nonempty=True,
            step_label="Company fit scoring",
        )
        text, _ = result if isinstance(result, tuple) else (result, {})
        st.text_area("LLM scores", text, height=200)
