import os
import re
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS

from generator import PAGE_BREAK_MARKER, normalize_pdf_breaks

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
    """Bold the label in 'Label: Rest of the bullet'."""
    parts = line.split(":", 1)
    if len(parts) == 2 and len(parts[0].split()) <= 5: # likely a label
        return f"<span class='skill-label'>{parts[0].strip()}:</span> {parts[1].strip()}"
    return line


def _is_page_break_line(line):
    return line.strip() in (PAGE_BREAK_MARKER, PAGE_BREAK_MARKER.strip("-"))


def _parse_role_block(role_text, page_break_before=False):
    """Parse one experience role chunk into template dict."""
    clean_role = strip_coaching_notes(role_text)
    lines = []
    pending_break = page_break_before
    for raw in clean_role.split("\n"):
        stripped = raw.strip()
        if not stripped:
            continue
        if _is_page_break_line(stripped):
            pending_break = True
            continue
        lines.append(stripped)

    if not lines:
        return None

    header_line = lines[0]
    title_company = header_line
    dates_location = ""
    header_parts = header_line.split(",")
    if len(header_parts) >= 3:
        title_company = header_parts[0].strip()
        dates_location = ", ".join(p.strip() for p in header_parts[1:])

    company_desc = lines[1] if len(lines) > 1 else ""
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
    }


def create_formatted_pdf(
    output_path,
    resume_sections,
    location="Sunnyvale, CA",
    include_scrum=False,
    pdf_breaks=None,
):
    """
    Build a letter-size resume PDF (typically 1-2 pages) by rendering template.html
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

    mission_text = resume_sections.get("mission", "")
    mission_lines = [l.strip() for l in mission_text.split("\n") if l.strip()]
    tagline = mission_lines[0] if mission_lines else ""
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
                parsed = _parse_role_block(
                    chunk,
                    page_break_before=role_break or chunk_i > 0,
                )
                if parsed:
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
                pending_proj_break = True
                continue
            if not stripped:
                if current_title:
                    projects_list.append({
                        "title": current_title,
                        "bullets": current_bullets,
                        "page_break_before": pending_proj_break,
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
            projects_list.append({
                "title": current_title,
                "bullets": current_bullets,
                "page_break_before": pending_proj_break,
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
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    HTML(string=html_content, base_url=str(TEMPLATE_DIR)).write_pdf(output_path)

    return output_path
