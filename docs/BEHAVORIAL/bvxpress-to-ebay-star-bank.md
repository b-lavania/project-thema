# STAR Story Bank — BVXpress → eBay Conversion Programs (Paloma HM Round)
> **Rules:** Each STAR is isolated — do not merge metrics. 8-min full + 90-sec cut + hypothesis/KPIs/PRD snippet. File-cited for defensibility.

---

## How to use in the HM round

Paloma will ask variants of:
- "Tell me about owning a roadmap with Eng/Data/Design"
- "How do you increase experimentation velocity?"
- "Tell me about sizing & prioritizing an opportunity"
- "Walk me through an A/B test you led"
- "Tell me about a time you aligned conflicting stakeholders"

**You answer with S1→S5 below.** Lead every answer with: *"At BVXpress, as first product hire operating 8 products for 1,400 users..."* then bridge to eBay with the trigger map.

---

## S1 — Owned Roadmap with Eng / Data Science / Design [Roadmap Ownership]

**JD tag:** `Own and implement roadmap in close partnership with Engineering, Data Science, Design` | `Lead dependencies, ensure execution-ready`

**Situation — `RES/data/master_context.md:491-494` + `PORTFOLIO/CONCEPT3/plg.html:451-457`**
In 2012 BVXpress was employee #3 / first product hire — no product function, 8-product SaaS suite in M&A advisory sold to heterogeneous buyers (advisors, brokers, appraisers). After launches 1-2, in-house telemetry showed **<20% WAU** despite strong demo feedback. Users abandoned before first deal flow. Opportunity maps ranked the stall not in deal modeling (what we'd built) but in client-facing presentation — advisors spent **4+ hours per engagement** manually formatting Excel into client-ready reports.

**Task**
Pivot roadmap from analytical depth to client-workflow speed; sequence products 3-5 to close the loop deal → presentation → suite expansion; gate every launch on adoption proof before scaling — without losing Eng/Data/Design trust.

**Action (DACI + tradeoffs)**
- **Driver (you):** reframed success metric from "most accurate valuation" to "fastest Excel→client presentation" — the value-metric diagnosis that unlocked prioritization.
- **Contributors:** Eng (build vs kill scope), Data/telemetry (in-house analytics suite + Pendo), Design (onboarding flows, message tests).
- **Decisions & cuts:** Killed deal-database (high build cost, low discovery demand) and fee-benchmarking (demo feature, zero workflow) — `RES/data/master_context.md:493` + `PORTFOLIO/CONCEPT3/bvxpress-pricing.html:695-716`. Deferred route-optimization-class complexity to protect quote-flow equivalent (first-deal-flow reliability).
- **Execution rhythm:** Roadmap as Now/Next/Later themes (activate → convert → expand → retain), not feature list; each Next gated on **20+ user cohort adoption** before scaling — `RES/data/master_context.md:493`.
- **Cross-functional cadence:** Aha! backlog, telemetry-driven fence tuning, Design-led onboarding prototype walkthroughs, Data-informed profile/segment tests.

**Result — `RES/data/master_context.md:500-504` + `PORTFOLIO/CONCEPT3/bvxpress-pricing.html:511-526` + `PORTFOLIO/CONCEPT3/plg.html:464-483`**
- **+45% TTV/adoption** from new onboarding flows (incl. complex cloud SKU) — `RES/data/master_context.md:502`
- **ARPU $450→$600** over 2 years from voluntary module upgrades, not list-price hikes
- **2× retention** at 3+ products vs single-product — drove GTM shift to onboarding depth over acquisition breadth
- Operated 8 products / 1,400+ users; launched 5 from whiteboard

**90-sec cut (speak this)**
> "At BVXpress I was first product hire owning 8 products for 1,400 users. After two launches, telemetry showed under 20% WAU — demos were loved, workflows weren't adopted. Opportunity maps showed the stall was presentation, not modeling — advisors spent four hours formatting Excel for clients. I reframed the roadmap from analytical depth to output speed, killed a deal-database and fee-benchmarking we'd planned, and sequenced the next three products to attack the client-facing workflow. Every launch gated on 20+ cohort adoption. That pivot drove 45% TTV lift, voluntary ARPU $450→$600, and 2× retention at 3+ products. That's the same muscle as owning Email/Push/Hub — you don't fund the next trigger until the onboarding and suppression logic prove the last one lands."

**eBay bridge**
> "For Conversion Programs I'd run the same Now/Next/Later — Now: fix onboarding + suppression, Next: trigger intelligence, Later: channel orchestration — gated on cohort adoption and guardrail health."

**PRD snippet Paloma expects**
Problem / Goals & Non-goals / JTBD (advisor: 'look professional to client fast') / Stories / Requirements (functional: export fence, non-functional: <2 min TTV) / Success: Primary TTV + ARPU, Guardrail WAU/WAR / Deps: telemetry, Pendo, Eng capacity / Launch: cohort gate → phased rollout / Open Q: pricing fence tuning per segment.

---

## S2 — Increased Experimentation Velocity [Operational Excellence]

**JD tag:** `Drive operational excellence by increasing experimentation velocity and improving cross-functional collaboration`

**Situation — `RES/data/master_context.md:478-480;499-500` + `PORTFOLIO/CONCEPT3/plg.html:695-716`**
Velocity was blocked by three things: (1) no single growth team — product owned growth, (2) feature ideas that demoed well but never hit workflow, (3) custom pricing per customer hid where to test. Eng wanted to build; Data had telemetry but no decision loop.

**Task**
Build a system that makes velocity cheap and decisions irrevocable — instrument → diagnose → hypothesize → change → measure — across Eng/Data/Design.

**Action**
- Built **Telemetry-to-Price loop**: Instrument (module usage, fence-hit, deal-flow completion, export actions) → Diagnose (<20% WAU, abandonment before first deal flow) → Hypothesize (output speed, not depth; NTV→BVX fences drive upgrade) → Change (kill/sequence, tune fences) → Measure (WAU, conversion, ARPU, retention) — `PORTFOLIO/CONCEPT3/bvxpress-pricing.html:695-716`
- Stack: **in-house telemetry suite** (custom) + Pendo + Mixpanel-class; Aha! backlog; opportunity maps, tree tests, focus groups before bets — `RES/data/master_context.md:478;112-114`
- Process: profile/segment tests to decide enhance vs deprecate; landing + onboarding as A/B surface; single hypothesis per release, one measurement window.
- Collaboration: Data defined fences and cohorts; Design owned onboarding prototypes; Eng owned adapter/instrumentation; you owned prioritization and "what to kill."

**Result — `RES/data/master_context.md:501-504`**
- **Experimentation became routine, not episodic:** landing repositioning +7% conversion (one test, one message), onboarding flows +45% TTV, lifecycle messaging +14% retention over 2 years, suite expansion ARPU $450→$600. Each result traced to a single lever, not a bundle.
- **Ops lesson:** velocity wasn't "more tests" — it was killing demo features that consumed backlog and gating launches on cohort signal.

**90-sec cut**
> "Velocity at BVXpress wasn't blocked by tooling — we had telemetry and Pendo. It was blocked by testing the wrong things. I built a tight loop: instrument fence-hit and deal-flow completion, diagnose where users stalled — under 20% WAU before first workflow — hypothesize output speed not depth, then change one lever at a time. We killed a planned deal-database that scored in demos but had no workflow demand, and ran profile/segment tests to decide enhance vs deprecate. That discipline turned ad-hoc ideas into a system: landing test +7% conversion, onboarding +45% TTV, lifecycle +14% retention. For eBay I'd bring the same loop — hypothesis per trigger, trigger-rate-aware power, pre-registered guardrails, and a habit of killing ideas that demo well but don't move RPR."

**eBay bridge — guardrails you never compromise**
Primary: RPR / incremental orders; Guardrails: unsub, spam, push opt-out, D30 retention — report absolute + relative + CI; 4-8 week holdout for fatigue.

---

## S3 — Sized & Prioritized Opportunity [Forecasting Business Impact]

**JD tag:** `Identify and size opportunities, using data to forecast business impact and prioritize initiatives`

**Situation — `PORTFOLIO/CONCEPT3/bvxpress-pricing.html:532-539;543-583;676-689` + `RES/data/master_context.md:484-488`**
No public price book — every account was `Module mix × Seats × Term × Discount × Expansion rights`. Heterogeneous buyers (advisors, brokers, appraisers, valuators) with different ACV tolerance. Wrong default: discount BVX to win deals NTV should land → erodes margin anchor and trains discount expectation.

**Task**
Size where to play and how to price without a SKU matrix — forecast blended deal margin, NTV→BVX conversion, and multi-product depth, not SKU P&L.

**Action**
- **Sizing model:** `Expected Value = Eligible Reach × Current Funnel Conversion × Lift Assumption × ARPU × p(success)` — built bottom-up from telemetry cohorts, not TAM.
  - Eligible Reach: adjacent segment that won't buy BVX at entry (appraiser/valuator terminal-value job)
  - Conversion: NTV→BVX fence-hit rate → upgrade rate
  - Lift: voluntary upgrade to presentation/suite modules
  - ARPU: $450 baseline → $600 post-upgrade (voluntary)
- **Architecture choices driven by sizing:**
  - **Loss-leader ladder:** NTV (thin/negative margin acceptable) → BVX (full margin target) → suite modules; measure blended deal margin, not loss-leader standalone — `PORTFOLIO/CONCEPT3/bvxpress-pricing.html:586-593`
  - **Feature fences** (not tier renaming): GGM vs AGM, spreadsheet vs desktop app, Deal Quantifier/Optimizer gating — tuned by telemetry — `PORTFOLIO/CONCEPT3/bvxpress-pricing.html:598-669`
  - **Custom deal composition:** deepest discount on NTV land, tighter bands on BVX, bundle preference when joint adoption predicted — `PORTFOLIO/CONCEPT3/bvxpress-pricing.html:676-689`
- **Prioritization:** RICE, then explicit override — funded onboarding depth over acquisition breadth when retention data showed **3+ products → 2× retention** despite RICE favoring acquisition — `RES/data/master_context.md:504`

**Result — `PORTFOLIO/CONCEPT3/bvxpress-pricing.html:788-794`**
- **ARPU $450→$600** without raising list price on existing modules
- **14% retention lift** + **7% conversion lift** + **2× retention** at 3+ products
- For the separate time-bounded Village Wellth experiment: **3× take rate** (4→3 tiers) — decision-architecture proof point to cite as range, not anchor — `RES/data/master_context.md:403-405`

**90-sec cut**
> "At BVXpress there was no price book — every deal was module times seats times term times discount times expansion rights. I sized opportunities bottom-up: eligible adjacent segment times fence-hit rate times upgrade frequency times ARPU lift. That sizing told us not to discount BVX to win — instead build NTV as a loss-leader for terminal-value buyers, fence capability by job — spreadsheet vs desktop, GGM vs AGM — and keep BVX margin tight. Prioritization wasn't RICE-pure; when data showed 3+ products retained at 2×, we funded onboarding depth over acquisition breadth even though acquisition scored higher. Result: ARPU $450→$600 voluntarily, 14% retention lift, 7% conversion lift — all without raising list price. For eBay I'd size the same way: eligible intent population times trigger rate times conversion times RPR uplift, then weigh against guardrail risk and eng cost."

**PRD snippet — sizing in PRD**
Expected Value table, breakeven lift vs eng effort, sensitivity (lift ±50%, trigger rate ±30%), guardrail cost (unsub bps), holdout-adjusted durable lift.

---

## S4 — Led A/B Test End-to-End [Hypothesis → KPIs → Ship/Scale]

**JD tag:** `Develop and lead A/B tests, including hypothesis development, experiment setup, and KPI definition`

**Situation — `PORTFOLIO/CONCEPT3/plg.html:470-472;460-483` + `RES/data/master_context.md:479-480`**
Landing and product messaging used "most accurate valuation tool" — demos loved, conversion stalled. Opportunity maps + focus groups surfaced the real JTBD: "I don't need better analysis. I need to get out of Excel faster and look professional to my client."

**Task**
Test whether value-metric repositioning (output speed, not accuracy) moves conversion, with defined KPIs and a decision rule before asking Eng to scale.

**Action**
- **Hypothesis:** `If we reposition from "most accurate" to "fastest Excel→client presentation" for M&A advisor segment, then landing conversion will +Δ because the stall is presentation speed, not model depth.`
- **Setup:** Mixpanel-class + Pendo + in-house telemetry; profile/segment split; single variable (headline + supporting proof), hold copy/price constant; pre-registered **Primary: landing conversion rate** (visitor→trial/request), **Diagnostic: click-through**, **Guardrail: trial→WAU/retention not regressing**. Null-hypothesis framing before scaling — `RES/data/master_context.md:479`
- **Analysis:** segment-aware (advisor vs appraiser vs broker), cohort follow-on to WAU; excluded novelty Day 1-3; reported absolute + relative + CI.
- **Second test surface:** onboarding flows (TTV) — same rigor, **+45% TTV/adoption** as distinct test, not merged with landing lift.

**Result — `PORTFOLIO/CONCEPT3/plg.html:464-483` + `RES/data/master_context.md:501-504`**
- **+7% conversion** from message alone (landing repositioning)
- **+45% TTV/adoption** from onboarding flows (separate lever)
- **+14% retention** from lifecycle messaging (two-year depth)
- Decision rule held: scale message + onboarding, kill demo-feature backlog

**90-sec cut**
> "We were losing at the headline — 'most accurate' sounded good in demos but conversion stalled. Hypothesis: if we reframe to 'fastest Excel to client presentation' for advisors, conversion lifts because the stall is presentation speed. Setup was one variable — headline plus proof — pre-registered primary conversion rate and guardrail WAU so we didn't spike signup but lose activation. We split by advisor segment and tracked cohort WAU past the novelty window. Result: 7% conversion lift from copy alone, and separately 45% TTV lift from onboarding flows. I scaled the winners and killed two planned features that demoed well but had no workflow signal. For eBay I'd run triggers the same way — one hypothesis per trigger, trigger-rate-aware power, open-time decisioning, and I never report CTR without RPR and guardrail health."

**Experimentation checklist Paloma will want to hear**
Randomization unit (sticky user_id), stratified by locale/device/tier, power/MDE with trigger rate, ramp 1%→10%→50%, SRM/CUPED, sequential boundaries (no peeking), 4-8 week holdout for fatigue, rollback if guardrail regresses.

---

## S5 — Aligned Conflicting Stakeholders / Led Complex Initiative [Cross-Functional]

**JD tag:** `Develop and maintain project plans, lead dependencies, and ensure teams are aligned and execution-ready` + `Track record leading complex, cross-functional initiatives end-to-end`

**Situation — `RES/data/master_context.md:460-466;526-535` + `PORTFOLIO/CONCEPT3/hris-ma.html:528-545`**
Two direct parallels for eBay stakeholder tension:

- **Netsweeper (MSP channel):** Eng wanted new detection categories (more coverage = more value) while district staff had stopped opening dashboards — **8/10 alerts false positives** — trust collapse threatened contract + MSP partner retention.
- **BVXpress HRIS (M&A):** Stakeholders wanted "replace every payroll system"; deal teams needed answers *now* while HRIS incompatibility blocked diligence.

**Task**
Resolve roadmap standoff with influence, not authority — reframe success metric so Eng/Data/Design could agree on what to ship first.

**Action — Netsweeper pattern (use for eBay influence story) — `RES/data/master_context.md:457-459`**
- Ran focus groups + tree tests: surfaced that adding detection with same false-positive rate would accelerate trust collapse.
- Reframed KPI from "detection accuracy" to **"operational trust"** — unlocked prioritization. Froze new features one quarter; redirected outsourced team to false-positive pruning, alert workflow redesign, QA cycles.
- DACI: you driver, Eng contributor (pruning + workflow), Data contributor (alert vector analysis), Design contributor (hierarchy).

**Action — BVXpress pattern (use for eBay platform story) — `PORTFOLIO/CONCEPT3/hris-ma.html:531-545`**
- Workflow interviews + build-vs-buy matrix killed "replace everything" — stakeholders wanted source systems to stay authoritative.
- Shipped **adapter-first architecture** (universal adapter pattern, Frappe HRMS reference, normalized model: job families, comp views, hierarchy) with ingestion validation + confidence scores before net-new analytics — because tree tests failed when dashboard numbers disagreed.
- Shipped to **3 HR/diligence teams on live deals** — `RES/data/master_context.md:521`

**Result — `RES/data/master_context.md:465-466;515-517`**
- Netsweeper: **85% false-alert reduction** across 35-school deployment; staff re-engaged unprompted; contract renewed; protected MSP channel retention.
- HRIS: adapter-first vs 6-18 month migrations; diligence dashboards answered headcount/comp/retention risk without custom report projects.

**90-sec cut (pick one, Netsweeper is punchier for behavioural)**
> "At Netsweeper, engineering wanted new detection categories while district staff had quit opening dashboards — 8 in 10 alerts were false. I ran focus groups and tree tests showing more detection would accelerate trust collapse. I reframed the KPI from detection accuracy to operational trust, froze new features a quarter, and redirected the outsourced team to pruning false-positive vectors and redesigning alert hierarchy. 85% false-alert reduction, staff re-engaged unprompted, contract renewed. That's the same influence motion as eBay comms — when Eng wants more triggers and Design wants cleaner cards, I bring the stall — inbox fatigue, not coverage — and propose the minimal viable experiment that proves trust first, then scales."

**eBay bridge — project plan language Paloma expects**
Theme → PRD → DACI → dependencies (telemetry, decisioning, Design system, Analytics instrumentation) → phased rollout (cohort → geo → portfolio) → success (primary + guardrail) → rollback criteria upfront.

---

## Appendix — Metric Hygiene (never merge across stories)

| Story | Metric | Isolation |
|-------|--------|-----------|
| S1/S2 | ARPU $450→$600 (voluntary upgrades) | Suite expansion, not landing test |
| S1/S2 | +45% TTV/adoption | Onboarding flows (cloud SKU incl.) — separate from conversion |
| S4 | +7% conversion | Landing repositioning alone |
| S1/S2 | +14% retention (2yr) | Lifecycle messaging + onboarding depth |
| S1 | 2× retention at 3+ products | Multi-product depth cohort |
| S5 | 85% false-alert reduction | Netsweeper 35-school deployment — cite as influence pattern, not BVXpress |
| S3 | 3× take rate | Village Wellth 4→3 tiers — time-bounded, cite as range proof, not BVXpress anchor |
| All | 1,400+ users / 8 products / 5 launches | Context `RES/data/master_context.md:498;504` — not hero, but scope credibility |

**Portfolio links to have open:**
- `PORTFOLIO/CONCEPT3/bvxpress-pricing.html` — pricing architecture deep-dive
- `PORTFOLIO/CONCEPT3/plg.html` — PLG loops + scorecard
- `PORTFOLIO/CONCEPT3/hris-ma.html` — adapter-first / trust-before-analytics pattern
