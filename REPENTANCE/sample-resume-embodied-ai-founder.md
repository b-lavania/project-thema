# Bharat "Bob" Lavania

**Calgary, AB & San Francisco, CA (Remote)** · xblavania@gmail.com · linkedin.com/in/blavania · github.com/blavania

**Technical Product Lead — Agentic AI, Eval Harnesses, and Physical Intent Systems**

Portfolio: [Case studies](https://xblavania.netlify.app/) · [Quotely evals deep-dive](https://xblavania.netlify.app/quotely-evals.html) · [Agent evals deep-dive](https://xblavania.netlify.app/sms-agent-evals.html) · [Eta Visor](https://eta-xr.com/) · [Platform thesis](https://p-eta.netlify.app/)

---

## Summary

Product operator who ships the layer between human judgment and machine action — not demos, production systems with eval gates and adoption metrics.

At **Quotely** (logistics SaaS), built the full agentic stack in live ops: conversational intake with structured handoffs, four-layer eval harness for vision-to-quote, hybrid RAG with playbook short-circuits, and a quote-accuracy ops loop (MAE, outcome capture, retrain export). **~50% support deflection**, job costing **60 min → 3 min**, **~93% marketplace fill rate**.

With **Eta Visor** (Eta XR, pre-seed), extending the same problem to physical work: gaze + motion → confidence-gated **intent events** for ROS2, MAVLink, and inspection logs — hands-free HMI for warehouse, inspection, and GPS-denied drone workflows.

**The through-line:** unstructured human input → structured, machine-trustworthy events → downstream automation. Same architecture whether the substrate is SMS or a wearable.

---

## Selected Work

### Moovez / Quotely — Founding Product Manager (Operator, Equity)
**Last-mile logistics marketplace + commercialized AI SaaS** · Jan 2024 – Present · Remote / Calgary

Early product hire (employee #6). Built and operate the marketplace ops platform (quote-to-dispatch) and the AI intelligence layer sold as **Quotely**. Not the founder — owned product, user research, conversion, eval architecture, and commercialization strategy while reporting to CEO.

**Agentic systems (production)**

- Deployed SMS/voice agent for intake, confirmations, and reschedules with **retrieval-backed replies and structured escalation** — not freeform chat. V1 ship gates: retrieval hit@4, HITL recall/precision, intake-completion floors measured **before** debating reply fluency.
- Achieved **~50% support ticket deflection** on routine flows; preserved dispatcher capacity for exceptions via hard handoffs to order state.
- Built customer order-status and ops workflows so "where's my crew?" calls drop before the agent layer.

**Eval harness & harness engineering**

- Designed **four-layer offline eval** for photo-to-quote pipeline so releases gate by subsystem, not end-to-end guesswork:
  1. Vision detection consistency / accuracy
  2. Structured catalog match rate + unknown-fallback tracking
  3. Logistics golden-file snapshot tests (frozen inputs)
  4. End-to-end minutes MAE and ±15% hit rate vs job actuals
- Built **multi-model testbench** (Gemini Flash, GPT-4.1) scoring vision path on accuracy, latency, and cost — failures isolate to one layer without re-running expensive VLM calls on every change.
- Specified **fixture task-success gates** and Cohen's κ calibration for conversational agent quality; documented approach in public portfolio deep-dive.

**Quote-accuracy ops (Quotely Command)**

- Internal console tracking MAE (minutes/crew), within ±15%, outcome-capture SLA (chase 7d / escalate 14d), attention queue for pending actuals, annotation export for Vision retrain.
- Closed loop: quoted job → captured actuals → annotations → retrain export — accuracy KPIs as product SLAs, not vanity model metrics.

**Institutional knowledge & agent packs (Quotely-Qortex)**

- Hybrid RAG: Markdown/YAML/ops-JSON → chunk → embed (OpenAI text-embedding-3-large) → Qdrant; dense + lexical + RRF retrieve; Gemini synthesis.
- **YAML playbooks short-circuit** high-stakes SLAs/metrics — numbers never LLM-invented; thin evidence → refuse.
- Golden eval suite as release gate; `/v1/retrieve` packs per agent (Vision, Content, Voice, Command). Custom pipeline by design (no LangChain).

**Core quoting & ops outcomes**

- CV photo intake + OR engine (3D bin packing, crew sizing, duration) cut job costing from **~60 min to ~3 min**; **~85%** of jobs finish within quoted window.
- Marketplace **~93% fill rate** vs ~70% industry; inbound operator interest drove **Quotely SaaS commercialization** (quoteperfectly.com).
- Ran controlled experiment (automated vs manual quoting) with null-hypothesis framing before full traffic cutover; instrumented with Segment.

**Deep-dives:** [Quotely eval architecture](https://xblavania.netlify.app/quotely-evals.html) · [Conversational agent evals](https://xblavania.netlify.app/sms-agent-evals.html)

---

### Eta Visor — Product & Platform Strategy
**Eta XR — hands-free intent layer for industrial work** · 2024 – Present · Pre-seed

Product and platform framing for a wearable that turns **worker attention into machine-ready action** — not raw gaze data, structured intent events with confidence, target, time, and operator context.

**Problem framed:** Field teams still stop to scan, tap, radio, and re-enter context. Robots and drones are autonomous, but humans still tell them what matters — usually with hands occupied.

**Product architecture**

- **Input:** NIR eye tracker + 6-DoF IMU + onboard edge compute — GPS-denied, indoor, no scene cameras required for core intent capture.
- **Intent layer:** Dwell / gesture / policy rules separate deliberate commands from casual glances; confidence scoring on every event.
- **Output routing:** ROS2-ready streams (robot tasks), MAVLink target requests (drone ops), inspection logs, BCI-style operator-state events.
- **Workflow:** Look → confirm → understand → route → act → record → improve — seven-step path from attention to audit trail.

**Platform thesis**

- One narrow hardware surface, three adjacency rights: warehouse picking, pipeline inspection, GPS-denied drone tasking — documented in [platform valuation memo](https://p-eta.netlify.app/) with repo-backed protocol outputs and simulation evidence.
- Competitive positioning: captures **intent**, not data — vs gaze-only research tools, display-heavy AR, and traditional HMI with no spatial audit trail.

**Pilot GTM:** Warehouse robotics, industrial inspection, confined-space / GPS-denied drone operations.

**Live:** [eta-xr.com](https://eta-xr.com/)

---

## Additional Experience (compressed)

**Netsweeper** — Product Manager · 2022–2023  
Reframed K-12 safety product from "detection accuracy" to **operational trust**; froze feature creep one quarter; **85% false-alert reduction** across 35-school deployment; contract renewed. Relevant pattern: operators ignore bad signals — same failure mode as bad quotes and bad robot suggestions.

**BVXpress / ICI** — Product Lead & Chief of Staff · 2012–2021  
Employee #3; built product function from zero; launched **5 products**, 1,400+ users; ARPU **$450→$600** from workflow-speed pivot; **14% retention lift**. Adapter-first HRIS for M&A diligence (shipped to clients, not internal-only).

**Fractional Product Lead** · 2022–2025  
Village Wellth pricing architecture (**3× take rate** via tier consolidation); Bayesian MMM for e-commerce attribution; cybersecurity marketplace discovery (MSP/MSSP channel).

---

## Skills (founder-relevant)

| Lane | Methods & systems |
|------|-------------------|
| **Agentic AI** | Structured handoffs, retrieval gates, HITL escalation, fixture task-success floors, agent retrieve packs |
| **Eval / harness** | Golden sets, multi-model scoring (accuracy/latency/cost), layered offline eval, CI release gates, Cohen's κ, hit@k |
| **RAG / knowledge** | Hybrid dense + lexical + RRF, playbook short-circuit, quarantine corpora, custom pipeline (no LangChain) |
| **Physical / embodied** | Intent event design, gaze + IMU fusion concept, ROS2 / MAVLink output routing, operator-in-the-loop workflows |
| **Ops AI** | CV pipelines, OR / bin packing, quote-accuracy loops, outcome capture SLAs, production adoption metrics |
| **Build / prototype** | FastAPI, Qdrant, OpenAI embeddings, Gemini, React/TypeScript, Cursor, Python OR/CV integration |
| **Product discipline** | Opportunity maps, tree tests, session replay, controlled experiments, STP, pricing architecture |

---

## Education & Certs

MBA, University of Calgary · Energy economics & product leadership (2022–2025, concurrent with product work)  
B.S. Business & Finance, Illinois Institute of Technology · 2012  
CSPO (Scrum Alliance, 2022) · CSM

---

## Why this profile for an embodied-AI founder

You are not hiring a generic PM or an ML researcher. You are hiring someone who has already:

1. **Shipped agentic workflows in production** with eval discipline — not slideware agents.
2. **Designed layered eval harnesses** so teams can gate releases by subsystem and measure trust, not fluency.
3. **Framed a physical intent product** (Eta) with the same mental model: ambiguous human signal → confidence-gated structured event → machine endpoint.
4. **Lived the adoption problem** — operators ignore systems that add rework; metrics are fill rate, deflection, and re-engagement, not demo scores.

**Current constraint:** Equity-only operator at Quotely; blocked on engineering execution by absentee technical leadership. Seeking a team with real build capacity and a problem worth holding for 12 months.

**Ask in a first conversation:** Where does intent capture break in your workflow — input ambiguity, confidence gating, or downstream routing? I've debugged all three in software; Eta is the physical extension.

---

*Sample resume — tailored for founders in embodied AI, robotics, drone ops, and agentic systems. Generated from master_context.md + embodied-ai-expansion.md. Not ATS-optimized; metrics-forward by design for founder screens.*
