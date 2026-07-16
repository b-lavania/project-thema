# ACQUISITION — Decision System

Bounded acquisition research for a small individual acquirer. This folder answers one question: **Should I spend another hour on this listing, or is acquisition research becoming avoidance?**

## Current call

**Not yet.** Do not make owner-operator acquisition your primary 12-month goal.

Acquisition is a gated secondary experiment only: max **5 hrs/week**, Archetype 1 (vertical ops SaaS / workflow businesses) until financing readiness is complete.

Source: [`decision/final_decision_memo.md`](decision/final_decision_memo.md) (2026-06-24).

## Start here

| Read first | Purpose |
|------------|---------|
| [`operator_fit.csv`](operator_fit.csv) | **Copy into Google Sheets first** — one row per listing, Yes/No operator-fit call |
| [`ideal-business-fit.md`](ideal-business-fit.md) | Operator fit narrative — what you'd actually run day-to-day, Buy/Conditional/Never |
| [`ownership-challenges.md`](ownership-challenges.md) | Deep thinking guide — OS vs ownership, argue-both-sides, relapse traps |
| [`decision/final_decision_memo.md`](decision/final_decision_memo.md) | Final call, kill rules, 30-day reps test |
| [`Acquisition planning.xlsx`](Acquisition%20planning.xlsx) | Later-stage diligence — only after CSV operator_fit_yesno = Yes |

## Files

| File | Purpose |
|------|---------|
| [`operator_fit.csv`](operator_fit.csv) | Google Sheets-ready listing screen — operator fit Yes/No before workbook |
| [`ideal-business-fit.md`](ideal-business-fit.md) | Operator fit narrative — what business you'd actually run day-to-day |
| [`Acquisition planning.xlsx`](Acquisition%20planning.xlsx) | Later-stage workbook — archetype screen, sizing, readiness, deal pipeline, scorecards |
| [`ownership-challenges.md`](ownership-challenges.md) | Profile-grounded ownership working paper (not a checklist) |
| [`build_workbook.py`](build_workbook.py) | Regenerates xlsx + CSV exports |
| [`exports/deal_pipeline.csv`](exports/deal_pipeline.csv) | Input-only mirror of deal pipeline tab (UTF-8) |
| [`exports/decision_log.csv`](exports/decision_log.csv) | Input-only mirror of decision log tab (UTF-8) |

## Decision memos (`decision/`)

| Document | Purpose |
|----------|---------|
| [`decision/final_decision_memo.md`](decision/final_decision_memo.md) | Final call + kill rules |
| [`decision/ground_truth.md`](decision/ground_truth.md) | Constraints, strengths, relapse risks |
| [`decision/decision_scorecard.md`](decision/decision_scorecard.md) | Weighted criteria + thresholds |
| [`decision/operator_readiness_checklist.md`](decision/operator_readiness_checklist.md) | Financing, runway, willingness |
| [`decision/acquisition_archetypes.md`](decision/acquisition_archetypes.md) | Archetype screen |
| [`decision/path_comparison.md`](decision/path_comparison.md) | Paths A / B / C |

## REPENTANCE context (identity + 12-month lock)

| Document | Purpose |
|----------|---------|
| [`../REPENTANCE/too-greedy.md`](../REPENTANCE/too-greedy.md) | Locked 12-month plan + GTM & CTO blocker |
| [`../REPENTANCE/fatalism.md`](../REPENTANCE/fatalism.md) | Relapse patterns + operating system |
| [`../REPENTANCE/too-deep.md`](../REPENTANCE/too-deep.md) | Positioning + identity spine |
| [`../RES/data/master_context.md`](../RES/data/master_context.md) | Operator credentials |

## Operating rules

1. **Three gates required** before deeper diligence on any deal:
   - Business you could **improve** (pricing, workflow, AI ops are the lever)
   - Business you could **realistically buy** (price, financing, transition in 12 months)
   - Business you would **operate for 3 years** (not an 18-month flip fantasy)

2. **Time budget:** Acquisition search + diligence ≤ 5 hrs/week until `03_Operator_Readiness` financing and runway pass.

3. **Archetype + operator-fit filter:** Pursue listings in **Archetype 1 (ops SaaS / workflow) ∩ Buy catalog** from [`ideal-business-fit.md`](ideal-business-fit.md). Log each listing in [`operator_fit.csv`](operator_fit.csv) first. Path B hours always outrank acquisition hours.

4. **Search SDE band:** **$150K–$400K** preferred (stretch to $500K only with financing documented in `03_Operator_Readiness`).

5. **Use normalized buyer SDE/EBITDA** for multiples and debt-service math, not seller-reported figures alone.

6. **Complete [`ownership-challenges.md`](ownership-challenges.md) section 9** before labeling any deal Pursue.

## Kill rules

Pause all acquisition search until January 2027 review if any trigger fires:

1. Acquisition research **> 8 hrs/week** for 2 consecutive weeks while Path B outbound **< 5 hrs/week**
2. Month-5 pattern: "more interesting" listing in a **new domain** outside ops-AI/logistics
3. LOI or offer without financing pre-approval and 12-month runway model
4. Any deal failing **all three gates** (improve / buy / operate 3yr)
5. Path B offer accepted — acquisition pauses 6 months minimum
6. Quotely hits **5+ paying operators** — re-evaluate whether acquisition dilutes Path A

## Target size bands (small individual acquirer)

| Band | SDE / EBITDA | EV |
|------|--------------|-----|
| Preferred | $150K–$400K | $500K–$2.0M |
| Stretch | $400K–$500K | $2.0M–$2.5M |
| Avoid | < $150K or > $750K EBITDA | > $3.0M EV |

Financing hard fails: no lender path, down payment > liquid capital, DSCR < 1.25x, post-debt cash flow below minimum income, full-time operator required before Path B resolved.

## Share in Google Sheets

**Operator fit (start here):** Upload [`operator_fit.csv`](operator_fit.csv) to Google Drive → **Open with → Google Sheets**. Paste one row per listing. Fill `day_to_day_primary_job` and `operator_fit_yesno` before any workbook diligence.

**Later-stage diligence:** The workbook is built for **Google Sheets as the runtime** after a listing passes the CSV screen. Formulas use Sheets-safe functions only (`IF`, `SUMPRODUCT`, `INDEX`/`MATCH` — no `XLOOKUP`, macros, or structured table refs).

### Upload and convert

1. Upload [`Acquisition planning.xlsx`](Acquisition%20planning.xlsx) to Google Drive.
2. Right-click → **Open with → Google Sheets** (creates a native copy; formulas recalculate).
3. **File → Save as Google Sheets** if prompted, to detach from the xlsx.
4. Share:
   - **Viewer** — advisors reviewing your framework
   - **Commenter** — broker discussing a specific listing
   - **Editor** — live collaboration only; protect formula ranges after import

The repo xlsx is the **source of truth** in git. The Drive `.gsheet` copy is the living shareable version.

### CSV fallback

Import [`operator_fit.csv`](operator_fit.csv) for listing screening. If xlsx import ever breaks, import [`exports/deal_pipeline.csv`](exports/deal_pipeline.csv) and [`exports/decision_log.csv`](exports/decision_log.csv) into blank tabs and re-apply scoring formulas from the `00_Readme` formula appendix in the workbook.

### Before sharing externally

- Fill personal finance cells in a **private copy** only (liquid capital, income needs, credit details).
- Do not share lender account numbers, API keys, or seller PII beyond diligence needs.

### Known Google Sheets quirks

- Cross-sheet references use quoted tab names (e.g. `'04_Deal_Pipeline'!B5`) — these import correctly.
- Comma argument separators are used throughout (Sheets accepts on import).
- Conditional formatting on Pursue/Watch/Kill labels may need a one-time re-apply after import if colors do not transfer; rules are simple text-match rules.
- Named ranges are workbook-scoped plain cell blocks — no structured Excel tables.
- `PMT` is used in `02_Target_Size_Bands` wrapped in `ABS()` so debt service displays as a positive number in both Excel and Sheets.

## Workflow

1. Path B outbound first that week.
2. Read [`ideal-business-fit.md`](ideal-business-fit.md) if you need the narrative refresher.
3. Paste 1–3 listings into [`operator_fit.csv`](operator_fit.csv) (Google Sheets copy) — answer day-to-day litmus and mark `operator_fit_yesno`.
4. If **No** or `hard_exclusion_triggered = Yes`, log reason and stop.
5. If **Yes**, read [`ownership-challenges.md`](ownership-challenges.md) before deepening.
6. Add listing to `04_Deal_Pipeline` and run workbook diligence tabs.
7. Track weekly hours in `08_Time_Budget` to catch avoidance.
8. Log pass/kill decisions in `09_Decision_Log`.

Regenerate workbook: `python build_workbook.py`
