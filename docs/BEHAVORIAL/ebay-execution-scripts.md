# Execution Scripts — eBay HM Paloma (Behavioural Round)
> Word-for-word tracks. Time-boxed. Each ends with an eBay bridge.

---

## 1. "Tell me about yourself" — 60 sec (why eBay + why this portfolio)

> "I'm Bob — founding product at BVXpress where I was employee three, first product hire, and built the product function 0→1. Over nine years I launched five products and operated eight for 1,400 users in M&A advisory — no public price book, every deal a custom composition of module, seats, term, discount, and expansion rights.
>
> What ties that work together is lifecycle comms instrumented by telemetry. I built an in-house analytics suite plus Pendo to tune triggers on usage patterns, SaaS renewal dates, and discount logic — not blast campaigns. The hard lesson: we had under 20% WAU despite demo love because users stalled before first deal flow. Fixing onboarding lifted TTV 45%, repositioning the value metric from 'most accurate' to 'fastest Excel to client presentation' lifted conversion 7%, and lifecycle depth lifted retention 14% over two years. Voluntary suite upgrades moved ARPU $450→$600 — not a price hike.
>
> That's why Conversion Programs fits: eBay's Email/Push/Native Hub portfolio is the same motion at marketplace scale — real-time intent signals like watchlist, saved search, cart, and ending-soon, decisioned at open-time, with suppression and channel orchestration so you drive incremental orders without burning trust. I'd bring the same loop: find where the lifecycle breaks, change one lever, write the metric back."

*Cite if pressed: `RES/data/master_context.md:470-505` + `PORTFOLIO/CONCEPT3/plg.html:411-483` + `PORTFOLIO/CONCEPT3/bvxpress-pricing.html:511-526`*

---

## 2. "Own and implement the roadmap with Eng/Data/Design" — 90 sec

> "At BVXpress the roadmap tension was Eng wanted analytical depth, Design wanted cleaner onboarding, Data wanted more instrumentation. After launches one and two, telemetry said under 20% WAU — users abandoned before first workflow. Opportunity maps ranked the stall as presentation, not modeling — four hours per engagement formatting Excel for clients.
>
> I reframed the roadmap from analytical depth to output speed. In DACI I was driver, Eng/Data/Design were contributors. I killed a planned deal-database and fee-benchmarking tool — both demoed well but had zero workflow demand — and sequenced the next three products to attack the client-facing workflow: presentation speed, then export, then suite expansion.
>
> I ran the roadmap as Now/Next/Later themes, not a feature list, and gated every Next on 20-plus cohort adoption before scaling. Aha! backlog, telemetry fence tuning, prototype walkthroughs. That pivot drove 45% TTV lift, ARPU $450→$600 voluntarily, and 2× retention at 3-plus products — which then became the GTM shift to onboarding depth over acquisition breadth.
>
> At eBay I'd run the same: Now is suppression and Send-Time Optimization, Next is trigger intelligence per intent signal, Later is cross-channel orchestration — each gated on cohort adoption and guardrail health. Eng gets a phased plan with dependencies explicit — telemetry, decisioning, Design system, Analytics instrumentation — and a clear de-commit path if trigger rate or guardrail regresses."

---

## 3. "How do you size and prioritize?" — 90 sec

> "I size bottom-up, not TAM. Expected Value equals eligible reach times funnel conversion times lift times ARPU times probability of success — built from telemetry cohorts.
>
> Example at BVXpress: there was no price book, so I sized the adjacent segment — appraisers doing terminal-value work who wouldn't buy BVX at entry. Eligible reach was that segment, conversion was NTV→BVX fence-hit to upgrade rate, lift was voluntary suite adoption, ARPU $450 to $600. I evaluated tradeoffs as blended deal margin, not SKU P&L — NTV accepted thin or negative margin because conversion to BVX at full margin plus suite expansion paid it back. Feature fences — GGM versus AGM, spreadsheet versus desktop, Deal Quantifier gating — were tuned per segment from telemetry.
>
> Prioritization was RICE plus explicit override. When retention data showed 3-plus products retained at 2×, I funded onboarding depth over acquisition breadth even though acquisition scored higher on reach. That call moved ARPU and retention durably; a Village Wellth parallel — 4→3 tier consolidation — drove 3× take rate by removing decision friction.
>
> For your portfolio I'd size the same: eligible intent population — watchlist, cart, saved search — times trigger rate times current conversion times RPR uplift at, say, 20-30 basis points, times probability. Then I cost it — Eng effort, data dependencies — and sensitivity-test lift plus/minus 50% and trigger rate plus/minus 30% to find breakeven. If breakeven needs a 40% lift but history says triggered flows max at 18% conversion lift, I pass."

---

## 4. "How do you increase experimentation velocity?" — 90 sec

> "Velocity at BVXpress wasn't blocked by tooling — we had an in-house suite and Pendo. It was blocked by testing the wrong things. I built a tight loop: instrument — module usage, fence-hit, deal-flow completion, export actions — diagnose — under 20% WAU before first workflow — hypothesize — output speed not accuracy, NTV lands adjacent segment, fences drive upgrade — change — kill or sequence — measure — WAU, conversion, ARPU, retention.
>
> Three moves unlocked velocity: one, single hypothesis per release with one measurement window — landing headline alone drove 7% conversion, onboarding flows alone drove 45% TTV; never bundled. Two, profile and segment tests to decide enhance versus deprecate — if telemetry showed a feature was demo-only, it was killed. Three, gating launches on 20-plus cohort adoption before scaling, so Eng wasn't building for ghosts.
>
> For eBay Email/Push/Hub I'd instrument the same loop but add marketplace-specific physics: trigger-rate-aware power — if only 12% of users hit a trigger, sample needs to be 8× — sticky user_id randomization stratified by locale/device/engagement, 1%→10%→50% ramp with pre-registered guardrails — unsub, spam, push opt-out, D30 retention — CUPED with pre-period, sequential boundaries so we don't peek, and a 4-8 week holdout to catch fatigue. Velocity goes up when you kill ideas that demo well but don't move RPR, and you gate every Next on cohort signal from the last."

---

## 5. "Walk me through an A/B test you led" — 90 sec

> "We were losing at the headline — 'most accurate valuation' stalled landing conversion despite strong demos. Hypothesis: if we reposition to 'fastest Excel to client presentation' for advisors, conversion lifts because the stall is presentation speed, not model depth. Focus groups had surfaced that exact quote: 'I don't need better analysis, I need to get out of Excel faster.'
>
> Setup: single variable — headline plus supporting proof — hold copy and price constant. Split by advisor segment, sticky user_id, stratified by engagement tier. Pre-registered primary landing conversion — visitor to trial — diagnostic click-through, guardrail trial to WAU and 30-day retention so we didn't spike signup but lose activation. Mixpanel-class plus Pendo plus in-house telemetry.
>
> Analysis: segment-aware, cohort follow-on past Day 1-3 novelty, reported absolute plus relative plus confidence interval. A second, separate surface — onboarding flows — lifted TTV 45% — kept isolated, never merged with the 7% landing lift.
>
> Result: 7% conversion from copy alone, scaled immediately; onboarding flows scaled on their own merit. What got killed: deal-database and fee-benchmarking — zero workflow signal.
>
> For eBay I'd run triggers identically — one hypothesis per trigger, e.g., 'price-drop Push within one hour for high-intent watchers lifts incremental orders 4% because urgency plus relevance' — primary incremental orders per 1K sends, guardrail unsub/spam/push opt-out, holdout 6 weeks to detect habituation. I never report CTR without RPR and guardrail health."

---

## 6. "Tell me about leading a complex cross-functional initiative" — 90 sec (pick one of two)

**Option A — Netsweeper (punchier influence story)**
> "At Netsweeper, Eng wanted new detection categories — more coverage equals more value — while district staff had quit opening dashboards because 8 in 10 alerts were false. Contract plus MSP partner retention at risk. I ran focus groups and tree tests showing more detection at the same false-positive rate would accelerate trust collapse. I reframed the KPI from detection accuracy to operational trust. In DACI I was driver, Eng contributor for pruning, Data for vector analysis, Design for hierarchy. Froze new features a quarter, redirected the outsourced team to false-positive pruning, alert workflow redesign, QA cycles. 85% false-alert reduction across 35 schools, staff re-engaged unprompted, contract renewed."

**Option B — BVXpress HRIS (platform story closer to eBay's scale)**
> "During an M&A wave, every acquisition meant 6-18 month HRIS migrations, duplicate records, deal teams unable to answer diligence. Stakeholders wanted 'replace every payroll system.' I ran workflow interviews and a build-versus-buy matrix that killed replacement — source systems needed to stay authoritative. As driver, I aligned Eng on an adapter-first architecture — universal adapter, Frappe HRMS reference, normalized model for job families, comp views, hierarchy — with Data validating at ingestion and scoring confidence before any new analytics. Design owned the minimal diligence dashboard. We shipped to three diligence teams on live deals. That's the same as eBay comms platform work — source of truth stays, intelligence layers on top."

> "Either way, my move is the same: bring the stall — inbox fatigue, not coverage; migration friction, not analytics — propose the minimal viable experiment that proves trust first, then scales. Project plan always themes to PRD to DACI to dependencies — telemetry, decisioning, Design system, instrumentation — to phased rollout — cohort to geo to portfolio — with success as primary plus guardrail and rollback criteria upfront."

---

## 7. "How do you handle trigger logic / audience strategy / suppression?" — 60 sec

> "Audience is not a segment — it's 1:1 decisioning per open. At BVXpress that was per-customer module composition tuned by usage; at eBay it's per-recipient ranking at open-time. I think in triggers as events — watchlist, saved search, cart, price-drop, seller follow, ending-soon — each with eligibility, suppression, and frequency cap. Suppression is first: if purchased or converted, exit. Then frequency cap — global send budget with queue prioritization, not channel-siloed blasts. Then Send-Time Optimization and channel orchestration — email not opened could become Push or Hub card — with impression caps so history doesn't look like spam. The portfolio wins when the wrong message is suppressed, not when the right message is sent faster."

---

## 8. Closing — "What questions do you have for me?" (pick 2, behavioural-appropriate)

**Tailored for Paloma as HM:**

1. "Where is experimentation velocity most constrained today — platform, data decisioning, or cross-functional process — and where would you want this role to unblock in the first 90 days?"

2. "For Offers, how do you weigh conversion lift against marketplace health — notification fatigue, promo-seeking, seller margin — what's the guardrail that actually governs your ship decision?"

**Backup if time:**
- "Is the portfolio run as one backlog or Conversion versus Offers as two? How do you arbitrate when they compete for Eng capacity?"
- "What does good look like at 90 days versus 12 months — more coverage or more intelligence per trigger?"

> **Close line:** "What resonated from BVXpress that you'd want me to double-click on for the next round?"

---

## Appendix — Numbers to keep straight (do not merge across stories)

- BVXpress scope: 8 products, 1,400+ users, 5 launches, first product hire — `RES/data/master_context.md:498`
- +45% TTV/adoption — onboarding flows (incl. cloud SKU) — `RES/data/master_context.md:502`
- Landing repositioning — +7% conversion (message alone) — `PORTFOLIO/CONCEPT3/plg.html:470-472`
- ARPU $450→$600 (voluntary upgrades, no list hike) — `PORTFOLIO/CONCEPT3/bvxpress-pricing.html:511-526`
- +14% retention over 2 years (lifecycle depth) — `RES/data/master_context.md:501`
- 2× retention at 3+ products — `PORTFOLIO/CONCEPT3/bvxpress-pricing.html:518; RES/data/master_context.md:504`
- 85% false-alert reduction (Netsweeper, 35 schools) — influence pattern, not BVXpress — `RES/data/master_context.md:465`
- 3× take rate (Village Wellth 4→3 tiers) — range proof, not anchor — `RES/data/master_context.md:403`

**Voice rule (per `RES/data/master_context.md:104`):** Name a tool only as evidence for a decision, never as headline — "telemetry showed <20% WAU, so I killed X" not "I used Pendo."
