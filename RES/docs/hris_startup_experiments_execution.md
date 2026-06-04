# HRIS + startup-size + experimentation upgrades (execution doc)

This is the execution/runbook version of the Cursor plan `hris_facts_+_startup_size_+_experiments_33a0261c.plan.md`, with one constraint change:

- **Keep DOCX/PDF as Legal size (8.5×14). Do not convert to Letter.**

This doc is the source of truth for what we’ll execute/verify going forward.

---

## Goals

- **HRIS (BVXpress / ICI)**: make the resume generator reliably surface a truthful 0→1 summary + adoption proof (**3 teams onboarded/using**).
- **Startup signal**: add compact at-join descriptors (e.g., **“Employee #6 (first product hire)”**) so resume company descriptor lines emphasize early-stage scope.
- **Experimentation + product analytics**: strengthen the narrative so outputs include A/B testing / controlled tests, telemetry-driven decisions, conversion lift, and attribution work when the JD calls for it.

---

## Non-goals / constraints

- **No Letter sizing**: keep **Legal** page size in DOCX/PDF exports.
- **No fabricated metrics**: if a lift is not explicitly in `RES/data/master_context.md`, it should not appear in outputs.
- **Don’t say “PM hire”**: use **product hire**.

---

## Files that should carry the facts (single source of truth)

- Primary truth source: [`RES/data/master_context.md`](../data/master_context.md)
- Prompt enforcement: [`RES/prompts/experience_bullets.md`](../prompts/experience_bullets.md)
- Track plumbing:
  - [`RES/app.py`](../app.py) (`TRACK_OPTIONS`)
  - [`RES/generator.py`](../generator.py) (`TRACK_EMPHASIS`)

---

## Role-by-role “killed product / feature” examples (grounded)

These are explicit de-scopes/cuts to include as examples in generated bullets (when relevant) and to keep as a reference for interview storytelling.

### ROLE 1 — Moovez / Quotely (Founding PM)

- **Killed / cut (v1)**: *real-time dispatcher chat overlay*, *customer subscription model*, *automated route optimization* — deferred to preserve quote-flow focus.
- **Experimentation example**: controlled test redirecting traffic to **automated quoting vs. manual quoting** before scaling (no invented lift).

### ROLE 2 — Fractional Product Consultant

- **Killed / cut**: Village Wellth pricing simplification — **consolidated 4 tiers → 3** by killing the **two lowest-adoption plans** (explicit tradeoff: reduced short-term upsell optionality).
- **Experimentation / analytics**: conversion lift and attribution clarity (MMM + telemetry-driven decisions) across engagements, framed as decisions and outcomes—not tool laundry lists.

### ROLE 4 — Netsweeper (AI Vision PM)

- **Killed / cut**: deprioritized **all new feature development for a full quarter**; rejected proposal to add new detection categories until false-positive rate and trust were fixed.

### ROLE 5 — BVXpress / ICI (PM & Chief of Staff)

- **Killed / cut (core BVXpress SaaS)**: planned “deal database” product; fee-benchmarking tool (telemetry showed it was a demo feature, not a workflow feature).
- **Killed / cut (HRIS)**: “replace every payroll system” hypothesis—pivoted to **adapter-first** integration with source systems remaining truth.

---

## Startup-size descriptors (compact format)

Use these exact compact strings in the **company description line** whenever the role is selected:

- **Moovez**: `Employee #6 (first product hire)` (company had 5 employees before join)
- **BVXpress / ICI**: `Employee #3 (first product hire)`
- **Netsweeper**: `Only product hire on the team at the time` (not a startup)
- **Fractional**: `Often the only product hire` (plus experimentation + attribution scope)

---

## Generator behavior: HR/HRIS track

Add/use a distinct track that increases the likelihood the output emphasizes:

- HRIS/HCM, people analytics, workforce integration
- M&A diligence + post-merger integration workflows
- payroll/contract risk dashboards, compliance/audit requirements
- adoption path: diligence/PMI teams → HRBPs/management in post-merger entity

Expected wiring:

- `RES/app.py`: include `"HR/HRIS"` in `TRACK_OPTIONS`
- `RES/generator.py`: define `TRACK_EMPHASIS["HR/HRIS"]`

---

## Execution checklist (what to do and verify)

### A) Update master truth (`master_context.md`)

- Add HRIS 0→1 overview + adoption proof (**3 teams**) inside ROLE 5 HRIS subsection and as a **resume-ready bullet**.
- Add compact startup descriptors in role headers (Moovez/BVXpress/Netsweeper/Fractional).
- Add experimentation facts:
  - Moovez automated-vs-manual quote test (no invented lift)
  - BVXpress telemetry-driven enhance vs deprecate decisions
  - Fractional: conversion-lift + attribution framing (MMM)
- Update “How I Work → Measure” lane to explicitly include **experimentation**.

### B) Enforce company descriptor inclusion in bullets prompt

- `RES/prompts/experience_bullets.md` must instruct: if role block contains `Employee #N (first product hire)` or `only product hire`, **include it** in the company description line.

### C) Verify output

- Run:

```bash
cd RES
streamlit run app.py
```

- Generate a resume with track **HR/HRIS** and confirm:
  - One experience block shows `Employee #6 (first product hire)` for Moovez when Moovez is selected.
  - HRIS bullets include: **0→1 HRIS + 3 teams onboarded/using**.
  - Experimentation phrasing appears when the JD includes “A/B testing”, “experimentation”, “product analytics”, or “attribution”.

---

## Template note (DOCX/PDF sizing)

- **Legal is intentional.** Do not “fix” DOCX to Letter.
- If we later tweak templates, changes should be layout/readability only (spacing, headings mapping, clickability), not page size.

