import os
import re
import datetime
from pathlib import Path
import streamlit as st
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from generator import (
    get_openai_client,
    extract_jd_keywords,
    select_relevant_roles,
    generate_mission_statement,
    generate_skills_statements,
    generate_experience_bullets,
    generate_cover_letter,
    answer_custom_questions,
)
from doc_generator import create_formatted_doc, extract_coaching_notes, strip_coaching_notes
from pdf_generator import create_formatted_pdf

# ---------------------------------------------------------------------------
# Path resolution (P0-PATH)
# ---------------------------------------------------------------------------
RES_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = RES_ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)
MASTER_CONTEXT_PATH = RES_ROOT / "master_context.md"
HISTORY_PATH = RES_ROOT / "history.md"
ENV_PATH = RES_ROOT / ".env"

# Load .env file if it exists
load_dotenv(ENV_PATH)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
TRACK_OPTIONS = ["Product/AI", "Pricing/Ops", "Growth", "Logistics/Marketplace", "BizOps", "Chief of Staff"]
LOCATION_OPTIONS = {
    "Sunnyvale, CA (SF / Silicon Valley / Remote USA)": "Sunnyvale, CA",
    "Calgary, AB (Canadian jobs)": "Calgary, AB",
}
MIN_JD_LENGTH = 200
GPT4O_INPUT_PRICE_PER_1K = 0.0025
GPT4O_OUTPUT_PRICE_PER_1K = 0.01


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
    """Append structured entry to history.md under ## Auto log section."""
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


def get_api_key():
    """Resolve API key: env var first, sidebar override second."""
    env_key = os.environ.get("OPENAI_API_KEY", "")
    sidebar_key = st.session_state.get("sidebar_api_key", "")
    return sidebar_key if sidebar_key else env_key


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


def estimate_cost(usage_list):
    """Estimate USD cost from list of usage dicts."""
    total_input = sum(u.get("prompt_tokens", 0) for u in usage_list)
    total_output = sum(u.get("completion_tokens", 0) for u in usage_list)
    total_tokens = total_input + total_output
    cost = (total_input / 1000 * GPT4O_INPUT_PRICE_PER_1K) + (total_output / 1000 * GPT4O_OUTPUT_PRICE_PER_1K)
    return total_tokens, cost


# ---------------------------------------------------------------------------
# Streamlit App
# ---------------------------------------------------------------------------
st.set_page_config(page_title="ResTron — Resume Generator", layout="wide")
st.title("ResTron — Resume & Cover Letter Generator")

# Sidebar
st.sidebar.header("Configuration")
st.sidebar.text_input(
    "OpenAI API Key",
    type="password",
    key="sidebar_api_key",
    help="Saved locally to .env so you only enter it once"
)
if st.sidebar.button("Save Key to .env", key="save_key_btn"):
    key_to_save = st.session_state.get("sidebar_api_key", "").strip()
    if key_to_save:
        ENV_PATH.write_text(f'OPENAI_API_KEY="{key_to_save}"\n', encoding="utf-8")
        os.environ["OPENAI_API_KEY"] = key_to_save
        st.sidebar.success("Key saved to .env")
    else:
        st.sidebar.warning("No key to save")
env_status = "Saved" if os.environ.get("OPENAI_API_KEY") else "Not set"
st.sidebar.caption(f"API Key status: {env_status}")

st.sidebar.divider()
st.sidebar.subheader("Location")
selected_location_label = st.sidebar.radio(
    "I am applying from:",
    list(LOCATION_OPTIONS.keys()),
    key="location_label",
)
candidate_location = LOCATION_OPTIONS[selected_location_label]

# Load master context once
if "master_context" not in st.session_state:
    st.session_state.master_context = load_master_context()

if not st.session_state.master_context:
    st.error(f"Master context not found at {MASTER_CONTEXT_PATH}. Please create it first.")
    st.stop()

# ---------------------------------------------------------------------------
# TABS
# ---------------------------------------------------------------------------
tab_job, tab_questions, tab_generate = st.tabs(["Job Details", "Application Questions", "Generate & Output"])

# --- TAB 1: Job Details ---
with tab_job:
    col1, col2 = st.columns(2)
    with col1:
        company_name = st.text_input("Company Name", key="company_name")
        target_role = st.text_input("Target Role Title", key="target_role")
    with col2:
        selected_track = st.selectbox("Target Track", TRACK_OPTIONS, key="selected_track")
        jd_url = st.text_input("JD URL (optional)", key="jd_url")

    jd_text = st.text_area("Job Description (paste full JD)", height=300, key="jd_text")

    if jd_url and not jd_text:
        if st.button("Scrape JD from URL"):
            result = scrape_url(jd_url)
            if result["ok"]:
                st.session_state.jd_text = result["text"]
                st.success(f"Scraped {len(result['text']):,} chars from URL")
                st.rerun()
            else:
                st.error(f"Scrape failed: {result['error']}")

# --- TAB 2: Application Questions ---
with tab_questions:
    custom_questions = st.text_area(
        "Application-specific questions (optional)",
        height=200,
        key="custom_questions",
        help="Paste any specific questions from the application portal. Each question on its own line."
    )

# --- TAB 3: Generate & Output ---
with tab_generate:
    # Pre-flight checklist
    st.subheader("Pre-flight Checklist")
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
            icon = "✅" if ok else "❌"
            st.markdown(f"{icon} **{label}**")
            if not ok:
                all_ready = False

    st.divider()

    if st.button("Generate Documents", disabled=not all_ready, type="primary"):
        api_key = get_api_key()
        company = st.session_state.company_name.strip()
        role = st.session_state.target_role.strip()
        track = st.session_state.selected_track
        jd = st.session_state.jd_text.strip()
        questions = st.session_state.get("custom_questions", "").strip()
        master_ctx = st.session_state.master_context

        usage_log = []

        try:
            with st.status("Generating resume...", expanded=True) as status:
                client = get_openai_client(api_key)

                # Step 1: Extract JD keywords (ATS-KW)
                st.write("Extracting JD duties and requirements...")
                extracted_keywords, usage = extract_jd_keywords(client, jd)
                usage_log.append(usage)

                # Parse duties section for skills statements
                jd_duties = ""
                if "DUTIES:" in extracted_keywords:
                    duties_part = extracted_keywords.split("REQUIREMENTS:")[0]
                    jd_duties = duties_part.replace("DUTIES:", "").strip()

                # Step 2: Select relevant roles
                st.write("Selecting relevant roles...")
                role_selection_text, usage = select_relevant_roles(client, jd, master_ctx)
                usage_log.append(usage)

                # Parse selected role blocks
                all_role_blocks = extract_role_blocks(master_ctx)
                selected_roles = []
                for line in role_selection_text.split("\n"):
                    line = line.strip()
                    if not line:
                        continue
                    for key, block in all_role_blocks.items():
                        if line.lower() in key.lower() or key.lower() in line.lower():
                            selected_roles.append((key, block))
                            break

                if not selected_roles:
                    selected_roles = list(all_role_blocks.items())[:3]

                # Step 3: Mission statement
                st.write("Generating mission statement...")
                jd_paragraphs = extract_jd_paragraphs(jd)
                mission, usage = generate_mission_statement(client, jd_paragraphs, role, company, track)
                usage_log.append(usage)

                # Step 4: Skills statements (use extracted duties if available)
                st.write("Generating skills statements...")
                skills_input = jd_duties if jd_duties else jd[:3000]
                skills, usage = generate_skills_statements(client, skills_input, master_ctx, role, track)
                usage_log.append(usage)

                # Step 5: Experience bullets (per role)
                st.write(f"Generating experience bullets for {len(selected_roles)} roles...")
                experience_blocks = []
                all_coaching_notes = []
                for role_name, role_block in selected_roles:
                    bullets, usage = generate_experience_bullets(client, role_block, jd, track)
                    usage_log.append(usage)
                    experience_blocks.append(bullets)
                    notes = extract_coaching_notes(bullets)
                    if notes:
                        all_coaching_notes.append(f"### {role_name}\n{notes}")

                # Collect coaching notes from skills too
                skills_notes = extract_coaching_notes(skills)
                if skills_notes:
                    all_coaching_notes.insert(0, f"### Skills\n{skills_notes}")

                # Step 5: Cover letter
                st.write("Generating cover letter...")
                cover_letter, usage = generate_cover_letter(client, jd, master_ctx, role, company, track)
                usage_log.append(usage)

                # Step 6: Custom Q&A
                custom_answers = ""
                if questions:
                    st.write("Answering application questions...")
                    custom_answers, usage = answer_custom_questions(client, questions, master_ctx, jd)
                    usage_log.append(usage)

                # Step 7: Assemble DOCX and PDF
                st.write("Assembling resume documents...")
                resume_sections = {
                    "mission": mission,
                    "skills": skills,
                    "experience": experience_blocks,
                }
                doc_filename = f"Application_{company.replace(' ', '_')}_{datetime.date.today().isoformat()}.docx"
                doc_path = str(OUTPUT_DIR / doc_filename)
                create_formatted_doc(doc_path, resume_sections, location=candidate_location)
                
                pdf_filename = f"Application_{company.replace(' ', '_')}_{datetime.date.today().isoformat()}.pdf"
                pdf_path = str(OUTPUT_DIR / pdf_filename)
                create_formatted_pdf(pdf_path, resume_sections, location=candidate_location)

                # Step 8: Keyword coverage check (ATS-COV)
                combined_output = " ".join([
                    mission, skills,
                    " ".join(experience_blocks),
                    cover_letter
                ])
                kw_found, kw_missing, kw_coverage = check_keyword_coverage(
                    extracted_keywords, combined_output
                )

                # Step 9: Cost summary
                total_tokens, total_cost = estimate_cost(usage_log)

                # Step 10: Log to history
                jd_source = st.session_state.get("jd_url", "") or "Pasted Text"
                append_to_history(
                    datetime.date.today().isoformat(),
                    company, role, track, jd_source,
                    total_tokens, total_cost
                )

                status.update(label="Generation complete!", state="complete", expanded=False)

            st.session_state.gen_results = {
                "total_tokens": total_tokens,
                "total_cost": total_cost,
                "kw_coverage": kw_coverage,
                "kw_found": kw_found,
                "kw_missing": kw_missing,
                "extracted_keywords": extracted_keywords,
                "doc_path": doc_path,
                "doc_filename": doc_filename,
                "pdf_path": pdf_path,
                "pdf_filename": pdf_filename,
                "mission": mission,
                "skills": skills,
                "experience_blocks": experience_blocks,
                "all_coaching_notes": all_coaching_notes,
                "cover_letter": cover_letter,
                "custom_answers": custom_answers,
                "usage_log": usage_log
            }

        except Exception as e:
            st.error(f"Generation failed: {str(e)}")
            st.caption("Check your API key and network connection. If the issue persists, try again.")

    if "gen_results" in st.session_state:
        res = st.session_state.gen_results

        # Display results
        st.success(f"Done! {res['total_tokens']:,} tokens used (~${res['total_cost']:.3f})")

        # ATS Keyword Coverage Report
        coverage_pct = int(res['kw_coverage'] * 100)
        coverage_color = "green" if coverage_pct >= 80 else ("orange" if coverage_pct >= 60 else "red")
        st.markdown(f"### ATS Keyword Coverage: :{coverage_color}[{coverage_pct}%]")
        col_found, col_missing = st.columns(2)
        with col_found:
            st.caption(f"**Found ({len(res['kw_found'])})**")
            for t in res['kw_found']:
                st.markdown(f"- {t}")
        with col_missing:
            st.caption(f"**Missing ({len(res['kw_missing'])})**")
            for t in res['kw_missing']:
                st.markdown(f"- {t}")

        with st.expander("JD Keywords Extracted", expanded=False):
            st.text(res['extracted_keywords'])

        st.divider()

        # Download buttons
        col_doc, col_pdf = st.columns(2)
        with col_doc:
            with open(res['doc_path'], "rb") as f:
                st.download_button(
                    label="Download Resume (DOCX)",
                    data=f,
                    file_name=res['doc_filename'],
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
        with col_pdf:
            with open(res['pdf_path'], "rb") as f:
                st.download_button(
                    label="Download Resume (PDF)",
                    data=f,
                    file_name=res['pdf_filename'],
                    mime="application/pdf",
                    type="primary"
                )

        # Previews
        with st.expander("Mission Statement", expanded=True):
            st.text(res['mission'])

        with st.expander("Skills Statements"):
            st.text(res['skills'])

        with st.expander(f"Experience ({len(res['experience_blocks'])} roles)"):
            for block in res['experience_blocks']:
                st.text(block)
                st.divider()

        if res['all_coaching_notes']:
            with st.expander("Coaching Notes (not in document)", expanded=False):
                st.caption("These are internal review notes stripped from the DOCX. Use them to improve your inputs for the next run.")
                for note_block in res['all_coaching_notes']:
                    st.markdown(note_block)

        st.subheader("Cover Letter")
        st.caption("Select all and copy to paste into your application.")
        st.text_area(
            label="cover_letter_text",
            value=strip_coaching_notes(res['cover_letter']),
            height=320,
            label_visibility="collapsed",
            key="cover_letter_area"
        )

        if res['custom_answers']:
            st.subheader("Application Q&A")
            st.caption("Select all and copy to paste into your application.")
            st.text_area(
                label="qa_text",
                value=strip_coaching_notes(res['custom_answers']),
                height=280,
                label_visibility="collapsed",
                key="qa_area"
            )

        # Cost breakdown
        with st.expander("Token Usage & Cost"):
            st.markdown(f"""
| Metric | Value |
|--------|-------|
| Total tokens | {res['total_tokens']:,} |
| Approx. cost | ${res['total_cost']:.3f} |
| API calls | {len(res['usage_log'])} |
""")
