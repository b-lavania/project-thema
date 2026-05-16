import os
import re
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS

TEMPLATE_DIR = Path(__file__).resolve().parent

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

def create_formatted_pdf(output_path, resume_sections, location="Sunnyvale, CA"):
    """
    Build a 1-page resume PDF by rendering template.html with Jinja2 
    and converting to PDF with WeasyPrint.
    """
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    template = env.get_template("template.html")

    # 1. Mission / Tagline
    mission_text = resume_sections.get("mission", "")
    mission_lines = [l.strip() for l in mission_text.split("\n") if l.strip()]
    tagline = mission_lines[0] if mission_lines else ""
    mission_body = "\n".join(mission_lines[1:]) if len(mission_lines) > 1 else ""

    # 2. Skills
    skills_raw = resume_sections.get("skills", "")
    skills_clean = strip_coaching_notes(skills_raw)
    skills_list = []
    for line in skills_clean.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        # Remove leading numbers like "1) " or "- "
        stripped = re.sub(r'^\d+\)\s*', '', stripped)
        stripped = re.sub(r'^-\s*', '', stripped)
        skills_list.append(parse_bullet_line(stripped))

    # 3. Experience
    experience_list = []
    if resume_sections.get("experience"):
        for role_text in resume_sections["experience"]:
            clean_role = strip_coaching_notes(role_text)
            lines = [l.strip() for l in clean_role.split("\n") if l.strip()]
            
            if not lines:
                continue

            # First line is usually "Job Title @ Company Name, Location, Employment Dates"
            # We want to split this into title_company and dates_location
            header_line = lines[0]
            title_company = header_line
            dates_location = ""
            
            # Simple heuristic: split by comma to find dates
            header_parts = header_line.split(",")
            if len(header_parts) >= 3:
                # "Title @ Company", "Location", "Dates"
                title_company = header_parts[0].strip()
                dates_location = ", ".join(p.strip() for p in header_parts[1:])
            
            company_desc = lines[1] if len(lines) > 1 else ""
            summary = lines[2] if len(lines) > 2 else ""
            
            bullets = []
            for line in lines[3:]:
                # remove leading bullet chars
                line = re.sub(r'^-\s*', '', line)
                bullets.append(parse_bullet_line(line))
                
            experience_list.append({
                "title_company": title_company,
                "dates_location": dates_location,
                "company_desc": company_desc,
                "summary": summary,
                "bullets": bullets
            })

    # Render HTML
    html_content = template.render(
        tagline=tagline,
        location=location,
        mission_body=mission_body,
        skills=skills_list,
        experience=experience_list
    )

    # Convert to PDF
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    HTML(string=html_content, base_url=str(TEMPLATE_DIR)).write_pdf(output_path)
    
    return output_path
