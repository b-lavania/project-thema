# BOOTCAMP Webapp — Convert 30-Day PM Shock Cycle into Streamlit Interactive App

## TL;DR

> **Quick Summary**: Convert the existing BOOTCAMP/ markdown files (30-day PM shock cycle with 8 drill types, daily scorecards, weekly audits, and a scoring rubric) into a standalone interactive Streamlit webapp at BOOTCAMP/app.py.
>
> **Deliverables**:
> - `BOOTCAMP/app.py` — Streamlit entrypoint
> - `BOOTCAMP/bootcamp/` — Python package (calendar, data, scoring, timer, drills modules)
> - `BOOTCAMP/data/` — User data directory (scorecards, progress.json, artifacts)
> - 7 in-app tabs: Today's Focus, Progress Dashboard, Weekly Audit, Drill Library, Calendar View, Artifacts, Export
>
> **Estimated Effort**: Medium (10-14 tasks, ~3 waves)
> **Parallel Execution**: YES — 3 waves, max 6 concurrent
> **Critical Path**: Calendar parser → Data module → Today's Focus tab → app.py integration

---

## Context

### Original Request
Convert BOOTCAMP/ (a 30-day PM shock cycle consisting of README.md, 30-day-calendar.md, daily-scorecard.md, scoring-rubric.md, weekly-audit.md, and 8 drill templates in drills/) into a standalone webapp for interactive daily use.

### Interview Summary
**Key Discussions**:
- **Core experience**: Guided day-by-day tracker showing "Today is Day N of 30" with daily plan, fillable drill forms, and auto-scoring scorecard
- **Persistence**: Scorecards saved as `data/day-N-scorecard.md` files, progress aggregated to `data/progress.json` cache
- **Integration**: Standalone app at `BOOTCAMP/app.py` (not a tab in the main app)
- **All features in one build**: fill-in drill forms, auto-scoring scorecard, progress dashboard, countdown timer per drill, public artifact helper (saves to `data/artifacts/`), auto-populated weekly audit, accountability partner export
- **No tests, no LLM, no multi-user, no notifications, no mobile, no cloud sync**

### Self-Review Gap Analysis
**Gaps Identified and Resolved**:
- **Day progression**: Default to manual advance — user marks a day complete, app advances. On relaunch, resume from last incomplete day (stored in progress.json)
- **Drill timer durations**: Hardcoded per drill type (Drill 1: 15min, D2: 10min, D3: 7min, D4: 10min, D5: 10min, D6: 8min, D7: 10min, D8: 5min)
- **Accountability export**: Simple markdown summary with daily scores, weekly grades, and artifact list — displayed in-app for copy-paste
- **Drill 5 table**: Uses `st.data_editor` for the editable 10-task table
- **Calendar start**: Bootcamp starts on Day 1. No date binding — days are sequential (1–30)

---

## Work Objectives

### Core Objective
Build a standalone Streamlit webapp that makes the 30-day PM shock cycle interactive — forms replace manual markdown editing, scoring is automatic, progress is visualized.

### Concrete Deliverables
- `BOOTCAMP/app.py` — Streamlit entrypoint with 7 tabs
- `BOOTCAMP/bootcamp/__init__.py` — Package init
- `BOOTCAMP/bootcamp/calendar.py` — Parse 30-day-calendar.md into structured data
- `BOOTCAMP/bootcamp/data.py` — Scorecard save/load, progress.json read/write
- `BOOTCAMP/bootcamp/scoring.py` — Daily/weekly/camp scoring from rubric
- `BOOTCAMP/bootcamp/timer.py` — Countdown timer component
- `BOOTCAMP/bootcamp/drills.py` — Render drill forms from templates
- `BOOTCAMP/bootcamp/state.py` — Session state + day progression management
- `BOOTCAMP/data/` — User data directory (created on first run, gitignored)

### Definition of Done
- [ ] `streamlit run BOOTCAMP/app.py` starts the app
- [ ] Landing page shows "Today is Day N of 30" with that day's focus, 3 morning blocks, HIIT drill assignments, and a scorecard form
- [ ] Scorecard auto-calculates daily score from checkboxes and fields
- [ ] Progress dashboard shows daily scores as bar chart + grade history
- [ ] Weekly audit auto-populates from saved scorecards
- [ ] Drill Library shows all 8 drills with fillable forms
- [ ] Calendar View shows 30-day overview with completion status
- [ ] Artifacts tab saves/view public artifacts (4 weekly + extras)
- [ ] Export tab generates accountability partner report
- [ ] Timer starts/stops per drill with configurable durations

### Must Have
- [ ] Every scorecard field from `daily-scorecard.md` must have a UI counterpart
- [ ] All 8 drill templates must render as fillable forms with proper field types
- [ ] Scoring must match scoring-rubric.md exactly (60 daily base + 20 bonus - penalties)
- [ ] Progress must persist across sessions (progress.json)
- [ ] Original markdown files in BOOTCAMP/ must NOT be modified

### Must NOT Have (Guardrails)
- [x] NO LLM calls or AI generation of any kind
- [x] NO user authentication or multi-user support
- [x] NO database (SQLite, PostgreSQL, etc.) — file-based persistence only
- [x] NO mobile/responsive design or PWA features
- [x] NO push notifications or email
- [x] NO cloud sync or remote storage
- [x] NO modification of existing BOOTCAMP/*.md files (read-only)
- [x] NO tests (unittest/pytest) — QA verification only
- [x] NO external API dependencies

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: YES (unittest in RES/, but NOT used for BOOTCAMP)
- **Automated tests**: None — per user request
- **Framework**: N/A
- **QA policy**: Agent-executed scenarios only (see each task)

### QA Policy
Every task includes agent-executed QA scenarios run via `streamlit run BOOTCAMP/app.py` and interactive_bash (tmux) or Playwright for UI interaction.
Evidence saved to `.omo/evidence/task-{N}-{scenario-slug}.{ext}`.

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately — foundation modules, ALL PARALLEL):
├── Task 1: bootcamp/ package scaffold + calendar.py [quick]
├── Task 2: bootcamp/data.py — scorecard save/load + progress.json [quick]
├── Task 3: bootcamp/scoring.py — daily/weekly/camp scoring [quick]
├── Task 4: bootcamp/timer.py — countdown timer component [quick]
├── Task 5: bootcamp/drills.py — drill form rendering [unspecified-high]
└── Task 6: bootcamp/state.py — session state + day progression [quick]

Wave 2 (After Wave 1 — 7 tab renderers, ALL PARALLEL):
├── Task 7: Today's Focus tab (main day experience) [unspecified-high]
├── Task 8: Progress Dashboard tab [quick]
├── Task 9: Weekly Audit tab [quick]
├── Task 10: Drill Library tab [quick]
├── Task 11: Calendar View tab [quick]
├── Task 12: Artifacts tab [quick]
└── Task 13: Export tab [quick]

Wave 3 (After Wave 2 — integration):
├── Task 14: app.py entrypoint + wire everything [unspecified-high]
└── Task 15: Styling, polish, data dir creation, .gitignore [quick]

Wave FINAL (After ALL tasks — 4 parallel reviews, then user okay):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real manual QA (unspecified-high)
└── Task F4: Scope fidelity check (deep)
→ Present results → Get explicit user okay

Critical Path: Task 1 → Task 7 → Task 14 → Task 15 → F1-F4 → user okay
Parallel Speedup: ~60% faster than sequential
Max Concurrent: 6 (Wave 1)
```

### Dependency Matrix

- **1–6**: Independently parallel — block Wave 2
- **7–13**: Independently parallel — all blocked by 1–6, block 14
- **14**: 7–13 — blocks 15
- **15**: 14 — blocks F1–F4
- **F1–F4**: 15 — user okay

### Agent Dispatch Summary

- **Wave 1**: 6 agents — Tasks 1–4, 6 → `quick`, Task 5 → `unspecified-high`
- **Wave 2**: 7 agents — Task 7 → `unspecified-high`, Tasks 8–13 → `quick`
- **Wave 3**: 2 agents — Task 14 → `unspecified-high`, Task 15 → `quick`
- **FINAL**: 4 agents — F1 → `oracle`, F2 → `unspecified-high`, F3 → `unspecified-high`, F4 → `deep`

---

## TODOs

- [ ] 1. **bootcamp/ package scaffold + calendar.py** — Parse 30-day-calendar.md into structured day objects

  **What to do**:
  - Create `BOOTCAMP/bootcamp/__init__.py` (empty/simple init)
  - Create `BOOTCAMP/bootcamp/calendar.py`
  - Parse `BOOTCAMP/30-day-calendar.md` into a list of Day objects:
    - Day number (1–30)
    - Day name (e.g., "Monday")
    - Theme (e.g., "Establish the protocol. First diagnosis.")
    - Week number (1–4)
    - Focus string
    - Blocks A, B, C with descriptions
    - HIIT 1 and HIIT 2 drill assignments (referenced by number: 1–8)
    - Daily quotas list (D1, WA, VR, BC, AR, SB ± PA)
    - Boolean: is_public_artifact_day (Day 7, 14, 21, 28)
  - Handle edge cases: blank lines, section headers, Legend lines
  - Export a `get_day(n)` function and a `get_all_days()` function
  - Calendar data is static (read from file at startup, cached in memory)

  **Must NOT do**:
  - Don't modify 30-day-calendar.md (read-only)
  - Don't store calendar data in session_state — it's static

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Purely mechanical parsing of structured markdown; no business logic complexity
  - **Skills**: None needed — pure Python string parsing

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2, 3, 4, 5, 6)
  - **Blocks**: Tasks 7–14 (all tabs depend on calendar data)
  - **Blocked By**: None

  **References**:
  - `BOOTCAMP/30-day-calendar.md` — The source calendar file to parse
  - Look at the Legend section for quota codes and how sections are structured

  **Acceptance Criteria**:
  - [ ] `from bootcamp.calendar import get_day; d = get_day(1)` returns a dict with day_number, focus, blocks, drills, quotas
  - [ ] `get_all_days()` returns 30 entries
  - [ ] Day 7, 14, 21, 28 have `is_public_artifact_day = True`
  - [ ] Drill assignments parse correctly (e.g., Day 1 → Drill 1 and Drill 3)
  - [ ] Handles parsing without modifying the source file

  **QA Scenarios**:
  ```
  Scenario: Calendar parses all 30 days correctly
    Tool: Bash (python3 -c)
    Preconditions: BOOTCAMP/30-day-calendar.md exists unchanged
    Steps:
      1. cd BOOTCAMP && python3 -c "import sys; sys.path.insert(0, 'bootcamp'); from calendar import get_all_days; days = get_all_days(); print(f'Days: {len(days)}')"
      2. Assert output contains "Days: 30"
      3. python3 -c "import sys; sys.path.insert(0, 'bootcamp'); from calendar import get_day; d = get_day(1); print(d['focus'])"
      4. Assert output contains "Establish the protocol"
    Expected Result: All 30 days parsed with correct focus, blocks, drills, and quotas
    Evidence: .omo/evidence/task-1-calendar-parse.txt
  ```

  **Evidence to Capture**:
  - [ ] Calendar parse output showing 30 days
  - [ ] Day 1 focus string verified

  **Commit**: YES
  - Message: `feat(bootcamp): add calendar parser for 30-day schedule`
  - Files: `BOOTCAMP/bootcamp/__init__.py`, `BOOTCAMP/bootcamp/calendar.py`

---

- [ ] 2. **bootcamp/data.py** — Scorecard load/save + progress.json cache

  **What to do**:
  - Create `BOOTCAMP/bootcamp/data.py`
  - Implement `load_scorecard(day_number)` — reads `data/day-{N}-scorecard.md` if it exists, returns structured dict with all fields from daily-scorecard.md
  - Implement `save_scorecard(day_number, data)` — writes scorecard dict back to markdown file matching the template format
  - Implement `scorecard_exists(day_number)` — checks if file exists
  - Implement `load_progress()` / `save_progress(data)` — reads/writes `data/progress.json` with:
    - `current_day` — which day the user is on
    - `completed_days` — list of day numbers fully completed
    - `grades` — dict of day_number → grade
    - `weekly_grades` — dict of week_number → grade
    - `start_date` — ISO date when bootcamp started
    - `streak` — consecutive days completed
  - Create `BOOTCAMP/data/` directory if it doesn't exist on first save
  - Use `pathlib` for all paths. Resolve BOOTCAMP root from `__file__` in data.py
  - Handle the scorecard markdown format by using template strings (not a markdown parser). The output must closely match the original daily-scorecard.md format so the user can also read them outside the app.

  **Must NOT do**:
  - Don't use any database
  - Don't parse the scorecard markdown back in — only write it. Reading uses progress.json
  - Don't modify existing scorecard files during reads

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: File I/O persistence with structured data; well-defined format
  - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 3, 4, 5, 6)
  - **Blocks**: Tasks 7–14
  - **Blocked By**: None

  **References**:
  - `BOOTCAMP/daily-scorecard.md` — The markdown template to replicate in save_scorecard output
  - The `day-N-scorecard.md` naming convention (e.g., `data/day-01-scorecard.md`)

  **Acceptance Criteria**:
  - [ ] `save_scorecard(1, {...})` creates `data/day-01-scorecard.md` matching the template
  - [ ] `load_scorecard(1)` returns the saved data as a dict
  - [ ] `load_progress()` returns default progress dict if no file exists
  - [ ] `save_progress({"current_day": 5})` creates `data/progress.json`
  - [ ] `data/` directory auto-created on first save

  **QA Scenarios**:
  ```
  Scenario: Scorecard save and reload roundtrip
    Tool: Bash (python3 -c)
    Preconditions: BOOTCAMP/data/ does not exist yet
    Steps:
      1. cd BOOTCAMP && python3 -c "import sys; sys.path.insert(0, 'bootcamp'); from data import save_scorecard, load_scorecard; save_scorecard(1, {'quotas_hit': 5, 'grade': 'B'}); result = load_scorecard(1); print(f'Loaded: {result}')"
      2. Assert output contains "quotas_hit" and "grade"
    Expected Result: Data saved to data/day-01-scorecard.md and reloaded successfully
    Evidence: .omo/evidence/task-2-scorecard-roundtrip.txt
  ```

  **Evidence to Capture**:
  - [ ] Roundtrip verification output
  - [ ] Confirm data/ directory was created

  **Commit**: YES
  - Message: `feat(bootcamp): add data persistence module for scorecards and progress`
  - Files: `BOOTCAMP/bootcamp/data.py`

---

- [ ] 3. **bootcamp/scoring.py** — Daily/weekly/camp scoring from rubric

  **What to do**:
  - Create `BOOTCAMP/bootcamp/scoring.py`
  - Implement `calculate_daily_score(scorecard_data)`:
    - Sum 6 quotas (10 pts each = 60 base max) from checkboxes
    - Add bonus points (public artifact +10, extra drill +5, stakeholder sim +5, compression +5)
    - Apply penalties (missed quota -10, etc. from penalty table)
    - Return: `{"base": N, "bonus": N, "penalties": N, "total": N, "grade": "A"/"B"/"C"/"F"}`
  - Implement `calculate_weekly_score(week_number, scorecard_dicts)`:
    - Sum 7 daily scores + bonuses - penalties
    - Apply weekly grade thresholds (A: 400+, B: 320-399, C: 240-319, F: <240)
    - Return: `{"total": N, "bonuses": N, "penalties": N, "adjusted": N, "grade": "X"}`
  - Implement `calculate_camp_score(all_weeks_data)`:
    - Total camp score, check pass threshold (8000+), check conditions
    - Return: `{"total": N, "pass": bool, "conditions": [...]}`
  - All scoring logic must exactly match scoring-rubric.md

  **Must NOT do**:
  - Don't infer grades from partial data — return None for incomplete weeks
  - Don't add custom scoring rules beyond the rubric

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Deterministic arithmetic from a well-defined scoring table
  - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 4, 5, 6)
  - **Blocks**: Tasks 7, 8, 9, 14
  - **Blocked By**: None

  **References**:
  - `BOOTCAMP/scoring-rubric.md` — All point values, penalties, and grade thresholds
  - `daily-scorecard.md` — The Quotas table (# 1–6) maps to daily base points

  **Acceptance Criteria**:
  - [ ] All 6 quotas checked → base score = 60
  - [ ] 0 quotas checked → base score = 0
  - [ ] Penalties subtract correctly (e.g., missed quota => -10)
  - [ ] Weekly score 400+ with ≤1 miss → grade A
  - [ ] Weekly score 240 → grade F
  - [ ] Camp score 8000+ with 3 A/B weeks → pass = True

  **QA Scenarios**:
  ```
  Scenario: Daily scoring with all quotas hit
    Tool: Bash (python3 -c)
    Preconditions: scoring.py exists
    Steps:
      1. cd BOOTCAMP && python3 -c "import sys; sys.path.insert(0, 'bootcamp'); from scoring import calculate_daily_score; s = calculate_daily_score({'quotas_hit': 6, 'extra_drill': False}); print(s)"
      2. Assert output contains "base": 60
      3. Assert grade is "A"
    Expected Result: Perfect day scores 60 base, grade A
    Evidence: .omo/evidence/task-3-daily-scoring.txt
  ```

  **Evidence to Capture**:
  - [ ] Perfect day score output
  - [ ] Weekly grade boundary test (400+ = A)

  **Commit**: YES (with Task 2)
  - Message: `feat(bootcamp): add scoring engine from rubric`
  - Files: `BOOTCAMP/bootcamp/scoring.py`

---

- [ ] 4. **bootcamp/timer.py** — Countdown timer component

  **What to do**:
  - Create `BOOTCAMP/bootcamp/timer.py`
  - Build a function `render_timer(drill_name, duration_minutes)` that renders a countdown timer in Streamlit
  - Timer shows: remaining time (MM:SS), start/stop/reset buttons, and records elapsed time when stopped
  - Use `st.empty()` placeholder for the timer display so it can update dynamically
  - Implement as a stateful component using `st.session_state`:
    - `timer_{drill_name}_start` — timestamp when started
    - `timer_{drill_name}_remaining` — seconds remaining
    - `timer_{drill_name}_running` — bool
    - `timer_{drill_name}_elapsed` — seconds elapsed when stopped
  - Timer does NOT auto-stop at zero — it shows "TIME'S UP" but the user dismisses it
  - Export a dict of default durations per drill:
    ```python
    DRILL_DURATIONS = {
        1: 15, 2: 10, 3: 7, 4: 10,
        5: 10, 6: 8, 7: 10, 8: 5
    }
    ```
  - Timer is purely visual/record-keeping — it does not enforce hard stops

  **Must NOT do**:
  - Don't use threading or async — Streamlit's rerun model handles it
  - Don't block the UI when time runs out — just show a message

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple stateful UI component; Streamlit patterns are well-established
  - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 3, 5, 6)
  - **Blocks**: Tasks 5, 7, 10, 14
  - **Blocked By**: None

  **References**:
  - `drills/drill-1-teardown.md:7` — Shows timer format ("15 minutes, hard stop")
  - Each drill file's Setup section specifies its time limit

  **Acceptance Criteria**:
  - [ ] Timer starts on button click and counts down
  - [ ] Timer stops and shows elapsed time on stop button
  - [ ] Timer resets to full duration on reset
  - [ ] "TIME'S UP" message appears when counter reaches 0
  - [ ] DRILL_DURATIONS dict has correct values for all 8 drills

  **QA Scenarios**:
  ```
  Scenario: Timer starts and counts down
    Tool: Bash (python3 -c) — test the DRILL_DURATIONS dict
    Preconditions: timer.py exists
    Steps:
      1. cd BOOTCAMP && python3 -c "import sys; sys.path.insert(0, 'bootcamp'); from timer import DRILL_DURATIONS; print(DRILL_DURATIONS[1])"
      2. Assert output is "15"
      3. print(DRILL_DURATIONS[8])
      4. Assert output is "5"
    Expected Result: Drill durations are correctly mapped
    Evidence: .omo/evidence/task-4-timer-durations.txt
  ```

  **Evidence to Capture**:
  - [ ] Duration values verified for all 8 drills

  **Commit**: YES (with Task 2, 3)
  - Message: `feat(bootcamp): add countdown timer component`
  - Files: `BOOTCAMP/bootcamp/timer.py`

---

- [ ] 5. **bootcamp/drills.py** — Render all 8 drill types as fillable Streamlit forms

  **What to do**:
  - Create `BOOTCAMP/bootcamp/drills.py`
  - For each drill (1–8), create a render function that displays the drill's form fields in Streamlit:
    - **Drill 1 (Teardown)**: 6 text_area fields (Who is it for, Core behavior, Friction, Metric, Cut, Real problem) + self-check checkboxes + grade slider (/10)
    - **Drill 2 (Recommendation)**: Text area for context, decision (single line), 3 rationale bullets, risk text area, rollback text area + checkboxes + grade
    - **Drill 3 (Anti-defensive)**: Text area for original text, 3 hedge list inputs, brutal rewrite text area, evidence radio buttons + checkboxes + grade
    - **Drill 4 (Translation)**: 3 text areas (PM/Executive/Operator) + synthesis text area + checkboxes + grade
    - **Drill 5 (Triage)**: `st.data_editor` with 10 rows × 5 columns (Task, Metric, Effort, Cut?, Why) + 2 surviving item inputs + hardest cut text + checkboxes + grade
    - **Drill 6 (Compression)**: Source material input, original length number inputs, 3 bullet text areas, recommendation, ask, compressed length + checkboxes + grade
    - **Drill 7 (Hostile Response)**: 3 short text inputs (decision, stakeholder, objection) + response text area + checkboxes + grade
    - **Drill 8 (Spoken Diagnosis)**: Product input, recorded radio, transcript text area, 6 self-assessment checkboxes + 2 reflective text areas + grade
  - Each drill uses `st.form()` with a unique key per drill instance
  - Each drill shows its time limit from `timer.DRILL_DURATIONS`
  - Each drill returns a dict with all field values when submitted
  - Export a `render_drill(drill_number, key_suffix)` function that dispatches to the correct render function
  - Export `DRILL_NAMES = {1: "Product Teardown", 2: "Recommendation Under Constraint", ...}`
  - All drills have a grade at the end: slider from 0–10, displayed as "Grade: X / 10"

  **Must NOT do**:
  - Don't use external UI libraries beyond Streamlit's built-in widgets
  - Don't implement drill timer here — timer.py provides the component, simply display the time limit duration from it

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 8 distinct form layouts, each with different field types. One drill (triage) uses st.data_editor with an editable table. Moderate complexity.
  - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 3, 4, 6)
  - **Blocks**: Tasks 7, 10, 14
  - **Blocked By**: Task 4 (timer.py for DRILL_DURATIONS)

  **References**:
  - `drills/drill-1-teardown.md` through `drills/drill-8-spoken-diagnosis.md` — All 8 drill templates with exact form fields and self-check lists
  - `timer.py:DRILL_DURATIONS` — Time limits per drill type
  - `app.py:150-200` — Streamlit form patterns from existing app (tabs, st.form, st.columns)

  **Acceptance Criteria**:
  - [ ] `render_drill(1, "day1")` renders Drill 1 form with all 6 questions + self-check + grade
  - [ ] `render_drill(5, "day1")` renders Drill 5 with a 10-row editable table
  - [ ] All 8 drills render without errors
  - [ ] Each drill form returns a dict with correct keys
  - [ ] Grade slider captures /10 value correctly

  **QA Scenarios**:
  ```
  Scenario: All 8 drills render without Streamlit errors
    Tool: Bash (python3 -c) — import and test render function signature
    Preconditions: drills.py, timer.py exist
    Steps:
      1. cd BOOTCAMP && python3 -c "import sys; sys.path.insert(0, 'bootcamp'); from drills import DRILL_NAMES, render_drill; print(f'Drills: {len(DRILL_NAMES)}'); print(DRILL_NAMES)"
      2. Assert output contains "Product Teardown"
      3. Assert all 8 drill names present
    Expected Result: All 8 drills registered with correct names
    Evidence: .omo/evidence/task-5-drills-registered.txt
  ```

  **Evidence to Capture**:
  - [ ] Drill name dict verified for all 8

  **Commit**: YES
  - Message: `feat(bootcamp): add drill form renderers for all 8 types`
  - Files: `BOOTCAMP/bootcamp/drills.py`

---

- [ ] 6. **bootcamp/state.py** — Session state management + day progression

  **What to do**:
  - Create `BOOTCAMP/bootcamp/state.py`
  - Implement `init_session_state()` — initializes all session_state keys used across the app:
    - `current_day` (int) — which day the user is viewing
    - `app_stage` (string) — `"daily"` | `"completed"` | `"finished"` (Day 31+)
    - `active_tab` (string) — which tab is selected
    - `day_completed` (bool) — whether current day has been fully completed
    - `timer_*` keys delegated to timer.py
  - Implement `advance_day()` — mark current day complete, increment current_day, save to progress.json
  - Implement `get_app_stage()` — returns current stage based on current_day and progress
  - Implement `load_or_init()` — on app start: load progress.json, determine which day to show, init session state accordingly
  - Day progression logic:
    - If no progress.json exists → start at Day 1
    - If progress.json has current_day = N and day N scorecard exists → show day N (resume)
    - If day N scorecard doesn't exist → still show day N (new day)
    - If current_day > 30 → show "Congratulations" finished view

  **Must NOT do**:
  - Don't auto-advance days — user must explicitly mark day as complete
  - Don't block navigation to past days (user can browse calendar freely)
  - Don't store calendar data here — that's calendar.py's job

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple state machine with session_state keys; straightforward progression logic
  - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 3, 4, 5)
  - **Blocks**: Tasks 7–14
  - **Blocked By**: Task 2 (data.py for load_progress/save_progress)

  **References**:
  - `bootcamp/data.py` — load_progress/save_progress functions
  - `app.py:100-130` — Existing Streamlit session_state patterns in the main app (initialize on first run, persist across reruns)

  **Acceptance Criteria**:
  - [ ] `init_session_state()` sets all required session_state keys to defaults
  - [ ] `load_or_init()` returns Day 1 when no progress.json exists
  - [ ] `advance_day()` increments current_day and persists to progress.json
  - [ ] `get_app_stage()` returns "finished" when current_day > 30
  - [ ] Past days still accessible for browsing

  **QA Scenarios**:
  ```
  Scenario: Fresh start returns Day 1
    Tool: Bash (python3 -c) — test with mock (no Streamlit runtime)
    Preconditions: state.py, data.py exist
    Steps:
      1. cd BOOTCAMP && python3 -c "
import sys; sys.path.insert(0, 'bootcamp');
import json, os
# Simulate fresh state
progress = {'current_day': 1, 'completed_days': []}
from data import save_progress, load_progress
save_progress(progress)
loaded = load_progress()
print(f'current_day: {loaded[\"current_day\"]}')
"
      2. Assert output contains "current_day: 1"
    Expected Result: Fresh state defaults to Day 1
    Evidence: .omo/evidence/task-6-fresh-state.txt
  ```

  **Evidence to Capture**:
  - [ ] Fresh state output showing Day 1

  **Commit**: YES (with Task 5)
  - Message: `feat(bootcamp): add session state and day progression manager`
  - Files: `BOOTCAMP/bootcamp/state.py`

---

- [ ] 7. **Today's Focus tab** — Main day-by-day interactive experience

  **What to do**:
  - Create `BOOTCAMP/bootcamp/today_tab.py` (or inline in renderers/ — keep it a single file)
  - The main tab shown on app launch. Displays:
    - **Header**: "Day N of 30" with big font, week label
    - **Day theme/subtitle**: from calendar data
    - **Today's Focus** section: 1-2 sentence focus from calendar
    - **Morning Setup** section: 3 checkboxes (wake time, phone away, day plan written)
    - **Schedule overview**: Blocks A, B, C descriptions (read-only) + checkboxes for completion
    - **HIIT Drills section**: Shows which 2 drills are assigned today via calendar. Each drill shows its name, time limit, and a "Launch Drill" button that opens the drill form
    - **Scorecard section**: All 6 daily quotas as checkboxes with time/note fields. Auto-calculates quotas-hit count. Shows current daily score from scoring.py
    - **Punishment Log section**: Conditional sections that show when quotas are missed
    - **Daily Review section**: Evening review with 4 reflection text areas + avoidance pattern checkboxes + self-grade radio + tomorrow's one thing
    - **Complete Day button**: Marks day as done, calls state.advance_day(), shows confirmation, advances to next day
    - **Drill form integration**: When "Launch Drill" is clicked, render the drill form inline (within an expander or conditionally)
    - Timer integration: Each drill launched shows the timer from timer.py alongside the form
    - All data saved to scorecard via data.save_scorecard()

  **Must NOT do**:
  - Don't block access to other tabs — user should be able to visit Progress while mid-day
  - Don't auto-save without user clicking save/submit

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Central tab orchestrating calendar data, drill forms, timer, scorecard, and daily review. Heaviest UI integration point.
  - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 8, 9, 10, 11, 12, 13)
  - **Blocks**: Task 14 (app.py)
  - **Blocked By**: Tasks 1, 2, 3, 4, 5, 6

  **References**:
  - `bootcamp/calendar.py:get_day()` — Day's focus, blocks, drills
  - `bootcamp/drills.py:render_drill()` — Form rendering
  - `bootcamp/timer.py:render_timer()` — Countdown
  - `bootcamp/scoring.py:calculate_daily_score()` — Live score calculation
  - `bootcamp/data.py:save_scorecard()` — Persistence
  - `BOOTCAMP/daily-scorecard.md` — The full template to replicate in form fields
  - `BOOTCAMP/30-day-calendar.md:19-26` — Shows Day 1 structure (focus, blocks, HIIT drills, quotas)

  **Acceptance Criteria**:
  - [ ] Header shows correct day number and week
  - [ ] 6 daily quotas render as checkboxes with time/note inputs
  - [ ] Block A/B/C descriptions from calendar shown with completion checkboxes
  - [ ] "Launch Drill" for each assigned drill opens fillable form + timer
  - [ ] Score auto-calculates and updates when checkboxes change
  - [ ] Daily Review section has all reflection fields from template
  - [ ] "Complete Day" saves scorecard and advances to next day
  - [ ] Morning Setup section with 3 checkboxes at top

  **QA Scenarios**:
  ```
  Scenario: Today's Focus renders with Day 1 data
    Tool: Playwright — verify key elements present on page load
    Preconditions: BOOTCAMP/app.py exists (after integration in Task 14) OR test via import
    Steps:
      1. streamlit run BOOTCAMP/app.py
      2. Navigate to localhost:8501
      3. Check header contains "Day 1 of 30"
      4. Check 6 quota checkboxes are present
      5. Check "Launch Drill 1" button is present
      6. Check Drill name "Product Teardown" appears
    Expected Result: Today's Focus tab shows complete Day 1 layout
    Evidence: .omo/evidence/task-7-todays-focus.png
  ```

  **Evidence to Capture**:
  - [ ] Screenshot of Today's Focus tab with Day 1 visible
  - [ ] Screenshot showing drill form opened inline

  **Commit**: YES
  - Message: `feat(bootcamp): add Today's Focus tab with drill forms and scorecard`
  - Files: `BOOTCAMP/bootcamp/today_tab.py`

---

- [ ] 8. **Progress Dashboard tab** — Score visualization and streaks

  **What to do**:
  - Create `BOOTCAMP/bootcamp/progress_tab.py`
  - Reads all completed scorecards and progress.json to display:
    - **Daily Score Chart**: `st.bar_chart()` of daily scores over days 1–current
    - **Grade History**: Color-coded table of day → grade (A/B/C/F)
    - **Weekly Summary**: 4 cards showing each week's total, grade, and miss count
    - **Streak Display**: Current consecutive days completed + longest streak
    - **Camp Progress**: Circular progress toward 8000-point camp goal (use st.progress or st.metric)
    - **Grade Distribution**: Pie-style breakdown using st.metric in a row (A: X, B: Y, C: Z, F: W)
    - **Public Artifact Status**: Shows 4 weekly artifacts required, how many done
    - **Overall Status**: Pass/fail prediction based on current trajectory

  **Must NOT do**:
  - Don't use plotly or external chart libraries — st.bar_chart only
  - Don't modify any data files — read-only view

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Read-only data visualization; Streamlit chart API usage is straightforward
  - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 7, 9, 10, 11, 12, 13)
  - **Blocks**: Task 14
  - **Blocked By**: Tasks 1, 2, 3, 6

  **References**:
  - `bootcamp/data.py:load_progress()` — Read progress data
  - `bootcamp/scoring.py:calculate_camp_score()` — Overall camp score
  - `bootcamp/state.py:get_app_stage()` — Current stage info

  **Acceptance Criteria**:
  - [ ] Bar chart renders with at least one data point (if any day completed)
  - [ ] Shows "No data yet" message when no scorecards exist
  - [ ] Grade history table has correct color coding
  - [ ] Streak displays correctly (0 if none)
  - [ ] Artifact status shows X/4
  - [ ] Progress bar for camp score works

  **QA Scenarios**:
  ```
  Scenario: Progress Dashboard shows empty state
    Tool: Playwright
    Preconditions: BOOTCAMP/app.py exists, no scorecards saved (fresh state)
    Steps:
      1. Navigate to Progress Dashboard tab
      2. Check for "No data yet" or empty state message
      3. Verify bar chart container exists (may be empty)
    Expected Result: Dashboard handles empty state gracefully
    Evidence: .omo/evidence/task-8-progress-empty.png
  ```

  **Evidence to Capture**:
  - [ ] Empty state screenshot
  - [ ] Screenshot with at least 3 days of data (after completing several days)

  **Commit**: YES
  - Message: `feat(bootcamp): add Progress Dashboard tab with charts and streaks`
  - Files: `BOOTCAMP/bootcamp/progress_tab.py`

---

- [ ] 9. **Weekly Audit tab** — Auto-populated weekly review

  **What to do**:
  - Create `BOOTCAMP/bootcamp/weekly_tab.py`
  - Displays the weekly audit form (from weekly-audit.md) with sections:
    - **Week selector**: Dropdown to pick week 1–4
    - **Scoreboard Summary**: Table of Mon–Sun with scores auto-populated from saved scorecards (read-only)
    - **Calculated fields**: Weekly total, bonuses, penalties, adjusted total, grade — all auto-calculated by scoring.py
    - **Quantified Review**: Editable fields for decisions count, artifacts list, stakeholder reps, tasks cut, missed quotas breakdown — pre-filled from scorecard data where possible
    - **Qualitative Review**: 6 text areas (decisions, cleverness, elegance, executive presence, cuts, lagging muscle) — filled by user during audit
    - **Anti-Pattern Detection**: 7 checkboxes (open-option addiction, defensive language, etc.)
    - **Muscle Progress Rating**: 5 sliders (1-10) for judgment, communication, commercial ownership, execution discipline, leadership under load
    - **Next Week Focus**: 4 text inputs (double down, fix, cut, day 1 priority)
    - **Accountability Check-in**: 4 checkboxes + partner feedback text area
    - **Grade Assignment**: Auto-calculated grade display + manual override radio
    - **Save Audit button**: Saves to `data/week-N-audit.md`

  **Must NOT do**:
  - Don't allow editing of auto-calculated fields (scores, grades)
  - Don't overwrite existing audit files — append or save with timestamp

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Form-based UI with auto-populated fields and save; moderate but not complex
  - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 7, 8, 10, 11, 12, 13)
  - **Blocks**: Task 14
  - **Blocked By**: Tasks 1, 2, 3, 6

  **References**:
  - `BOOTCAMP/weekly-audit.md` — Complete template with all form fields
  - `bootcamp/scoring.py:calculate_weekly_score()` — Auto-calculate weekly grade
  - `bootcamp/data.py:load_scorecard()` — Read daily scorecards for auto-population

  **Acceptance Criteria**:
  - [ ] Week 1 selected by default
  - [ ] Mon–Sun scorecard data auto-populated if those days exist
  - [ ] Weekly grade auto-calculated and displayed
  - [ ] All qualitative fields editable and saveable
  - [ ] Saved audit creates `data/week-1-audit.md`

  **QA Scenarios**:
  ```
  Scenario: Weekly Audit loads with week selector
    Tool: Playwright
    Preconditions: BOOTCAMP/app.py exists
    Steps:
      1. Navigate to Weekly Audit tab
      2. Check week dropdown is present with options 1-4
      3. Check Scoreboard Summary table is visible
      4. Check Grade Assignment section has A/B/C/F radio buttons
    Expected Result: Weekly Audit tab renders all sections
    Evidence: .omo/evidence/task-9-weekly-audit.png
  ```

  **Evidence to Capture**:
  - [ ] Screenshot of Weekly Audit tab
  - [ ] Saved audit file content verified

  **Commit**: YES
  - Message: `feat(bootcamp): add Weekly Audit tab with auto-populated review`
  - Files: `BOOTCAMP/bootcamp/weekly_tab.py`

---

- [ ] 10. **Drill Library tab** — Browse and practice any drill anytime

  **What to do**:
  - Create `BOOTCAMP/bootcamp/drill_library_tab.py`
  - Displays all 8 drills in a browsable layout:
    - **Grid/Cards view**: 2×4 or 4×2 grid of drill cards, each showing drill name, time limit, short description
    - Clicking a card opens that drill's form inline (within an expander)
    - Each drill form is identical to what appears in Today's Focus (reuses drills.render_drill())
    - Drill Library is for standalone practice — results saved as "extra" drills in progress.json, not as daily scorecard entries
    - Track which drills have been practiced and when
    - Filter/search: simple text search on drill name

  **Must NOT do**:
  - Don't duplicate the drill form rendering logic — reuse drills.render_drill()
  - Don't save library drills to the daily scorecard — they're extracurricular

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Browse-and-select UI, reuses existing render_drill function
  - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 7, 8, 9, 11, 12, 13)
  - **Blocks**: Task 14
  - **Blocked By**: Tasks 1, 5, 6

  **References**:
  - `bootcamp/drills.py:render_drill(), DRILL_NAMES` — Reuse drill form rendering
  - `bootcamp/timer.py:DRILL_DURATIONS` — Display time limits

  **Acceptance Criteria**:
  - [ ] All 8 drills displayed as cards with names and time limits
  - [ ] Clicking a drill opens its form
  - [ ] Drill form reuses drills.render_drill() — no duplicate rendering code
  - [ ] Practice results saved as extracurricular entries
  - [ ] Text search filters drill cards

  **QA Scenarios**:
  ```
  Scenario: Drill Library shows all 8 drill cards
    Tool: Playwright
    Preconditions: BOOTCAMP/app.py exists
    Steps:
      1. Navigate to Drill Library tab
      2. Check for 8 drill cards visible
      3. Verify drill names: Product Teardown, Recommendation Under Constraint, etc.
      4. Click first card and verify form renders
    Expected Result: All 8 drills visible and clickable
    Evidence: .omo/evidence/task-10-drill-library.png
  ```

  **Evidence to Capture**:
  - [ ] Screenshot of Drill Library with all 8 cards

  **Commit**: YES (with Task 9)
  - Message: `feat(bootcamp): add Drill Library tab for standalone practice`
  - Files: `BOOTCAMP/bootcamp/drill_library_tab.py`

---

- [ ] 11. **Calendar View tab** — 30-day overview with completion status

  **What to do**:
  - Create `BOOTCAMP/bootcamp/calendar_view_tab.py`
  - Displays the full 30-day calendar as a visual grid:
    - **Week rows**: 4 rows (weeks 1–4) × 7 columns (Mon–Sun)
    - Each day cell shows: Day number, focus keyword, completion status (✓/✗/—)
    - Completed days highlighted in green, current day in blue, future days in gray
    - Clicking a day navigates to that day (sets session_state.current_day and switches to Today's Focus tab)
    - Below the grid: mini-legend showing quota codes and drill numbers
    - Weekly totals shown as mini scorecards under each week row

  **Must NOT do**:
  - Don't allow editing from Calendar View — it's read-only navigation
  - Don't scroll horizontally — use st.container with fixed-width columns

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Grid layout rendering with conditional styling; pure display logic
  - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 7, 8, 9, 10, 12, 13)
  - **Blocks**: Task 14
  - **Blocked By**: Tasks 1, 2, 6

  **References**:
  - `bootcamp/calendar.py:get_all_days()` — All day data
  - `bootcamp/data.py:load_progress()` — Completed days list
  - `BOOTCAMP/30-day-calendar.md` — Visual layout reference for the grid

  **Acceptance Criteria**:
  - [ ] 4×7 grid renders with all 30 days
  - [ ] Completed days show green checkmark
  - [ ] Current day shows blue highlight
  - [ ] Future days show gray
  - [ ] Clicking a completed day navigates to it
  - [ ] Legend section present at bottom

  **QA Scenarios**:
  ```
  Scenario: Calendar View renders 4-week grid
    Tool: Playwright
    Preconditions: BOOTCAMP/app.py exists
    Steps:
      1. Navigate to Calendar View tab
      2. Check 4 rows visible (Weeks 1-4)
      3. Check 7 columns (Mon-Sun)
      4. Check Day 1 cell visible with focus text
      5. Check current day highlighted
    Expected Result: Full 30-day grid rendered with status indicators
    Evidence: .omo/evidence/task-11-calendar-view.png
  ```

  **Evidence to Capture**:
  - [ ] Screenshot showing full calendar grid

  **Commit**: YES (with Task 10)
  - Message: `feat(bootcamp): add Calendar View tab with completion grid`
  - Files: `BOOTCAMP/bootcamp/calendar_view_tab.py`

---

- [ ] 12. **Artifacts tab** — Publish and view public artifacts

  **What to do**:
  - Create `BOOTCAMP/bootcamp/artifacts_tab.py`
  - Displays artifact management:
    - **Required Artifacts**: Shows 4 weekly mandatory artifacts (Week 1: product teardown, Week 2: prioritization framework, Week 3: stakeholder template, Week 4: strategy memo). Each shows completion status.
    - **Create New Artifact**: Form with fields:
      - Title (text input)
      - Type (dropdown: Teardown, Framework, Template, Memo, Analysis, Other)
      - Content (large text area — user writes or pastes)
      - Week association (optional dropdown 1-4)
    - **Saved Artifacts List**: Scrollable list of all saved artifacts with title, type, date, week. Click to view full content.
    - **Publish (local only)**: "Publish" button saves artifact to `data/artifacts/{slug}.md` with a clean format suitable for copying to a portfolio
    - Artifact count updates progress dashboard
    - All artifacts saved as markdown files in `data/artifacts/`

  **Must NOT do**:
  - Don't implement actual publishing to the web — "publish" means save to data/artifacts/
  - Don't require LLM for content generation — user writes everything

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: CRUD form for text content with file-based persistence
  - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 7, 8, 9, 10, 11, 13)
  - **Blocks**: Task 14
  - **Blocked By**: Tasks 1, 2, 6

  **References**:
  - `BOOTCAMP/30-day-calendar.md:76` — Shows Day 7: PUBLIC ARTIFACT #1
  - `BOOTCAMP/scoring-rubric.md:22` — Public artifact bonus points

  **Acceptance Criteria**:
  - [ ] 4 required artifacts listed with completion status
  - [ ] Create form saves to `data/artifacts/{slug}.md`
  - [ ] Saved artifacts listed with title, type, date
  - [ ] Clicking artifact shows full content
  - [ ] Artifact count updates in progress.json

  **QA Scenarios**:
  ```
  Scenario: Create and view an artifact
    Tool: Bash + Playwright
    Preconditions: BOOTCAMP/app.py exists
    Steps:
      1. Navigate to Artifacts tab
      2. Click "Create New Artifact"
      3. Fill title: "Test Teardown", type: "Teardown", content: "This is a test"
      4. Click Save
      5. Verify artifact appears in Saved Artifacts list
      6. Check data/artifacts/test-teardown.md exists
    Expected Result: Artifact saved and displayed in list
    Evidence: .omo/evidence/task-12-artifact-create.png
  ```

  **Evidence to Capture**:
  - [ ] Screenshot showing artifact list with saved entry
  - [ ] Verify artifact file content matches

  **Commit**: YES
  - Message: `feat(bootcamp): add Artifacts tab for public artifact publishing`
  - Files: `BOOTCAMP/bootcamp/artifacts_tab.py`

---

- [ ] 13. **Export tab** — Accountability partner report

  **What to do**:
  - Create `BOOTCAMP/bootcamp/export_tab.py`
  - Generates an accountability partner summary report:
    - **Report content**: Shows in a text area (copy-paste ready):
      - Bootcamp stage (Day N of 30, days completed)
      - Current streak
      - Weekly scores and grades so far
      - Artifacts shipped (count and titles)
      - Recent daily scores (last 7 days)
      - Today's self-grade and tomorrow's one thing
      - "I am now a ___ PM because ___" (editable — from Day 30)
    - **Export formats**: Radio button to choose:
      - Copy-paste markdown (default — shown in text area with copy button)
    - **Share buttons**: Not actual send — button copies to clipboard and shows success message
    - **Camp Completion Certificate**: If all 30 days complete, show a simple completion certificate (styled markdown with grade)
    - Past reports accessible via dropdown (previous exports saved to `data/exports/`)

  **Must NOT do**:
  - Don't implement email/text/any actual sending — clipboard copy only
  - Don't require external services

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Read-only report generation with clipboard copy; simple formatting
  - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 7, 8, 9, 10, 11, 12)
  - **Blocks**: Task 14
  - **Blocked By**: Tasks 1, 2, 6

  **References**:
  - `bootcamp/data.py:load_progress()` — Current state and scores
  - `bootcamp/scoring.py:calculate_camp_score()` — Overall results
  - `BOOTCAMP/weekly-audit.md:131-137` — Accountability partner check-in section

  **Acceptance Criteria**:
  - [ ] Report shows current bootcamp stage and scores
  - [ ] Copy button copies report to clipboard
  - [ ] Export saves to `data/exports/{timestamp}.md`
  - [ ] Past exports accessible via dropdown
  - [ ] Completion certificate visible only when all 30 days done

  **QA Scenarios**:
  ```
  Scenario: Export generates report without errors
    Tool: Playwright
    Preconditions: BOOTCAMP/app.py exists, at least one day completed
    Steps:
      1. Navigate to Export tab
      2. Verify report content is generated (not empty)
      3. Check report contains "Day N of 30"
      4. Check copy button is present
      5. Check completion certificate is NOT visible (< 30 days)
    Expected Result: Report generated with current progress data
    Evidence: .omo/evidence/task-13-export-report.png
  ```

  **Evidence to Capture**:
  - [ ] Screenshot of export report with data
  - [ ] Saved export file verified

  **Commit**: YES (with Task 12)
  - Message: `feat(bootcamp): add Export tab for accountability reports`
  - Files: `BOOTCAMP/bootcamp/export_tab.py`

---

- [ ] 14. **app.py entrypoint** — Wire everything together

  **What to do**:
  - Create `BOOTCAMP/app.py`
  - This is the standalone entrypoint for the bootcamp webapp
  - Structure:
    ```python
    import streamlit as st
    import sys
    from pathlib import Path

    # Path setup
    ROOT = Path(__file__).resolve().parent
    sys.path.insert(0, str(ROOT / "bootcamp"))

    # Imports
    from state import init_session_state, load_or_init, get_app_stage
    from calendar import get_all_days, get_day
    import today_tab, progress_tab, weekly_tab, drill_library_tab
    import calendar_view_tab, artifacts_tab, export_tab
    ```
  - Page config: `st.set_page_config(page_title="PM Shock Cycle Bootcamp", layout="wide")`
  - On first load: `load_or_init()` to restore/resume state
  - **Tab bar**: `st.tabs()` with 7 tabs:
    1. "🎯 Today's Focus" → `today_tab.render()`
    2. "📊 Progress" → `progress_tab.render()`
    3. "📋 Weekly Audit" → `weekly_tab.render()`
    4. "🏋️ Drill Library" → `drill_library_tab.render()`
    5. "📅 Calendar" → `calendar_view_tab.render()`
    6. "📦 Artifacts" → `artifacts_tab.render()`
    7. "📤 Export" → `export_tab.render()`
  - **Sidebar**: Shows:
    - Current day / total (e.g., "Day 5 of 30")
    - Current streak (from progress)
    - Quick stats: days completed, current week
    - "About" expander with link to BOOTCAMP README
  - Handle tab switching via `st.session_state.active_tab` for cross-tab navigation (e.g., Calendar → Today)
  - Error handling: wrap tab rendering in try/except, show user-friendly error if a module fails

  **Must NOT do**:
  - Don't import anything from RES/ or app.py — this is standalone
  - Don't use multipage Streamlit — use st.tabs() within a single page

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Integration point that imports all tab modules, manages tab routing and session state coordination
  - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: NO (must come after all tabs)
  - **Parallel Group**: Sequential (Wave 3)
  - **Blocks**: Task 15
  - **Blocked By**: Tasks 7, 8, 9, 10, 11, 12, 13

  **References**:
  - `app.py:1-75` — Existing main app structure for path setup and page config patterns
  - All bootcamp/*_tab.py modules — Each exports a `render()` function
  - `bootcamp/state.py` — `init_session_state()`, `load_or_init()`
  - `bootcamp/calendar.py` — `get_all_days()`, `get_day()`

  **Acceptance Criteria**:
  - [ ] `streamlit run BOOTCAMP/app.py` starts without import errors
  - [ ] 7 tabs visible in the tab bar
  - [ ] Each tab renders its content without errors
  - [ ] Sidebar shows current day and quick stats
  - [ ] Tab switching works without errors
  - [ ] First load initializes session state and shows Day 1

  **QA Scenarios**:
  ```
  Scenario: App starts without errors and shows 7 tabs
    Tool: Playwright
    Preconditions: All bootcamp/* modules exist
    Steps:
      1. Run: streamlit run BOOTCAMP/app.py
      2. Wait for server start (up to 10s)
      3. Navigate to http://localhost:8501
      4. Check page title contains "PM Shock Cycle Bootcamp"
      5. Verify 7 tab labels visible (Today's Focus, Progress, Weekly Audit, Drill Library, Calendar, Artifacts, Export)
      6. Verify sidebar shows "Day 1 of 30"
      7. Verify no error messages in the UI
    Expected Result: App loads cleanly with all 7 tabs, no import errors
    Evidence: .omo/evidence/task-14-app-startup.png
  ```

  **Evidence to Capture**:
  - [ ] Screenshot of full app with all 7 tabs visible
  - [ ] Terminal output showing no import errors

  **Commit**: YES (with Task 15)
  - Message: `feat(bootcamp): add standalone Streamlit entrypoint app.py`
  - Files: `BOOTCAMP/app.py`

---

- [ ] 15. **Data directory, .gitignore, styling polish**

  **What to do**:
  - Create `BOOTCAMP/data/.gitkeep` (empty marker file so data/ dir is tracked by git)
  - Update/add `BOOTCAMP/.gitignore`:
    ```
    data/day-*.md
    data/progress.json
    data/artifacts/
    data/exports/
    # Keep .gitkeep but ignore everything else in data/
    data/*
    !data/.gitkeep
    ```
  - Styling pass on all tabs:
    - Consistent header styling using `st.markdown()` with bold/highlight
    - Responsive columns for drill cards in Drill Library
    - Clean spacing with `st.divider()` between sections
    - Color coding: green for completed, blue for current, gray for future
    - Use `st.success()` / `st.warning()` / `st.error()` for status messages
  - Verify all imports work end-to-end: `python3 -c "import sys; sys.path.insert(0, 'BOOTCAMP/bootcamp'); from state import init_session_state; from calendar import get_all_days; from scoring import calculate_daily_score; print('All imports OK')"`

  **Must NOT do**:
  - Don't modify the main project .gitignore — keep it in BOOTCAMP/
  - Don't add CSS beyond Streamlit's built-in theming

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Housekeeping (gitignore, data dir) + minor visual polish
  - **Skills**: None needed

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on app.py existing)
  - **Parallel Group**: Sequential (Wave 3)
  - **Blocks**: F1–F4
  - **Blocked By**: Task 14

  **References**:
  - `app.py:1-10` — Existing app.py for import conventions
  - `BOOTCAMP/daily-scorecard.md` — Visual template reference for polished display

  **Acceptance Criteria**:
  - [ ] `BOOTCAMP/data/.gitkeep` exists
  - [ ] `BOOTCAMP/.gitignore` has correct patterns
  - [ ] `git status` shows BOOTCAMP/data/ as tracked (only .gitkeep)
  - [ ] All bootcamp module imports succeed

  **QA Scenarios**:
  ```
  Scenario: Gitignore prevents scorecard files from being tracked
    Tool: Bash
    Preconditions: Task 15 completed
    Steps:
      1. mkdir -p BOOTCAMP/data && touch BOOTCAMP/data/day-01-scorecard.md
      2. cd BOOTCAMP && git add --dry-run data/
      3. Check output does NOT contain "day-01-scorecard.md"
    Expected Result: Scorecard files ignored, .gitkeep tracked
    Evidence: .omo/evidence/task-15-gitignore.txt
  ```

  **Evidence to Capture**:
  - [ ] Git dry-run output showing correct ignore behavior
  - [ ] Import verification output

  **Commit**: YES (with Task 14)
  - Message: `chore(bootcamp): add data dir, gitignore, and styling polish`
  - Files: `BOOTCAMP/.gitignore`, `BOOTCAMP/data/.gitkeep`

---

## Final Verification Wave

> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.
>
> **Do NOT auto-proceed after verification. Wait for user's explicit approval before marking work complete.**

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read BOOTCAMP/app.py, BOOTCAMP/bootcamp/*.py, run `streamlit run BOOTCAMP/app.py`). For each "Must NOT Have": search codebase for forbidden patterns (LLM calls, database imports, mobile styling) — reject with file:line if found. Check evidence files exist in `.omo/evidence/`. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** — `unspecified-high`
  Run `python3 -c "import py_compile; py_compile.compile('BOOTCAMP/app.py', doraise=True)"` to check syntax. Review all changed files for: unused imports, redundant imports, overly long functions (>60 lines), duplicated logic across drill renderers, hardcoded file paths, bare `except:` clauses, `st.stop()` used incorrectly.
  Output: `Syntax [PASS/FAIL] | Imports [PASS/FAIL] | Code quality [PASS/FAIL] | VERDICT`

- [ ] F3. **Real Manual QA** — `unspecified-high` (+ `playwright` skill)
  Start from clean state (no BOOTCAMP/data/). Launch `streamlit run BOOTCAMP/app.py`. Execute EVERY QA scenario from EVERY task — follow exact steps, capture evidence. Test cross-tab integration (Calendar View click → Today's Focus). Test edge cases: empty state for all tabs, navigating to future days, completing Day 1 and Day 2 in sequence, creating artifact, exporting report. Save to `.omo/evidence/task-f3-qa/`.
  Output: `Scenarios [N/N pass] | Integration [N/N] | Edge Cases [N tested] | VERDICT`

- [ ] F4. **Scope Fidelity Check** — `deep`
  For each task 1–15: read "What to do", read actual diff (git log/diff or file contents). Verify 1:1 — everything in spec was built (no missing), nothing beyond spec was built (no creep). Check "Must NOT do" compliance. Detect cross-task contamination: Task X touching Task Y's files. Flag unaccounted changes.
  Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

- **1**: `feat(bootcamp): add calendar parser for 30-day schedule`
- **2–4**: `feat(bootcamp): add data/scoring/timer modules`
- **5–6**: `feat(bootcamp): add drill renderers and state management`
- **7**: `feat(bootcamp): add Today's Focus tab`
- **8**: `feat(bootcamp): add Progress Dashboard tab`
- **9–10**: `feat(bootcamp): add Weekly Audit and Drill Library tabs`
- **11–13**: `feat(bootcamp): add Calendar View, Artifacts, Export tabs`
- **14–15**: `feat(bootcamp): add app.py entrypoint and housekeeping`

---

## Success Criteria

### Verification Commands
```bash
cd BOOTCAMP && streamlit run app.py  # Expected: opens at localhost:8501, 7 tabs visible
cd BOOTCAMP && python3 -c "import sys; sys.path.insert(0, 'bootcamp'); from calendar import get_all_days; print(len(get_all_days()))"  # Expected: 30
cd BOOTCAMP && python3 -c "import sys; sys.path.insert(0, 'bootcamp'); from scoring import calculate_daily_score; print(calculate_daily_score({'quotas_hit': 6}))"  # Expected: {'base': 60, ...}
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] BOOTCAMP/app.py starts and renders all 7 tabs without errors
- [ ] Day 1 completes fully (all quotas, drills, review) and saves correctly
- [ ] Progress persisted across app restarts
- [ ] All 8 drills renderable from Drill Library
- [ ] Calendar view shows correct completion status
- [ ] Artifact created, saved, and viewable
- [ ] Export report generated and copyable
- [ ] .gitignore prevents scorecard files from being tracked
