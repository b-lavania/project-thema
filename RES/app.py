import os
import re
import datetime
from pathlib import Path
import streamlit as st
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from llm_client import (
    get_llm_client,
    model_choices,
    GEMINI_DEFAULTS,
    OPENAI_DEFAULTS,
    LLMResponseError,
    normalize_gemini_model_id,
)
from generator import (
    extract_jd_keywords,
    extract_jd_pain_point,
    generate_narrative_brief,
    select_relevant_roles,
    generate_profile_angle,
    generate_profile_with_lint,
    normalize_pdf_breaks,
    generate_skills_statements,
    generate_experience_bullets,
    generate_personal_projects,
    generate_cover_letter,
    answer_custom_questions,
    review_resume_quality,
    PAGE_BREAK_MARKER,
)
from doc_generator import create_formatted_doc, extract_coaching_notes, strip_coaching_notes
from pdf_generator import create_formatted_pdf

# ---------------------------------------------------------------------------
# Path resolution (P0-PATH)
# ---------------------------------------------------------------------------
RES_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = RES_ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)
MASTER_CONTEXT_PATH = RES_ROOT / "data" / "master_context.md"
HISTORY_PATH = RES_ROOT / "data" / "history.md"
ENV_PATH = RES_ROOT / ".env"

# Load .env file if it exists
load_dotenv(ENV_PATH)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
TRACK_OPTIONS = ["Product/AI", "Pricing/Ops", "Growth", "Logistics/Marketplace", "BizOps", "Chief of Staff"]
VOICE_OPTIONS = ["Sharp Product PM", "Technical Product PM", "Growth / GTM PM", "Chief of Staff / BizOps"]
LOCATION_OPTIONS = {
    "Sunnyvale, CA (SF / Silicon Valley / Remote USA)": "Sunnyvale, CA",
    "Calgary, AB (Canadian jobs)": "Calgary, AB",
}
MIN_JD_LENGTH = 200
PROVIDER_OPTIONS = ["OpenAI", "Google Gemini"]
OPENAI_INPUT_PRICE_PER_1K = 0.0025
OPENAI_OUTPUT_PRICE_PER_1K = 0.01
# Gemini 2.5 Flash approximate (AI Studio; profile steps may use Pro at higher cost)
GEMINI_INPUT_PRICE_PER_1K = 0.00015
GEMINI_OUTPUT_PRICE_PER_1K = 0.0006


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def load_master_context():
    """Load master context file at startup."""
    if MASTER_CONTEXT_PATH.exists():
        return MASTER_CONTEXT_PATH.read_text(encoding="utf-8")
    return ""


def extract_role_blocks(master_context):
    """Split master context into individual role blocks based on ### ROLE headers."""
    blocks = {}
    current_key = None
    current_lines = []
    for line in master_context.split("\n"):
        if line.startswith("### ROLE"):
            if current_key:
                blocks[current_key] = "\n".join(current_lines)
            current_key = line.strip("# ").strip()
            current_lines = [line]
        elif current_key:
            if line.startswith("### ") and not line.startswith("### ROLE"):
                current_lines.append(line)
            elif line.startswith("## ") and current_key:
                blocks[current_key] = "\n".join(current_lines)
                current_key = None
                current_lines = []
            else:
                current_lines.append(line)
    if current_key:
        blocks[current_key] = "\n".join(current_lines)
    return blocks


def extract_condensed_role_line(role_block: str) -> str:
    """Extract title, org, dates from role block for condensed display."""
    lines = role_block.split("\n")
    title = ""
    company = ""
    dates = ""
    
    for line in lines:
        # Extract title from header line (### ROLE X: Title)
        if line.startswith("### ROLE") and ":" in line:
            title = line.split(":", 1)[1].strip()
        # Or from explicit Title field
        elif line.startswith("- **Title**:"):
            title = line.split(":", 1)[1].strip()
        elif line.startswith("- **Company**:"):
            company = line.split(":", 1)[1].strip().split("—")[0].strip()
        elif line.startswith("- **Dates**:"):
            dates = line.split(":", 1)[1].strip()
    
    if not title or not company or not dates:
        return f"Role information incomplete (title={bool(title)}, company={bool(company)}, dates={bool(dates)})"
    
    return f"{title} @ {company} ({dates})"


SCRUM_KEYWORDS = {"scrum", "agile", "csm", "cspo", "certified scrum", "sprint planning"}


def jd_requires_scrum(jd_text):
    """Return True if JD contains Scrum/Agile certification signals."""
    lower = jd_text.lower()
    return any(kw in lower for kw in SCRUM_KEYWORDS)


BUILDER_VERBS = ["Built", "Engineered", "Automated", "Deployed", "Architected"]
CORPORATE_FOG = [
    # Existing
    "cross-functional", "stakeholder management", "alignment", "synergies",
    "best practices", "impactful", "strategic leader", "proven track record",
    "dynamic environments", "holistic", "fast-paced", "landscape",
    # Gemini-specific additions
    "accelerate", "prioritize", "ensure", "enable", "drive",
    "systemic breakdowns", "operational trust", "measurable business outcomes",
    "workflow simplification", "reduce ambiguity", "deployment", "engagement",
    "scalability", "retention",
]


def lint_generated_text(text: str) -> list[str]:
    """Static lint: flag repeated builder verbs and corporate fog words."""
    flags = []
    for phrase in BUILDER_VERBS:
        count = text.count(phrase)
        if count >= 3:
            flags.append(f"Builder-heavy: '{phrase}' appears {count} times")
    for phrase in CORPORATE_FOG:
        if phrase.lower() in text.lower():
            flags.append(f"Corporate fog: '{phrase}'")
    return flags


GEMINI_BANNED_VERBS = ["accelerate", "prioritize", "ensure", "enable", "drive", "deployment", "engagement"]
ABSTRACT_NOUNS = ["systemic breakdowns", "operational trust", "measurable business outcomes", "workflow simplification", "reduce ambiguity"]


def lint_quick_take(mission_text: str) -> list[str]:
    """Lint Quick Take for Gemini-specific corporate patterns."""
    import re
    flags = []
    lower = mission_text.lower()
    
    # Check for Gemini banned verbs
    for verb in GEMINI_BANNED_VERBS:
        if verb in lower:
            flags.append(f"Gemini fog: '{verb}'")
    
    # Check for abstract nouns
    for noun in ABSTRACT_NOUNS:
        if noun in lower:
            flags.append(f"Abstract language: '{noun}'")
    
    # Check for company names (CamelCase or ALLCAPS words)
    potential_names = re.findall(r'\b[A-Z][a-z]+[A-Z][a-z]+\b|\b[A-Z]{2,}\b', mission_text)
    # Filter out common role titles
    common_titles = {"PM", "AI", "ML", "API", "UI", "UX", "CEO", "CTO", "VP"}
    potential_names = [n for n in potential_names if n not in common_titles]
    if potential_names:
        flags.append(f"Possible company name: {', '.join(potential_names)}")
    
    return flags


def extract_projects_block(master_context):
    """Extract the Additional Projects section from master_context."""
    lines = master_context.split("\n")
    in_section = False
    result = []
    for line in lines:
        if "### Additional Projects" in line:
            in_section = True
        elif in_section and line.startswith("## "):
            break
        if in_section:
            result.append(line)
    return "\n".join(result)


def extract_jd_paragraphs(jd_text):
    """Extract first 1-2 paragraphs (non-bullet text) from a JD for mission statement."""
    paragraphs = []
    for para in jd_text.split("\n\n"):
        stripped = para.strip()
        if not stripped:
            continue
        if stripped.startswith(("-", "•", "*", "·")):
            continue
        if re.match(r"^\d+\.", stripped):
            continue
        paragraphs.append(stripped)
        if len(paragraphs) >= 2:
            break
    return "\n\n".join(paragraphs) if paragraphs else jd_text[:800]


def scrape_url(url):
    """Scrape JD from URL. Returns dict with ok, text, error."""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return {"ok": False, "text": "", "error": f"HTTP {response.status_code}"}
        soup = BeautifulSoup(response.content, "html.parser")
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text(separator=" ", strip=True)
        if len(text) < MIN_JD_LENGTH:
            return {"ok": False, "text": text, "error": f"Scraped text too short ({len(text)} chars)"}
        return {"ok": True, "text": text, "error": ""}
    except Exception as e:
        return {"ok": False, "text": "", "error": str(e)}


def append_to_history(date, company, role, track, jd_source, tokens_used, cost_usd):
    """Append structured entry to data/history.md under ## Auto log section."""
    entry = f"""
### {company} - {role}
- **Date**: {date}
- **Track**: {track}
- **JD source**: {jd_source}
- **Tokens used**: {tokens_used:,}
- **Approx cost**: ${cost_usd:.3f}
- **Outputs**: Resume, Cover Letter
"""
    if HISTORY_PATH.exists():
        content = HISTORY_PATH.read_text(encoding="utf-8")
    else:
        content = "# Application History Log\n\n## Auto log\n"

    auto_log_header = "## Auto log"
    if auto_log_header in content:
        content = content.replace(auto_log_header, auto_log_header + "\n" + entry)
    else:
        content += f"\n{auto_log_header}\n{entry}"

    HISTORY_PATH.write_text(content, encoding="utf-8")


def get_provider() -> str:
    """Return 'openai' or 'gemini' from sidebar selection."""
    label = st.session_state.get("llm_provider", PROVIDER_OPTIONS[0])
    return "gemini" if label == "Google Gemini" else "openai"


def update_env_file(updates: dict):
    """Merge API keys into .env without removing unrelated variables."""
    existing = {}
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, _, val = stripped.partition("=")
            existing[key.strip()] = val.strip().strip('"').strip("'")
    existing.update(updates)
    ENV_PATH.write_text(
        "\n".join(f'{k}="{v}"' for k, v in existing.items()) + "\n",
        encoding="utf-8",
    )


def get_api_key() -> str:
    """Resolve API key for the active provider (sidebar override, then env)."""
    provider = get_provider()
    if provider == "gemini":
        return (
            st.session_state.get("sidebar_gemini_key", "").strip()
            or os.environ.get("GEMINI_API_KEY", "").strip()
        )
    return (
        st.session_state.get("sidebar_openai_key", "").strip()
        or os.environ.get("OPENAI_API_KEY", "").strip()
    )


def build_model_overrides() -> dict:
    """Session-selected model IDs for default / profile / pain tiers."""
    provider = get_provider()
    prefix = "gemini" if provider == "gemini" else "openai"
    overrides = {}
    for tier in ("default", "profile", "pain"):
        val = st.session_state.get(f"{prefix}_model_{tier}")
        if val:
            overrides[tier] = (
                normalize_gemini_model_id(val) if provider == "gemini" else val
            )
    return overrides


def init_provider_defaults():
    """Seed model pickers from env defaults once per session."""
    for tier, val in OPENAI_DEFAULTS.items():
        key = f"openai_model_{tier}"
        if key not in st.session_state and tier != "pain_fallback":
            st.session_state[key] = val
    for tier, val in GEMINI_DEFAULTS.items():
        key = f"gemini_model_{tier}"
        if key not in st.session_state and tier != "pain_fallback":
            st.session_state[key] = normalize_gemini_model_id(val)
    if "sidebar_openai_key" not in st.session_state:
        st.session_state.sidebar_openai_key = os.environ.get("OPENAI_API_KEY", "")
    if "sidebar_gemini_key" not in st.session_state:
        st.session_state.sidebar_gemini_key = os.environ.get("GEMINI_API_KEY", "")


def build_pdf_breaks_from_session():
    """Read PDF layout controls from sidebar session state."""
    sections = []
    for flag_key, section_key in (
        ("break_before_skills", "skills"),
        ("break_before_experience", "experience"),
        ("break_before_projects", "projects"),
        ("break_before_credentials", "credentials"),
    ):
        if st.session_state.get(flag_key):
            sections.append(section_key)
    role_idx = int(st.session_state.get("break_before_role_index", 0) or 0)
    return normalize_pdf_breaks({
        "before_sections": sections,
        "before_role_index": role_idx if role_idx > 0 else None,
    })


def rerender_resume_files(
    res,
    mission_text=None,
    skills_text=None,
    experience_blocks=None,
    projects_text=None,
    pdf_breaks=None,
):
    """Rebuild DOCX/PDF from stored sections without full LLM regen."""
    sections = {
        "mission": mission_text if mission_text is not None else res["mission"],
        "skills": skills_text if skills_text is not None else res["skills"],
        "experience": experience_blocks if experience_blocks is not None else res["experience_blocks"],
        "projects": projects_text if projects_text is not None else res.get("projects", ""),
    }
    breaks = pdf_breaks if pdf_breaks is not None else res.get("pdf_breaks") or normalize_pdf_breaks()
    loc = LOCATION_OPTIONS.get(st.session_state.get("location_label", ""), "Sunnyvale, CA")
    include_scrum = jd_requires_scrum(st.session_state.get("jd_text", ""))
    create_formatted_doc(
        res["doc_path"], sections, location=loc, include_scrum=include_scrum, pdf_breaks=breaks
    )
    create_formatted_pdf(
        res["pdf_path"], sections, location=loc, include_scrum=include_scrum, pdf_breaks=breaks
    )


def check_keyword_coverage(extracted_keywords_text, combined_output):
    """Check which extracted JD duties/requirements appear in the generated output.

    Returns (found, missing, coverage_pct) where found/missing are lists of term strings.
    Uses full-line matching first, then falls back to bigram matching.
    """
    if not extracted_keywords_text:
        return [], [], 0.0

    terms = []
    for line in extracted_keywords_text.split("\n"):
        match = re.match(r"^\d+\.\s+(.+)", line.strip())
        if match:
            terms.append(match.group(1).strip())

    if not terms:
        return [], [], 0.0

    output_lower = combined_output.lower()
    found, missing = [], []
    for term in terms:
        words = term.lower().split()
        # Try full term, then slide a 3-word window, then bigrams
        if term.lower() in output_lower:
            found.append(term)
        elif any(
            " ".join(words[i:i+3]) in output_lower
            for i in range(len(words) - 2)
        ):
            found.append(term)
        elif any(
            f"{words[i]} {words[i+1]}" in output_lower
            for i in range(len(words) - 1)
        ):
            found.append(term)
        else:
            missing.append(term)

    coverage = len(found) / len(terms) if terms else 0.0
    return found, missing, coverage


def estimate_cost(usage_list, provider: str = "openai"):
    """Estimate USD cost from list of usage dicts (approximate by provider)."""
    total_input = sum(u.get("prompt_tokens", 0) for u in usage_list)
    total_output = sum(u.get("completion_tokens", 0) for u in usage_list)
    total_tokens = total_input + total_output
    if provider == "gemini":
        cost = (total_input / 1000 * GEMINI_INPUT_PRICE_PER_1K) + (
            total_output / 1000 * GEMINI_OUTPUT_PRICE_PER_1K
        )
    else:
        cost = (total_input / 1000 * OPENAI_INPUT_PRICE_PER_1K) + (
            total_output / 1000 * OPENAI_OUTPUT_PRICE_PER_1K
        )
    return total_tokens, cost


def inject_sf_professional_theme():
    """Modern SF-style professional theme with clean typography and neutral palette."""
    st.markdown(
        """
<style>
/* Load fonts: Inter for body, Lora for headings */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Lora:ital,wght@0,400..700;1,400..700&display=swap');

/* Root variables */
:root {
    --sf-primary: #007AFF;
    --sf-bg: #F9FAFB;
    --sf-card: #FFFFFF;
    --sf-border: #E5E7EB;
    --sf-text: #111827;
    --sf-text-muted: #6B7280;
}

/* Main app background */
.stApp {
    background-color: var(--sf-bg);
}

/* Typography & Readability */
section[data-testid="stMain"], .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: var(--sf-text);
    line-height: 1.6;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Lora', serif !important;
    color: var(--sf-text) !important;
    letter-spacing: -0.01em !important;
    font-weight: 600 !important;
}

section[data-testid="stMain"] h1 {
    font-size: 2.25rem !important;
    margin-bottom: 0.5rem !important;
}

section[data-testid="stMain"] h2 {
    font-size: 1.5rem !important;
    margin-top: 1.5rem !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #F3F4F6 !important;
    border-right: 1px solid var(--sf-border);
}

/* Modern Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: transparent;
}

.stTabs [data-baseweb="tab"] {
    font-weight: 500;
    border-radius: 8px;
    padding: 8px 16px;
    color: var(--sf-text-muted);
}

.stTabs [aria-selected="true"] {
    background-color: var(--sf-card) !important;
    color: var(--sf-primary) !important;
    border: 1px solid var(--sf-border) !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
}

/* Improved Inputs */
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
    border-radius: 8px !important;
    border: 1px solid var(--sf-border) !important;
}

/* Output Preview Readability */
div[data-testid="stText"] pre {
    font-family: 'SF Mono', 'Inter', sans-serif !important;
    font-size: 15px !important;
    line-height: 1.6 !important;
    background-color: var(--sf-card) !important;
    padding: 20px !important;
    border-radius: 12px !important;
    border: 1px solid var(--sf-border) !important;
    white-space: pre-wrap !important;
    color: var(--sf-text) !important;
}

/* ATS Card */
.ats-card {
    background: white;
    padding: 24px;
    border-radius: 12px;
    border: 1px solid var(--sf-border);
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

/* Button Refinement */
.stButton button {
    border-radius: 8px !important;
    font-weight: 600 !important;
}
</style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Streamlit App
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Project Thema", layout="wide", page_icon="📄")
inject_sf_professional_theme()
st.title("Project Thema")
st.caption("AI-powered resume and cover letter generator with ATS optimization")

# Sidebar
st.sidebar.title("⚙️ Configuration")
st.sidebar.divider()

init_provider_defaults()

st.sidebar.subheader("LLM Provider")
st.sidebar.radio(
    "Provider",
    PROVIDER_OPTIONS,
    key="llm_provider",
    help="One provider per generation run (OpenAI or Google AI Studio)",
)

_active_provider = get_provider()
st.sidebar.subheader("API Key")
if _active_provider == "gemini":
    st.sidebar.text_input(
        "Gemini API Key",
        type="password",
        key="sidebar_gemini_key",
        help="From aistudio.google.com — saved to GEMINI_API_KEY in .env",
    )
    _env_var = "GEMINI_API_KEY"
else:
    st.sidebar.text_input(
        "OpenAI API Key",
        type="password",
        key="sidebar_openai_key",
        help="Saved to OPENAI_API_KEY in .env",
    )
    _env_var = "OPENAI_API_KEY"

if st.sidebar.button("Save Key to .env", key="save_key_btn", use_container_width=True):
    key_to_save = get_api_key()
    if key_to_save:
        update_env_file({_env_var: key_to_save})
        os.environ[_env_var] = key_to_save
        st.sidebar.success("Key saved to .env")
    else:
        st.sidebar.warning("No key to save")

_key_ok = bool(get_api_key())
st.sidebar.caption(f"Status: {'Set' if _key_ok else 'Not set'} ({_active_provider})")
if _active_provider == "gemini":
    st.sidebar.caption(
        "Gemini: profile defaults to **2.5 Flash** (thinking off, higher token caps). "
        "Avoid **2.5 Pro** on free tier (quota / empty output). Use OpenAI for highest quality."
    )

with st.sidebar.expander("Advanced: models", expanded=False):
    _prefix = "gemini" if _active_provider == "gemini" else "openai"
    _label = "Gemini" if _active_provider == "gemini" else "OpenAI"
    st.caption(f"{_label} model IDs per pipeline tier")
    st.selectbox(
        "Bulk sections (keywords, narrative, skills, bullets, cover)",
        model_choices(_active_provider, "default"),
        key=f"{_prefix}_model_default",
    )
    st.selectbox(
        "Profile + lint (The Quick Take)",
        model_choices(_active_provider, "profile"),
        key=f"{_prefix}_model_profile",
    )
    st.selectbox(
        "Pain + profile angle",
        model_choices(_active_provider, "pain"),
        key=f"{_prefix}_model_pain",
    )

st.sidebar.divider()
st.sidebar.subheader("📍 Location")
selected_location_label = st.sidebar.radio(
    "I am applying from:",
    list(LOCATION_OPTIONS.keys()),
    key="location_label",
)
candidate_location = LOCATION_OPTIONS[selected_location_label]

st.sidebar.divider()
st.sidebar.subheader("PDF layout")
st.sidebar.caption("Optional page breaks (letter PDF, typically 1-2 pages)")
st.sidebar.checkbox("Break before How I Work", key="break_before_skills")
st.sidebar.checkbox("Break before The Work", key="break_before_experience")
st.sidebar.checkbox("Break before Side Builds", key="break_before_projects")
st.sidebar.checkbox("Break before Credentials", key="break_before_credentials")
st.sidebar.number_input(
    "Break before role # (0 = none)",
    min_value=0,
    max_value=8,
    value=0,
    step=1,
    key="break_before_role_index",
    help="1 = first role in The Work. Also supported in experience text: "
    f"a line containing only `{PAGE_BREAK_MARKER}`.",
)

st.sidebar.divider()
st.sidebar.subheader("⚡ Cost Controls")
st.sidebar.caption("Skip expensive steps to reduce API cost")
st.sidebar.checkbox("Skip quality review", key="skip_quality_review")
st.sidebar.checkbox("Skip cover letter", key="skip_cover_letter")
st.sidebar.checkbox("Skip custom Q&A", key="skip_custom_qa")

# Load master context once
if "master_context" not in st.session_state:
    st.session_state.master_context = load_master_context()

if not st.session_state.master_context:
    st.error(f"Master context not found at {MASTER_CONTEXT_PATH}. Please create it first.")
    st.stop()

# ---------------------------------------------------------------------------
# TABS
# ---------------------------------------------------------------------------
tab_job, tab_questions, tab_generate = st.tabs(["📋 Job Details", "❓ Application Questions", "🚀 Generate & Output"])

# --- TAB 1: Job Details ---
with tab_job:
    st.markdown("### Company & Role Information")
    col1, col2 = st.columns(2)
    with col1:
        company_name = st.text_input("Company Name", key="company_name", placeholder="e.g., Acme Corp")
        target_role = st.text_input("Target Role Title", key="target_role", placeholder="e.g., Senior Product Manager")
    with col2:
        selected_track = st.selectbox("Target Track", TRACK_OPTIONS, key="selected_track")
        selected_voice = st.selectbox("Resume Voice", VOICE_OPTIONS, key="selected_voice")
        jd_url = st.text_input("JD URL (optional)", key="jd_url", placeholder="https://...")

    st.markdown("### Job Description")
    jd_text = st.text_area("Job Description (paste full JD)", height=300, key="jd_text", placeholder="Paste the complete job description here...")

    if jd_url and not jd_text:
        if st.button("🔍 Scrape JD from URL", use_container_width=True):
            result = scrape_url(jd_url)
            if result["ok"]:
                st.session_state.jd_text = result["text"]
                st.success(f"✅ Scraped {len(result['text']):,} chars from URL")
                st.rerun()
            else:
                st.error(f"❌ Scrape failed: {result['error']}")
    
    # Role Selection UI
    st.divider()
    st.markdown("### 📋 Role Selection")
    st.caption("Choose how each role appears on your resume")
    
    # Extract all roles from master context
    all_role_blocks = extract_role_blocks(st.session_state.master_context)
    
    # Initialize role selections if not present
    if "role_selections" not in st.session_state:
        st.session_state.role_selections = {key: "skip" for key in all_role_blocks.keys()}
    
    # LLM Suggestion button
    col_suggest, col_fill = st.columns(2)
    with col_suggest:
        if st.button("🤖 Run LLM Suggestion", use_container_width=True, help="Let AI select most relevant roles"):
            if jd_text:
                with st.spinner("Analyzing JD for relevant roles..."):
                    try:
                        api_key = get_api_key()
                        provider = get_provider()
                        llm = get_llm_client(provider, api_key, build_model_overrides())
                        role_selection_text, _ = select_relevant_roles(llm, jd_text, st.session_state.master_context)
                        
                        # Reset all to skip
                        for key in st.session_state.role_selections:
                            st.session_state.role_selections[key] = "skip"
                        
                        # Mark LLM-selected as full
                        for line in role_selection_text.split("\n"):
                            line = line.strip()
                            if not line:
                                continue
                            for key in all_role_blocks.keys():
                                if line.lower() in key.lower() or key.lower() in line.lower():
                                    st.session_state.role_selections[key] = "full"
                                    break
                        st.success("✅ LLM suggestions applied")
                        st.rerun()
                    except Exception as e:
                        st.error(f"LLM suggestion failed: {e}")
            else:
                st.warning("Please enter a job description first")
    
    with col_fill:
        if st.button("📝 Fill Timeline (All Condensed)", use_container_width=True, help="Show all roles as condensed"):
            for key in st.session_state.role_selections:
                if st.session_state.role_selections[key] == "skip":
                    st.session_state.role_selections[key] = "condensed"
            st.success("✅ All skipped roles set to condensed")
            st.rerun()
    
    # Display role selection radios
    for role_key in all_role_blocks.keys():
        # Extract short display name
        display_name = role_key.replace("ROLE ", "Role ")
        
        current_selection = st.session_state.role_selections.get(role_key, "skip")
        selection = st.radio(
            display_name,
            options=["full", "condensed", "skip"],
            index=["full", "condensed", "skip"].index(current_selection),
            key=f"role_radio_{role_key}",
            horizontal=True,
            format_func=lambda x: {"full": "✅ Full", "condensed": "📝 Condensed", "skip": "❌ Skip"}[x]
        )
        st.session_state.role_selections[role_key] = selection

# --- TAB 2: Application Questions ---
with tab_questions:
    st.markdown("### Custom Application Questions")
    st.caption("Optional: Add any specific questions from the application portal")
    custom_questions = st.text_area(
        "Application-specific questions (optional)",
        height=200,
        key="custom_questions",
        placeholder="Paste each question on its own line...",
        help="Paste any specific questions from the application portal. Each question on its own line."
    )

# --- TAB 3: Generate & Output ---
with tab_generate:
    # Pre-flight checklist
    st.subheader("Pre-flight Checklist")
    st.caption("Ensure all requirements are met before generating documents")
    
    checks = {
        "API Key": bool(get_api_key()),
        "Company Name": bool(st.session_state.get("company_name", "").strip()),
        "Target Role": bool(st.session_state.get("target_role", "").strip()),
        "Job Description": len(st.session_state.get("jd_text", "")) >= MIN_JD_LENGTH,
        "Master Context": bool(st.session_state.master_context),
    }

    cols = st.columns(len(checks))
    all_ready = True
    for i, (label, ok) in enumerate(checks.items()):
        with cols[i]:
            icon = "✅" if ok else "⚠️"
            status_color = "green" if ok else "orange"
            st.markdown(f"<div style='text-align: center; padding: 12px; background-color: {'rgba(52, 199, 89, 0.05)' if ok else 'rgba(255, 149, 0, 0.05)'}; border-radius: 10px; border: 1px solid {'#34C759' if ok else '#FF9500'};'><div style='font-size: 1.5rem;'>{icon}</div><div style='font-weight: 600; font-size: 0.85rem; margin-top: 4px; color: #374151;'>{label}</div></div>", unsafe_allow_html=True)
            if not ok:
                all_ready = False

    st.divider()

    if st.button("🚀 Generate Documents", disabled=not all_ready, type="primary", use_container_width=True):
        api_key = get_api_key()
        provider = get_provider()
        company = st.session_state.company_name.strip()
        role = st.session_state.target_role.strip()
        track = st.session_state.selected_track
        voice = st.session_state.selected_voice
        jd = st.session_state.jd_text.strip()
        questions = st.session_state.get("custom_questions", "").strip()
        master_ctx = st.session_state.master_context

        usage_log = []

        try:
            with st.status("Generating resume...", expanded=True) as status:
                llm = get_llm_client(provider, api_key, build_model_overrides())

                # Step 1: Extract JD keywords (ATS-KW)
                st.write("Extracting JD duties and requirements...")
                extracted_keywords, usage = extract_jd_keywords(llm, jd)
                usage_log.append(usage)

                # Parse duties section for skills statements
                jd_duties = ""
                if "DUTIES:" in extracted_keywords:
                    duties_part = extracted_keywords.split("REQUIREMENTS:")[0]
                    jd_duties = duties_part.replace("DUTIES:", "").strip()

                # Step 2: Use role selections from UI
                st.write("Processing role selections...")
                all_role_blocks = extract_role_blocks(master_ctx)
                
                # Get user's role selections (full or condensed)
                role_selections = st.session_state.get("role_selections", {})
                
                # Validate at least one role selected
                has_selection = any(sel in ["full", "condensed"] for sel in role_selections.values())
                if not has_selection:
                    st.error("Please select at least one role (Full or Condensed)")
                    st.stop()
                
                # Collect roles for processing (both full and condensed)
                selected_roles = []
                for key, block in all_role_blocks.items():
                    selection = role_selections.get(key, "skip")
                    if selection in ["full", "condensed"]:
                        selected_roles.append((key, block, selection))
                
                # Sort roles in reverse-chronological order (ROLE 1 = newest)
                def _role_sort_key(role_tuple):
                    m = re.search(r'ROLE\s+(\d+)', role_tuple[0], re.IGNORECASE)
                    return int(m.group(1)) if m else 99
                selected_roles.sort(key=_role_sort_key)

                # Step 3: Narrative brief
                st.write("Synthesizing narrative brief...")
                narrative_brief, usage = generate_narrative_brief(
                    llm, jd, master_ctx, role, company, track, voice=voice
                )
                usage_log.append(usage)

                # Step 3b: JD pain analysis (feeds profile)
                st.write("Analyzing JD pain points...")
                jd_pain, usage = extract_jd_pain_point(llm, jd, role, jd_duties=jd_duties)
                usage_log.append(usage)

                # Step 3c: Profile angle (WHY framing)
                st.write("Building profile angle...")
                profile_angle, usage = generate_profile_angle(
                    llm, jd_pain, narrative_brief, role, master_context=master_ctx
                )
                usage_log.append(usage)

                # Step 4: Mission statement / profile (with optional WHY lint)
                st.write("Generating mission statement...")
                jd_paragraphs = extract_jd_paragraphs(jd)
                mission, profile_usage = generate_profile_with_lint(
                    llm,
                    jd_paragraphs,
                    role,
                    company,
                    track,
                    voice=voice,
                    narrative_brief=narrative_brief,
                    jd_pain=jd_pain,
                    profile_angle=profile_angle,
                    master_context=master_ctx,
                    run_lint=True,
                )
                if profile_usage:
                    usage_log.extend(
                        profile_usage
                        if isinstance(profile_usage, list)
                        else [profile_usage]
                    )

                if len(selected_roles) >= 3:
                    st.warning(
                        "Dense resume (3+ roles) — letter PDF is typically 2 pages. "
                        "Consider fewer roles for cleaner layout."
                    )

                # Step 5: Skills statements (use extracted duties if available)
                st.write("Generating skills statements...")
                skills_input = jd_duties if jd_duties else jd[:3000]
                skills, usage = generate_skills_statements(llm, skills_input, master_ctx, role, track, voice=voice, narrative_brief=narrative_brief)
                usage_log.append(usage)

                # Step 6: Experience bullets (per role) - handle full vs condensed
                full_count = sum(1 for _, _, sel in selected_roles if sel == "full")
                condensed_count = sum(1 for _, _, sel in selected_roles if sel == "condensed")
                st.write(f"Generating experience: {full_count} full roles, {condensed_count} condensed...")
                
                experience_blocks = []
                all_coaching_notes = []
                for role_name, role_block, selection in selected_roles:
                    if selection == "full":
                        # Generate full bullets
                        bullets, usage = generate_experience_bullets(llm, role_block, jd, track, voice=voice, narrative_brief=narrative_brief)
                        usage_log.append(usage)
                        experience_blocks.append(bullets)
                        notes = extract_coaching_notes(bullets)
                        if notes:
                            all_coaching_notes.append(f"### {role_name}\n{notes}")
                    elif selection == "condensed":
                        # Generate condensed single-line entry
                        condensed_line = extract_condensed_role_line(role_block)
                        experience_blocks.append(condensed_line)

                # Collect coaching notes from skills too
                skills_notes = extract_coaching_notes(skills)
                if skills_notes:
                    all_coaching_notes.insert(0, f"### Skills\n{skills_notes}")

                # Step 6.5: Personal Projects
                st.write("Generating projects section...")
                projects_block = extract_projects_block(master_ctx)
                projects, usage = generate_personal_projects(llm, projects_block, jd, track, voice=voice, narrative_brief=narrative_brief)
                usage_log.append(usage)

                # Step 6.75: Quality review (punchiness + PM signal + builder-heavy risk)
                quality_review = ""
                if not st.session_state.get("skip_quality_review"):
                    st.write("Running punchiness review...")
                    quality_review, usage = review_resume_quality(
                        llm,
                        jd,
                        jd_pain,
                        profile_angle,
                        narrative_brief,
                        mission,
                        skills,
                        experience_blocks,
                        projects,
                    )
                    usage_log.append(usage)

                # Step 7: Cover letter
                cover_letter = ""
                if not st.session_state.get("skip_cover_letter"):
                    st.write("Generating cover letter...")
                    cover_letter, usage = generate_cover_letter(llm, jd, master_ctx, role, company, track, voice=voice, narrative_brief=narrative_brief)
                    usage_log.append(usage)

                # Step 8: Custom Q&A
                custom_answers = ""
                if questions and not st.session_state.get("skip_custom_qa"):
                    st.write("Answering application questions...")
                    custom_answers, usage = answer_custom_questions(llm, questions, master_ctx, jd)
                    usage_log.append(usage)

                # Step 9: Assemble DOCX and PDF
                st.write("Assembling resume documents...")
                include_scrum = jd_requires_scrum(jd)
                resume_sections = {
                    "mission": mission,
                    "skills": skills,
                    "experience": experience_blocks,
                    "projects": projects,
                }
                doc_filename = f"Application_{company.replace(' ', '_')}_{datetime.date.today().isoformat()}.docx"
                pdf_breaks = build_pdf_breaks_from_session()
                doc_path = str(OUTPUT_DIR / doc_filename)
                create_formatted_doc(
                    doc_path,
                    resume_sections,
                    location=candidate_location,
                    include_scrum=include_scrum,
                    pdf_breaks=pdf_breaks,
                )

                pdf_filename = f"Application_{company.replace(' ', '_')}_{datetime.date.today().isoformat()}.pdf"
                pdf_path = str(OUTPUT_DIR / pdf_filename)
                create_formatted_pdf(
                    pdf_path,
                    resume_sections,
                    location=candidate_location,
                    include_scrum=include_scrum,
                    pdf_breaks=pdf_breaks,
                )

                # Step 10: Keyword coverage check (ATS-COV)
                combined_output = " ".join([
                    mission, skills,
                    " ".join(experience_blocks),
                    cover_letter
                ])
                kw_found, kw_missing, kw_coverage = check_keyword_coverage(
                    extracted_keywords, combined_output
                )

                # Step 11: Cost summary
                total_tokens, total_cost = estimate_cost(usage_log, provider=provider)

                # Step 12: Log to history
                jd_source = st.session_state.get("jd_url", "") or "Pasted Text"
                append_to_history(
                    datetime.date.today().isoformat(),
                    company, role, track, jd_source,
                    total_tokens, total_cost
                )

                status.update(label="Generation complete!", state="complete", expanded=False)

            st.session_state.gen_results = {
                "provider": provider,
                "total_tokens": total_tokens,
                "total_cost": total_cost,
                "kw_coverage": kw_coverage,
                "kw_found": kw_found,
                "kw_missing": kw_missing,
                "extracted_keywords": extracted_keywords,
                "narrative_brief": narrative_brief,
                "jd_pain": jd_pain,
                "profile_angle": profile_angle,
                "pdf_breaks": pdf_breaks,
                "doc_path": doc_path,
                "doc_filename": doc_filename,
                "pdf_path": pdf_path,
                "pdf_filename": pdf_filename,
                "mission": mission,
                "skills": skills,
                "experience_blocks": experience_blocks,
                "projects": projects,
                "jd_duties": jd_duties,
                "selected_roles": selected_roles,
                "projects_block": projects_block,
                "all_coaching_notes": all_coaching_notes,
                "cover_letter": cover_letter,
                "custom_answers": custom_answers,
                "quality_review": quality_review,
                "usage_log": usage_log
            }

        except LLMResponseError as e:
            st.error(f"Generation failed: {e}")
            if e.model:
                st.caption(f"Model: `{e.model}`" + (f" · finish: `{e.finish_reason}`" if e.finish_reason else ""))
            st.caption(
                "For Gemini: set **Profile** to `gemini-2.5-flash`, confirm API quota at "
                "https://aistudio.google.com , or switch provider to OpenAI."
            )
        except Exception as e:
            st.error(f"Generation failed: {str(e)}")
            st.caption("Check your API key and network connection. If the issue persists, try again.")
            with st.expander("Error details"):
                import traceback
                st.code(traceback.format_exc())

    if "gen_results" in st.session_state:
        res = st.session_state.gen_results

        # Display results
        _prov = res.get("provider", "openai")
        _cost_note = " (Gemini Flash estimate; Pro profile steps may cost more)" if _prov == "gemini" else ""
        st.success(
            f"Generation complete! {res['total_tokens']:,} tokens used "
            f"(~${res['total_cost']:.3f}{_cost_note}) — {_prov}"
        )

        # ATS Keyword Coverage Report
        coverage_pct = int(res['kw_coverage'] * 100)
        coverage_color = "green" if coverage_pct >= 80 else ("orange" if coverage_pct >= 60 else "red")
        
        st.markdown(f"""
        <div class="ats-card" style='background: linear-gradient(135deg, {'rgba(52, 199, 89, 0.05)' if coverage_pct >= 80 else ('rgba(255, 149, 0, 0.05)' if coverage_pct >= 60 else 'rgba(255, 59, 48, 0.05)')} 0%, white 100%); 
                    border-color: {'#34C759' if coverage_pct >= 80 else ('#FF9500' if coverage_pct >= 60 else '#FF3B30')};'>
            <h3 style='margin: 0 0 8px 0;'>ATS Keyword Coverage</h3>
            <div style='font-size: 3.5rem; font-weight: 700; color: {'#34C759' if coverage_pct >= 80 else ('#FF9500' if coverage_pct >= 60 else '#FF3B30')}; letter-spacing: -0.05em;'>{coverage_pct}%</div>
            <p style='margin: 8px 0 0 0; color: #6B7280; font-weight: 500;'>
                {'Excellent coverage' if coverage_pct >= 80 else ('Good coverage' if coverage_pct >= 60 else 'Needs improvement')} — 
                {len(res['kw_found'])} of {len(res['kw_found']) + len(res['kw_missing'])} keywords found
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col_found, col_missing = st.columns(2)
        with col_found:
            st.markdown("**✅ Found Keywords**")
            if res['kw_found']:
                for t in res['kw_found']:
                    st.markdown(f"<div style='padding: 6px 12px; margin: 4px 0; background-color: rgba(52, 199, 89, 0.1); border-radius: 6px; font-size: 0.9rem;'>• {t}</div>", unsafe_allow_html=True)
            else:
                st.caption("No keywords extracted")
        with col_missing:
            st.markdown("**⚠️ Missing Keywords**")
            if res['kw_missing']:
                for t in res['kw_missing']:
                    st.markdown(f"<div style='padding: 6px 12px; margin: 4px 0; background-color: rgba(255, 149, 0, 0.1); border-radius: 6px; font-size: 0.9rem;'>• {t}</div>", unsafe_allow_html=True)
            else:
                st.caption("All keywords covered!")

        with st.expander("JD Keywords Extracted", expanded=False):
            st.text(res['extracted_keywords'])

        # Static lint warning chips
        combined_text = "\n".join([res.get("mission", ""), res.get("skills", ""), "\n".join(res.get("experience_blocks", []))])
        lint_flags = lint_generated_text(combined_text)
        if lint_flags:
            st.markdown("**⚠️ Language Flags**")
            for flag in lint_flags:
                st.markdown(
                    f"<div style='display:inline-block; padding: 4px 10px; margin: 2px 4px 2px 0; background-color: rgba(255, 149, 0, 0.12); color: #B45309; border-radius: 12px; font-size: 0.82rem; font-weight: 500;'>🔸 {flag}</div>",
                    unsafe_allow_html=True,
                )

        # Strategy Panel (combined into tabs)
        if any([res.get('narrative_brief'), res.get('jd_pain'), res.get('profile_angle')]):
            st.markdown("**Strategy Panel**")
            strat_tabs = st.tabs(["Narrative Brief", "JD Pain", "Profile Angle"])
            with strat_tabs[0]:
                if res.get('narrative_brief'):
                    st.caption("Strategic positioning that guided all resume sections.")
                    st.text(res['narrative_brief'])
                else:
                    st.caption("No narrative brief generated.")
            with strat_tabs[1]:
                if res.get('jd_pain'):
                    st.caption("Reasoning step that frames The Quick Take.")
                    st.text(res['jd_pain'])
                else:
                    st.caption("No JD pain analysis generated.")
            with strat_tabs[2]:
                if res.get('profile_angle'):
                    st.caption("Situation, thesis, and forbidden resume nouns.")
                    st.text(res['profile_angle'])
                else:
                    st.caption("No profile angle generated.")

        # Punchiness Review
        if res.get('quality_review'):
            with st.expander("🧨 Punchiness Review", expanded=True):
                st.caption("Editorial critique before you download. Fix flagged issues first.")
                st.text(res['quality_review'])

        st.divider()

        # Download buttons
        st.subheader("📥 Download Documents")
        col_doc, col_pdf = st.columns(2)
        with col_doc:
            with open(res['doc_path'], "rb") as f:
                st.download_button(
                    label="📄 Download Resume (DOCX)",
                    data=f,
                    file_name=res['doc_filename'],
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
        with col_pdf:
            with open(res['pdf_path'], "rb") as f:
                st.download_button(
                    label="📑 Download Resume (PDF)",
                    data=f,
                    file_name=res['pdf_filename'],
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )

        # Previews
        st.divider()
        st.subheader("📋 Document Preview")

        with st.expander("✨ Quick Take", expanded=True):
            edited_mission = st.text_area(
                "Edit profile (tagline on line 1, then three sentences)",
                value=res["mission"],
                height=160,
                key="profile_edit_area",
            )
            
            # Word counter for paragraph
            lines = edited_mission.split("\n")
            paragraph = "\n".join(lines[1:]) if len(lines) > 1 else ""
            word_count = len(paragraph.split()) if paragraph.strip() else 0
            color = "green" if word_count <= 60 else "orange" if word_count <= 75 else "red"
            st.caption(f"Paragraph: <span style='color: {color}'>{word_count} words</span> (target: ≤60)", unsafe_allow_html=True)
            
            col_apply, col_regen = st.columns(2)
            with col_apply:
                if st.button("Apply profile edit to DOCX/PDF", use_container_width=True):
                    try:
                        rerender_resume_files(res, mission_text=edited_mission)
                        st.session_state.gen_results["mission"] = edited_mission
                        st.success("Documents updated with your profile text.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Update failed: {e}")
            with col_regen:
                regen_clicked = st.button("↻ Regenerate Profile Only", use_container_width=True)
            
            # Quick Take lint warnings
            qt_flags = lint_quick_take(res["mission"])
            if qt_flags:
                st.caption("⚠️ Quick Take Issues:")
                for flag in qt_flags:
                    st.markdown(f"<span style='color: #FF9500; font-size: 0.85rem;'>• {flag}</span>", unsafe_allow_html=True)

        if regen_clicked:
            api_key = get_api_key()
            provider = get_provider()
            try:
                with st.spinner("Regenerating profile..."):
                    _llm = get_llm_client(provider, api_key, build_model_overrides())
                    _jd = st.session_state.get("jd_text", "")
                    _role = st.session_state.get("target_role", "")
                    _company = st.session_state.get("company_name", "")
                    _track = st.session_state.get("selected_track", "")
                    _voice = st.session_state.get("selected_voice", "")
                    _narrative = res.get("narrative_brief", "")
                    _master = st.session_state.master_context
                    _jd_paragraphs = extract_jd_paragraphs(_jd)
                    old_mission = res["mission"]
                    _angle = res.get("profile_angle", "")
                    if not _angle:
                        _angle, _ = generate_profile_angle(
                            _llm,
                            res.get("jd_pain", ""),
                            _narrative,
                            _role,
                            master_context=_master,
                        )
                    new_mission, _ = generate_profile_with_lint(
                        _llm,
                        _jd_paragraphs,
                        _role,
                        _company,
                        _track,
                        voice=_voice,
                        narrative_brief=_narrative,
                        jd_pain=res.get("jd_pain", ""),
                        profile_angle=_angle,
                        master_context=_master,
                        run_lint=True,
                    )
                    rerender_resume_files(res, mission_text=new_mission)
                    st.session_state.gen_results["mission"] = new_mission
                    st.session_state.gen_results["regen_old_mission"] = old_mission
                st.rerun()
            except Exception as e:
                st.error(f"Regeneration failed: {e}")

        if st.button("↻ Re-export DOCX/PDF with current PDF layout", use_container_width=False):
            try:
                breaks = build_pdf_breaks_from_session()
                rerender_resume_files(res, pdf_breaks=breaks)
                st.session_state.gen_results["pdf_breaks"] = breaks
                st.success("Re-exported with sidebar PDF layout settings.")
                st.rerun()
            except Exception as e:
                st.error(f"Re-export failed: {e}")

        if res.get("regen_old_mission"):
            st.caption("Profile comparison - previous vs regenerated:")
            col_old, col_new = st.columns(2)
            with col_old:
                st.markdown("**Previous**")
                st.text(res["regen_old_mission"])
            with col_new:
                st.markdown("**Regenerated**")
                st.text(res["mission"])

        with st.expander("🎯 Skills Statements"):
            edited_skills = st.text_area("Edit How I Work", value=res["skills"], height=220, key="skills_edit_area")
            if st.button("Apply How I Work edit to DOCX/PDF", use_container_width=True, key="skills_apply_btn"):
                try:
                    rerender_resume_files(res, skills_text=edited_skills)
                    st.session_state.gen_results["skills"] = edited_skills
                    st.success("Documents updated with your skills text.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Update failed: {e}")

        with st.expander(f"💼 Experience ({len(res['experience_blocks'])} roles)"):
            new_experience_blocks = []
            for i, block in enumerate(res['experience_blocks'], 1):
                st.markdown(f"**Role {i}**")
                edited_block = st.text_area(f"Edit Role {i}", value=block, height=260, key=f"role_edit_{i}")
                new_experience_blocks.append(edited_block)
                if i < len(res['experience_blocks']):
                    st.divider()
            if st.button("Apply Experience edits to DOCX/PDF", use_container_width=True, key="exp_apply_btn"):
                try:
                    rerender_resume_files(res, experience_blocks=new_experience_blocks)
                    st.session_state.gen_results["experience_blocks"] = new_experience_blocks
                    st.success("Documents updated with your experience text.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Update failed: {e}")

        if res.get("projects"):
            with st.expander("🔧 Side Builds"):
                edited_projects = st.text_area("Edit Side Builds", value=res["projects"], height=220, key="projects_edit_area")
                if st.button("Apply Side Builds edit to DOCX/PDF", use_container_width=True, key="projects_apply_btn"):
                    try:
                        rerender_resume_files(res, projects_text=edited_projects)
                        st.session_state.gen_results["projects"] = edited_projects
                        st.success("Documents updated with your projects text.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Update failed: {e}")

        if res['all_coaching_notes']:
            with st.expander("💡 Coaching Notes (not in document)", expanded=False):
                st.caption("These are internal review notes stripped from the DOCX. Use them to improve your inputs for the next run.")
                for note_block in res['all_coaching_notes']:
                    st.markdown(note_block)

        # Plain-text copy area
        plain_text = "\n\n".join([
            res.get("mission", ""),
            res.get("skills", ""),
            *res.get("experience_blocks", []),
            res.get("projects", ""),
        ])
        with st.expander("📄 Plain Text (copy-paste)", expanded=False):
            st.caption("Copy this into Google Docs, Notion, or any plain-text field.")
            st.text_area("resume_plain", value=plain_text, height=400, label_visibility="collapsed", key="plain_text_area")

        st.divider()
        st.subheader("✉️ Cover Letter")
        st.caption("Select all and copy to paste into your application.")
        st.text_area(
            label="cover_letter_text",
            value=strip_coaching_notes(res['cover_letter']),
            height=320,
            label_visibility="collapsed",
            key="cover_letter_area"
        )

        if res['custom_answers']:
            st.divider()
            st.subheader("❓ Application Q&A")
            st.caption("Select all and copy to paste into your application.")
            st.text_area(
                label="qa_text",
                value=strip_coaching_notes(res['custom_answers']),
                height=280,
                label_visibility="collapsed",
                key="qa_area"
            )

        # Cost breakdown
        with st.expander("💰 Token Usage & Cost Breakdown"):
            st.markdown(f"""
<div style='background-color: white; padding: 16px; border-radius: 10px; border: 1px solid #E5E7EB; box-shadow: 0 1px 2px rgba(0,0,0,0.05);'>

| Metric | Value |
|--------|-------|
| **Total tokens** | {res['total_tokens']:,} |
| **Approx. cost** | ${res['total_cost']:.3f} |
| **API calls** | {len(res['usage_log'])} |
| **Cost per token** | ${(res['total_cost'] / res['total_tokens']):.6f} |

</div>
""", unsafe_allow_html=True)
