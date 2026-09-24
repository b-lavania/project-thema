# eBay — HM Paloma — Behavioural Round Cheat-Sheet
### Conversion Programs (CRM) | Email / Push / Native Hub | Hybrid Conversion + Offers

> **How to use:** Skim tables before the call. Speak from STAR bank (next file). Close with 2 questions *for Paloma*.

---

## 1. Company Snapshot — eBay Now (anchor every answer in this)

| Metric | Value | Why Paloma cares |
|--------|-------|------------------|
| **GMV** | ~$80B (2025), US +10% | Your portfolio *is* conversion — GMV = buyers × conversion × AOV |
| **Revenue** | $11.1B (+7%), take rate **14%** | Revenue = fees on paid transactions + $2B ads + shipping |
| **Buyers** | **136M active**, 16M enthusiasts @ **~$3,600/yr**, 70% of GMV from Focus/C2C/Recommerce | Enthusiast velocity is the north star; new-buyer acquisition feeds it |
| **Listings** | 2.6B live, 1.3B promoted | More supply ≠ more conversion unless matching improves |
| **Strategy pillars** | Focus Categories (parts, collectibles, fashion, electronics), C2C (+20%), Recommerce (>40% GMV), eBay Live 8×, Magical Listing (+50% listings/lister) | Your comms sit mid-bottom funnel re-engaging high-intent lapsed intent |
| **2025-26 inflection** | GenAI CRM emails +40% quality visits, agentic search beta +50% engagement, ads 2.8% of GMV (target 3%+) | "AI decisioning" is not buzzword — it's open-time rendering + bandit in her stack |

**One-liner if she asks "what do you know about eBay?":**
> "Two-sided marketplace at ~$80B GMV where I'm successful when sellers are successful — 136M buyers, 2.6B listings, take rate 14%. The bet is Focus/C2C/Recommerce as 70% of GMV growing 20%, with Live and Magical Listing unlocking supply — and Conversion Programs is the real-time CRM layer that turns intent (watch, cart, saved search) into completed purchases without burning trust."

---

## 2. Team & Role — What Paloma Owns

**Conversion Programs = multimillion-dollar communications portfolio.** Not batch blasts. Core job:

> Activate expressed + observed intent across **Email, Push, Native Hub** — using **personalization, trigger logic, ranking, suppression, frequency capping, STO, channel orchestration** — to drive incremental orders while protecting marketplace health.

**Hybrid reality (your read):** Conversion (browse→purchase) + **Offers CRM** (Make Offer, price-drop, ending-soon, saved-seller new listings). Offer negotiation is eBay's unique conversion mechanic — psychology matters (anchoring, urgency, social proof) as much as tech.

**Stakeholders:** Engineering (notification streaming platform, targeting infra), Data Science (ranking/bandit/recommendations), Design (email/push/hub UX), Analytics/Build/CRM, plus Buyer/Seller product teams.

**Her KPIs (what she measures you on):**
- **Primary (decision):** Incremental orders / conversion rate / 7-day reactivation / revenue-per-recipient (RPR) — defined as numerator/denominator + attribution window
- **Guardrails (must not regress):** unsubscribe, spam complaint, push opt-out/uninstall, deliverability, D30 retention, seller quality
- **Diagnostic:** open rate, CTR/CTOR — never optimize these alone post Apple MPP

**What "good" looks like in 90 days (use to ask her):**
> "Shipped 2-3 experiments that move RPR without regressing guardrails, with a clear suppression/orchestration model and a holdout proving durable lift, not just novelty."

---

## 3. Marketplace Lens — Speak Like an eBay PM

**Liquidity triangle:** Supply density × Demand frequency × Match speed/quality. Weakest edge = priority. For comms, match quality *is* the lever — right offer, right message, right time, right channel.

**Why not just "more notifications"?**
- Buyer win vs seller hurt tradeoff (push too hard → returns/cancellations, trust erosion)
- Cold-start: new sellers need liquidity injection differently than power sellers
- Second-order: promo-seeking, fatigue, habituation (need 4-8 week holdouts, not 7-day sugar highs)

**Trust accelerators to name-drop:** Authenticity Guarantee, Money Back Guarantee, Managed Shipping, Promoted Listings — conversion doesn't happen without them.

---

## 4. Trigger Mapping — BVXpress → eBay (your translation table)

| BVXpress (your truth) | eBay equivalent | What you'd say to Paloma |
|-----------------------|-----------------|--------------------------|
| **Telemetry: module usage, fence-hit events, deal-flow completion, export actions** — `RES/data/master_context.md:486;499` | Watchlist, saved searches (up to 100), watched-item-ending-soon, cart, checkout abandon, followed seller new listing | "At BVXpress I instrumented fence-hit events and deal-flow completion with an in-house telemetry suite — same motion as watching watchlist/cart/saved-search as intent signals, then ranking at open-time." |
| **Usage patterns: <20% WAU, abandonment before first deal flow** — `PORTFOLIO/CONCEPT3/plg.html:451-457` | Browse abandon, high-intent browsing, recently viewed | "Diagnosed <20% WAU despite demo love — identical to browse-abandon leakage; the fix wasn't more triggers, it was fixing the stall before the trigger." |
| **SaaS renewal date + lifecycle stage (NTV→BVX→suite)** — `PORTFOLIO/CONCEPT3/bvxpress-pricing.html:543-583` | Price-drop, back-in-stock, ending-soon urgency, renewal is re-engagement window | "Renewal date is eBay's ending-soon moment — urgency + price-drop trigger. I built NTV→BVX as a loss-leader ladder measuring blended deal margin, not SKU P&L." |
| **Discounting: custom deal composition (module×seats×term×discount×expansion)** — `PORTFOLIO/CONCEPT3/bvxpress-pricing.html:676-689` | Offers / Make Offer, promotions, coupon, deal-based shopping interactions | "Every deal was custom — deepest discount on NTV land, tight bands on BVX. That's Offers CRM: right offer, right timing, without training permanent discount expectation." |
| **Onboarding/lifecycle messaging: personalized onboarding, lead-routing → +14% retention, +45% TTV** — `RES/data/master_context.md:501-502;505` | Welcome/onboarding flows, post-purchase, winback | "Welcome flow drove +45% TTV/adoption; lifecycle messaging +14% retention over 2 years — but only after fixing the onboarding stall first." |
| **Pricing repositioning: "most accurate" → "fastest Excel→presentation" → +7% conversion** — `PORTFOLIO/CONCEPT3/plg.html:470-472` | Message/market fit for Email subject, Push copy, Hub card | "7% conversion from message alone — same lever as subject/push copy. The value metric was output speed, not accuracy." |

**One-liner bridge:**
> "BVXpress was 8 products / 1,400 users with no public price book — every account a custom composition tuned by telemetry. That's the same muscle as eBay's 1:1 open-time decisioning: instrument, diagnose stall, hypothesize, change one lever, write metric back."

---

## 5. Communications Craft — Email vs Push vs Native Hub

| Surface | Constraints | Your POV |
|---------|-------------|----------|
| **Email** | Deliverability, 6-8 slots as ad slots, open-time rendering, inbox competition | Personalize at open, not send; bandit amplifies winners; cross-channel cap if not opened |
| **Push** | 40 chars title, opt-in fragility, timezone, frequency cap (global send budget), uninstall risk | Queue-based prioritization; STO; suppression if purchased; never optimize CTR alone |
| **Native Hub** | In-app, logged-in, highest intent, UX hierarchy matters | Hub is post-open: ranking + suppression + relevance; test card order, not just copy |
| **All channels** | Fatigue, habituation, cannibalization | 4-8 week holdout or dark test; 2×2 factorial (Email On/Off × Feature On/Off) to isolate; CUPED with pre-period |

---

## 6. Metrics — What You Track (and What You Never Ship Without)

**Hierarchy:**
- **Primary:** Incremental orders per 1K sends, conversion rate, 7-day reactivation, RPR
- **Guardrails (one-sided, must not regress):** unsub, spam, push opt-out, D30 retention
- **Diagnostic:** open (deliverability canary), CTR/CTOR, click-to-open

**Benchmarks to cite (for sizing, not as targets):**
- Campaign avg: open ~30.7%, CTR 1.3-1.7%, conversion 0.08%, $0.11-0.18/email
- Flows (triggered): open 38-48% (welcome 52%, cart 42%), CTR 4.7-5.6% (3× campaigns), conversion 1.49% (18×), **$2.87-3.41/email (22×)** — flows = 5% sends, **41% revenue**
- Best automations: cart $3.55, welcome $2.35, back-in-stock $9.14 (rare, highest RPR)
- eBay historical: Phrasee AI +15.8% open / +31.2% click (101M subs); GenAI CRM +40% quality visits

**Interview move:** Always define numerator/denominator + window. Report absolute + relative + CI. "CTR +12% is meaningless until I tell you incremental orders and whether unsub regressed."

---

## 7. Experimentation — HM Will Test This Hard

**Structure you will recite:**
1. Hypothesis: `If [change] for [segment], then [metric] Δ because [insight]`
2. Randomization: sticky `user_id` hash, stratified by locale/device/engagement tier; trigger-rate aware
3. Power/MDE: `n ≈ (Z1-α/2+Z1-β)²·2p̄(1-p̄)/Δ²`, α=0.05, power 80-90%; inflate for cluster/trigger rate
4. Ramp: 1%→10%→50% with health checks; pre-defined rollback if guardrail ↑ >0.3ppt & p<0.05
5. Analysis: ITT, SRM, CUPED, cluster-robust SEs if needed; exclude Day 1-3 novelty; 4-8 week holdout for fatigue
6. Decision: Primary must clear; guardrails must not regress; report $ impact + CI, not just relative lift

**When NOT to test:** cost of being wrong < cost of delay, <5% users or reversible in 10 mins, accessibility/bug fix.

---

## 8. Smart Questions FOR Paloma (pick 2, behavioural round)

**Velocity & ownership:**
- "Where is experimentation velocity bottlenecked today — platform, data/decisioning, or cross-functional process? Where would you want a PM to unblock in first 90 days?"
- "How do you split roadmap ownership between Conversion vs Offers — are they one backlog or two, and how do you arbitrate when they compete for Eng capacity?"

**Craft & tradeoffs:**
- "For Offers, how do you think about balancing conversion lift vs marketplace health — notification fatigue, promo-seeking, seller margin — what's the guardrail that actually governs ship decisions?"
- "Email/Push/Hub orchestration — is the portfolio managed as a global send budget with queue prioritization, or channel-siloed? Where's the biggest cannibalization risk you've seen?"

**Success & scope:**
- "What does 'good' look like at 90 days vs 12 months for this portfolio? Is it more coverage (more triggers) or more intelligence (better ranking/suppression per trigger)?"
- "GenAI CRM drove +40% quality visits — how much of the roadmap is AI decisioning vs trigger/messaging fundamentals? Where's the next headroom?"

**Cross-functional:**
- "Who are the closest partners — Data Science, Build, Design — and where does DACI get fuzzy in practice? Where do you need the PM to be driver vs contributor?"

---

## 9. Your Positioning Pillars (30-sec spine, metric-free per resume rules)

> "I find the real bottleneck, reduce ambiguity, build the system that makes the fix permanent — `RES/data/master_context.md:5-10`"

**BVXpress proof (Lead with this, not Moovez):**
- Built product function 0→1 as employee #3, launched 5 products, operated 8 for 1,400+ users — `RES/data/master_context.md:498`
- +14% retention over 2 years from onboarding depth + lifecycle messaging, built from scratch — `RES/data/master_context.md:501`
- +45% TTV/adoption from new onboarding flows (including complex cloud SKU) — `RES/data/master_context.md:502`
- Landing message repositioning +7% conversion — `PORTFOLIO/CONCEPT3/plg.html:470-472`

**eBay translation (one sentence):**
> "I ran lifecycle comms at BVXpress instrumented by in-house telemetry — custom triggers on usage + renewal + discount logic — the same motion as eBay's intent-signal triggering, but I learned the hard lesson: you don't start with a trigger or discount, you find where the lifecycle breaks first."

---

## Appendix: File Guide

- `RES/data/master_context.md:470-505` — BVXpress ROLE 5 truth (telemetry stack, A/B tests, GTM)
- `PORTFOLIO/CONCEPT3/bvxpress-pricing.html:511-583` — Pricing architecture (loss-leader ladder, feature fences, custom deals)
- `PORTFOLIO/CONCEPT3/plg.html:411-483` — PLG loops, TTV/ARPU/retention scorecard
- `RES/outputs/bvxpress-to-ebay-star-bank.md` — 5 STARs (next file)
- `RES/outputs/ebay-execution-scripts.md` — Roadmap/sizing/velocity word tracks (third file)
