import os
import time
from pathlib import Path
from openai import OpenAI

PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"

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

def get_openai_client(api_key):
    return OpenAI(api_key=api_key)


def _track_instruction(track: str) -> str:
    """Return track-specific instruction string or empty."""
    return TRACK_EMPHASIS.get(track, "")

def get_anti_fluff() -> str:
    """Load the shared ANTI_FLUFF block."""
    path = PROMPTS_DIR / "anti_fluff.md"
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return ""

def load_prompt(filename: str, **kwargs) -> tuple[str, str]:
    """Load a markdown prompt template and split into system and user prompts."""
    path = PROMPTS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Prompt template {filename} not found.")
        
    text = path.read_text(encoding="utf-8")
    
    if "---USER---" in text:
        sys_part, usr_part = text.split("---USER---", 1)
        return sys_part.format(**kwargs).strip(), usr_part.format(**kwargs).strip()
    else:
        return text.format(**kwargs).strip(), ""

def _call_openai(client, system_prompt, user_prompt, max_tokens=600, temperature=0.4, retries=3):
    """Call OpenAI with retry logic. Returns (content, usage_dict)."""
    last_error = None
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
            return response.choices[0].message.content.strip(), usage
        except Exception as e:
            last_error = e
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
    raise last_error

# ---------------------------------------------------------------------------
# JD Keyword Extraction (ATS-KW)
# ---------------------------------------------------------------------------
def extract_jd_keywords(client, jd_text):
    """Extract top 5 duties and top 5 requirements from a raw JD for ATS targeting."""
    system_prompt, user_prompt = load_prompt(
        "extract_keywords.md", 
        jd_text=jd_text[:4000]
    )
    return _call_openai(client, system_prompt, user_prompt, max_tokens=400, temperature=0.2)

# ---------------------------------------------------------------------------
# Role selection
# ---------------------------------------------------------------------------
def select_relevant_roles(client, jd_text, master_context):
    """LLM picks which roles from master context are most relevant to the JD."""
    system_prompt, user_prompt = load_prompt(
        "select_roles.md",
        jd_text=jd_text[:3000],
        master_context=master_context
    )
    return _call_openai(client, system_prompt, user_prompt, max_tokens=300)

# ---------------------------------------------------------------------------
# Mission Statement
# ---------------------------------------------------------------------------
def generate_mission_statement(client, jd_paragraphs, target_title, company_name, track=""):
    track_line = f"\nTRACK EMPHASIS: {_track_instruction(track)}" if track else ""
    system_prompt, user_prompt = load_prompt(
        "mission_statement.md",
        track_line=track_line,
        ANTI_FLUFF=get_anti_fluff(),
        company_name=company_name,
        target_role=target_title,
        jd_paragraphs=jd_paragraphs[:1500]
    )
    return _call_openai(client, system_prompt, user_prompt, max_tokens=200)

# ---------------------------------------------------------------------------
# Skills Statements
# ---------------------------------------------------------------------------
def generate_skills_statements(client, jd_duties, master_context, target_role, track=""):
    track_line = f"\nTRACK EMPHASIS: {_track_instruction(track)}" if track else ""
    system_prompt, user_prompt = load_prompt(
        "skills_statements.md",
        track_line=track_line,
        ANTI_FLUFF=get_anti_fluff(),
        target_role=target_role,
        jd_duties=jd_duties,
        master_context=master_context[:6000]
    )
    return _call_openai(client, system_prompt, user_prompt, max_tokens=800)

# ---------------------------------------------------------------------------
# Experience Bullets (per-role)
# ---------------------------------------------------------------------------
def generate_experience_bullets(client, role_block, jd_text, track=""):
    """Generate bullets for ONE role."""
    track_line = f"\nTRACK EMPHASIS: {_track_instruction(track)}" if track else ""
    system_prompt, user_prompt = load_prompt(
        "experience_bullets.md",
        track_line=track_line,
        ANTI_FLUFF=get_anti_fluff(),
        role_block=role_block,
        jd_text=jd_text[:2000]
    )
    return _call_openai(client, system_prompt, user_prompt, max_tokens=800)

# ---------------------------------------------------------------------------
# Cover Letter
# ---------------------------------------------------------------------------
def generate_cover_letter(client, jd_text, master_context, target_role, company_name, track=""):
    track_line = f"\nTRACK EMPHASIS: {_track_instruction(track)}" if track else ""
    system_prompt, user_prompt = load_prompt(
        "cover_letter.md",
        track_line=track_line,
        target_role=target_role,
        company_name=company_name,
        jd_text=jd_text[:3000],
        master_context=master_context[:5000]
    )
    return _call_openai(client, system_prompt, user_prompt, max_tokens=700)

# ---------------------------------------------------------------------------
# Custom Q&A
# ---------------------------------------------------------------------------
def answer_custom_questions(client, questions, master_context, jd_text):
    """Answer application-specific questions grounded in real experience."""
    if not questions.strip():
        return "", {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    system_prompt, user_prompt = load_prompt(
        "custom_qa.md",
        questions=questions,
        master_context=master_context[:4000],
        jd_text=jd_text[:2000]
    )
    return _call_openai(client, system_prompt, user_prompt, max_tokens=800)
