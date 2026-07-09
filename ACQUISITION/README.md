# ACQUISITION — Decision System

Bounded acquisition research for a small individual acquirer. This folder answers one question: **Should I spend another hour on this listing, or is acquisition research becoming avoidance?**

## Current call

**Not yet.** Do not make owner-operator acquisition your primary 12-month goal.

Acquisition is a gated secondary experiment only: max **5 hrs/week**, Archetype 1 (vertical ops SaaS / workflow businesses) until financing readiness is complete.

Source: [`REPENTANCE/acquisition-decision/final_decision_memo.md`](../REPENTANCE/acquisition-decision/final_decision_memo.md) (2026-06-24).

## Files

| File | Purpose |
|------|---------|
| [`Acquisition planning.xlsx`](Acquisition%20planning.xlsx) | Primary workbook — archetype screen, sizing, readiness, deal pipeline, scorecards, diligence |
| [`exports/deal_pipeline.csv`](exports/deal_pipeline.csv) | Input-only mirror of deal pipeline tab (UTF-8) |
| [`exports/decision_log.csv`](exports/decision_log.csv) | Input-only mirror of decision log tab (UTF-8) |

Legacy file `Acqusition planning.xlsx` (typo) is superseded by `Acquisition planning.xlsx`.

## Operating rules

1. **Three gates required** before deeper diligence on any deal:
   - Business you could **improve** (pricing, workflow, AI ops are the lever)
   - Business you could **realistically buy** (price, financing, transition in 12 months)
   - Business you would **operate for 3 years** (not an 18-month flip fantasy)

2. **Time budget:** Acquisition search + diligence ≤ 5 hrs/week until `03_Operator_Readiness` financing and runway pass.

3. **Archetype filter:** Pursue listings in Tier 1 verticals only until readiness passes. See workbook `01_Archetype_Scorecard` and [`acquisition_archetypes.md`](../REPENTANCE/acquisition-decision/acquisition_archetypes.md).

4. **Use normalized buyer SDE/EBITDA** for multiples and debt-service math, not seller-reported figures alone.

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
| Preferred | $150K–$500K | $500K–$2.0M |
| Stretch | $500K–$750K | $2.0M–$3.0M |
| Avoid | < $150K or > $750K EBITDA | > $3.0M EV |

Financing hard fails: no lender path, down payment > liquid capital, DSCR < 1.25x, post-debt cash flow below minimum income, full-time operator required before Path B resolved.

## REPENTANCE decision docs

| Document | Purpose |
|----------|---------|
| [`final_decision_memo.md`](../REPENTANCE/acquisition-decision/final_decision_memo.md) | Final call + kill rules |
| [`decision_scorecard.md`](../REPENTANCE/acquisition-decision/decision_scorecard.md) | Weighted criteria + thresholds |
| [`operator_readiness_checklist.md`](../REPENTANCE/acquisition-decision/operator_readiness_checklist.md) | Financing, runway, willingness |
| [`acquisition_archetypes.md`](../REPENTANCE/acquisition-decision/acquisition_archetypes.md) | Archetype screen |
| [`path_comparison.md`](../REPENTANCE/acquisition-decision/path_comparison.md) | Paths A / B / C |
| [`ground_truth.md`](../REPENTANCE/acquisition-decision/ground_truth.md) | Constraints, strengths, relapse risks |

## Share in Google Sheets

The workbook is built for **Google Sheets as the primary runtime**. Formulas use Sheets-safe functions only (`IF`, `SUMPRODUCT`, `INDEX`/`MATCH` — no `XLOOKUP`, macros, or structured table refs).

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

If xlsx import ever breaks, import [`exports/deal_pipeline.csv`](exports/deal_pipeline.csv) and [`exports/decision_log.csv`](exports/decision_log.csv) into blank tabs and re-apply scoring formulas from the `00_Readme` formula appendix in the workbook.

### Before sharing externally

- Fill personal finance cells in a **private copy** only (liquid capital, income needs, credit details).
- Do not share lender account numbers, API keys, or seller PII beyond diligence needs.

### Known Google Sheets quirks

- Cross-sheet references use quoted tab names (e.g. `'04_Deal_Pipeline'!B5`) — these import correctly.
- Comma argument separators are used throughout (Sheets accepts on import).
- Conditional formatting on Pursue/Watch/Kill labels may need a one-time re-apply after import if colors do not transfer; rules are simple text-match rules.
- Named ranges are workbook-scoped plain cell blocks — no structured Excel tables.
- `PMT` is used in `02_Target_Size_Bands` wrapped in `ABS()` so debt service displays as a positive number in both Excel and Sheets.

### Local verification (2026-07-05)

- 10 tabs, 133 formulas, **0 errors** after LibreOffice recalc.
- No `XLOOKUP`, macros, structured table refs, or external workbook links.
- Google Sheets import not automated in CI; after upload, spot-check `01_Archetype_Scorecard!J3`, `02_Target_Size_Bands!B26`, `05_Deal_Scorecard!R3`, `06_Business_Risk_Diligence!V2`, and `08_Time_Budget!F2`.

## Workflow

1. Screen verticals in `01_Archetype_Scorecard`.
2. Confirm readiness in `03_Operator_Readiness` (default: Not yet).
3. Add real listings to `04_Deal_Pipeline` only.
4. Score each deal in `05_Deal_Scorecard` + `06_Business_Risk_Diligence`.
5. Write one-page memo in `07_Diligence_Memo`.
6. Track weekly hours in `08_Time_Budget` to catch avoidance.
7. Log pass/kill decisions in `09_Decision_Log`.
