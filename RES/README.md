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
