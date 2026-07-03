"""Artifacts Tab — public artifact management."""

from __future__ import annotations

import streamlit as st


def render_artifacts_tab() -> None:
    st.subheader("Public Artifacts")
    st.caption(
        "Public artifacts are required on Sundays (PA quota). "
        "Save drafts or completed artifacts here."
    )

    from bootcamp.data import list_artifacts, save_artifact

    # ── Create new artifact ────────────────────────────────
    with st.expander("✏️ Create New Artifact", expanded=False):
        artifact_day = st.number_input(
            "Day", min_value=1, max_value=30, value=1, key="art_day"
        )
        artifact_title = st.text_input(
            "Title", placeholder="e.g. Product Teardown: Flexport", key="art_title"
        )
        artifact_content = st.text_area(
            "Content (Markdown)",
            height=300,
            placeholder="Write your artifact here…",
            key="art_content",
        )

        if st.button("💾 Save Artifact", type="primary", key="save_artifact"):
            if artifact_title and artifact_content:
                path = save_artifact(artifact_day, artifact_title, artifact_content)
                st.success(f"Saved to {path.name}")
                st.rerun()
            else:
                st.warning("Title and content required.")

    # ── Week assignment ────────────────────────────────────
    st.markdown("### Required Artifacts")
    required = [
        ("Week 1 (Day 7)", "Product teardown"),
        ("Week 2 (Day 14)", "Prioritization framework or kill memo"),
        ("Week 3 (Day 21)", "Stakeholder pre-alignment template or commercial translation example"),
        ("Week 4 (Day 28)", "Product strategy memo or market thesis"),
    ]
    for week_label, description in required:
        st.markdown(f"- **{week_label}**: {description}")

    # ── Existing artifacts ─────────────────────────────────
    artifacts = list_artifacts()

    if artifacts:
        st.markdown("### Saved Artifacts")
        art_df_data = [
            {
                "Day": a["day"],
                "Title": a["title"],
                "Path": a["path"],
            }
            for a in artifacts
        ]
        import pandas as pd

        st.dataframe(pd.DataFrame(art_df_data), use_container_width=True, hide_index=True)

        selected_idx = st.selectbox(
            "Select artifact to preview",
            range(len(artifacts)),
            format_func=lambda i: f"Day {artifacts[i]['day']}: {artifacts[i]['title']}",
            key="art_preview_select",
        )
        selected = artifacts[selected_idx]
        with st.expander("Preview", expanded=True):
            text = st.session_state.get(f"art_text_{selected['day']}")
            if text is None:
                text = open(selected["path"], encoding="utf-8").read()
                st.session_state[f"art_text_{selected['day']}"] = text
            st.markdown(text)
    else:
        st.info("No artifacts saved yet. Create one above!")
