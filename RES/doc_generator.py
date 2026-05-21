import os
from pathlib import Path
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from lxml import etree

from generator import PAGE_BREAK_MARKER, normalize_pdf_breaks

TEMPLATE_PATH = Path(__file__).resolve().parent / "assets" / "template.docx"


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


def _add_para(
    doc,
    text,
    style="Normal",
    align=None,
    bold=False,
    italic=False,
    font_size=None,
    keep_with_next=False,
    page_break_before=False,
):
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
    if keep_with_next:
        p.paragraph_format.keep_with_next = True
    if page_break_before:
        p.paragraph_format.page_break_before = True
    return p


def _strip_page_break_lines(text):
    """Remove ---PAGEBREAK--- lines from text before writing to DOCX."""
    lines = []
    for line in text.split("\n"):
        if line.strip() == PAGE_BREAK_MARKER:
            continue
        lines.append(line)
    return "\n".join(lines)


def _is_bullet_line(line):
    """Labeled experience bullets (Skill Label: sentence) or dash bullets."""
    stripped = line.strip()
    if stripped.startswith("-") or stripped.startswith("•"):
        return True
    if "@" in stripped:
        return False
    if ": " in stripped:
        label = stripped.split(":", 1)[0].strip()
        if 1 <= len(label.split()) <= 5:
            return True
    return False


def _add_section_paragraphs(doc, text, keep_together=False):
    """Write text block to doc line by line, skipping COACHING NOTEs."""
    clean = strip_coaching_notes(text)
    lines = [ln.strip() for ln in clean.split("\n") if ln.strip()]
    in_preface = keep_together
    for stripped in lines:
        keep = keep_together and in_preface
        if _is_bullet_line(stripped):
            in_preface = False
        _add_para(doc, stripped, style="Normal", keep_with_next=keep)


def create_formatted_doc(
    output_path,
    resume_sections,
    location="Sunnyvale, CA",
    include_scrum=False,
    pdf_breaks=None,
):
    """
    Build a letter-size resume DOCX (typically 1-2 pages) by loading assets/template.docx,
    and writing generated resume content using the template's own styles.

    Args:
        output_path: Where to save the .docx
        resume_sections: dict with keys 'mission', 'skills', 'experience' (list of role texts)
        location: Candidate location string
        include_scrum: Whether to include CSM & CSPO certification line

    Returns:
        output_path on success
    """
    breaks = normalize_pdf_breaks(pdf_breaks)
    break_sections = breaks["before_sections"]
    break_role_index = breaks["before_role_index"]

    doc = Document(str(TEMPLATE_PATH))
    _clear_body(doc)

    # ===== PAGE 1: RESUME =====

    # Name — Heading 1 (font_size override reduces from template default)
    _add_para(doc, 'Bharat "Bob" Lavania', style="Heading 1", font_size=16)

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
        _add_para(doc, "THE QUICK TAKE", style="Heading 3")
        _add_para(doc, mission_body, style="Normal")

    # Technical Expertise / Skills
    if resume_sections.get("skills"):
        _add_para(
            doc,
            "HOW I WORK",
            style="Heading 3",
            page_break_before="skills" in break_sections,
        )
        _add_section_paragraphs(doc, _strip_page_break_lines(resume_sections["skills"]))

    # Professional Experience
    if resume_sections.get("experience"):
        _add_para(
            doc,
            "THE WORK",
            style="Heading 3",
            page_break_before="experience" in break_sections,
        )
        for i, role_text in enumerate(resume_sections["experience"], start=1):
            if i > 0:
                doc.add_paragraph()  # spacer between roles
            if break_role_index is not None and i == break_role_index:
                _add_para(doc, "", style="Normal", page_break_before=True)
            _add_section_paragraphs(
                doc,
                _strip_page_break_lines(role_text),
                keep_together=True,
            )

    # Projects
    if resume_sections.get("projects"):
        _add_para(
            doc,
            "SIDE BUILDS",
            style="Heading 3",
            page_break_before="projects" in break_sections,
        )
        _add_section_paragraphs(doc, _strip_page_break_lines(resume_sections["projects"]))

    # Education
    _add_para(
        doc,
        "CREDENTIALS",
        style="Heading 3",
        page_break_before="credentials" in break_sections,
    )
    _add_para(doc, "MBA, Energy Economics and Product Leadership, University of Calgary (2025)", style="Normal")
    _add_para(doc, "Bachelor of Science, Finance, Illinois Tech, Chicago, IL (2012)", style="Normal")
    if include_scrum:
        _add_para(doc, "CSM & CSPO, Scrum Alliance (2022)", style="Normal")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)
    return output_path
