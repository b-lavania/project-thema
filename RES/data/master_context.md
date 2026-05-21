# Master Resume Context — Bob Lavania

This file consolidates all resume variants and portfolio metrics into a single source of truth for generation. It is optimized for LLM context windows using metadata tags and structured formatting.

---

## Target Personas (For LLM Context)
- **Persona A (AI/Technical PM)**: Lead AI Product Manager, Technical Product Manager, PM - AI, PM - Prompting
- **Persona B (Platform/Ops PM)**: Product Manager - Marketplaces, Product Operations Manager
- **Persona C (Growth PM)**: PM - Growth/Monetization

---

## Contact
- **Name**: Bharat "Bob" Lavania
- **Email**: xblavania@gmail.com
- **Phone**: (312) 772-7962
- **LinkedIn**: linkedin.com/in/blavania
- **GitHub**: github.com/blavania
- **Location**: Calgary, AB & San Francisco, CA (Remote across US and Canada)

---

## Three Operating Themes (Portfolio-Derived Positioning)
1. **Pricing Architecture** — Redesigning how value is captured: tier consolidation, real-time quote engines, discount logic, ARPU optimization. Done across M&A SaaS, logistics, education, and insurance.
   - Proof: 3x take rate · $450→$600 ARPU · 18% lower CAC
2. **Operational Intelligence** — Replacing manual, chaotic processes with AI systems (computer vision, conversational agents, OR engines, predictive frameworks). Built and deployed in production.
   - Proof: 60 min→3 min quoting · 50% support deflection · 85% false-alert reduction
3. **Zero-to-One Build** — Launching products from whiteboard and building the commercial engine around them: messaging, funnels, retention, unit economics.
   - Proof: 5 products launched · 14% retention lift · 7% conversion lift · 93% fill rate

---

## Key Insights (from Case Studies)

- **AI systems**: "AI systems succeed when they reduce operational ambiguity, not when they maximize sophistication. Focused on structured information capture and reliable handoffs over open-ended interaction." (Moovez/Quotely) → Led me to engineer hard operational handoffs instead of freeform chat loops, deflecting 50% of support tickets.
- **Pricing**: "Pricing problems are often decision architecture problems, not just monetization problems. Simplifying choices can be more valuable than optimizing price points." (Village Wellth) → Led me to consolidate 4 pricing tiers into 3, resulting in a 3x increase in take rate by eliminating plan confusion.
- **Detection**: "Detection systems fail when users stop trusting the signal. Accuracy metrics alone are insufficient. Operational reliability matters more than theoretical performance." (Netsweeper) → Led me to freeze feature additions and aggressively prune high false-alert vectors, reducing alerts by 85% and restoring district trust.
- **Energy/Infrastructure**: "Each workflow step surfaces a risk class the others cannot see. Deployability is a coupling problem — the product's job is to make those couplings explicit, comparable, and reviewable." (Project Epsilon) → Drove the architecture of the Scenario contract interface, eliminating model drift.

---

## Working Principles
- Build for operational simplicity first; add features only when they solve real problems
- Ship AI that reduces friction in existing workflows, not AI for novelty's sake
- Fix decision-making upstream before building dashboards downstream
- Prioritize signal quality over data volume
- Design products that reduce cognitive load, not increase it
- **Research narrative rule**: Treat research tools like engineering tools — frame outcomes as **decisions influenced** (funnel change, tier consolidation, alert workflow redesign), not tool laundry lists ("used Hotjar"). Name a tool only when it supports a concrete product decision in that role block.

---

## Skills & Core Domains (Structured for LLM Parsing)
- **Product contexts**: Marketplaces, eCommerce, Risk & insurance, Applied tech (chatbots, voice agents, computer vision)
- **Domains**: AI/Engineering, Marketplace Commerce, eCommerce, Risk & Insurance, Marketing Science, Operations Research, User Research
- **AI/Modeling Methods**: LLM pipelines, prompt orchestration, Computer Vision (CV), conversational/SMS agents, Bayesian Media Mix Modeling (MMM), Multi-Touch Attribution (MTA), Ridge Regression, Monte Carlo stress testing, PyPSA linear programming, 3D bin packing
- **Product/Growth Methods**: Supply-demand balancing, checkout funnel optimization, pricing systems, entitlement logic, hypothesis testing, cohort analysis, STP (segmentation, targeting, positioning), GTM scaling
- **User research methods**: User interviews, focus groups, tree testing, opportunity maps, session replay, funnel diagnostics, clickable prototypes
- **Market research / analytics**: Hypothesis testing, R, SQL, Media Mix Models, attribution models, STP
- **Tools/Tech (confirmed by role)**: Aha! (Netsweeper, BVXpress), Pendo (BVXpress), Heap (Moovez), Segment (Moovez), Microsoft Clarity & Hotjar (Moovez), opportunity maps (fractional startups, BVXpress, Moovez, Liohan, and others), Jira, Confluence, Mixpanel, R, SQL, HubSpot, ActiveCampaign, Zoho, Cursor, Windsurf, Lovable, Stripe/Square APIs

---

## Career Arc

8+ years in product management across B2B SaaS, AI, marketplaces, logistics, healthcare, and FinTech.

- **2012–2021 (9 yrs)**: Built the product function from scratch at BVXpress — first PM hire, launched 5 products, 1,400+ users.
- **2022–2023**: Full-time PM at Netsweeper, shipping an AI content-compliance product for K-12.
- **2022–2025 (concurrent)**: Fractional Product Lead across AI, logistics, FinTech, and healthcare startups.
- **2024–Present**: Founding PM at Moovez/Quotely — logistics AI platform commercialized as a standalone SaaS.

---

## Professional Experience

### ROLE 1: Founding Product Manager
- **Company**: Moovez — marketplace for last-mile delivery & moving (Calgary, AB; ~5 employees)
- **Title**: Founding Product Manager
- **Dates**: Jan 2024 - Present
- **Location**: Remote / Calgary, AB
- **Tags**: `[0-to-1]`, `[Marketplace]`, `[AI/CV]`, `[Pricing]`, `[Operations]`, `[User Research]`, `[eCommerce-adjacent logistics]`
- **Research & analytics tooling (confirmed)**: Heap, Microsoft Clarity, Hotjar, Segment, focus groups, tree testing, opportunity maps
- **Environment**: Reported directly to CEO. Product lead owning user research, conversions, and retention. Oversaw a team of 4 developers (1 direct report).
- **Problem**: Dispatchers were manually estimating job costs over the phone (60+ min per quote), causing margin erosion from inaccurate pricing and losing customers to faster competitors.
- **Key Outcomes**: GMV $500k+; CAC ~$100; LTV $1,000+; Retention 12+ months; Fill rate ~93% (vs. ~70% industry avg). Time-to-quote reduced from ~1 hour to 3 minutes (20x faster).
- Engineered 3D bin-packing Operations Research engine solving three NP-hard sub-problems simultaneously (job duration, crew count, truck loading) — reduced job costing latency by 95% and increased volume predictive accuracy to 85%.
- Built Computer Vision pipeline where customers photograph items for instant quote generation; CV model estimates volume, weight class, and handling complexity — no dispatcher call required. Built multi-model evaluation testbench scoring Gemini Flash and GPT-4.1 on accuracy, latency, and cost.
- Deployed SMS/Voice AI agent for automated intake, booking confirmations, and reschedules, deflecting 50% of support tickets with zero human intervention.
- Built real-time pricing and payment flows (Stripe, Square) based on distance and volume, eliminating the major checkout bottleneck and reducing quote-to-payment drop-off.
- Built opportunity maps for quote-to-booking; focus groups and tree tests plus session replay (Heap, Clarity, Hotjar) and event instrumentation (Segment) drove checkout simplification and intake prioritization — not tool-led discovery.
- System successfully commercialized as Quotely (quoteperfectly.com), a standalone SaaS now sold to other logistics operators.

### ROLE 2: Principal Product Lead (Fractional)
- **Company**: Various startups (Village Wellth, Liohan, e-commerce, insurance/finance, construction)
- **Dates**: Feb 2022 - May 2024 (includes short Liohan engagement, Jan–May 2024)
- **Location**: Remote / Calgary, AB
- **Tags**: `[Fractional]`, `[eCommerce]`, `[Risk/Insurance]`, `[Marketplace]`, `[User Research]`
- **Research tooling (confirmed)**: Focus groups, tree testing, opportunity maps (across fractional engagements — pricing, funnel, onboarding, and positioning decisions)
- **Liohan (Jan–May 2024, small engagement)**: Opportunity maps clarified problem spaces and sequenced bets before build; informed roadmap priorities and scope cuts.

#### Village Wellth (M&A Financing Platform)
- **Company**: Village Wellth — technology-first M&A financing platform (Calgary, AB; ~4 employees)
- **Problem**: Four overlapping pricing tiers were causing customer confusion and decision paralysis, with churn attributable to plan indecision rather than product dissatisfaction.
- Opportunity maps surfaced plan-confusion patterns; STP and segmentation informed tier consolidation validated with focus groups and tree tests before launch.
- Achieved a 3x increase in take rate and materially reduced churn from plan confusion.

#### Marketing Science & MMM (E-commerce)
- Replaced legacy last-click attribution with a Bayesian Media Mix Model (MMM) in R, merging 134,900 records across 6 spend channels with GA4 and HubSpot data; applied adstock and Hill-function saturation logic with ridge regression.
- Achieved projected 18% reduction in CAC and leveraged segmentation for 24% increase in ARPU.

#### B2B Series-A SaaS (Insurance and Finance)
- Converted legacy Excel actuarial and waterfall models into scalable APIs. Delivered a $140k pilot automating legacy calculation processes for a private-equity firm.

#### Marketplace in Building & Construction Materials
- Architected TMS/WMS integration hooks and monetization strategy for a construction materials marketplace.

---

### ROLE 3: Product Manager, Health-Tech (User Research & GTM)
- **Company**: Various health-tech, digital health, and medical device startups
- **Dates**: 2022 – 2025
- **Location**: Remote / Calgary, AB
- **Tags**: `[Healthcare]`, `[GTM]`, `[Pricing]`, `[User Research]`, `[0-to-1]`
- **Scope**: 0-to-1 product management across health-tech, medical device, and digital health startups — spanning user research, clinical prototyping, GTM strategy, and pricing.

#### Patient Healthcare Journey SaaS (2024)
- Architected clinical intake patient journeys and built clickable prototypes for knowledge-based patient intake with targeted interventions for specialized clinics.
- Won the 2024 TechStars Calgary Hackathon; spearheaded user research and MVP prototyping for a telehealth network targeting 100k-user national intake.

#### Eye-Gaze Tracking Wearable (2025)
- Directed product requirements for millisecond-precision eye tracking applied to clinical research and kinesiology.

#### Telehealth Delivery Network (2023)
- Orchestrated comprehensive go-to-market and regulatory strategy for a developing-country telehealth network, securing a national government grant.

#### Medical Device GTM & Pricing (2023)
- Designed value-based pricing strategy for a seed-funded respiratory therapeutics device.
- Led product scoping, clinical proof metrics, and pricing strategy for a Brain-Computer Interface dementia-detection wearable.

---

### ROLE 4: Product Manager (AI Vision)
- **Company**: Netsweeper — web filtering & content intelligence platform (Waterloo, ON; ~40 employees)
- **Title**: Product Manager
- **Dates**: Jul 2022 - 2023 (Full-Time)
- **Location**: Remote / Waterloo, ON
- **Tags**: `[AI/CV]`, `[Trust/Safety]`, `[Data Quality]`, `[User Research]`
- **Research & roadmap tooling (confirmed)**: Aha!, focus groups, tree testing
- **Problem**: A student-monitoring and content-compliance AI product was behind schedule, running on an outsourced engineering team, with a district client losing trust in the system due to high false-alert rates — staff were ignoring alerts because they couldn't trust the signal.
- Managed roadmap and backlog in Aha!; aligned district stakeholders and internal teams on prioritization after focus groups and tree tests on alert workflows.
- Took ownership of the backlog and engineering relationship, reframing the product's core metric from "detection accuracy" to "operational trust" — a shift that unlocked the right prioritization framework.
- Prioritized signal quality over feature expansion; redesigned alert workflows to aggressively prune false-positive vectors through iterative model refinement and structured QA cycles with the outsourced team.
- Reduced false alerts by 85% across the 35-school district deployment, restoring staff trust and stabilizing the client relationship.
- Redesigned workflow edge-case handling that had previously caused the highest-volume incorrect alerts.

---

### ROLE 5: Product Manager & Chief of Staff
- **Company**: BVXpress — deal structuring & valuation SaaS for M&A advisors, business brokers, and appraisers (Chicago, IL; ~5 employees)
- **Title**: Product Manager & Chief of Staff
- **Dates**: Sep 2012 - Dec 2021 (9-year tenure)
- **Location**: Chicago, IL
- **Tags**: `[Growth]`, `[0-to-1]`, `[Pricing]`, `[M&A]`, `[User Research]`
- **Research & product tooling (confirmed)**: Aha!, Pendo, focus groups, tree testing, opportunity maps
- **Problem**: The firm had no product function, no digital tooling, and all advisory work was manual and relationship-dependent — no repeatable growth engine.
- Built the Product Business Unit from scratch; launched 5 products from whiteboard to market and operated a total of 8 products serving 1,400+ users across research, workflow, and growth operations.
- Roadmap and releases tracked in Aha!; Pendo adoption signals and opportunity maps informed which workflows to fix first; focus groups and tree tests validated pricing, onboarding, and workflow changes across the 8-product suite.
- Automated pricing evolution based on customer usage-pattern analysis, increasing ARPU from $450 to $600 over 2 years (3x take rate improvement).
- Built personalized onboarding, lifecycle messaging, and lead-routing workflows, driving a 14% retention increase over 2 years.
- Re-architected landing page and product messaging funnels, achieving a 7% conversion lift.
- GTM automation: built MQL→SQL pipeline velocity and CAC payback tracking from scratch.

---

### Additional Projects & Prototypes

#### Project Epsilon (Energy Modeling Platform)
- **Live platform**: epsilon.xblavania.workers.dev
- Built scenario-first modeling engine for microgrid, data center, and RTO-style energy planning using PyPSA linear programs.
- Designed a typed Scenario contract driving all engines (sizing, stress-testing, finance, network) from a single source of truth, eliminating copy-paste model drift.

#### ChurnOS (Retention & Attribution Platform)
- **Live platform**: churnos.xblavania.workers.dev
- Built causal analytics platform using Bayesian inference for retention forecasting, churn analysis, and CRO; includes P&L outcome simulation for subscription and marketplace operators.

---

## Education
- **MBA**, University of Calgary (2025) — Energy Economics and Product Leadership
- **Bachelor of Science, Business & Finance**, Illinois Tech (2012) — Chicago, IL
- **Certifications**: CSM (Certified Scrum Master) & CSPO (Certified Scrum Product Owner), Scrum Alliance (2022)

---

## Resume generation notes
- **Voice (research & analytics)**: Never write "used Hotjar/Pendo/Heap" as the outcome. Write the **decision or change**: tier consolidation, funnel fix, alert workflow redesign, scope cut, checkout step removed. Tools may appear only as evidence for that decision, inside the relevant ROLE block.
- **UX / research-heavy JDs**: Prioritize ROLE 1, ROLE 5, ROLE 4, ROLE 2 fractional (Village Wellth, Liohan line, etc.), ROLE 3.
- **Growth / analytics JDs**: Prioritize ROLE 2 (MMM, R, SQL, attribution, STP), Segment/Moovez funnel work, ChurnOS, BVXpress GTM metrics.
- **Marketplace / ops JDs**: Prioritize ROLE 1, construction marketplace (ROLE 2), Moovez/Quotely outcomes.
- **Only cite tools listed under a ROLE block or in Skills above** — do not invent tools per engagement.

---

## Positioning Narrative
Chief of Staff turned Product Leader. A decade inside M&A deal-making taught that every business problem is a pricing problem, an operations problem, or a growth problem — usually all three at once.

Brings the ability to translate high-level technical paradigms (Operations Research, Computer Vision, Bayesian Modeling, PyPSA) into commercial levers (Pricing Architecture, MMM, ARPU optimization) that unlock scalable revenue. User research and analytics are not checkbox skills — they change what gets built: opportunity maps and discovery work precede roadmap bets; session replay and instrumentation inform funnel and pricing decisions; focus groups and tree tests gate launches. Specialized in taking chaotic 0-to-1 operational processes and replacing them with high-accuracy, automated systems that increase throughput without adding head count proportionally. Proven track record of scaling LogTech, FinTech, and Applied AI products from blank whiteboard to production.
