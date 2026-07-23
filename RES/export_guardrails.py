"""PDF page limits, ATS readiness checks, and deterministic 2-page compaction."""

from __future__ import annotations

import re
from typing import Any

MAX_PDF_PAGES = 2

# Tool names that should not appear in Summary paragraph (belong in method bullets / Experience)
_QUICK_TAKE_TOOL_NAMES = (
    "heap", "segment", "mixpanel", "pypsa", "hotjar", "clarity", "pendo", "aha",
)


def recommended_page_limit(export_mode: str = "standard") -> int:
    """Return the recommended page limit for an export mode."""
    return 3 if export_mode == "digital" else MAX_PDF_PAGES


def _count_bulletish_lines(text: str) -> int:
    count = 0
    for line in (text or "").split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(("-", "•")) or re.match(r"^\d+[\.)]\s+", stripped):
            count += 1
    return count


def _extract_bullet_bodies(experience_blocks: list[str]) -> list[str]:
    bullets: list[str] = []
    for block in experience_blocks or []:
        for line in block.split("\n"):
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("-"):
                bullets.append(re.sub(r"^-\s*", "", stripped))
            elif re.match(r"^\d+[\.)]\s+", stripped):
                bullets.append(re.sub(r"^\d+[\.)]\s*", "", stripped))
    return bullets


def _count_condensed_roles(experience_blocks: list[str]) -> int:
    return sum(
        1
        for block in experience_blocks or []
        if bool(re.match(r"^.+\s+@\s+.+\s+\(.+\)$", (block or "").strip()))
    )


def _count_full_roles(experience_blocks: list[str]) -> int:
    return sum(1 for block in experience_blocks or [] if block and "\n" in block.strip())


def ats_readiness_checks(
    mission: str,
    skills: str,
    projects: str,
    kw_coverage: float,
    pdf_page_count: int | None,
    *,
    experience_blocks: list[str] | None = None,
    export_mode: str = "standard",
    pdf_page_size: str = "letter",
    coaching_notes_in_output: bool = False,
    skill_bank: str = "",
) -> list[dict[str, Any]]:
    """Return checklist items: {label, ok, detail}."""
    checks: list[dict[str, Any]] = []
    page_limit = recommended_page_limit(export_mode)

    # Keyword coverage
    pct = int(kw_coverage * 100) if kw_coverage is not None else 0
    checks.append({
        "label": "JD keyword coverage",
        "ok": kw_coverage >= 0.8,
        "detail": f"{pct}% (target ≥80%, in-app only)",
    })

    # Summary paragraph metrics (positioning only; method bullets may have metrics)
    paragraph = _quick_take_paragraph(mission)
    has_metric = bool(
        re.search(
            r"\d+%|\d+\s*[x×]|[$]\d+|\d+\s*(min|mins|minutes|hours|days)\b",
            paragraph,
            re.I,
        )
    )
    checks.append({
        "label": "Summary paragraph has no metrics",
        "ok": not has_metric,
        "detail": "Numbers belong in Summary method bullets / Experience, not the paragraph",
    })

    quick_take_words = len(paragraph.split()) if paragraph else 0
    qt_limit = 75 if export_mode == "digital" else 60
    checks.append({
        "label": f"Summary paragraph stays within {qt_limit} words",
        "ok": quick_take_words <= qt_limit,
        "detail": f"{quick_take_words} words",
    })

    # Summary paragraph tools
    lower = paragraph.lower()
    tools_found = [t for t in _QUICK_TAKE_TOOL_NAMES if t in lower]
    checks.append({
        "label": "Summary paragraph has no tool laundry list",
        "ok": not tools_found,
        "detail": "Move tools to Summary method bullets" if tools_found else "OK",
    })

    # Coaching notes
    checks.append({
        "label": "No coaching notes in export",
        "ok": not coaching_notes_in_output,
        "detail": "COACHING NOTE lines must be removed before send",
    })

    skill_bullets = _count_bulletish_lines(skills)
    skill_limit = 7 if export_mode == "digital" else 6
    checks.append({
        "label": f"Summary method bullets stay within {skill_limit}",
        "ok": 0 < skill_bullets <= skill_limit,
        "detail": f"{skill_bullets} bullet(s)",
    })

    bank_rows = []
    for ln in (skill_bank or "").split("\n"):
        stripped = ln.strip()
        if not stripped:
            continue
        upper = stripped.upper()
        if upper.startswith("COACHING NOTE") or upper.startswith("ALT ("):
            continue
        bank_rows.append(stripped)
    category_rows = [ln for ln in bank_rows if ":" in ln]
    row_count = len(category_rows) if category_rows else len(bank_rows)
    checks.append({
        "label": "Skills section has 3–4 category rows",
        "ok": 3 <= row_count <= 5,
        "detail": f"{row_count} row(s)" if row_count else "missing",
    })

    full_roles = _count_full_roles(experience_blocks or [])
    condensed_roles = _count_condensed_roles(experience_blocks or [])
    condensed_limit = 4 if export_mode == "digital" else 2
    checks.append({
        "label": f"Condensed roles kept ≤ {condensed_limit}",
        "ok": condensed_roles <= condensed_limit,
        "detail": f"{full_roles} full / {condensed_roles} condensed",
    })

    bullets = _extract_bullet_bodies(experience_blocks or [])
    long_bullets = [b for b in bullets if len(b.split()) > 34]
    checks.append({
        "label": "Bullets stay scannable",
        "ok": len(long_bullets) <= 2,
        "detail": f"{len(long_bullets)} bullet(s) over 34 words",
    })

    page_size_ok = export_mode == "digital" or pdf_page_size == "letter"
    checks.append({
        "label": "Page size matches export mode",
        "ok": page_size_ok,
        "detail": f"{pdf_page_size.title()} in {export_mode} mode",
    })

    # Page count
    if pdf_page_count is not None:
        checks.append({
            "label": f"PDF ≤ {page_limit} pages",
            "ok": pdf_page_count <= page_limit,
            "detail": f"{pdf_page_count} page(s)",
        })
    else:
        checks.append({
            "label": f"PDF ≤ {page_limit} pages",
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
    max_bullets_per_role: int | None = None,
    omit_projects: bool = False,
    export_mode: str = "standard",
) -> dict:
    """Return a copy of resume sections with tighter budgets."""
    out = dict(sections)
    bullet_cap = max_bullets_per_role if max_bullets_per_role is not None else (4 if export_mode == "digital" else 3)
    if omit_projects:
        out["projects"] = ""
    exp = out.get("experience") or []
    if isinstance(exp, list):
        out["experience"] = [
            trim_role_block_bullets(block, max_bullets=bullet_cap)
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
    export_mode: str = "standard",
) -> tuple[dict, dict[str, str], list[tuple]]:
    """
    Deterministic compaction: demote extra full roles, trim bullets, drop School Projects.
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
            "skill_bank": res.get("skill_bank", ""),
            "experience": experience,
            "projects": res.get("projects", ""),
        },
        max_bullets_per_role=None,
        omit_projects=True,
        export_mode=export_mode,
    )
    return sections, new_selections, updated_selected
