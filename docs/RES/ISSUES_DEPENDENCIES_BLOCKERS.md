# Project Thema: Issues, Dependencies & Blockers Analysis

**Purpose:** Deep analysis of SPEC.md to identify all issues, dependencies, and blockers that could impact execution.

**Last Updated:** May 2026

---

## Table of Contents

1. [Critical Blockers](#critical-blockers)
2. [Phase Dependencies](#phase-dependencies)
3. [Technical Debt & Issues](#technical-debt--issues)
4. [Resource Constraints](#resource-constraints)
5. [Risk Matrix](#risk-matrix)
6. [Mitigation Strategies](#mitigation-strategies)
7. [Execution Recommendations](#execution-recommendations)

---

## Critical Blockers

### 🚨 BLOCKER 1: Phase 3 Not Actually Complete

**Issue:** SPEC.md claims "Phase 3 In Progress" but lists it as incomplete in roadmap.

**Evidence:**
- Roadmap shows: "🚧 **Phase 3**: Remaining Backlog (3-5 days)"
- All Phase 3 tasks have `[ ]` (unchecked) status
- Tasks: ATS-FMT, P2-TPL, P3-BAT, FEED all pending

**Impact:** 
- Cannot start Phase V until Phase 3 is complete (foundation must be stable)
- Phase 3 tasks are prerequisites for Second Brain features
- Estimated 3-5 days of work before Phase V can begin

**Blocker Severity:** 🔴 **HIGH** — Must complete before proceeding

**Resolution:**
1. Complete ATS-FMT (2-3 hours)
2. Complete P2-TPL (1 day)
3. Complete P3-BAT (2-3 days)
4. Complete FEED (1 day)
5. **Total:** 4-5 days before Phase V can start

---

### 🚨 BLOCKER 2: No Voice Profile Creation Process Defined

**Issue:** Phase V requires `voice_profile.md` but provides no guidance on how to create it.

**Evidence:**
- SPEC.md says: "3-5 writing samples (50-100 words each) from actual emails/docs"
- No process for: selecting samples, extracting style, validating quality
- No examples of what good vs bad voice profiles look like
- No tooling to help create or validate voice profiles

**Impact:**
- Phase V cannot start without voice profile
- Risk of poor-quality voice profile leading to gate failure
- Unclear effort estimate (could be 1 hour or 1 day)

**Blocker Severity:** 🟡 **MEDIUM** — Needs specification before Phase V

**Resolution:**
1. Define voice profile creation process
2. Create template with examples
3. Add validation checklist
4. Estimate: 2-4 hours to define process

---

### 🚨 BLOCKER 3: SQLite Schema Incomplete

**Issue:** Phase A schema missing critical tables and constraints.

**Evidence:**
- No `reflections` table (needed for Phase C)
- No indexes defined (performance issue for 100+ opportunities)
- No foreign key enforcement pragma
- No migration strategy beyond "delete db"

**Impact:**
- Phase A implementation will be incomplete
- Phase C blocked (no reflections table)
- Performance issues at scale
- Data loss risk during schema changes

**Blocker Severity:** 🟡 **MEDIUM** — Must fix before Phase A implementation

**Resolution:**
```sql
-- Missing table
CREATE TABLE reflections (
    id INTEGER PRIMARY KEY,
    opportunity_id INTEGER,
    reflection_type TEXT, -- interview, offer, rejection, learning
    reflection_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (opportunity_id) REFERENCES opportunities(id)
);

-- Missing indexes
CREATE INDEX idx_opportunities_status ON opportunities(status);
CREATE INDEX idx_opportunities_created ON opportunities(created_at);
CREATE INDEX idx_events_opportunity ON events(opportunity_id);

-- Enable foreign keys
PRAGMA foreign_keys = ON;
```

---

### 🚨 BLOCKER 4: Streamlit Version Compatibility

**Issue:** SPEC.md assumes `st.data_editor` exists, but this requires Streamlit ≥1.23.0.

**Evidence:**
- Current requirements.txt: `streamlit==1.32.2` ✅ (compatible)
- Phase A.5 uses `st.data_editor` for opportunities table
- No fallback if feature unavailable

**Impact:**
- Low risk (current version supports it)
- But no fallback for older Streamlit versions
- Could break if requirements.txt is downgraded

**Blocker Severity:** 🟢 **LOW** — Already resolved, but needs documentation

**Resolution:**
- Document minimum Streamlit version: ≥1.23.0
- Add version check in app.py startup
- Provide fallback UI (simple table) if version too old

---

## Phase Dependencies

### Dependency Graph

```
Phase 0 (Complete) ✅
    ↓
Phase 1 (Complete) ✅
    ↓
Phase 2 (Complete) ✅
    ↓
Phase 3 (BLOCKER) 🔴
    ↓
Phase V (Voice)
    ↓
Phase Vb (Polish - Optional Spike)
    ↓
Phase A (Memory)
    ↓
Phase B (Advisory) ← depends on Phase A
    ↓
Phase C (Reflection) ← depends on Phase A
    ↓
Phase D (Deferred)
```

### Critical Path Analysis

**Longest path to Phase C (full Second Brain):**
- Phase 3: 4-5 days
- Phase V: 3-5 days
- Phase Vb: 2-3 days (optional)
- Phase A: 5-7 days
- Phase B: 5-7 days
- Phase C: 3-5 days

**Total:** 20-29 days (without Phase Vb) or 22-32 days (with Phase Vb)

### Parallel Work Opportunities

**Can be done in parallel:**
- Phase 3 tasks (ATS-FMT, P2-TPL, P3-BAT, FEED) are mostly independent
- Phase V.1 (voice profile) + V.2 (BUL prompts) can be done concurrently
- Phase B (Advisory) + Phase C (Reflection) can be developed in parallel after Phase A

**Cannot be parallelized:**
- Phase 3 must complete before Phase V
- Phase A must complete before Phase B or C
- All phases must pass gates before proceeding

---

## Technical Debt & Issues

### ISSUE 1: Cost Tracking Incomplete

**Problem:** SPEC.md claims P1-COST is complete, but doesn't track Second Brain costs.

**Evidence:**
- Current cost tracking: $0.08-0.17 per generation (5 API calls)
- Phase V adds: voice profile injection (longer prompts)
- Phase Vb adds: polish pass (2x cost)
- Phase B adds: fit brief + strategy (2 more API calls)
- **Estimated new cost:** $0.30-0.50 per generation (8-10 API calls)

**Impact:**
- Users unaware of cost increases
- No budget alerts or warnings
- Could lead to unexpected API bills

**Severity:** 🟡 **MEDIUM**

**Resolution:**
- Add cost projection for each phase
- Show "Estimated cost with Voice: $0.25" before enabling
- Add monthly budget tracking
- Alert when approaching limits

---

### ISSUE 2: No Rollback Strategy

**Problem:** If a phase fails its gate, no clear rollback process.

**Evidence:**
- SPEC.md says: "Stop, narrow scope, re-test"
- But no guidance on: how to rollback code, how to preserve data, how to communicate to users
- No feature flags or gradual rollout strategy

**Impact:**
- Failed gates could leave system in broken state
- Users might see half-implemented features
- No way to A/B test new features safely

**Severity:** 🟡 **MEDIUM**

**Resolution:**
- Implement feature flags for each phase
- Add `RES/config.py` with feature toggles
- Use git branches for each phase
- Document rollback procedures

---

### ISSUE 3: master_context.md Maintenance Burden

**Problem:** master_context.md is 267 lines and growing. No maintenance process defined.

**Evidence:**
- Current size: 267 lines
- Built from: `extracted/*.txt` + portfolio HTML
- No process for: updating, versioning, validating
- Phase C adds evidence miner (suggests additions)
- Risk: becomes stale, contradictory, or bloated

**Impact:**
- Outdated context leads to poor generation quality
- No way to track what changed and when
- Evidence miner suggestions could accumulate without review

**Severity:** 🟡 **MEDIUM**

**Resolution:**
- Add `master_context_version` field to opportunities table
- Track which version was used for each generation
- Add "Last Updated" timestamp to master_context.md
- Create quarterly review process
- Add validation script to check for contradictions

---

### ISSUE 4: No Testing Strategy

**Problem:** SPEC.md has no testing plan for any phase.

**Evidence:**
- No unit tests mentioned
- No integration tests
- No regression tests
- Gates rely on manual testing only
- "Automated diff check" mentioned but not implemented

**Impact:**
- High risk of regressions
- Gates are subjective and time-consuming
- No way to verify "no new facts" automatically
- Difficult to refactor with confidence

**Severity:** 🔴 **HIGH**

**Resolution:**
- Add `RES/tests/` directory
- Create test fixtures (sample JDs, expected outputs)
- Implement automated diff checker for Phase Vb gate
- Add regression test suite
- Run tests before each phase gate
- Estimated effort: 2-3 days

---

### ISSUE 5: Prompt Template Management

**Problem:** Prompts are scattered across multiple files with no versioning.

**Evidence:**
- Current: `RES/prompts/*.md` (8 files)
- Future: `voice_profile.md`, `ai_tells.md`, `fit_brief.md`, `strategy.md`
- No version control for prompts
- No A/B testing framework
- No way to rollback prompt changes

**Impact:**
- Prompt changes could degrade quality
- No way to compare prompt versions
- Difficult to debug prompt-related issues
- A/B testing (Phase V gate) will be manual and error-prone

**Severity:** 🟡 **MEDIUM**

**Resolution:**
- Add `PROMPT_VERSION` constant to each prompt file
- Track prompt version used in opportunities table
- Create prompt changelog
- Build simple A/B testing framework
- Estimated effort: 1 day

---

## Resource Constraints

### CONSTRAINT 1: Single Developer

**Issue:** SPEC.md assumes one developer working sequentially.

**Evidence:**
- Total estimated time: 20-32 days
- No parallelization of work
- No code review process
- No pair programming for complex features

**Impact:**
- Longer time to completion
- Higher risk of bugs and oversights
- No knowledge sharing
- Burnout risk on long phases

**Mitigation:**
- Break phases into smaller milestones
- Add checkpoints every 2-3 days
- Use AI coding assistants (Cursor, Windsurf)
- Document decisions as you go

---

### CONSTRAINT 2: No Staging Environment

**Issue:** All development and testing happens in production.

**Evidence:**
- No mention of dev/staging/prod environments
- Streamlit runs locally only
- No CI/CD pipeline
- No automated deployments

**Impact:**
- Testing on real data (privacy risk)
- No safe place to experiment
- Difficult to share work-in-progress
- No rollback capability

**Mitigation:**
- Create `RES/.env.dev` and `RES/.env.prod`
- Use separate SQLite databases for dev/prod
- Add `--dev` flag to app.py
- Consider Docker for isolation

---

### CONSTRAINT 3: API Rate Limits

**Issue:** OpenAI API has rate limits that could block development.

**Evidence:**
- GPT-4o rate limits: 10,000 TPM (tokens per minute) for Tier 1
- Current generation: ~11,000 tokens
- Phase V adds ~2,000 tokens (voice profile)
- Phase B adds ~4,000 tokens (fit brief + strategy)
- **New total:** ~17,000 tokens per generation

**Impact:**
- Could hit rate limits during testing
- Batch runner (Phase 3) could be throttled
- A/B testing (Phase V gate) could be slow

**Mitigation:**
- Add rate limiting to batch runner
- Cache API responses during development
- Use cheaper models for testing (GPT-3.5)
- Upgrade to Tier 2 if needed ($50/month spend)

---

### CONSTRAINT 4: No Budget Defined

**Issue:** SPEC.md tracks costs but has no budget or spending limits.

**Evidence:**
- Current cost: $0.08-0.17 per generation
- Future cost: $0.30-0.50 per generation
- No monthly budget defined
- No cost alerts or limits

**Impact:**
- Unexpected API bills
- No way to prioritize cost vs features
- Could make expensive features without realizing

**Mitigation:**
- Define monthly budget (e.g., $50/month)
- Add cost tracking dashboard
- Alert at 80% of budget
- Optimize expensive prompts first

---

## Risk Matrix

| Risk | Probability | Impact | Severity | Mitigation Priority |
|------|-------------|--------|----------|---------------------|
| Phase 3 not complete | High | High | 🔴 Critical | 1 |
| Voice profile quality poor | Medium | High | 🟡 High | 2 |
| SQLite schema incomplete | Medium | Medium | 🟡 Medium | 3 |
| No testing strategy | High | High | 🔴 Critical | 1 |
| Cost overruns | Medium | Medium | 🟡 Medium | 4 |
| Gate failures | Medium | High | 🟡 High | 2 |
| Prompt version drift | Low | Medium | 🟢 Low | 5 |
| API rate limits | Low | Low | 🟢 Low | 6 |
| master_context.md staleness | Medium | Medium | 🟡 Medium | 4 |
| No rollback strategy | Low | High | 🟡 Medium | 3 |

---

## Mitigation Strategies

### Strategy 1: Complete Phase 3 First (CRITICAL)

**Action Items:**
1. [ ] ATS-FMT: Run DOCX through Jobscan (2-3 hours)
2. [ ] P2-TPL: Create corporate + startup templates (1 day)
3. [ ] P3-BAT: Build CSV batch runner (2-3 days)
4. [ ] FEED: Add outcome tracking to history.md (1 day)

**Timeline:** 4-5 days
**Owner:** Primary developer
**Blocker for:** Phase V

---

### Strategy 2: Build Testing Infrastructure (CRITICAL)

**Action Items:**
1. [ ] Create `RES/tests/` directory
2. [ ] Add test fixtures (5 sample JDs + expected outputs)
3. [ ] Implement automated diff checker
4. [ ] Add regression test suite
5. [ ] Document testing process

**Timeline:** 2-3 days
**Owner:** Primary developer
**Blocker for:** All future phases (quality gates depend on this)

---

### Strategy 3: Define Voice Profile Process (HIGH)

**Action Items:**
1. [ ] Create voice profile template
2. [ ] Document selection criteria for writing samples
3. [ ] Add validation checklist
4. [ ] Create 2-3 example voice profiles
5. [ ] Test voice profile injection with current system

**Timeline:** 4-6 hours
**Owner:** Primary developer
**Blocker for:** Phase V

---

### Strategy 4: Fix SQLite Schema (MEDIUM)

**Action Items:**
1. [ ] Add `reflections` table to schema.sql
2. [ ] Add indexes for performance
3. [ ] Enable foreign key constraints
4. [ ] Create migration script
5. [ ] Test with 100+ mock opportunities

**Timeline:** 4-6 hours
**Owner:** Primary developer
**Blocker for:** Phase A, Phase C

---

### Strategy 5: Implement Feature Flags (MEDIUM)

**Action Items:**
1. [ ] Create `RES/config.py` with feature toggles
2. [ ] Add flags for: voice_enabled, polish_enabled, advisory_enabled, reflection_enabled
3. [ ] Update app.py to check flags before showing features
4. [ ] Document flag usage

**Timeline:** 2-3 hours
**Owner:** Primary developer
**Blocker for:** Safe rollouts

---

## Execution Recommendations

### Recommended Sequence (Revised)

**Week 1: Foundation Hardening**
- Day 1-2: Complete Phase 3 (ATS-FMT, P2-TPL)
- Day 3-4: Build testing infrastructure
- Day 5: Complete Phase 3 (P3-BAT, FEED)

**Week 2: Phase V Preparation**
- Day 1: Define voice profile process
- Day 2: Fix SQLite schema
- Day 3: Implement feature flags
- Day 4-5: Start Phase V (voice profile + BUL prompts)

**Week 3: Phase V Completion**
- Day 1-3: Complete Phase V (readability hints, A/B testing)
- Day 4: Phase V gate testing
- Day 5: Phase Vb spike (optional)

**Week 4: Phase A**
- Day 1-2: SQLite implementation
- Day 3-4: Wire generation + FEED callback
- Day 5: History table UI

**Week 5: Phase A Completion + Phase B Start**
- Day 1: Phase A gate testing
- Day 2-5: Phase B (fit brief + strategy prompts)

**Week 6: Phase B Completion + Phase C**
- Day 1-2: Phase B (Decide UI + gate testing)
- Day 3-5: Phase C (reflection journal + evidence miner)

**Total:** 6 weeks (30 working days)

### Critical Success Factors

1. **Complete Phase 3 before starting Phase V** (non-negotiable)
2. **Build testing infrastructure early** (enables all gates)
3. **Define voice profile process** (unblocks Phase V)
4. **Fix SQLite schema** (unblocks Phase A and C)
5. **Implement feature flags** (enables safe rollouts)
6. **Respect phase gates** (stop if quality degrades)

### Red Flags to Watch For

- 🚩 Phase 3 taking longer than 5 days
- 🚩 Voice profile A/B test shows <50% preference
- 🚩 Coaching note rate increases after Phase V
- 🚩 SQLite queries taking >1s
- 🚩 Cost per generation exceeds $0.50
- 🚩 Any gate failure (requires stop and reassess)

---

## Conclusion

**SPEC.md is well-structured but has critical execution gaps:**

### Must Fix Before Proceeding:
1. 🔴 Complete Phase 3 (4-5 days)
2. 🔴 Build testing infrastructure (2-3 days)
3. 🟡 Define voice profile process (4-6 hours)
4. 🟡 Fix SQLite schema (4-6 hours)

### Total Pre-Work: 7-9 days before Phase V can start

### Revised Timeline:
- **Original estimate:** 20-32 days to Phase C
- **Revised estimate:** 30-40 days to Phase C (including pre-work)

### Key Insight:
The spec is **feasible and logical**, but **underestimates preparation work**. The quality gate approach is excellent, but needs supporting infrastructure (testing, feature flags, rollback) to work effectively.

**Recommendation:** Invest 1-2 weeks in foundation hardening before starting Second Brain phases. This will make subsequent phases faster, safer, and more likely to pass gates.
