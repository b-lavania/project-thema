# Prompt Harness Memories (auto-generated)
Use these as persistent constraints/context for resume + cover-letter harness. Keep plain text for easy reuse.

## resume_cover_letter_harness_requirements
- Scope: system ingests job-specific info, outputs resume and cover letter.
- Tracks: Product/AI, Pricing/Ops, Growth, Logistics/Marketplace, BizOps, Chief of Staff (keep open within these bounds).
- Output: Google Docs–friendly text (avoid Markdown formatting).
- Data: may reuse details/metrics from RES/historic PDFs and portfolio HTMLs; tailor for competitive SF/tech market.
- State: store run history in repo (Markdown file).

## source_files_for_resume_cover_letter
- Core prompts: RES/prompt.md (experience, skills statements, mission statement).
- Data sources: RES/extracted/*.txt (parsed resumes) and PORTFOLIO/concept1-3.html (metrics/case studies) for grounding.

## format_constraint_google_docs
- Outputs must be easy to paste into Google Docs; plain text/DOCX-friendly; avoid Markdown syntax.

## history_storage_preference
- Keep application run history in-repo Markdown (e.g., RES/history.md) with inputs/outputs/notes per run.

## competitive_positioning_requirement
- Tone: sharp, outcome-led, metrics-rich; aligned to cutthroat SF/tech competition. Use conservative, truthful metrics from sources.

## planning_state_reset (meta)
- Note: previously exited planning accidentally; continue normal flow now.
