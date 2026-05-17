# Project Thema: Execution Roadmap (Revised)

**Based on:** SPEC.md + ISSUES_DEPENDENCIES_BLOCKERS.md analysis

**Key Finding:** SPEC.md underestimates preparation work by 7-9 days.

---

## Executive Summary

**Original Timeline:** 20-32 days to Phase C  
**Revised Timeline:** 30-40 days to Phase C  
**Additional Pre-Work:** 7-9 days (foundation hardening)

**Critical Blockers:**
- 🔴 Phase 3 incomplete (4-5 days)
- 🔴 No testing infrastructure (2-3 days)
- 🟡 Voice profile process undefined (4-6 hours)
- 🟡 SQLite schema incomplete (4-6 hours)

---

## Revised 6-Week Plan

### Week 1: Foundation Hardening (CRITICAL)

**Goal:** Complete Phase 3 + build testing infrastructure

| Day | Task | Hours | Status |
|-----|------|-------|--------|
| Mon | ATS-FMT: Run DOCX through Jobscan | 2-3 | [ ] |
| Mon | P2-TPL: Create corporate template | 3-4 | [ ] |
| Tue | P2-TPL: Create startup template | 3-4 | [ ] |
| Wed | Testing: Create test fixtures | 4 | [ ] |
| Wed | Testing: Implement diff checker | 3-4 | [ ] |
| Thu | P3-BAT: Build CSV batch runner | 6-8 | [ ] |
| Fri | FEED: Add outcome tracking | 4-6 | [ ] |
| Fri | Testing: Regression suite | 2-3 | [ ] |

**Deliverables:**
- ✅ Phase 3 complete (all tasks checked)
- ✅ Testing infrastructure operational
- ✅ 5 test fixtures with expected outputs
- ✅ Automated diff checker working

**Gate:** All Phase 3 tasks pass acceptance criteria

---

### Week 2: Phase V Preparation + Start

**Goal:** Unblock Phase V + start voice profile work

| Day | Task | Hours | Status |
|-----|------|-------|--------|
| Mon | Define voice profile creation process | 2-3 | [ ] |
| Mon | Create voice profile template | 2-3 | [ ] |
| Tue | Fix SQLite schema (add reflections, indexes) | 4-6 | [ ] |
| Wed | Implement feature flags (config.py) | 2-3 | [ ] |
| Wed | Create actual voice_profile.md | 3-4 | [ ] |
| Thu | V.1: Add {{VOICE_PROFILE}} injection | 4-6 | [ ] |
| Fri | V.2: Extend anti_fluff.md with BUL rules | 4-6 | [ ] |

**Deliverables:**
- ✅ Voice profile process documented
- ✅ SQLite schema complete
- ✅ Feature flags implemented
- ✅ voice_profile.md created
- ✅ Voice injection working

**Gate:** Voice profile injection doesn't break existing generation

---

### Week 3: Phase V Completion

**Goal:** Complete voice features + pass Phase V gate

| Day | Task | Hours | Status |
|-----|------|-------|--------|
| Mon | V.2: Add ai_tells.md (AI-tell phrases) | 3-4 | [ ] |
| Mon | V.2: Update all prompts with BUL rules | 3-4 | [ ] |
| Tue | V.3: Implement readability stats | 4-6 | [ ] |
| Tue | V.3: Add readability UI expander | 2-3 | [ ] |
| Wed | V.4 Gate: A/B test on 2 real JDs | 4-6 | [ ] |
| Thu | V.4 Gate: Automated diff check | 3-4 | [ ] |
| Thu | V.4 Gate: Coaching note rate check | 2-3 | [ ] |
| Fri | Vb Spike: Implement polish_pass() | 6-8 | [ ] |

**Deliverables:**
- ✅ BUL rules in all prompts
- ✅ Readability stats working
- ✅ Phase V gate passed (or failed with documented reasons)
- ✅ Polish pass spike complete (ship or kill decision)

**Gate:** 
- A/B test: >60% prefer new output
- No new ungrounded metrics
- Coaching note rate ≤ baseline
- Readability: Flesch-Kincaid 60-70

**Decision Point:** Ship or kill polish pass based on spike results

---

### Week 4: Phase A (Memory)

**Goal:** Implement SQLite opportunity tracking

| Day | Task | Hours | Status |
|-----|------|-------|--------|
| Mon | A.2: Create brain_store.py (init_db, CRUD) | 6-8 | [ ] |
| Tue | A.3: Wire generation → upsert_opportunity | 4-6 | [ ] |
| Tue | A.3: Handle DB errors gracefully | 2-3 | [ ] |
| Wed | A.4: Add "Update Status" button + dropdown | 4-6 | [ ] |
| Thu | A.5: Create "Application History" tab | 4-6 | [ ] |
| Thu | A.5: Implement st.data_editor table | 3-4 | [ ] |
| Fri | A.6 Gate: DB stability testing | 4-6 | [ ] |

**Deliverables:**
- ✅ brain_store.py operational
- ✅ Generation auto-logs to DB
- ✅ Status updates working
- ✅ History table UI functional

**Gate:**
- DB survives restart (no data loss)
- No latency regression >1s
- Corrupted DB fails gracefully
- Table UI loads <2s for 100 opportunities

---

### Week 5: Phase B (Advisory)

**Goal:** Implement fit brief + strategy prompts

| Day | Task | Hours | Status |
|-----|------|-------|--------|
| Mon | B.1: Create fit_brief.md prompt | 4-6 | [ ] |
| Mon | B.1: Test fit brief on 3 JDs | 2-3 | [ ] |
| Tue | B.2: Create strategy.md prompt | 4-6 | [ ] |
| Tue | B.2: Test strategy on 3 JDs | 2-3 | [ ] |
| Wed | B.3: Add "Decide" tab in Streamlit | 4-6 | [ ] |
| Thu | B.4: Implement context management | 3-4 | [ ] |
| Thu | B.4: Add master_context.md reload | 2-3 | [ ] |
| Fri | B.5 Gate: Advisory quality testing | 4-6 | [ ] |

**Deliverables:**
- ✅ Fit brief prompt working
- ✅ Strategy prompt working
- ✅ Decide tab functional
- ✅ Context management implemented

**Gate:**
- Outputs include risks/gaps every time
- No contradictions with master_context.md (5 test cases)
- No sycophantic language without evidence
- 3/5 test users find advice useful

---

### Week 6: Phase C (Reflection)

**Goal:** Implement reflection journal + evidence miner

| Day | Task | Hours | Status |
|-----|------|-------|--------|
| Mon | C.1: Add "Reflect" tab in Streamlit | 3-4 | [ ] |
| Mon | C.1: Create reflections table/file storage | 3-4 | [ ] |
| Tue | C.2: Create evidence miner prompt | 4-6 | [ ] |
| Tue | C.2: Test evidence miner on 3 reflections | 2-3 | [ ] |
| Wed | C.3: Add privacy warning UI | 2-3 | [ ] |
| Wed | C.3: Add optional redact field | 2-3 | [ ] |
| Thu | C.4 Gate: No auto-merge verification | 4-6 | [ ] |
| Fri | Documentation + final testing | 6-8 | [ ] |

**Deliverables:**
- ✅ Reflection journal working
- ✅ Evidence miner producing suggestions
- ✅ Privacy warnings in place
- ✅ Phase C gate passed

**Gate:**
- Zero automatic writes to master_context.md
- Evidence suggestions are copy-paste only
- User can review and edit before adding

---

## Dependency Chart

```
Week 1: Foundation Hardening
├── Phase 3 Complete ✓
└── Testing Infrastructure ✓
    ↓
Week 2: Phase V Prep
├── Voice Profile Process ✓
├── SQLite Schema Fixed ✓
└── Feature Flags ✓
    ↓
Week 3: Phase V
├── Voice Injection ✓
├── BUL Prompts ✓
└── Gate Passed ✓
    ↓
Week 4: Phase A
├── SQLite Implementation ✓
└── Gate Passed ✓
    ↓
Week 5: Phase B (depends on A)
├── Fit Brief ✓
├── Strategy ✓
└── Gate Passed ✓
    ↓
Week 6: Phase C (depends on A)
├── Reflection Journal ✓
├── Evidence Miner ✓
└── Gate Passed ✓
```

---

## Risk Mitigation Checkpoints

### End of Week 1 Checkpoint
**Question:** Is Phase 3 complete and testing infrastructure working?
- ✅ Yes → Proceed to Week 2
- ❌ No → Extend Week 1, delay subsequent weeks

### End of Week 3 Checkpoint
**Question:** Did Phase V pass its gate?
- ✅ Yes → Proceed to Week 4
- ❌ No → Stop, narrow scope, re-test (could add 1-2 weeks)

### End of Week 4 Checkpoint
**Question:** Did Phase A pass its gate?
- ✅ Yes → Proceed to Week 5 and 6 (can parallelize B and C)
- ❌ No → Stop, fix issues, re-test (could add 1 week)

### End of Week 5 Checkpoint
**Question:** Did Phase B pass its gate?
- ✅ Yes → Proceed to Week 6
- ❌ No → Stop, narrow scope, re-test

### End of Week 6 Checkpoint
**Question:** Did Phase C pass its gate?
- ✅ Yes → Second Brain complete!
- ❌ No → Stop, narrow scope, re-test

---

## Success Criteria

### Week 1 Success
- [ ] All Phase 3 tasks checked off
- [ ] 5 test fixtures created
- [ ] Automated diff checker working
- [ ] Regression tests passing

### Week 3 Success (Phase V Gate)
- [ ] A/B test: >60% prefer new output
- [ ] No new ungrounded metrics (automated check passes)
- [ ] Coaching note rate ≤ baseline
- [ ] Readability: Flesch-Kincaid 60-70

### Week 4 Success (Phase A Gate)
- [ ] DB survives restart
- [ ] No latency regression >1s
- [ ] Corrupted DB fails gracefully
- [ ] Table UI loads <2s for 100 opportunities

### Week 5 Success (Phase B Gate)
- [ ] Outputs include risks/gaps every time
- [ ] No contradictions with master_context.md
- [ ] No sycophantic language without evidence
- [ ] 3/5 test users find advice useful

### Week 6 Success (Phase C Gate)
- [ ] Zero automatic writes to master_context.md
- [ ] Evidence suggestions are copy-paste only
- [ ] User can review and edit before adding

---

## Budget & Resources

### Time Budget
- **Total:** 30-40 working days (6-8 weeks)
- **Per week:** 40 hours (full-time)
- **Contingency:** 20% buffer for gate failures and rework

### Cost Budget
- **Current:** $0.08-0.17 per generation
- **Phase V:** +$0.05-0.10 (voice profile)
- **Phase Vb:** +$0.08-0.17 (polish pass, if shipped)
- **Phase B:** +$0.10-0.15 (fit brief + strategy)
- **Total:** $0.30-0.60 per generation

**Monthly budget recommendation:** $50-100 (assumes 100-200 generations/month)

### Developer Resources
- **Primary developer:** 1 full-time
- **AI coding assistants:** Cursor, Windsurf (recommended)
- **Testing support:** Manual testing for gates (4-6 hours per gate)

---

## Emergency Procedures

### If Phase 3 Takes >5 Days
- **Action:** Defer P3-BAT (batch runner) to later
- **Impact:** Can still proceed to Phase V
- **Timeline:** No change

### If Phase V Gate Fails
- **Action:** Stop, analyze failure, narrow scope
- **Options:**
  1. Remove voice profile, keep BUL prompts only
  2. Simplify voice profile (fewer samples)
  3. Skip Phase Vb entirely
- **Timeline:** +1-2 weeks for rework

### If Phase A Gate Fails
- **Action:** Stop, fix DB issues, re-test
- **Impact:** Blocks Phase B and C
- **Timeline:** +1 week for fixes

### If Budget Exceeded
- **Action:** Optimize expensive prompts
- **Options:**
  1. Use GPT-3.5 for non-critical features
  2. Cache API responses more aggressively
  3. Reduce token limits
- **Timeline:** No change, but quality may degrade

---

## Conclusion

**Revised timeline is realistic:** 6 weeks (30-40 days) to complete Second Brain through Phase C.

**Critical success factors:**
1. Complete Phase 3 first (non-negotiable)
2. Build testing infrastructure early
3. Respect phase gates (stop if quality degrades)
4. Monitor costs and performance
5. Document decisions and learnings

**Key insight:** The original SPEC.md was optimistic but achievable with proper preparation. The 7-9 days of pre-work (Week 1-2) will make subsequent phases faster and safer.

**Recommendation:** Follow this revised roadmap. It accounts for all blockers, dependencies, and risks identified in the deep analysis.
