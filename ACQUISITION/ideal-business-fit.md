# Ideal Business Fit Map

Single source of truth for **what kind of business fits you as an operator** — not generic ETA playbooks. Use this before opening the workbook or pasting a listing into the pipeline.

**Framing:** Acquisition is a **bounded secondary experiment** (max 5 hrs/week). Path B outbound remains primary. This document answers: *If I spend those 5 hours wisely, what am I actually looking for?*

**Related:** [`operator_fit.csv`](operator_fit.csv) · [`decision/final_decision_memo.md`](decision/final_decision_memo.md) · [`decision/acquisition_archetypes.md`](decision/acquisition_archetypes.md) · [`decision/ground_truth.md`](decision/ground_truth.md) · [`ownership-challenges.md`](ownership-challenges.md)

**Primary working surface:** Copy [`operator_fit.csv`](operator_fit.csv) into Google Sheets and paste one row per listing. This doc is the narrative; the CSV is where you make the Yes/No operator-fit call.

---

## One-sentence ideal

A **software-wrapped ops business** (or SaaS with a service wrapper) in **logistics / field service / dispatch / quoting**, where your job is **product + pricing + workflow**, not daily crew management.

---

## Strengths → required deal traits

| Your strength | Buy businesses that need this as the *lever* |
|---------------|-----------------------------------------------|
| Diagnostic reframing | Stated problem is wrong (pricing confusion, alert noise, slow quote) and fixable by product/process redesign |
| Pricing + commercial fluency | Opaque tiers, gut-feel quoting, margin leakage on complex jobs |
| Ops / AI / workflow build | Manual intake → quote → schedule → deliver → bill loop that can be systematized |
| Integration-first (BVXpress) | Messy multi-system data, not "rip and replace the whole stack" |
| 0-to-1 / first product hire | Underbuilt software wrapping a real ops workflow; small team, founder retiring |

---

## Weaknesses → hard exclusions

| Weakness / trap | Never buy (or Watch → Kill) |
|-----------------|---------------------------|
| Thin people leadership / GM aversion | Heavy W2 labor shops where you are dispatcher, scheduler, and HR |
| Avoidance via novelty | Domains outside ops-AI/logistics/field-service (healthcare clinics, restaurants, generic agencies, pure M&A services return) |
| Distribution avoidance | Deals that only reward diligence theater with no path to a defended number |
| Financing incomplete | Anything requiring LOI without pre-qual / runway model |
| Insight over outcome | "Interesting problem" with no SDE path or no product wedge |

---

## Day-to-day litmus (must pass)

Ask of every listing: **After close, what do I do Mon–Fri for 3 years?**

| Pass | Fail |
|------|------|
| Roadmap, pricing, instrumentation, customer discovery, light sales | Personally covering loads, managing technicians' schedules |
| One ops hire who owns dispatch | Payroll drama as primary job |
| Product + commercial decisions | You are the dispatcher |

**If the answer is Fail → Kill** even if the listing looks attractive on paper.

---

## What I actually want to operate

After close, my job should look like this for 3 years:

| I want to spend time on | I do not want as my primary job |
|-------------------------|----------------------------------|
| Product roadmap and workflow redesign | Dispatching loads or crews |
| Pricing architecture and margin repair | Technician scheduling and payroll drama |
| Instrumentation, funnels, customer discovery | Being the hero seller or dispatcher |
| Light sales on a defined wedge | Full-time GM / HR for a labor shop |
| Hiring one ops lead who owns daily dispatch | Multi-site operations management |

**Business shapes that fit:** software-wrapped ops, vertical SaaS with a service wrapper, workflow intelligence with recurring ops buyers.

**Business shapes that trap me:** heavy W2 labor shops, generic cash-flow SMBs, M&A services return, out-of-domain novelty plays.

---

## Harmonized filter

Use filters in this order — do not skip to economics or vertical scores:

1. **Archetype 1 first** — vertical ops SaaS / workflow businesses ([`decision/acquisition_archetypes.md`](decision/acquisition_archetypes.md))
2. **Operator-fit narrative** — Buy / Conditional / Never catalogs below (no vertical ranking yet)
3. **Day-to-day litmus** — answer in [`operator_fit.csv`](operator_fit.csv) (`day_to_day_primary_job`, `operator_fit_yesno`)
4. **Hard exclusions** — mark `hard_exclusion_triggered` in the CSV; if Yes, stop
5. **Three gates + economics** — improve / buy / operate 3yr; then SDE/EV/DSCR as pass/fail gates only

**Archetype vs workbook Tier:** Archetype = deal *shape*. Workbook Tier = weighted vertical score. **Do not use Tier as a buy override** until you have operator-fit reps logged in the CSV.

**Search rule:** Screen Archetype 1 listings against the Buy catalog below. Log every listing in `operator_fit.csv` before opening the workbook.

---

## Buy shortlist (search these)

1. **Vertical SaaS in ops niches** — logistics TMS-lite, quoting, field-service scheduling, dispatch, broker back-office automation; founder retiring; churn or pricing broken; eng or contractors exist or hireable.
2. **Niche workflow SaaS with service wrapper** — underbuilt software is the product; services exist but are not the identity.
3. **Industry data / workflow intelligence** — recurring data + ops buyers, low labor burden.
4. **Permit / estimating software** (not pure labor shops) — only if recurring software revenue and low owner-as-estimator dependence.

**Preferred economics (gates, not ranking):** SDE/EBITDA **$150K–$400K** preferred (stretch to $500K only with financing documented), EV **$500K–$2.0M**, DSCR ≥ **1.25x** on normalized buyer EBITDA, seller transition ≥ **60 days**.

---

## Conditional (Watch only with written ops-hire plan)

- **Freight brokerage / last-mile ops** businesses — only if structured as Quotely deployment vehicle + hire ops manager ≤ 12 months (Archetype 2/3 rules).
- **Industrial distribution** — only if pricing/catalog/quote complexity is the wedge and inventory risk is bounded.
- **Insurance inspections / field compliance** — only if software-led and low owner-as-dispatcher dependence.

---

## Never (Kill for this cycle)

- HVAC, roofing, laundromat, self-storage, generic local services (workbook Tier 3 labor plays)
- Pure cash-flow SMBs with no product wedge
- M&A / diligence services businesses (return to BVXpress cage)
- Multi-site GM plays
- MSP / generic IT services without workflow wedge
- Heavy staffing / W2 shops (Specialty Staffing pattern)
- EV > **$3.0M** or SDE < **$150K** without written exception
- Any new domain outside ops-AI / logistics / field-service workflow

---

## Listing pass/fail template (30-day reps test)

Copy this block for each listing review (one per week max while Path B is active), or paste a row into [`operator_fit.csv`](operator_fit.csv):

```
LISTING: [name / broker link]
DATE:
VERTICAL:
ARCHETYPE (1–5):
FIT CLASS (Buy / Conditional / Never):

DAY-TO-DAY LITMUS — After close, Mon–Fri for 3 years I would:
[ ] Pass — product, pricing, workflow, instrumentation; ops hire owns dispatch
[ ] Fail — I am dispatcher / scheduler / HR

GATE: Could I improve it? (pricing, workflow, AI ops)     YES / NO
GATE: Could I realistically buy it? (price, financing, transition)  YES / NO
GATE: Would I operate it 3 years? (not 18-mo flip)        YES / NO

HARD EXCLUSION TRIGGERED?  YES / NO — reason:

NORMALIZED SDE/EBITDA (rough):
ASKING / EV:
FINANCING PATH (SBA / seller note / cash): 

ONE SENTENCE WEDGE:
ONE SENTENCE KILL REASON:

DECISION: Pursue / Watch / Kill
NEXT ACTION (if Watch): [written ops-hire plan required for Conditional]
LOGGED IN 09_Decision_Log: YES / NO
```

**Rep rule:** If you cannot fill the day-to-day litmus in 10 minutes, the listing is not ready for diligence — log as Kill or parking lot.

### CSV column values (for Google Sheets data validation)

| Column | Allowed values |
|--------|----------------|
| `business_model` | SaaS, SaaS+services, services, unknown |
| `day_to_day_primary_job` | Product_pricing_workflow, GM_dispatch_payroll, Sales_only, Unknown |
| `operator_fit_yesno` | Yes, No |
| `hard_exclusion_triggered` | Yes, No |
| `domain_fit` | OpsAI_logistics, FieldService, Adjacent, NewDomain |
| `owner_dependence` | Low, Med, High, Unknown |
| `labor_burden` | Low, Med, High, Unknown |

---

## Weekly use (secondary path)

1. Path B outbound first that week.
2. Only then: paste 1–3 listings into [`operator_fit.csv`](operator_fit.csv) and answer the day-to-day litmus.
3. If **operator_fit_yesno = No**, log the reason and stop (do not research your way out of it).
4. If **Yes**, then and only then move the listing into the workbook pipeline for deeper diligence.
5. If tempted by a "more interesting" out-of-domain listing → parking lot, not calendar (kill rule 2).

---

## Bottom line

The business that fits you is not "any messy ops SMB." It is a **product-levered ops business** in your locked domain where you improve pricing, workflow, and instrumentation — and hire (or inherit) someone else for daily dispatch labor. Everything else is either Conditional with a written ops plan, or Never for this cycle.
