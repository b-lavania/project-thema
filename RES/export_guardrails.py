"""PDF page limits, ATS readiness checks, and deterministic 2-page compaction."""

from __future__ import annotations

import re
from typing import Any

MAX_PDF_PAGES = 2

# Tool names that should not appear in Quick Take (belong in How I Work / The Work)
_QUICK_TAKE_TOOL_NAMES = (
    "heap", "segment", "mixpanel", "pypsa", "hotjar", "clarity", "pendo", "aha",
)


def ats_readiness_checks(
    mission: str,
    skills: str,
    projects: str,
    kw_coverage: float,
    pdf_page_count: int | None,
    *,
    coaching_notes_in_output: bool = False,
) -> list[dict[str, Any]]:
    """Return checklist items: {label, ok, detail}."""
    checks: list[dict[str, Any]] = []

    # Keyword coverage
    pct = int(kw_coverage * 100) if kw_coverage is not None else 0
    checks.append({
        "label": "JD keyword coverage",
        "ok": kw_coverage >= 0.8,
        "detail": f"{pct}% (target ≥80%, in-app only)",
    })

    # Quick Take metrics
    paragraph = _quick_take_paragraph(mission)
    has_metric = bool(
        re.search(
            r"\d+%|\d+\s*[x×]|[$]\d+|\d+\s*(min|mins|minutes|hours|days)\b",
            paragraph,
            re.I,
        )
    )
    checks.append({
        "label": "Quick Take has no metrics",
        "ok": not has_metric,
        "detail": "Numbers belong in The Work, not Quick Take",
    })

    # Quick Take tools
    lower = paragraph.lower()
    tools_found = [t for t in _QUICK_TAKE_TOOL_NAMES if t in lower]
    checks.append({
        "label": "Quick Take has no tool laundry list",
        "ok": not tools_found,
        "detail": "Move tools to How I Work" if tools_found else "OK",
    })

    # Coaching notes
    checks.append({
        "label": "No coaching notes in export",
        "ok": not coaching_notes_in_output,
        "detail": "COACHING NOTE lines must be removed before send",
    })

    # Page count
    if pdf_page_count is not None:
        checks.append({
            "label": f"PDF ≤ {MAX_PDF_PAGES} pages",
            "ok": pdf_page_count <= MAX_PDF_PAGES,
            "detail": f"{pdf_page_count} page(s)",
        })
    else:
        checks.append({
            "label": f"PDF ≤ {MAX_PDF_PAGES} pages",
            "ok": False,
            "detail": "Not rendered yet",
        })

    return checks


def _quick_take_paragraph(mission: str) -> str:
    lines = [ln.strip() for ln in (mission or "").split("\n") if ln.strip()]
    return " ".join(lines[1:]) if len(lines) > 1 else ""


def trim_role_block_bullets(role_text: str, max_bullets: int = 3) -> str:
    """Keep header/company/summary lines; cap bullet lines."""
    lines = role_text.split("\n")
    out: list[str] = []
    bullet_count = 0
    preface_done = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            out.append(line)
            continue
        if stripped.startswith("COACHING NOTE") or stripped.startswith("Alt (general)"):
            continue
        is_bullet = stripped.startswith("-") or (
            ": " in stripped
            and len(stripped.split(":", 1)[0].split()) <= 5
            and preface_done
        )
        if is_bullet:
            if bullet_count >= max_bullets:
                continue
            bullet_count += 1
            preface_done = True
        else:
            if len([l for l in out if l.strip()]) >= 1:
                preface_done = True
        out.append(line)
    return "\n".join(out).strip()


def compact_resume_sections(
    sections: dict,
    *,
    max_bullets_per_role: int = 3,
    omit_projects: bool = False,
) -> dict:
    """Return a copy of resume sections with tighter budgets."""
    out = dict(sections)
    if omit_projects:
        out["projects"] = ""
    exp = out.get("experience") or []
    if isinstance(exp, list):
        out["experience"] = [
            trim_role_block_bullets(block, max_bullets=max_bullets_per_role)
            for block in exp
        ]
    return out


def apply_compact_role_selections(role_selections: dict[str, str], max_full: int = 2) -> dict[str, str]:
    """Keep up to max_full 'full' roles (newest ROLE n first); demote rest to condensed."""
    updated = dict(role_selections)

    def role_num(key: str) -> int:
        m = re.search(r"ROLE\s+(\d+)", key, re.I)
        return int(m.group(1)) if m else 99

    full_keys = sorted(
        [k for k, v in updated.items() if v == "full"],
        key=role_num,
    )
    for i, key in enumerate(full_keys):
        if i >= max_full:
            updated[key] = "condensed"
    return updated


def rebuild_experience_after_compact(
    selected_roles: list[tuple],
    existing_blocks: list[str],
    new_selections: dict[str, str],
) -> list[str]:
    """Rebuild experience blocks when role density changes (full ↔ condensed)."""
    from generator import extract_condensed_role_line

    blocks: list[str] = []
    exist_i = 0
    for key, role_block, old_sel in selected_roles:
        sel = new_selections.get(key, old_sel)
        if sel == "skip":
            continue
        if sel == "full":
            if old_sel == "full" and exist_i < len(existing_blocks):
                blocks.append(trim_role_block_bullets(existing_blocks[exist_i], max_bullets=3))
                exist_i += 1
            else:
                blocks.append(trim_role_block_bullets(role_block, max_bullets=3))
        elif sel == "condensed":
            if exist_i < len(existing_blocks):
                exist_i += 1
            blocks.append(extract_condensed_role_line(role_block))
    return blocks


def apply_two_page_compact(
    res: dict,
    role_selections: dict[str, str],
    max_full: int = 2,
) -> tuple[dict, dict[str, str], list[tuple]]:
    """
    Deterministic compaction: demote extra full roles, trim bullets, drop Side Builds.
    Returns (resume_sections, new_role_selections, updated_selected_roles).
    """
    new_selections = apply_compact_role_selections(role_selections, max_full=max_full)
    selected_roles = res.get("selected_roles") or []
    updated_selected = [
        (key, block, new_selections.get(key, sel))
        for key, block, sel in selected_roles
    ]
    experience = rebuild_experience_after_compact(
        selected_roles, res.get("experience_blocks") or [], new_selections
    )
    sections = compact_resume_sections(
        {
            "mission": res.get("mission", ""),
            "skills": res.get("skills", ""),
            "experience": experience,
            "projects": res.get("projects", ""),
        },
        max_bullets_per_role=3,
        omit_projects=True,
    )
    return sections, new_selections, updated_selected
