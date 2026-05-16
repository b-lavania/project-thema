# ResTron: System Spec & Improvement Backlog

**Scope:** The `RES/` resume-and-cover-letter pipeline (Streamlit UI, OpenAI generation, Word output, `master_context.md`, `history.md`). This document reflects current implementation state and the remaining improvement backlog.

---

## What's been built (as of May 2026)

### Architecture

| Layer | Role | Files |
|--------|------|-------|
| UI | Job inputs, track selection, location, API key, trigger generation | `RES/app.py` |
| AI | Mission, skills, bullets, cover letter, custom Q&A — 5 LLM functions | `RES/generator.py` |
| Context | Single source of truth for all generation; derived from extracted resumes + portfolio HTMLs | `RES/master_context.md` |
| Documents | Load `template.docx`, clear body, write resume-only (1 page) using template styles | `RES/doc_generator.py` |
| History | Auto log under `## Auto log` section after each run | `RES/history.md` |

### Completed features

| ID | Feature | Status |
|----|---------|--------|
| `P0-PATH` | `RES_ROOT` via `__file__`; template + outputs paths cwd-independent | Done |
| `P0-KEY` | API key loaded from `.env` via `python-dotenv`; persisted on entry | Done |
| `P0-ERR` | try/except around full generation chain; plain-language `st.error` | Done |
| `P1-COST` | Token usage + approximate USD shown after each run | Done |
| `P1-SES` | `st.session_state` for sticky fields across reruns | Done |
| `P2-TRK` | `selected_track` passed into all `generate_*` via `TRACK_EMPHASIS` dict | Done |
| `P2-HIST` | Auto log written to `## Auto log` section in `history.md` | Done |
| `M-DOCX` | `doc_generator.py` splits on real `\n`; coaching notes stripped from DOCX | Done |
| `M-XP` | Experience bullets use role blocks from `master_context.md`, not manual paste | Done |
| — | Anti-fluff forbidden phrase list enforced in all prompts | Done |
| — | Temperature lowered to 0.4; max_tokens tuned per function | Done |
| — | Coaching notes separated from output; shown in dedicated UI expander | Done |
| — | DOCX is resume-only (1 page); cover letter + Q&A shown in-app as copyable text areas | Done |
| — | Location selector (Sunnyvale CA / Calgary AB) in sidebar; flows into contact line | Done |
| — | `master_context.md` built from all `extracted/*.txt` + portfolio HTML metrics/case studies | Done |
| — | `prompt.md` gaps patched: 1:1 duty mapping, char targets, 5-tier ordering logic | Done |
| — | Role selection: LLM picks 2–4 most relevant roles from master context per JD | Done |

### Current workflow (working today)

```bash
cd /home/bl/Documents/GitHub/project-thema/RES
pip install -r requirements.txt
# API key auto-loaded from RES/.env or enter in sidebar (persisted to .env)
streamlit run app.py
```

1. Sidebar: API key (auto-loaded), location, track
2. Main: company, role, JD text or URL
3. Optional: custom application questions
4. Click **Generate** → mission statement, skills (1:1 duty mapping), experience bullets (role-selected from master context), cover letter
5. **Download Resume (1-page DOCX)**
6. Copy-paste cover letter and Q&A from in-app text areas

### Estimated costs (GPT-4o)

| Section | Tokens | Cost |
|---------|--------|------|
| Role selection | ~300 | ~$0.002 |
| Mission statement | ~1,700 | ~$0.013 |
| Skills statements | ~2,600 | ~$0.020 |
| Experience bullets (per role) | ~800 | ~$0.006 |
| Cover letter | ~2,600 | ~$0.020 |
| Custom Q&A (optional) | ~2,000 | ~$0.015 |
| **Total (2 roles)** | **~11,000** | **~$0.08–0.17** |

---

## ATS-proofing assessment

The goal is to generate ATS-proof, metrics-rich resumes. Here's where we stand:

### Content layer (~85% covered)

| Check | Status |
|-------|--------|
| Keywords derived from JD duties (1:1 mapping) | Done |
| Metrics grounded in master_context.md (real numbers) | Done |
| Forbidden generic phrases enforced | Done |
| STAR structure in experience bullets | Done |
| Skill labels (2–5 words, Title Case, ATS-keyword-rich) | Done |
| Truth filter + coaching notes for ungrounded claims | Done |
| ATS-safe characters only (no symbols beyond `\| , . -`) | Done |
| No first-person in resume sections | Done |
| **JD keyword extraction** (auto-extract top duties + requirements from raw JD) | Missing |
| **Post-gen keyword coverage check** (verify JD terms landed in output) | Missing |
| **Qualifications section keyword injection** | Ignored by design |
| **Track keyword banks** (curated 15–20 ATS terms per track) | Missing |

### Format layer (unverified)

| Check | Status |
|-------|--------|
| Standard section headers (Experience, Skills, Education) | Done |
| No markdown in DOCX output | Done |
| Plain text, no tables in body | Done |
| **`template.docx` ATS audit** (single column? no text boxes? standard fonts?) | Not done |
| **Parser test** (Workday, Greenhouse, Lever simulation) | Not done |

---

## Remaining backlog

### High priority (content quality)

- [x] **`ATS-KW`** — JD keyword extraction *(Done)*
  - `extract_jd_keywords()` in `generator.py` extracts top 5 duties + top 5 requirements from raw JD
  - Extracted duties auto-fed into `generate_skills_statements` (no manual duty paste needed)
  - Runs as Step 1 of the generation pipeline; full extracted list shown in "JD Keywords Extracted" expander

- [x] **`ATS-COV`** — Post-generation keyword coverage check *(Done)*
  - `check_keyword_coverage()` in `app.py` matches extracted terms against combined output (mission + skills + experience + cover letter)
  - Coverage % shown with color coding (green ≥80%, orange ≥60%, red <60%)
  - Two-column Found/Missing breakdown displayed before download button

- [ ] **`ATS-FMT`** — `template.docx` format audit *(Manual step — not automatable)*
  - Run generated DOCX through an ATS parser (Jobscan, Resume Worded, or similar)
  - Verify: single-column layout, no text boxes, no headers/footers with critical info, standard fonts
  - **Acceptance:** Parser extracts all sections correctly with no missing content

- [x] **`ATS-KWB`** — Track keyword banks *(Done)*
  - `TRACK_EMPHASIS` in `generator.py` expanded from 1-sentence hints to full keyword banks (15–20 terms per track)
  - LLM instructed to weave keywords in naturally where grounded
  - Covers all 6 tracks: Product/AI, Pricing/Ops, Growth, Logistics/Marketplace, BizOps, Chief of Staff

### Medium priority (robustness)

- [x] **`P0-SCRAPE`** — Scrape truthfulness *(Done)*
  - `scrape_url()` returns structured `{"ok", "text", "error"}`; HTTP non-2xx, exceptions, and body < 200 chars all treated as failure
  - `st.error` shown on failure; generate button gated by pre-flight checklist (JD length check blocks generation)

- [x] **`P0-VAL`** — Minimum JD length check *(Done)*
  - `MIN_JD_LENGTH = 200` constant in `app.py`; pre-flight checklist enforces `len(jd_text) >= MIN_JD_LENGTH` before enabling the Generate button

- [x] **`P1-UX`** — Layout polish *(Done)*
  - Three tabs: **Job Details** | **Application Questions** | **Generate & Output**
  - Pre-flight checklist (API Key, Company, Role, JD length, Master Context) with pass/fail indicators before Generate button

### Lower priority / future

- [ ] **`P2-TPL`** — Multiple DOCX templates (corporate vs startup)
- [ ] **`P3-BAT`** — CSV batch runner (company, role, jd_url, track → N docx files)
- [ ] **`FEED`** — Feedback log: track which applications got callbacks (optional field in history)
- [ ] **`P3-API`** — Optional FastAPI headless wrapper for non-Streamlit clients

### Icebox

- Job board scrapers / LinkedIn API (ToS and fragility)
- ML interview-offer prediction
- Redis caching (only if concurrent usage)
- Multi-user auth (Phase 4 — not before single-user workflow is excellent)

---

## Success metrics

| Area | Target |
|------|--------|
| ATS keyword coverage | ≥80% of JD key terms present in output |
| Generation cost | <$0.20 per run |
| Time to usable draft | <5 min from JD paste to download |
| Fabrication rate | 0 invented metrics (enforced by truth filter) |
| Coaching note rate | <2 per generation (indicates grounding quality) |
| Interview callback rate | Self-reported; tracked in `history.md` (optional) |

---

## Architecture notes

- **UI:** Streamlit remains appropriate; no need for `streamlit-component-lib` yet.
- **Context:** `master_context.md` is the single source of truth; do not bypass it with manual textarea pastes.
- **Storage:** `history.md` for lightweight audit; SQLite only if structured querying becomes needed.
- **Deployment:** Local only; Docker + `.env` if shared deployment ever needed.
- **Non-goals:** Full job-board automation, Redis, multi-user auth — all deferred until single-user workflow is proven.