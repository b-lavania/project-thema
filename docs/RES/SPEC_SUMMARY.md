# Project Thema: Specification Summary

**Full Spec:** See [SPEC.md](./SPEC.md) for complete details.

**Note:** All files in `docs/RES/` are planning/spec material. Runtime career data and the app live in [`../../RES/README.md`](../../RES/README.md).

---

## What We Built (Phases 0-2) ✅

**A quality-first resume generator** that produces ATS-optimized, metrics-rich, truthful application materials.

### Key Features
- ✅ Track-aware prompts (6 tracks with 15-20 keywords each)
- ✅ JD keyword extraction + coverage checking (≥80% target)
- ✅ Role selection from master_context.md (LLM picks 2-4 relevant roles)
- ✅ Truth filters + coaching notes (zero fabrication rate)
- ✅ Cost tracking ($0.08-0.17 per generation)
- ✅ Pre-flight checklist + 3-tab UI
- ✅ Single source of truth: `master_context.md`

### Current Workflow
```bash
cd RES && streamlit run app.py
# 1. Enter company, role, JD
# 2. Click Generate
# 3. Download 1-page resume DOCX
# 4. Copy-paste cover letter
```

---

## What We're Building Next

### Phase 3: Remaining Backlog (3-5 days)
- [ ] ATS format audit (manual testing)
- [ ] Multiple DOCX templates (corporate vs startup)
- [ ] CSV batch runner
- [ ] Feedback tracking (interview callbacks)

### Phase V: Voice (3-5 days)
- [ ] `voice_profile.md` (writing samples + anti-patterns)
- [ ] BUL prompts (Believable, Understandable, Likeable)
- [ ] Readability hints (sentence length + stdlib/regex proxies; optional approximate F–K)
- **Gate:** A/B test, no new facts, coaching note rate stable, readability proxies within targets ([SPEC.md](./SPEC.md) V.3–V.4)

### Phase A: Memory (5-7 days)
- [ ] SQLite schema (opportunities, events, artifacts)
- [ ] `brain_store.py` (CRUD operations)
- [ ] Wire generation → DB
- [ ] History table UI (`st.data_editor`)
- **Gate:** DB stability, no latency regression

### Phase B: Advisory (5-7 days)
- [ ] Fit brief prompt (evidence + gaps + risks)
- [ ] Strategy prompt (positioning + talking points)
- [ ] "Decide" tab in UI
- **Gate:** Risks/gaps mandatory, no contradictions

### Phase C: Perform (3-5 days)
- [ ] Reflection journal
- [ ] Evidence miner (copy-paste suggestions only)
- **Gate:** No auto-merge to master_context.md

### Phase D: Plan (Deferred)
- [ ] Manual tags + frequency table
- [ ] No embeddings or clustering (until proven necessary)

---

## Product Principles (Non-Negotiable)

1. **Believability beats cleverness** — No new facts without human confirmation
2. **Understandable beats comprehensive** — Fewer features that work well
3. **Likeable = respectful + clear** — No sycophantic language
4. **Single source of truth** — `master_context.md` is canonical; AI never auto-merges

### Anti-Goals
- ❌ Auto-merge LLM edits into `master_context.md`
- ❌ LLM "fit scores" as authoritative
- ❌ Second polish pass (until spike proves safety)
- ❌ Heavy Kanban CRUD (without UI spike)

---

## Phase Gates

**Each phase has a gate. If it fails, we STOP and narrow scope.**

| Phase | Gate Criteria |
|-------|---------------|
| V | A/B preference >60%, no new facts, readability proxies (see SPEC V.3–V.4) |
| Vb | Automated diff test passes, human review 5/5, cost acceptable |
| A | DB survives restart, latency <1s, graceful failures |
| B | Risks/gaps mandatory, no contradictions, self-review ≥5 fixtures (optional peers) |
| C | Zero auto-merge, copy-paste only |

**Gate failure is not a failure — it's the process working correctly.**

---

## Success Metrics

### Current (Phases 0-2)
- ✅ ATS keyword coverage: 85-95% (target ≥80%)
- ✅ Generation cost: $0.08-0.17 (target <$0.20)
- ✅ Time to draft: 2-3 min (target <5 min)
- ✅ Fabrication rate: 0 (target 0)
- ✅ Coaching notes: 0-2 per run (target <2)

### Future (Second Brain)
- Voice preference: >60% prefer new output
- Advisory usefulness: useful on ≥5 self-reviewed fixtures; optional peer feedback
- Application tracking: 100% logged
- Interview callback rate: Self-reported in DB

---

## Key Files

### Current
- `app.py` — Streamlit UI (3 tabs, pre-flight checklist)
- `generator.py` — 5 LLM functions, track-aware prompts
- `data/master_context.md` — Single source of truth
- `doc_generator.py` — DOCX generation (1-page resume)
- `data/history.md` — Auto log under `## Auto log`

### Future
- `voice_profile.md` — Writing samples + anti-patterns
- `brain_store.py` — SQLite CRUD
- `schema.sql` — Opportunities + events + artifacts
- `prompts/fit_brief.md` — Fit analysis
- `prompts/strategy.md` — Application strategy

---

## Roadmap Timeline

| Phase | Duration | Status |
|-------|----------|--------|
| 0-2 | 8 days | ✅ Complete |
| 3 | 3-5 days | 🚧 In Progress |
| V | 3-5 days | 📋 Planned |
| Vb | 2-3 days | 📋 Spike Only |
| A | 5-7 days | 📋 Planned |
| B | 5-7 days | 📋 Planned |
| C | 3-5 days | 📋 Planned |
| D | 2-3 days | ⏸️ Deferred |

**Total estimated time to Phase C:** ~30-40 days

---

## Quick Start

### Current System
```bash
cd /home/bl/Documents/GitHub/project-thema/RES
pip install -r requirements.txt
# Add OPENAI_API_KEY to .env
streamlit run app.py
```

### Next Steps
1. Complete Phase 3 (ATS audit, templates, batch, feedback)
2. Start Phase V (voice profile, BUL prompts)
3. Gate strictly — stop if quality degrades
4. Proceed to Memory/Advisory only after Voice is stable

---

## Questions?

- **Full details:** [SPEC.md](./SPEC.md)
- **Current code:** `RES/app.py`, `RES/generator.py`
- **Context:** `RES/data/master_context.md`
- **History:** `RES/data/history.md`
