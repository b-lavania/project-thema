# AGENTS.md — project-thema

Single-user Streamlit resume/cover letter generator. Career truth lives in Markdown; LLMs (OpenAI / Gemini) produce tailored output per job.

## Directory map

| Path | Role |
|------|------|
| `RES/` | Streamlit modules + career data + prompts — **this is the active code** |
| `app.py` | Streamlit entrypoint (run from project root) |
| `RES/generator.py` | LLM orchestration (calls `llm_client.py`, loads `prompts/*.md`) |
| `RES/llm_client.py` | Unified OpenAI + Gemini client |
| `RES/data/master_context.md` | **Single source of truth** for generation — edit this to change career facts |
| `RES/data/history.md` | Auto-appended run log |
| `RES/data/applications.csv` | CSV-backed outcome tracker (updated by Outcomes tab) |
| `RES/prompts/*.md` | 15 prompt fragments (loaded by `generator.py`) |
| `RES/assets/template.html` / `template.docx` | PDF / DOCX render templates |
| `RES/outputs/` | Generated files (gitignored) |
| `docs/RES/` | Specs, roadmaps, plans (not loaded by app) |
| `PORTFOLIO/` | Static HTML case studies |
| `ENGiNEERING/` | Essays / notes |
| `HUNT-AGENT/` | Job scraper package: board APIs + SerpAPI search + discovery pipeline + lead storage |

## Run

```bash
# app.py lives at project root; modules stay in RES/
pip install -r requirements.txt
# API keys in RES/.env (gitignored) or sidebar:
#   OPENAI_API_KEY="..."
#   GEMINI_API_KEY="..."
streamlit run app.py
```

## Test

Uses `unittest` (not pytest). Run from repo root or `RES/`:

```bash
cd RES && python -m unittest discover -s tests
```

Test files: `test_ats_coverage.py`, `test_quick_take_normalize.py`, `test_how_i_work_jd_context.py`.

## Key conventions

- **Quick Take must be metric-free** — zero metrics, zero tool names, zero em/en dashes. Metrics only in How I Work / The Work / optional Key Results row.
- **Profile lint** no longer rewrites every 2-line Quick Take (was truncating output at 400 tokens).
- Gemini `gemini-2.0-flash` retired for new API keys — auto-remapped to `gemini-2.5-flash-lite`. Free-tier `gemini-2.5-pro` often has zero quota (use Flash or OpenAI for profile).
- PDF compaction is 3-tier: role density → section budgets → CSS compaction. Triggered by "Compact to 2 pages" button or sidebar checkbox.
- `COACHING NOTE:` lines are stripped from exports (truth filter against fabrication).
- Export modes: `standard` (ATS, 2-page max) and `digital` (presentation, 3-page max).
- `---PAGEBREAK---` in an experience block forces a page break before the following content.

## Provider model defaults

| Tier | OpenAI | Gemini |
|------|--------|--------|
| Bulk sections | `gpt-4o` | `gemini-2.5-flash` |
| Profile + lint | `gpt-4.1` | `gemini-2.5-flash` |
| Pain + angle | `o4-mini` | `gemini-2.5-flash` |

Override via sidebar Advanced or `GEMINI_*_MODEL` / `PAIN_POINT_MODEL` env vars.

## Editing workflow

1. Update `RES/data/master_context.md` with latest career facts.
2. Run app → paste JD → select track/voice → generate.
3. Outcome tracking written to `RES/data/applications.csv` automatically per generation.

## Notable absences

No CI, no pre-commit, no pyproject.toml, no Makefile, no linting/typecheck config. Single user, local only, no infrastructure.
