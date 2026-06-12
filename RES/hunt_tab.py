"""Streamlit tab: Job Search (HUNT-AGENT integration).

Four sections:
  1. Run Controls — full scrape, search-only, ATS-only, discover boards
  2. Board Discovery — find and add new board tokens
  3. Leads Browser — filter/sort/manage scraped leads
  4. Configuration — view/edit search_profile + target_companies
"""

from __future__ import annotations

import contextlib
import io
import sys
from pathlib import Path

import streamlit as st

# ---------------------------------------------------------------------------
# Path setup — add HUNT-AGENT to Python path
# ---------------------------------------------------------------------------
HUNT_ROOT = Path(__file__).resolve().parents[1] / "HUNT-AGENT"
if str(HUNT_ROOT) not in sys.path:
    sys.path.insert(0, str(HUNT_ROOT))

from scraper.leads import load_leads, get_lead, update_lead_stage
from scraper.config import load_profile, load_target_companies, save_target_companies
from scraper.board_discovery import discover_boards, merge_into_targets
from scraper.run import run_google_jobs, run_direct_ats, _make_args
from scraper.env import SERPAPI_KEY

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
        st.caption("")
        st.caption("")
        st.caption(f"SerpAPI key: {'✅ set' if SERPAPI_KEY else '❌ missing'}")

    col_a, col_b, col_c = st.columns(3)
    args = _make_args(max_results=max_results, mode=mode)

    leads_bucket: list = []

    def _full_scrape():
        nonlocal leads_bucket
        profile = load_profile()
        companies = load_target_companies()
        all_leads = []
        gj = run_google_jobs(profile, args)
        all_leads.extend(gj)
        ats = run_direct_ats(companies)
        all_leads.extend(ats)
        leads_bucket.extend(all_leads)
        return all_leads

    def _search_only():
        nonlocal leads_bucket
        profile = load_profile()
        gj = run_google_jobs(profile, args)
        leads_bucket.extend(gj)
        return gj

    def _ats_only():
        nonlocal leads_bucket
        companies = load_target_companies()
        ats = run_direct_ats(companies)
        leads_bucket.extend(ats)
        return ats

    with col_a:
        if st.button("🔄 Full Scrape", use_container_width=True, type="primary"):
            raw = _run_with_status("Running full scrape…", _full_scrape)
            if raw:
                filtered = _filter_and_save(raw, dry_run)
                _show_result(filtered, raw, dry_run)
            if not dry_run:
                st.rerun()

    with col_b:
        if st.button("🔍 Google Jobs Only", use_container_width=True):
            raw = _run_with_status("Searching Google Jobs…", _search_only)
            if raw:
                filtered = _filter_and_save(raw, dry_run)
                _show_result(filtered, raw, dry_run)
            if not dry_run:
                st.rerun()

    with col_c:
        if st.button("🏢 ATS Only", use_container_width=True):
            raw = _run_with_status("Scraping ATS boards…", _ats_only)
            if raw:
                filtered = _filter_and_save(raw, dry_run)
                _show_result(filtered, raw, dry_run)
            if not dry_run:
                st.rerun()

    # ------------------------------------------------------------------
    # Section 2: Board Discovery
    # ------------------------------------------------------------------
    st.divider()
    st.markdown("### 🌐 Board Discovery")
    st.caption("Search Google for new company board tokens (Greenhouse, Lever, Ashby, SmartRecruiters).")
    if st.button("🔍 Discover New Boards", use_container_width=True):
        discovered = _run_with_status("Discovering board tokens…", discover_boards)
        if discovered:
            merge_into_targets(discovered)
            st.success("✅ target_companies.json updated")
            st.rerun()
        else:
            st.warning("No new tokens discovered.")

    # Show last scrape result if stored
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
        st.info("No leads yet — run a scrape above.")
    else:
        _render_leads_table(leads)

    # ------------------------------------------------------------------
    # Section 4: Configuration
    # ------------------------------------------------------------------
    st.divider()
    with st.expander("⚙️ Configuration Files", expanded=False):
        _render_config()


# ------------------------------------------------------------------ helpers


def _filter_and_save(raw_leads: list, dry_run: bool):
    """Filter + optionally save leads. Returns filtered list."""
    from scraper.filter import filter_leads
    profile = load_profile()
    filtered = filter_leads(
        raw_leads,
        exclude_senior=True,
        profile_keywords=profile.get("keywords"),
        require_product_adjacent=True,
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
    """Show a compact table of results inline."""
    skipped = len(raw) - len(filtered)
    st.caption(f"{len(filtered)} filtered, {skipped} skipped")
    if filtered:
        for l in filtered[:20]:
            st.markdown(f"- **{l.title}** @ {l.company} — `{l.source}`")
        if len(filtered) > 20:
            st.caption(f"… and {len(filtered) - 20} more")


def _render_leads_table(leads):
    """Filterable, sortable leads table with stage management."""
    # Filters
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

    # Summary stats
    col_n, col_s = st.columns(2)
    with col_n:
        st.caption(f"**{len(filtered)}** leads (of {len(leads)} total)")
    with col_s:
        stage_counts = {s: sum(1 for l in filtered if l.stage == s) for s in STAGE_OPTIONS}
        summary = " | ".join(f"{s}: {c}" for s, c in stage_counts.items() if c)
        st.caption(summary)
    st.divider()

    for l in filtered:
        with st.container(border=True):
            cols = st.columns([4, 1, 1])
            with cols[0]:
                st.markdown(f"**{l.title}** @ **{l.company}**")
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
                    st.success("✓", icon="✅")
                    st.rerun()
            with cols[2]:
                if st.button("📝 Use for Gen", key=f"hunt_use_{l.id}", help="Pre-fill Job Details tab"):
                    st.session_state.company_name = l.company
                    st.session_state.target_role = l.title
                    if l.url:
                        st.session_state.jd_url = l.url
                        st.session_state._auto_scrape_from_url = True
                    st.success("Copied to Job Details → generate resume")
                    st.rerun()


def _render_config():
    """Editable view of search_profile.json and target_companies.json."""
    tab_p, tab_c = st.tabs(["Search Profile", "Target Companies"])

    with tab_p:
        profile = load_profile()
        edited = {
            "roles": st.text_area("Roles (one per line)", "\n".join(profile["roles"]), key="hunt_profile_roles"),
            "locations": st.text_area("Locations (one per line)", "\n".join(profile["locations"]), key="hunt_profile_locs"),
            "keywords": st.text_input("Keywords (comma-separated)", ", ".join(profile["keywords"]), key="hunt_profile_kw"),
        }
        if st.button("💾 Save Profile", key="hunt_save_profile"):
            import json
            updated = {
                "roles": [r.strip() for r in edited["roles"].strip().split("\n") if r.strip()],
                "locations": [l.strip() for l in edited["locations"].strip().split("\n") if l.strip()],
                "keywords": [k.strip() for k in edited["keywords"].split(",") if k.strip()],
                "exclude_titles": profile.get("exclude_titles", []),
                "exclude_industries": profile.get("exclude_industries", []),
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
