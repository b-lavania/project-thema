import os
import re
import time
from pathlib import Path

from llm_client import LLMClient, call_llm, get_llm_client, resolve_model

PAGE_BREAK_MARKER = "---PAGEBREAK---"
PROFILE_WHAT_VERBS = re.compile(
    r"\b(Built|Engineered|Deployed|Launched|Led implementation)\b",
    re.IGNORECASE,
)

PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"

# Legacy OpenAI env overrides (used when provider=openai via llm_client)
PAIN_POINT_MODEL = os.environ.get("PAIN_POINT_MODEL", "o4-mini")
PAIN_POINT_FALLBACK = os.environ.get("PAIN_POINT_FALLBACK", "gpt-4.1")

# ---------------------------------------------------------------------------
# Track-specific prompt fragments
# ---------------------------------------------------------------------------
TRACK_EMPHASIS = {
    "Product/AI": (
        "Emphasize shipping AI/ML to production, experimentation loops, measurement frameworks, and measurable user impact. "
        "Weave in naturally where grounded: product-led growth, A/B testing, LLM evaluation, model deployment, "
        "prompt engineering, RAG, inference latency, feature prioritization, product metrics, experimentation platform, "
        "user research, roadmap, model accuracy, fine-tuning, observability."
    ),
    "Pricing/Ops": (
        "Emphasize quoting/pricing clarity, operational reliability, support deflection, throughput gains, and unit economics. "
        "Weave in naturally where grounded: pricing strategy, take rate, ARPU, churn reduction, revenue optimization, "
        "unit economics, operational efficiency, cost reduction, SLA, throughput, workflow automation, "
        "CAC, LTV, margin, pricing architecture, monetization."
    ),
    "Growth": (
        "Emphasize user acquisition, retention, conversion optimization, GTM experiments, and funnel metrics. "
        "Weave in naturally where grounded: growth loops, conversion rate optimization, A/B testing, funnel analysis, "
        "lifecycle marketing, cohort analysis, activation, retention, CAC, LTV, MQL, SQL, attribution modeling, "
        "media mix modeling, GTM strategy, landing page optimization."
    ),
    "Logistics/Marketplace": (
        "Emphasize supply/demand matching, operational efficiency, marketplace dynamics, fill rates, and logistics automation. "
        "Weave in naturally where grounded: marketplace design, supply-demand balance, fill rate, GMV, take rate, "
        "last-mile delivery, TMS, WMS, dispatch optimization, operations research, bin packing, route optimization, "
        "carrier management, fulfillment."
    ),
    "BizOps": (
        "Emphasize cross-functional execution, decision systems, narrative clarity, and measurable business lift. "
        "Weave in naturally where grounded: cross-functional alignment, OKRs, KPIs, process improvement, "
        "business intelligence, executive reporting, decision framework, stakeholder management, "
        "operating cadence, P&L ownership, resource allocation, strategic planning."
    ),
    "Chief of Staff": (
        "Emphasize strategic planning, organizational alignment, executive support, and cross-functional coordination. "
        "Weave in naturally where grounded: chief of staff, executive alignment, strategic initiatives, "
        "organizational design, board reporting, M&A, due diligence, cross-functional coordination, "
        "operating model, change management, executive communication, special projects."
    ),
}


def _track_instruction(track: str) -> str:
    """Return track-specific instruction string or empty."""
    return TRACK_EMPHASIS.get(track, "")


# ---------------------------------------------------------------------------
# Voice-specific prompt fragments
# ---------------------------------------------------------------------------
VOICE_EMPHASIS = {
    "Sharp Product PM": (
        "Lead with market/user insight, product decisions, tradeoffs, and measured behavior change. "
        "Every bullet must show product judgment before implementation."
    ),
    "Technical Product PM": (
        "Keep technical credibility, but lead with product judgment before implementation details. "
        "Show how technical depth informs product decisions, not just what was built."
    ),
    "Growth / GTM PM": (
        "Lead with funnel, pricing, activation, retention, monetization, and GTM learning loops. "
        "Emphasize measured growth outcomes and go-to-market decisions."
    ),
    "Chief of Staff / BizOps": (
        "Lead with decision systems, operating cadence, executive leverage, and measurable business clarity. "
        "Emphasize cross-functional execution and strategic alignment."
    ),
}


def _voice_instruction(voice: str) -> str:
    """Return voice-specific instruction string or empty."""
    return VOICE_EMPHASIS.get(voice, "")


def get_anti_fluff() -> str:
    """Load the shared ANTI_FLUFF block."""
    path = PROMPTS_DIR / "anti_fluff.md"
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return ""


def normalize_pdf_breaks(pdf_breaks=None):
    """Return a consistent pdf_breaks dict for PDF/DOCX renderers."""
    if not pdf_breaks:
        return {"before_sections": [], "before_role_index": None}
    raw_sections = pdf_breaks.get("before_sections")
    sections = list(raw_sections) if raw_sections else []
    role_idx = pdf_breaks.get("before_role_index")
    if role_idx in (0, "0", None, ""):
        role_idx = None
    else:
        role_idx = int(role_idx)
    return {"before_sections": sections, "before_role_index": role_idx}


def extract_profile_context_excerpt(master_context: str, max_chars: int = 2500) -> str:
    """Key Insights + Working Principles (+ resume generation notes) for profile prompts."""
    parts = []
    text = master_context or ""
    for heading in ("## Key Insights", "## Working Principles", "## Resume generation notes"):
        start = text.find(heading)
        if start == -1:
            continue
        end = len(text)
        for other in ("## Key Insights", "## Working Principles", "## Resume generation notes", "## Skills"):
            if other == heading:
                continue
            pos = text.find(other, start + len(heading))
            if pos != -1 and pos < end:
                end = pos
        parts.append(text[start:end].strip())
    excerpt = "\n\n".join(parts) if parts else text[:max_chars]
    return excerpt[:max_chars]


def profile_is_what_heavy(mission: str) -> bool:
    """Heuristic: profile likely needs lint pass."""
    if not mission:
        return False
    return bool(PROFILE_WHAT_VERBS.search(mission))


def profile_needs_lint(mission: str) -> bool:
    """True if profile is WHAT-heavy, vague, or missing parallel-experience beat."""
    if profile_is_what_heavy(mission):
        return True
    lines = [ln.strip() for ln in mission.split("\n") if ln.strip()]
    if not lines:
        return False
    body_text = " ".join(lines[1:]).lower() if len(lines) > 1 else mission.lower()
    parallel_markers = (
        "seen",
        "same",
        "years",
        "across",
        "prior",
        "pattern",
        "marketplace",
        "logistics",
        "saas",
        "fintech",
        "health",
        "fractional",
        "m&a",
        "pricing",
        "ops",
    )
    vague_markers = ("dynamic", "landscape", "fast-paced", "holistic", "strategic leader")
    if sum(1 for v in vague_markers if v in body_text) >= 2:
        return True
    if not any(m in body_text for m in parallel_markers):
        return True
    # Legacy 4-line profiles: still lint if structure is incomplete
    if len(lines) >= 4:
        line3 = lines[2].lower()
        if not any(m in line3 for m in parallel_markers):
            return True
    return False


def load_prompt(filename: str, **kwargs) -> tuple[str, str]:
    """Load a markdown prompt template and split into system and user prompts."""
    path = PROMPTS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Prompt template {filename} not found.")

    text = path.read_text(encoding="utf-8")

    if "---USER---" in text:
        sys_part, usr_part = text.split("---USER---", 1)
        return sys_part.format(**kwargs).strip(), usr_part.format(**kwargs).strip()
    return text.format(**kwargs).strip(), ""


def _llm(
    llm,
    system_prompt: str,
    user_prompt: str,
    *,
    max_tokens: int,
    temperature: float = 0.4,
    tier: str = "default",
    step: str = "Generation step",
):
    """Wrapper: require non-empty output (critical for Gemini Flash)."""
    return call_llm(
        llm,
        system_prompt,
        user_prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        tier=tier,
        require_nonempty=True,
        step_label=step,
    )


def _call_with_pain_fallback(llm, system_prompt, user_prompt, max_tokens, temperature, step: str):
    """Pain-tier call with one fallback model on transient/API failure (not 404 / empty text)."""
    from llm_client import LLMResponseError

    try:
        return _llm(
            llm,
            system_prompt,
            user_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            tier="pain",
            step=step,
        )
    except LLMResponseError:
        raise
    except Exception as e:
        err = str(e)
        if "404" in err or "NOT_FOUND" in err:
            raise
        return _llm(
            llm,
            system_prompt,
            user_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            tier="pain_fallback",
            step=f"{step} (fallback)",
        )


# ---------------------------------------------------------------------------
# JD Keyword Extraction (ATS-KW)
# ---------------------------------------------------------------------------
def extract_jd_keywords(llm, jd_text):
    """Extract top 5 duties and top 5 requirements from a raw JD for ATS targeting."""
    system_prompt, user_prompt = load_prompt(
        "extract_keywords.md",
        jd_text=jd_text[:4000],
    )
    return _llm(
        llm,
        system_prompt,
        user_prompt,
        max_tokens=512,
        temperature=0.2,
        step="JD keyword extraction",
    )


# ---------------------------------------------------------------------------
# Narrative Brief
# ---------------------------------------------------------------------------
def generate_narrative_brief(llm, jd_text, master_context, target_role, company_name, track="", voice=""):
    """Synthesize master_context + JD into a coherent positioning brief."""
    track_line = f"\nTRACK EMPHASIS: {_track_instruction(track)}" if track else ""
    voice_line = f"\nRESUME VOICE: {_voice_instruction(voice)}" if voice else ""
    system_prompt, user_prompt = load_prompt(
        "narrative_brief.md",
        track_line=track_line,
        voice_line=voice_line,
        target_role=target_role,
        company_name=company_name,
        jd_text=jd_text[:4000],
        master_context=master_context,
    )
    return _llm(
        llm,
        system_prompt,
        user_prompt,
        max_tokens=900,
        temperature=0.4,
        step="Narrative brief",
    )


# ---------------------------------------------------------------------------
# Role selection
# ---------------------------------------------------------------------------
def select_relevant_roles(llm, jd_text, master_context):
    """LLM picks which roles from master context are most relevant to the JD."""
    system_prompt, user_prompt = load_prompt(
        "select_roles.md",
        jd_text=jd_text[:3000],
        master_context=master_context,
    )
    return _llm(
        llm,
        system_prompt,
        user_prompt,
        max_tokens=512,
        step="Role selection",
    )


# ---------------------------------------------------------------------------
# JD pain point (reasoning step before profile)
# ---------------------------------------------------------------------------
def extract_jd_pain_point(llm, jd_text, target_role, jd_duties=""):
    """Extract CORE_PAIN and related framing from the JD (no company name)."""
    jd_slice = jd_text[:3000]
    if jd_duties:
        jd_slice = f"{jd_slice}\n\nKey duties (from keyword extract):\n{jd_duties[:1500]}"
    system_prompt, user_prompt = load_prompt(
        "jd_pain_point.md",
        target_role=target_role,
        jd_text=jd_slice,
    )
    return _call_with_pain_fallback(
        llm, system_prompt, user_prompt, 600, 0.2, step="JD pain analysis"
    )


# ---------------------------------------------------------------------------
# Profile angle (WHY framing before The Quick Take)
# ---------------------------------------------------------------------------
def generate_profile_angle(
    llm,
    jd_pain,
    narrative_brief,
    target_role,
    master_context="",
):
    excerpt = extract_profile_context_excerpt(master_context)
    system_prompt, user_prompt = load_prompt(
        "profile_angle.md",
        target_role=target_role,
        jd_pain=jd_pain or "(none)",
        narrative_brief=narrative_brief or "(none)",
        profile_context_excerpt=excerpt,
    )
    return _call_with_pain_fallback(
        llm, system_prompt, user_prompt, 768, 0.2, step="Profile angle"
    )


def lint_profile_why(llm, mission, profile_angle):
    """Rewrite profile if it reads WHAT-heavy vs profile_angle."""
    system_prompt, user_prompt = load_prompt(
        "profile_lint.md",
        profile_angle=profile_angle or "(none)",
        mission=mission,
    )
    return _llm(
        llm,
        system_prompt,
        user_prompt,
        max_tokens=768,
        temperature=0.2,
        tier="profile",
        step="Profile lint",
    )


# ---------------------------------------------------------------------------
# Mission Statement
# ---------------------------------------------------------------------------
def generate_mission_statement(
    llm,
    jd_paragraphs,
    target_title,
    company_name="",
    track="",
    voice="",
    narrative_brief="",
    jd_pain="",
    profile_angle="",
    profile_context_excerpt="",
):
    track_line = f"\nTRACK EMPHASIS: {_track_instruction(track)}" if track else ""
    voice_line = f"\nRESUME VOICE: {_voice_instruction(voice)}" if voice else ""
    if not profile_context_excerpt:
        profile_context_excerpt = "(not provided)"
    system_prompt, user_prompt = load_prompt(
        "mission_statement.md",
        track_line=track_line,
        voice_line=voice_line,
        ANTI_FLUFF=get_anti_fluff(),
        target_role=target_title,
        jd_paragraphs=jd_paragraphs[:1500],
        narrative_brief=narrative_brief,
        jd_pain=jd_pain or "(No pain analysis provided — infer pain only from JD paragraphs.)",
        profile_angle=profile_angle or "(No profile angle — use jd_pain and narrative brief only.)",
        profile_context_excerpt=profile_context_excerpt,
    )
    return _llm(
        llm,
        system_prompt,
        user_prompt,
        max_tokens=768,
        temperature=0.3,
        tier="profile",
        step="The Quick Take (profile)",
    )


def generate_profile_with_lint(
    llm,
    jd_paragraphs,
    target_title,
    company_name="",
    track="",
    voice="",
    narrative_brief="",
    jd_pain="",
    profile_angle="",
    master_context="",
    run_lint=True,
):
    """Mission statement plus optional WHY lint pass. Returns (mission, usage_list)."""
    excerpt = extract_profile_context_excerpt(master_context)
    mission, u1 = generate_mission_statement(
        llm,
        jd_paragraphs,
        target_title,
        company_name,
        track,
        voice=voice,
        narrative_brief=narrative_brief,
        jd_pain=jd_pain,
        profile_angle=profile_angle,
        profile_context_excerpt=excerpt,
    )
    usage = [u1] if u1 else []
    if run_lint and profile_angle and profile_needs_lint(mission):
        mission, u2 = lint_profile_why(llm, mission, profile_angle)
        if u2:
            usage.append(u2)
    return mission or "", usage


# ---------------------------------------------------------------------------
# Skills Statements
# ---------------------------------------------------------------------------
def generate_skills_statements(llm, jd_duties, master_context, target_role, track="", voice="", narrative_brief=""):
    track_line = f"\nTRACK EMPHASIS: {_track_instruction(track)}" if track else ""
    voice_line = f"\nRESUME VOICE: {_voice_instruction(voice)}" if voice else ""
    system_prompt, user_prompt = load_prompt(
        "skills_statements.md",
        track_line=track_line,
        voice_line=voice_line,
        ANTI_FLUFF=get_anti_fluff(),
        target_role=target_role,
        jd_duties=jd_duties,
        narrative_brief=narrative_brief,
        master_context=master_context[:4000],
    )
    return _llm(
        llm,
        system_prompt,
        user_prompt,
        max_tokens=1200,
        step="Skills statements",
    )


# ---------------------------------------------------------------------------
# Experience Bullets (per-role)
# ---------------------------------------------------------------------------
def generate_experience_bullets(llm, role_block, jd_text, track="", voice="", narrative_brief=""):
    """Generate bullets for ONE role."""
    track_line = f"\nTRACK EMPHASIS: {_track_instruction(track)}" if track else ""
    voice_line = f"\nRESUME VOICE: {_voice_instruction(voice)}" if voice else ""
    system_prompt, user_prompt = load_prompt(
        "experience_bullets.md",
        track_line=track_line,
        voice_line=voice_line,
        ANTI_FLUFF=get_anti_fluff(),
        role_block=role_block,
        narrative_brief=narrative_brief,
        jd_text=jd_text[:2000],
    )
    return _llm(
        llm,
        system_prompt,
        user_prompt,
        max_tokens=1200,
        step="Experience bullets",
    )


# ---------------------------------------------------------------------------
# Personal Projects
# ---------------------------------------------------------------------------
def generate_personal_projects(llm, projects_block, jd_text, track="", voice="", narrative_brief=""):
    """Generate a JD-tailored PROJECTS section from the Additional Projects block."""
    track_line = f"\nTRACK EMPHASIS: {_track_instruction(track)}" if track else ""
    voice_line = f"\nRESUME VOICE: {_voice_instruction(voice)}" if voice else ""
    system_prompt, user_prompt = load_prompt(
        "personal_projects.md",
        track_line=track_line,
        voice_line=voice_line,
        ANTI_FLUFF=get_anti_fluff(),
        projects_block=projects_block,
        narrative_brief=narrative_brief,
        jd_text=jd_text[:2000],
    )
    return _llm(
        llm,
        system_prompt,
        user_prompt,
        max_tokens=900,
        step="Personal projects",
    )


# ---------------------------------------------------------------------------
# Cover Letter
# ---------------------------------------------------------------------------
def generate_cover_letter(llm, jd_text, master_context, target_role, company_name, track="", voice="", narrative_brief=""):
    track_line = f"\nTRACK EMPHASIS: {_track_instruction(track)}" if track else ""
    voice_line = f"\nRESUME VOICE: {_voice_instruction(voice)}" if voice else ""
    system_prompt, user_prompt = load_prompt(
        "cover_letter.md",
        track_line=track_line,
        voice_line=voice_line,
        target_role=target_role,
        company_name=company_name,
        jd_text=jd_text[:3000],
        narrative_brief=narrative_brief,
        master_context=master_context[:3000],
    )
    return _llm(
        llm,
        system_prompt,
        user_prompt,
        max_tokens=1000,
        step="Cover letter",
    )


# ---------------------------------------------------------------------------
# Custom Q&A
# ---------------------------------------------------------------------------
def answer_custom_questions(llm, questions, master_context, jd_text):
    """Answer application-specific questions grounded in real experience."""
    if not questions.strip():
        return "", {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    system_prompt, user_prompt = load_prompt(
        "custom_qa.md",
        questions=questions,
        master_context=master_context[:4000],
        jd_text=jd_text[:2000],
    )
    return _llm(
        llm,
        system_prompt,
        user_prompt,
        max_tokens=1200,
        step="Application Q&A",
    )


def review_resume_quality(
    llm,
    jd_text,
    jd_pain,
    profile_angle,
    narrative_brief,
    mission,
    skills,
    experience_blocks,
    projects,
):
    """Post-generation quality review: punchiness, PM signal, JD fit, builder-heavy risk."""
    system_prompt, user_prompt = load_prompt(
        "resume_quality_review.md",
        jd_pain=jd_pain or "(none)",
        profile_angle=profile_angle or "(none)",
        narrative_brief=narrative_brief or "(none)",
        mission=mission or "(none)",
        skills=skills or "(none)",
        experience_blocks="\n\n".join(experience_blocks) if experience_blocks else "(none)",
        projects=projects or "(none)",
    )
    return _llm(
        llm,
        system_prompt,
        user_prompt,
        max_tokens=900,
        temperature=0.2,
        step="Resume quality review",
    )
