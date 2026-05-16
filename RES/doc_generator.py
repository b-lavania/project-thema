import os
from pathlib import Path
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from lxml import etree

TEMPLATE_PATH = Path(__file__).resolve().parent / "historic" / "template.docx"


def strip_coaching_notes(text):
    """Remove COACHING NOTE lines from text before writing to doc."""
    lines = []
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("COACHING NOTE:") or stripped.startswith("Alt (general)"):
            continue
        lines.append(line)
    return "\n".join(lines)


def extract_coaching_notes(text):
    """Extract only COACHING NOTE lines from text for UI display."""
    notes = []
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("COACHING NOTE:") or stripped.startswith("Alt (general)"):
            notes.append(stripped)
    return "\n".join(notes)


def _clear_body(doc):
    """Remove all paragraphs and tables from document body."""
    body = doc.element.body
    for child in list(body):
        tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
        if tag in ("p", "tbl", "sdt"):
            body.remove(child)


def _add_para(doc, text, style="Normal", align=None, bold=False, italic=False, font_size=None):
    """Add a paragraph with the given style and optional formatting."""
    p = doc.add_paragraph(style=style)
    run = p.add_run(text)
    if bold:
        run.bold = True
    if italic:
        run.italic = True
    if font_size:
        run.font.size = Pt(font_size)
    if align:
        p.alignment = align
    return p


def _add_section_paragraphs(doc, text):
    """Write text block to doc line by line, skipping COACHING NOTEs."""
    clean = strip_coaching_notes(text)
    for line in clean.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        _add_para(doc, stripped, style="Normal")


def create_formatted_doc(output_path, resume_sections, location="Sunnyvale, CA"):
    """
    Build a 1-page resume DOCX by loading template.docx, clearing its content,
    and writing generated resume content using the template's own styles.

    Args:
        output_path: Where to save the .docx
        resume_sections: dict with keys 'mission', 'skills', 'experience' (list of role texts)
        location: Candidate location string

    Returns:
        output_path on success
    """
    doc = Document(str(TEMPLATE_PATH))
    _clear_body(doc)

    # ===== PAGE 1: RESUME =====

    # Name — Heading 1
    _add_para(doc, 'Bharat "Bob" Lavania', style="Heading 1")

    # Tagline from mission (line 1 only)
    mission_text = resume_sections.get("mission", "")
    mission_lines = [l.strip() for l in mission_text.split("\n") if l.strip()]
    tagline = mission_lines[0] if mission_lines else ""
    mission_body = "\n".join(mission_lines[1:]) if len(mission_lines) > 1 else ""

    if tagline:
        _add_para(doc, tagline, style="Normal")

    # Contact line
    _add_para(
        doc,
        f"(312) 772-7962 | xblavania@gmail.com | linkedin.com/in/blavania | {location}",
        style="Normal"
    )

    # Professional Profile section (mission body)
    if mission_body:
        _add_para(doc, "PROFESSIONAL PROFILE", style="Heading 3")
        _add_para(doc, mission_body, style="Normal")

    # Technical Expertise / Skills
    if resume_sections.get("skills"):
        _add_para(doc, "TECHNICAL EXPERTISE", style="Heading 3")
        _add_section_paragraphs(doc, resume_sections["skills"])

    # Professional Experience
    if resume_sections.get("experience"):
        _add_para(doc, "PROFESSIONAL EXPERIENCE", style="Heading 3")
        for i, role_text in enumerate(resume_sections["experience"]):
            if i > 0:
                doc.add_paragraph()  # spacer between roles
            _add_section_paragraphs(doc, role_text)

    # Education
    _add_para(doc, "EDUCATION", style="Heading 3")
    _add_para(doc, "MBA, Energy Economics and Product Leadership | University of Calgary (2025)", style="Normal")
    _add_para(doc, "Bachelor of Science | Illinois Tech, Chicago, IL (2012)", style="Normal")
    _add_para(doc, "CSM & CSPO | Scrum Alliance (2022)", style="Normal")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)
    return output_path
