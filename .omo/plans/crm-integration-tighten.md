# CRM Integration Tighten

## TL;DR

> **Quick Summary**: Tighten 5 integration points between the CRM Pipeline tab, RES resume generation, and HUNT-AGENT job scraper in the Streamlit app, reducing friction when flowing data between subsystems.
>
> **Deliverables**:
> - `tab_tempus` → `tab_crm` rename across app.py
> - Sidebar cadence widget (day-of-week GTM hints visible on every tab)
> - Session-state tab index tracking + CRM→Job Details redirect with persistent notification
> - RES→CRM auto-advance (stage to `applied` + log outreach) on successful resume generation
> - HUNT-AGENT→CRM promote button per lead card in Job Search tab
>
> **Estimated Effort**: Short (5 small changes, ~1-2 hrs total)
> **Parallel Execution**: YES - 2 waves
> **Critical Path**: None — all tasks are independent

---

## Context

### Original Request
Tighten the seams between 3 existing subsystems in the Streamlit job-hunt app: the resume generator (RES/), the pipeline CRM (CRM/), and the job scraper (HUNT-AGENT/). Five changes identified as high/medium priority.

### Interview Summary
**Key Discussions**:
- **Company matching** for auto-advance: **Exact name match** (case-insensitive) — only advance when `company_name` in the generate tab exactly matches a CRM company name.
- **Tab auto-switch**: Streamlit `st.tabs()` does not support programmatic tab switching in any version. Chosen approach: use `st.session_state.active_tab` to flag intent, plus a persistent visual notification in the target tab that's impossible to miss. User will click the tab manually (one click) with data pre-filled and waiting.
- **Sidebar placement**: Cadence widget goes in the sidebar and appears **on every tab** (not Pipeline-only), reinforcing the GTM cadence across the entire app.
- **Test strategy**: No unit tests — agent executes QA by running the app and clicking through each flow.

### Research Findings
- `mark_published()` in `CRM/crm/services/artifacts.py:56` **already writes to disk** — artifact file saving is DONE, removed from scope.
- `import_from_leads()` in `CRM/crm/services/companies.py:138` exists but is **not called from any UI** — needs wiring into hunt_tab.py.
- `tab_tempus` appears in **2 places** in app.py: tabs assignment (line 852) and the `with tab_tempus:` block (line 1837).
- Generate success block ends at line 1308 (`status.update(label="Generation complete!")`) — ideal hook point for CRM auto-advance.
- HUNT-AGENT lead cards render at RES/hunt_tab.py:241-270 with company name, title, URL, and stage selector.

---

## Work Objectives

### Core Objective
Eliminate friction between the 3 subsystems so data flows one direction (scraper→CRM→resume generator) without manual re-entry.

### Concrete Deliverables
1. Variable rename in app.py (2 edits)
2. Sidebar widget added to app.py + cadence hint removed from crm_tab.py
3. Session-state tab index tracking + CRM "Generate Resume" redirect with persistent notification
4. Auto-advance hook after resume generation that matches company → advance stage → log outreach
5. "Promote to CRM" button on each lead card in hunt_tab.py

### Must Have
- All changes must survive `streamlit run app.py` without errors
- Auto-advance must NOT block resume generation if CRM lookup fails (wrapped in try/except)
- Sidebar cadence widget must not display at startup if CRM DB isn't initialized yet

### Must NOT Have (Guardrails)
- No changes to CRM data model (no new tables/columns)
- No rearchitecture of the tab system — tabs remain `st.tabs()` with the same layout
- No new Python dependencies
- No changes to RES/generator.py or RES/llm_client.py
- No changes to HUNT-AGENT/scraper/ internals

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed.
> The app must be running via `streamlit run app.py` for UI checks.

### Test Decision
- **Infrastructure exists**: NO (Streamlit UI tests)
- **Automated tests**: None
- **Agent QA**: YES — run the app and verify each change by interacting with the UI

### QA Policy
Every task includes agent-executed QA scenarios. Evidence captured to `.omo/evidence/`.

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start immediately — ALL INDEPENDENT):
├── Task 1: tab_tempus → tab_crm rename [quick]
├── Task 2: Sidebar cadence widget [quick]
├── Task 3: Tab index tracking + CRM→Job Details redirect [quick]
├── Task 4: HUNT-AGENT → CRM promote button [quick]
└── Task 5: RES → CRM auto-advance [quick]

Wave FINAL (After ALL tasks):
├── F1: Plan compliance audit (self-check each change against spec)
├── F2: Code quality review (no dead code, no errors)
├── F3: Real manual QA (run app, click through ALL 5 flows)
└── F4: Scope fidelity check (nothing beyond spec was built)

Critical Path: None — all tasks are independent
Parallel Speedup: ~80% faster than sequential (5 tasks × 1 wave)
Max Concurrent: 5 (all domain-independent files)
```

### Agent Dispatch Summary
- Wave 1: 5 × `quick` — all are small, well-understood edits to existing files

---

## TODOs

- [ ] 1. Rename `tab_tempus` → `tab_crm` in app.py

  **What to do**:
  - Change line 852: `tab_tempus` → `tab_crm` in the tuple unpacking from `st.tabs()`
  - Change line 1837: `with tab_tempus:` → `with tab_crm:`
  - Both are simple variable renames — no functional change

  **Must NOT do**:
  - Do not change the displayed tab label (still "🎯 Pipeline")
  - Do not rename anything in CRM/ package or crm_tab.py

  **Recommended Agent Profile**:
  > - **Category**: `quick`
  >   - Reason: 2-line rename, zero risk, trivial scope
  > - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (all tasks)
  - **Blocks**: None
  - **Blocked By**: None

  **References**:
  - `app.py:852` — `tab_tempus` in tabs tuple unpacking
  - `app.py:1837` — `with tab_tempus:` usage block

  **Acceptance Criteria**:
  - `grep -n "tab_tempus" app.py` returns 0 matches
  - `streamlit run app.py` starts without NameError

  **QA Scenarios**:
  ```
  Scenario: Verify rename doesn't break app startup
    Tool: Bash
    Preconditions: app.py exists at project root
    Steps:
      1. Run `grep -n "tab_tempus" app.py` — must return 0 results
      2. Run `streamlit run app.py &` — check process starts without Python traceback (wait 5s, check stderr)
      3. Kill streamlit process
    Expected Result: No tab_tempus references remain. App starts without NameError.
    Failure Indicators: grep returns matches, app crashes on startup
    Evidence: .omo/evidence/task-1-rename-grep.txt
  ```

  **Commit**: YES (groups with Task 2, 3, 4, 5)
  - Message: `refactor(app): rename tab_tempus to tab_crm and tighten CRM integration`
  - Files: `app.py`, `RES/hunt_tab.py`, `CRM/crm/ui/crm_tab.py`

---

- [ ] 2. Add sidebar cadence widget to app.py

  **What to do**:
  - In `app.py`, add a sidebar section (before or around the existing sidebar provider/API key area) that shows:
    - Current day of week
    - Cadence hint: Mon=Pipeline Review, Tue-Thu=Outreach, Fri=Publish
    - Navigation hint: "→ Go to Pipeline tab"
  - Copy the day-of-week logic from `CRM/crm/ui/crm_tab.py:93-104` (the `dow`/`day_names`/`cadence_hints` block)
  - Remove the inline cadence hint from `CRM/crm/ui/crm_tab.py` (lines 92-104)
  - The widget should gracefully handle: if CRM DB not initialized, show a generic day-of-week hint without crashing

  **Must NOT do**:
  - Do not obstruct the sidebar provider/API key section (keep it below or beside)
  - Do not import CRM modules in the sidebar — keep cadence logic self-contained (day-of-week calculation is pure Python)

  **Recommended Agent Profile**:
  > - **Category**: `quick`
  >   - Reason: Moving existing logic between files, minor UI addition
  > - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (all tasks)
  - **Blocks**: None
  - **Blocked By**: None

  **References**:
  - `CRM/crm/ui/crm_tab.py:92-104` — Existing day-of-week cadence logic to move
  - `app.py` — Locate sidebar section (search for `st.sidebar`) for placement

  **Acceptance Criteria**:
  - Sidebar shows current day of week + cadence hint on every tab
  - CRM tab no longer shows duplicate inline hint
  - No errors when CRM DB doesn't exist

  **QA Scenarios**:
  ```
  Scenario: Sidebar shows cadence hint
    Tool: interactive_bash (tmux) + Streamlit
    Preconditions: App is running at localhost:8501
    Steps:
      1. Curl app homepage, grep for day-name in response (e.g., "Mon", "Tue")
      2. Navigate to each tab, verify sidebar widget persists
      3. Verify CRM tab does NOT have a duplicate inline hint
    Expected Result: Sidebar shows day + cadence on every tab. No inline hint in CRM tab.
    Evidence: .omo/evidence/task-2-sidebar-widget.txt
  ```

---

- [ ] 3. Session state tab index tracking + CRM→Job Details redirect

  **What to do**:
  This task addresses the "Generate Resume" button in the CRM tab. Since Streamlit's `st.tabs()` does not support programmatic tab switching, implement the best-available workaround:

  1. Add session state tracking:
     ```python
     if "active_tab" not in st.session_state:
         st.session_state.active_tab = 0
     ```
     This can be placed near the top of app.py with other session state init logic.

  2. In `CRM/crm/ui/crm_tab.py`, update the "Generate Resume" button (around line 301-305):
     - Keep setting `st.session_state.company_name` and `st.session_state.jd_url`
     - Also set `st.session_state.active_tab = 0` to flag intent
     - Set `st.session_state._crm_redirect = True` as a flag for the notification

  3. In `app.py`, in the Job Details tab (around line 865), add a persistent notification:
     ```python
     if st.session_state.pop("_crm_redirect", False):
         st.success("📌 Ready to generate — company pre-filled from CRM. Click Generate when ready.")
     ```
     This shows a prominent green banner that disappears after the first render.

  4. The `active_tab` value can be used in future enhancements but currently serves as intent tracking.

  **Must NOT do**:
  - Do NOT try to use `st.experimental_set_query_params` or JavaScript hacks — Streamlit doesn't support programmatic tab switching
  - Do NOT change the `st.tabs()` call or restructure existing tabs
  - Do NOT add any JS/CSS workarounds

  **Recommended Agent Profile**:
  > - **Category**: `quick`
  >   - Reason: Small session-state wiring, well-understood Streamlit pattern
  > - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (all tasks)
  - **Blocks**: None
  - **Blocked By**: None

  **References**:
  - `app.py:865` — Job Details tab content area (where to add notification)
  - `CRM/crm/ui/crm_tab.py:301-305` — "Generate Resume" button (where to set active_tab)
  - `app.py` — top of file for session state init (look for existing `if "..." not in st.session_state` patterns)

  **Acceptance Criteria**:
  - Clicking "Generate Resume" in CRM tab → sets session state + shows green notification on Job Details tab
  - Pre-filled company name and role visible in Job Details form fields
  - No errors on page render
  - Notification only appears once (cleared by session_state.pop)

  **QA Scenarios**:
  ```
  Scenario: CRM → Job Details redirect flow
    Tool: interactive_bash (tmux) + Streamlit
    Preconditions: App running, CRM seeded with companies
    Steps:
      1. Open Pipeline tab in Streamlit
      2. Expand a company card with a company
      3. Click "Generate Resume" button
      4. Navigate to Job Details tab
      5. Check: Company Name field is pre-filled
      6. Check: Green notification banner visible "Ready to generate..."
      7. Refresh page → notification is gone (state was popped)
    Expected Result: Company data pre-fills, notification guides user, works on one click
    Evidence: .omo/evidence/task-3-tab-redirect.txt
  ```

---

- [ ] 4. Add HUNT-AGENT → CRM promote button in hunt_tab.py

  **What to do**:
  In `RES/hunt_tab.py`, in the lead card section (around lines 241-270), add a "Promote to CRM" button next to the existing "Use for Gen" button. This button calls `crm.services.companies.import_from_leads()` to promote the lead to a CRM company.

  Specific changes:

  1. Add the import at the top of `hunt_tab.py`:
     ```python
     from crm.services.companies import import_from_leads
     ```

  2. In the lead card cols (around line 262), add a new button column or extend existing cols:
     ```python
     with cols[2]:
         # Existing "Use for Gen" button (already here)
         # Add "Promote to CRM" button below or alongside
         if st.button("+ CRM", key=f"hunt_crm_{l.id}", help="Add to Pipeline CRM"):
             result = import_from_leads(l)
             if result:
                 st.success(f"✅ {l.company} added to CRM")
             else:
                 st.warning(f"⚠️ {l.company} already in CRM")
             st.rerun()
     ```

  3. Handle the response: `import_from_leads` returns a dict on success, `None` on duplicate.

  **Must NOT do**:
  - Do not modify any HUNT-AGENT/scraper/ internals
  - Do not add a bulk promote button (per-lead only)
  - Do not auto-promote on scrape — this is a manual action

  **Recommended Agent Profile**:
  > - **Category**: `quick`
  >   - Reason: Single button addition with existing backend function
  > - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (all tasks)
  - **Blocks**: None
  - **Blocked By**: None

  **References**:
  - `CRM/crm/services/companies.py:138-156` — `import_from_leads()` function (exists, needs UI wiring)
  - `RES/hunt_tab.py:241-270` — Lead card rendering (where to add button)
  - `RES/hunt_tab.py:26` — `from scraper.leads import load_leads` (import pattern to follow for adding CRM import)

  **Acceptance Criteria**:
  - Each lead card has a "+ CRM" or "Promote to CRM" button
  - Clicking it adds the lead's company to CRM (visible in Pipeline tab)
  - If company already exists, shows warning (not error)
  - Button updates without page reload

  **QA Scenarios**:
  ```
  Scenario: Promote lead to CRM
    Tool: interactive_bash (tmux) + Streamlit
    Preconditions: App running, HUNT-AGENT has leads (from previous scrape)
    Steps:
      1. Open Job Search tab
      2. Find a lead card in the Leads section
      3. Click "+ CRM" button
      4. Check: Success message shows "added to CRM"
      5. Switch to Pipeline tab → new company appears in "Sourced" stage
      6. Try promoting the same lead again → warning shows "already in CRM"
    Expected Result: Lead promotes to CRM cleanly, duplicate detection works
    Evidence: .omo/evidence/task-4-promote-crm.txt
  ```

---

- [ ] 5. Add RES → CRM auto-advance on successful resume generation

  **What to do**:
  After resume generation completes successfully (at the point where `st.session_state.gen_results` is set, around line 1308-1310 in app.py), add a hook that:

  1. Checks if `company_name` is non-empty AND exists in CRM (exact match, case-insensitive)
  2. If match found: 
     - Call `move_stage(company_id, "applied")` to advance the company stage
     - Call `log_outreach(company_id, "application", "sent", body="Resume submitted")` to log the application
  3. If no match: silently skip (user may not be tracking this company in CRM)
  4. Wrap the entire hook in try/except so CRM issues never crash resume generation

  Implementation outline:
  ```python
  # --- CRM auto-advance hook ---
  if company_name:
      try:
          from crm.db import init_db
          from crm.services.companies import get_company_by_name
          from crm.services.pipeline import move_stage
          from crm.services.outreach import log_outreach
          init_db()
          crm_co = get_company_by_name(company_name)
          if crm_co:
              move_stage(crm_co["id"], "applied")
              log_outreach(crm_co["id"], "application", "sent", body="Resume submitted via app")
      except Exception:
          pass  # CRM error must never block resume generation
  ```

  Note: `get_company_by_name` does not exist yet — you need to add it to `CRM/crm/services/companies.py`. It should:
  - Accept a name string
  - Query companies with case-insensitive exact match (`Company.name.ilike(name)`)
  - Return the first match or None

  **Must NOT do**:
  - Do NOT import CRM at the top of app.py (lazy import in the hook to avoid startup dependency)
  - Do NOT crash if CRM DB doesn't exist or is empty
  - Do NOT add fuzzy/partial matching — exact match only
  - Do NOT auto-advance if no company_name was entered

  **Recommended Agent Profile**:
  > - **Category**: `quick`
  >   - Reason: Small hook function, one new service method, well-defined scope
  > - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (all tasks)
  - **Blocks**: None
  - **Blocked By**: None

  **References**:
  - `app.py:1300-1310` — Right after `status.update(label="Generation complete!")`, before `st.session_state.gen_results`
  - `CRM/crm/services/companies.py` — Where to add `get_company_by_name()`
  - `CRM/crm/models.py` — `Company.name` field definition for query
  - `CRM/crm/services/companies.py:10-30` — Existing CRUD patterns to follow for the new function

  **Acceptance Criteria**:
  - Generating a resume with a company_name that matches a CRM company → company advances to "applied" stage
  - Generating a resume with a non-CRM company name → no error, nothing happens
  - Generating a resume with no company_name → no error, nothing happens
  - If CRM DB is missing/corrupt → resume generation succeeds, error silently swallowed

  **QA Scenarios**:
  ```
  Scenario: Auto-advance on resume generation
    Tool: interactive_bash (tmux) + Streamlit
    Preconditions: App running, CRM has a seeded company (e.g., "Flexport" or similar), API key configured
    Steps:
      1. Open Job Details tab
      2. Enter company_name that matches a CRM company exactly (e.g., "Flexport")
      3. Enter/paste a job description (can be minimal)
      4. Click Generate
      5. Wait for generation to complete
      6. Switch to Pipeline tab → verify company is now in "Applied" stage
      7. Check outreach log for "Resume submitted" entry
    Expected Result: Company auto-advances to applied. Outreach logged.
    Evidence: .omo/evidence/task-5-auto-advance.txt

  Scenario: No CRM match → graceful skip
    Tool: Bash + Streamlit
    Preconditions: Same as above, but use a non-CRM company name
    Steps:
      1. Generate resume with company_name="Some Unknown Company"
      2. Generation completes without CRM-related errors
    Expected Result: No errors. CRM unaffected.
    Evidence: .omo/evidence/task-5-no-match.txt
  ```

  **Commit**: YES (groups with all tasks)
  - Message: `refactor(app): tighten CRM integration across RES, HUNT-AGENT, and CRM tabs`
  - Files: `app.py`, `RES/hunt_tab.py`, `CRM/crm/ui/crm_tab.py`, `CRM/crm/services/companies.py`
  - Pre-commit: `streamlit run app.py &` (quick smoke test, kill after 5s)

---

## Final Verification Wave

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each task: verify the implementation matches "What to do" and respects "Must NOT do." Check that no file outside the listed scope was modified.
  Output: `Tasks [N/5 compliant] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** — `quick`
  Run `grep -rn "tab_tempus" app.py` (should be 0). Check for: `try: ... except: pass` (ensure it's `except Exception: pass`), unused imports, console.log in Streamlit code. No build/type tools available for this Python project.
  Output: `Rename [PASS/FAIL] | Imports [CLEAN/ISSUES] | Error handling [PASS/FAIL] | VERDICT`

- [ ] F3. **Real Manual QA** — `quick`
  Run the app (`streamlit run app.py &`). Test all 5 changes:
  1. Navigate all tabs — no NameError related to tab_tempus
  2. Sidebar shows cadence hint on every tab, CRM tab has no duplicate inline hint
  3. Click "Generate Resume" in CRM → Job Details tab shows notification + pre-filled data
  4. Click "+ CRM" on a lead → company appears in Pipeline tab
  5. Generate resume with a CRM-tracked company → stage advances to "applied"
  Save evidence to `.omo/evidence/final-qa/`.
  Output: `Scenarios [N/5 pass] | VERDICT`

- [ ] F4. **Scope Fidelity Check** — `deep`
  For each task: read the diff (`git diff`) against "What to do" and "Must NOT do." Verify nothing beyond the 5 changes was added. Check no packages changed, no schema changes, no scraper internals modified.
  Output: `Tasks [N/5 compliant] | Creep [CLEAN/ISSUES] | VERDICT`

---

## Commit Strategy

- **1 commit** (all 5 tasks — they're interdependent in the same app session):
  ```
  refactor(app): tighten CRM integration across RES, HUNT-AGENT, and CRM tabs

  - Rename tab_tempus → tab_crm
  - Add sidebar cadence widget (day-of-week GTM hints)
  - Add session-state tab tracking + CRM→Job Details redirect
  - Add HUNT-AGENT→CRM promote button per lead card
  - Add RES→CRM auto-advance on resume generation (stage→applied + outreach log)
  ```

---

## Success Criteria

### Verification Commands
```bash
streamlit run app.py  # App starts without errors
grep -rn "tab_tempus" app.py  # Returns 0 results
```

### Final Checklist
- [ ] App starts without NameError
- [ ] Sidebar shows cadence hint on every tab
- [ ] CRM tab has no duplicate inline cadence hint
- [ ] "Generate Resume" in CRM pre-fills Job Details + shows notification
- [ ] "+ CRM" button promotes leads to Pipeline tab
- [ ] Resume generation auto-advances CRM company to "applied"
- [ ] Auto-advance silently skips if no CRM match
- [ ] No new Python dependencies
- [ ] No changes to RES/generator.py, RES/llm_client.py, or HUNT-AGENT/scraper/
