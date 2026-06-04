import os
import re
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS

from generator import (
    PAGE_BREAK_MARKER,
    bold_anchor_words_html,
    bold_first_metric_html,
    normalize_pdf_breaks,
    normalize_quick_take_text,
)

TEMPLATE_DIR = Path(__file__).resolve().parent / "assets"

def strip_coaching_notes(text):
    """Remove COACHING NOTE lines from text."""
    lines = []
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("COACHING NOTE:") or stripped.startswith("Alt (general)"):
            continue
        lines.append(line)
    return "\n".join(lines)


def parse_bullet_line(line):
    """Bold PM MOVE label and the first metric in the bullet body."""
    parts = line.split(":", 1)
    if len(parts) == 2 and len(parts[0].split()) <= 5:
        body = bold_first_metric_html(parts[1].strip())
        return f"<span class='skill-label'>{parts[0].strip()}:</span> {body}"
    return bold_first_metric_html(line)


def _is_page_break_line(line):
    return line.strip() in (PAGE_BREAK_MARKER, PAGE_BREAK_MARKER.strip("-"))


def _is_condensed_role(text):
    """Check if text is a condensed role (single line with @ and parentheses)."""
    # Pattern: "Title @ Company (Dates)"
    return bool(re.match(r'^.+\s+@\s+.+\s+\(.+\)$', text.strip()))


def _extract_condensed_dates(condensed_text):
    """Extract title_company and simplified dates from condensed role string.
    
    Input:  'Title @ Company (Feb 2022 - May 2024 (includes ...))'
    Output: ('Title @ Company', '2022–2024')
    """
    # Match: Title @ Company (dates...)
    match = re.match(r'^(.+)\s+@\s+(.+)\s+\((.+)\)$', condensed_text.strip())
    if not match:
        return condensed_text, ""
    
    title = match.group(1).strip()
    company = match.group(2).strip()
    dates_raw = match.group(3).strip()
    
    # Strip nested parenthetical notes: "Feb 2022 - May 2024 (includes...)" → "Feb 2022 - May 2024"
    dates_clean = re.sub(r'\s*\([^)]*\)', '', dates_raw).strip()
    
    # Simplify to year range: extract years (4-digit numbers)
    years = re.findall(r'\b(20\d{2})\b', dates_clean)
    if len(years) >= 2:
        dates_simplified = f"{years[0]}–{years[-1]}"
    elif len(years) == 1:
        dates_simplified = years[0]
    else:
        dates_simplified = dates_clean  # fallback
    
    return f"{title} @ {company}", dates_simplified


def _parse_role_block(role_text, page_break_before=False):
    """Parse one experience role chunk into template dict."""
    clean_role = strip_coaching_notes(role_text)
    lines = []
    pending_break = page_break_before
    saw_content = False
    for raw in clean_role.split("\n"):
        stripped = raw.strip()
        if not stripped:
            continue
        if _is_page_break_line(stripped):
            # Leading marker before any role lines would orphan "The Work" heading
            if saw_content:
                pending_break = True
            continue
        saw_content = True
        lines.append(stripped)

    if not lines:
        return None

    # Check if this is a condensed role (single line)
    if len(lines) == 1 and _is_condensed_role(lines[0]):
        title_company, dates_location = _extract_condensed_dates(lines[0])
        return {
            "title_company": title_company,
            "dates_location": dates_location,
            "company_desc": "",
            "summary": "",
            "bullets": [],
            "page_break_before": pending_break,
            "is_condensed": True,
        }

    header_line = lines[0]
    title_company = header_line
    dates_location = ""
    header_parts = header_line.split(",")
    if len(header_parts) >= 3:
        title_company = header_parts[0].strip()
        dates_location = ", ".join(p.strip() for p in header_parts[1:])

    company_desc = bold_anchor_words_html(lines[1]) if len(lines) > 1 else ""
    summary = lines[2] if len(lines) > 2 else ""
    bullets = []
    for line in lines[3:]:
        line = re.sub(r'^-\s*', '', line)
        bullets.append(parse_bullet_line(line))

    return {
        "title_company": title_company,
        "dates_location": dates_location,
        "company_desc": company_desc,
        "summary": summary,
        "bullets": bullets,
        "page_break_before": pending_break,
        "is_condensed": False,
    }


def render_resume_pdf(
    output_path,
    resume_sections,
    location="Sunnyvale, CA",
    include_scrum=False,
    pdf_breaks=None,
    compact_pdf=False,
    export_mode="standard",
    pdf_page_size="letter",
):
    """
    Build a resume PDF by rendering template.html
    with Jinja2 and converting to PDF with WeasyPrint. Role blocks use CSS to avoid
    splitting a job header from its bullets across pages.

    pdf_breaks: optional dict with before_sections (skills|experience|projects|credentials)
    and before_role_index (1-based int).
    """
    breaks = normalize_pdf_breaks(pdf_breaks)
    break_sections = breaks["before_sections"]
    break_role_index = breaks["before_role_index"]

    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    template = env.get_template("template.html")
    effective_page_size = "legal" if export_mode == "digital" and pdf_page_size == "legal" else "letter"
    first_page_margin = "0.4in 0.55in 0.5in 0.55in" if export_mode == "digital" else "0.45in 0.5in 0.5in 0.5in"

    mission_text = normalize_quick_take_text(resume_sections.get("mission", ""))
    mission_lines = [l.strip() for l in mission_text.split("\n") if l.strip()]
    tagline = mission_lines[0] if mission_lines else ""
    if tagline and " - " in tagline and ": " not in tagline[: tagline.find(" - ") + 1]:
        tagline = tagline.replace(" - ", ": ", 1)
    mission_body = "\n".join(mission_lines[1:]) if len(mission_lines) > 1 else ""

    skills_raw = resume_sections.get("skills", "")
    skills_clean = strip_coaching_notes(skills_raw)
    skills_list = []
    for line in skills_clean.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        stripped = re.sub(r'^\d+\)\s*', '', stripped)
        stripped = re.sub(r'^-\s*', '', stripped)
        skills_list.append(parse_bullet_line(stripped))

    experience_list = []
    if resume_sections.get("experience"):
        for idx, role_text in enumerate(resume_sections["experience"], start=1):
            role_break = break_role_index is not None and idx == break_role_index
            # Support marker splitting one block into multiple roles
            chunks = re.split(
                rf"(?m)^\s*{re.escape(PAGE_BREAK_MARKER)}\s*$",
                role_text,
            )
            for chunk_i, chunk in enumerate(chunks):
                chunk = chunk.strip()
                if not chunk:
                    continue
                want_break = role_break or chunk_i > 0
                parsed = _parse_role_block(chunk, page_break_before=want_break)
                if parsed:
                    # Never break before the first role (avoids orphan section title)
                    if not experience_list and parsed.get("page_break_before"):
                        parsed = {**parsed, "page_break_before": False}
                    experience_list.append(parsed)

    projects_raw = resume_sections.get("projects", "")
    projects_list = []
    if projects_raw:
        proj_clean = strip_coaching_notes(projects_raw)
        current_title = None
        current_bullets = []
        pending_proj_break = False
        for line in proj_clean.split("\n"):
            stripped = line.strip()
            if _is_page_break_line(stripped):
                if current_title is not None:
                    pending_proj_break = True
                continue
            if not stripped:
                if current_title:
                    proj_break = pending_proj_break and bool(projects_list)
                    projects_list.append({
                        "title": current_title,
                        "bullets": current_bullets,
                        "page_break_before": proj_break,
                    })
                    current_title = None
                    current_bullets = []
                    pending_proj_break = False
                continue
            if not stripped.startswith("-") and current_title is None:
                current_title = stripped
            else:
                bullet = re.sub(r'^-\s*', '', stripped)
                current_bullets.append(parse_bullet_line(bullet))
        if current_title:
            proj_break = pending_proj_break and bool(projects_list)
            projects_list.append({
                "title": current_title,
                "bullets": current_bullets,
                "page_break_before": proj_break,
            })

    html_content = template.render(
        tagline=tagline,
        location=location,
        mission_body=mission_body,
        skills=skills_list,
        experience=experience_list,
        projects=projects_list,
        include_scrum=include_scrum,
        break_sections=break_sections,
        compact_pdf=compact_pdf,
        export_mode=export_mode,
        pdf_page_size=pdf_page_size,
    )

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    page_css = CSS(
        string=(
            f"@page {{ size: {effective_page_size}; margin: 0.5in; }} "
            f"@page :first {{ margin: {first_page_margin}; }}"
        )
    )
    doc = HTML(string=html_content, base_url=str(TEMPLATE_DIR)).render(stylesheets=[page_css])
    page_count = len(doc.pages)
    doc.write_pdf(output_path, stylesheets=[page_css])
    return output_path, page_count


def create_formatted_pdf(
    output_path,
    resume_sections,
    location="Sunnyvale, CA",
    include_scrum=False,
    pdf_breaks=None,
    compact_pdf=False,
    export_mode="standard",
    pdf_page_size="letter",
):
    """Build PDF; returns output path only (backward compatible)."""
    path, _page_count = render_resume_pdf(
        output_path,
        resume_sections,
        location=location,
        include_scrum=include_scrum,
        pdf_breaks=pdf_breaks,
        compact_pdf=compact_pdf,
        export_mode=export_mode,
        pdf_page_size=pdf_page_size,
    )
    return path
