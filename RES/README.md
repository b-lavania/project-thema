# RES — resume & cover letter pipeline (runtime)

This directory is the **Streamlit app and everything it reads/writes** while running. Keep it free of roadmaps and long-form specs so career truth stays obvious.

## What the app uses (runtime)

| Path | Purpose |
|------|---------|
| `app.py` | Streamlit entrypoint — run from this directory |
| `generator.py`, `doc_generator.py`, `pdf_generator.py` | Generation logic |
| `data/` | **Career truth + memory log** — `master_context.md`, `history.md` (hand-edited / auto-appended) |
| `assets/` | Templates (`template.docx`, `template.html`) |
| `assets/archive_pdfs/` | Archived resume PDFs (reference only) |
| `prompts/` | LLM prompt fragments loaded by `generator.py` |
| `outputs/` | Generated DOCX/PDF (gitignored) |
| `.env` | API key (local; gitignored) |

## Planning & build docs (not loaded by the app)

Specs, roadmaps, second-brain plan, and analysis live under **[`../docs/RES/`](../docs/RES/)** — see [`../docs/RES/README.md`](../docs/RES/README.md).

## Run

```bash
cd RES
pip install -r requirements.txt
# API key: create `RES/.env` with your key (Streamlit sidebar can persist it).
streamlit run app.py
```

## Editing workflow

1. Update career facts in **`data/master_context.md`** (single source of truth for generation).
2. Application runs append to **`data/history.md`** under `## Auto log`.
3. Prompts used by the app are only under **`prompts/*.md`**. For legacy human-only workflows, see **`../docs/RES/legacy_prompt.md`**.

## Resume layout (PDF / DOCX)

- Output is **letter size**, typically **1–2 pages** depending on role count and profile length.
- **PDF:** each experience/project block uses `page-break-inside: avoid` so a role title is not orphaned with bullets on the next page.
- **DOCX:** role header, company description, and summary use `keep_with_next` where possible.
- **Manual page breaks (sidebar “PDF layout”):** checkboxes to start a new page before How I Work, The Work, Side Builds, or Credentials; optional “break before role #” (1-based).
- **Power user:** put a line containing only `---PAGEBREAK---` in an experience block to force a break before the following content (stripped from DOCX).
- After generation, use **Re-export DOCX/PDF with current PDF layout** to apply changed sidebar breaks without re-running LLMs.
- With **3+ roles**, the app warns that the resume may be dense; fewer roles usually yields a cleaner layout.

## Professional profile pipeline (problem → parallel → solve)

1. **Narrative brief** (`gpt-4o`) — positioning; proof points use decision/outcome labels and WHY IT MATTERS.
2. **JD pain analysis** (`o4-mini`) — `prompts/jd_pain_point.md` (SITUATION, CORE_PAIN, stakes, success); no company name.
3. **Profile angle** (`o4-mini`) — `prompts/profile_angle.md` — THEIR_PROBLEM, ANALOGOUS_EXPERIENCE, SOLUTION_PATTERN, PROOF_SNIPPET, forbidden nouns.
4. **The Quick Take** (`gpt-4.1`, temperature 0.3) — tagline + 3 sentences: **their problem** / **your parallel** / **how you solve** (one metric max in line 4).
5. **Profile lint** — rewrites if WHAT-heavy, missing parallel beat in line 3, or vague corporate phrasing.

**Voice rule:** line 2 is employer-only; line 3 is candidate-only; line 4 is approach + proof. Domain labels OK; employer names not.

**UI:** expanders for JD pain and profile angle; editable profile with **Apply profile edit to DOCX/PDF**; **Regenerate Profile Only** reuses stored angle and pain.

Optional future spike: `PROFILE_PROVIDER=anthropic` if OpenAI path still reads template-heavy on blind A/B across 3 JDs.
