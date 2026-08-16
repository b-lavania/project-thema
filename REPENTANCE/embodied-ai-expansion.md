# Embodied / Physical AI — Expansion Note

> **Purpose:** Explain why your agentic AI track record and embodied AI work (Eta Visor) belong in one story — for intros, recruiter conversations, founder outreach, and portfolio updates.
>
> **Assets:** [Eta Visor homepage](https://eta-xr.com/) · [Platform valuation & thesis](https://p-eta.netlify.app/) · Cross-links: [Positioning audit](01-positioning-audit.md) · [Career reset v2](career_direction_reset_v2_748fb06f.plan.md) · [Grizzly prep](GrizzlyHunt.md)

---

## The one-sentence expansion

**I build the layer that turns messy human intent into structured, machine-trustworthy action — in software agents today, and in physical workflows through gaze + motion interfaces.**

That is not a pivot. It is the same product problem in a new substrate.

---

## Why these two lanes are one lane

Most teams treat "agentic AI" and "physical / embodied AI" as separate markets. In practice the hard parts overlap:

| What breaks | Agentic AI (Quotely / Moovez) | Physical AI (Eta Visor) |
|-------------|-------------------------------|---------------------------|
| **Input ambiguity** | Free-text SMS, vague job descriptions | Casual glances vs deliberate gaze |
| **Intent inference** | Structured intake vs chatbot theater | Dwell / gesture / policy rules before act |
| **Confidence & trust** | Operators ignore bad quotes | Dispatchers ignore bad robot suggestions |
| **Output shape** | Job orders, WMS events, audit logs | ROS2 streams, MAVLink targets, inspection records |
| **Failure mode** | Rework for dispatchers | Rework for technicians; safety risk |
| **What you actually ship** | Not "an LLM" — a **workflow event** with target, time, confidence, context | Not "eye tracking" — an **intent event** with the same fields |

**Your rare combination:** you have shipped production systems on the software side (conversational agents, eval harnesses, OR-backed quoting) and you are building product strategy / platform framing on the physical side (Eta Visor: gaze-VIO + intent layer → multi-protocol machine output).

Hiring managers and founders in robotics, drone ops, warehouse automation, and industrial inspection care about the second column. Your Quotely proof makes the first column credible — you know what "production" means beyond a demo stack.

---

## What Eta Visor is (plain language)

**Eta Visor** is a hands-free intent layer for industrial work.

- **Problem:** Field teams still stop to scan, tap, radio, annotate, and re-enter context. Robots and drones may be autonomous, but humans still tell them what matters — usually with hands occupied.
- **Insight:** Workers already look at the bin, valve, defect, or landing zone before they act. Attention is the input.
- **Product:** A small wearable (NIR eye tracker + 6-DoF IMU + onboard edge compute) that converts gaze, motion, and context into **structured intent events** — not raw sensor dumps.
- **Outputs:** Machine-ready signals for robot tasks (ROS2), drone targets (MAVLink), inspection logs, safety / operator-state monitoring (BCI-style event streams).
- **Field fit:** Indoor, GPS-denied, dusty, dark environments — no scene cameras required for core intent capture.
- **Platform thesis:** One narrow hardware surface with broad option value — warehouse picking, pipeline inspection, drone tasking share the same intent layer ([valuation memo](https://p-eta.netlify.app/)).

**Stage:** Pre-seed · Eta XR · pilot conversations for warehouse robotics, industrial inspection, GPS-denied drone ops.

---

## Your through-line (use this in every pitch)

The move you repeat:

1. **Find the real bottleneck** — "slow quoting" was trust and speed-to-price; "bad HMI" is trapped attention, not missing screens.
2. **Reduce operational ambiguity** — structured capture beats open-ended interaction (SMS agent design; gaze dwell + confidence gating).
3. **Ship machine-trustworthy output** — events downstream systems can route, not raw model output (eval gates + job orders; ROS2 / MAVLink intent events).
4. **Measure adoption, not sophistication** — fill rate and deflection; operator re-engagement and audit completeness.

**Quotely proof (software / agentic):** CV + OR quoting (60 min → 3 min), ~50% support deflection via structured conversational intake, multi-layer eval architecture, commercialization signal from inbound operator interest.

**Eta proof (physical / embodied):** Platform positioning, workflow walkthrough (look → confirm → understand → route → act → record → improve), multi-protocol output architecture, simulation-backed telemetry, pilot GTM for three verticals.

---

## Who to pitch (embodied / physical AI lane)

**Primary buyers / employers**

| Segment | Why you map | Example targets |
|---------|-------------|-----------------|
| **Warehouse robotics + AMR/AGV** | Pick confirmation without scanners; WMS ↔ fleet handoff | Locus, 6 River, Vecna, Dexterity, Covariant-adjacent startups |
| **Drone inspection / remote ops** | GPS-denied target tasking; operator-in-the-loop | Skydio, Percepto, Flyability ecosystem, defense-adjacent field ops |
| **Industrial inspection / QMS-adjacent** | Hands-free logging; time-stamped target events | Isolocity-style ops tooling, asset-heavy manufacturers |
| **Robotics platform / middleware** | Intent events as product API | ROS2-native startups, MAVLink flight stacks, human-in-the-loop autonomy |
| **Wearables / HMI challengers** | Gaze + motion intent vs tablet-heavy AR | Compare lane: Tobii/Pupil (gaze only), Vision Pro (display-heavy), traditional HMI |

**Roles that fit this combined story**

- Technical Product Owner / PM for agentic or embodied systems
- Founding PM at pre-seed–Series A robotics / drone / warehouse automation
- Product lead for human-machine interface or operator-in-the-loop autonomy
- Solutions / product owner for pilot deployments (2–8 week scoped engagements)

**Do not spray** generic robotics companies where your proof is slideware. Lead with **intent routing + production eval discipline + field workflow design**.

---

## How this fits the career plan (without diluting)

From [career reset v2](career_direction_reset_v2_748fb06f.plan.md):

| Motion | Relationship to embodied AI |
|--------|------------------------------|
| **Primary: salaried role** | Embodied AI companies are a **target segment**, not a separate identity. Same headline: technical product operator for agentic / operational AI. |
| **Warm lead (agentic TPO)** | Reinforce with Eta as **adjacent depth** — you understand human-in-the-loop and structured handoffs in physical ops, not just chat agents. |
| **Consulting bridge** | Optional wedge: "Agentic pilot scoping" OR "Intent-layer workflow discovery for robotics/drone pilot" — one offer, not two brands. |
| **Quotely / Moovez** | Software-side proof; time-boxed. Eta is forward-looking lane, not a second full-time job unless pulled by funding. |

**Identity rule:** One spine — *founding / technical product lead for operational AI*. Eta is **evidence of range into physical substrates**, not a competing founder story unless you choose that path explicitly.

---

## Copy-paste pitches

### 30-second verbal

> I'm a technical product operator. At Quotely I built production agentic systems for logistics — conversational intake, eval harnesses, quoting automation — and proved operators adopt systems that reduce ambiguity, not systems that sound smart. I'm also working on Eta Visor, a hands-free intent layer that turns worker attention into robot-ready events for warehouse, inspection, and drone workflows. Same problem either way: turn messy human intent into structured action the machine can trust.

### LinkedIn / intro message (embodied AI recipient)

> I build the layer between human judgment and machine action. In logistics I shipped agentic intake + quoting in production (60 min → 3 min job costing, structured SMS deflection). With Eta Visor I'm extending that to physical work — gaze + motion → confidence-gated intent events for ROS2, MAVLink, and inspection logs, without scanners or tablets. If you're building operator-in-the-loop robotics or drone ops, I'd love to compare notes on where intent capture breaks in the field.

### Recruiter bridge (agentic role + embodied depth)

> My core credential is production agentic AI in operational workflows — not demos. I've scoped agents around structured handoffs, eval gates, and adoption metrics in live logistics. I'm also deep in embodied interface work (Eta Visor: wearable intent layer for industrial + drone command). That combination matters for agentic roles that touch field ops, robotics integrations, or human-in-the-loop autonomy — I understand both the LLM workflow side and the physical routing side.

### Founder ask (pilot / product conversation)

> Most tools capture data. Eta captures **intent** — what the worker meant to select, with confidence, before a robot or drone acts. I've already lived the software version of that problem at Quotely: unstructured input → structured job events → downstream automation. Happy to walk through the seven-step workflow on [eta-xr.com](https://eta-xr.com/) and where I'd pressure-test pilot scope for [their vertical].

---

## Interview answers (expect these)

| Question | Answer anchor |
|----------|---------------|
| Why physical AI now? | Not "now" — same bottleneck, new interface. Physical ops still lose to judgment latency and bad handoffs. I've been fixing that in software; Eta is the wearable expression. |
| Are you a founder or employee? | Operator at Quotely on equity (built the AI product layer). Product / platform contributor on Eta Visor at pre-seed. Job search is for a team with engineering execution I don't have today. |
| What's evidenced vs early? | Quotely: production metrics, eval architecture, live ops context. Eta: repo-backed protocol outputs, simulation, platform thesis — pilot-stage, not scaled deployment. Lead with Quotely for hiring; lead with Eta for robotics/drone conversations. |
| Why not just robotics PM? | I'm not a generic robotics PM. I'm strongest where **intent routing, trust, and workflow adoption** are the product — that's the overlap between agentic software and embodied interfaces. |
| Conflict with logistics lane? | Adjacent, not scattered. Logistics, warehouse, field inspection, drone ops share workflow complexity and operator trust problems. Domain specificity is the asset. |

---

## Guardrails (do not overclaim)

- **Quotely:** Operator who built AI systems in production; not founder; blocked by absentee CTO — resource constraint narrative.
- **Eta:** Pre-seed platform asset; pilot-stage; valuation memo overlays are illustrative, not closed deals.
- **Do not claim:** Mass manufacturing, deployed fleet scale, FDA/regulatory clearance, or revenue from Eta unless true.
- **Do not conflate:** Raw gaze data vs structured intent events; chatbot UI vs structured agent handoffs.
- **Portfolio:** Add Eta as a case study / deep-dive link when ready; do not rewrite concept1 into a robotics-only identity.

---

## Next artifacts (when you want to go further)

1. **PORTFOLIO** — `embodied-ai.html` or Eta section on CONCEPT3 index (workflow diagram + protocol outputs + link to eta-xr.com).
2. **master_context.md** — One ROLE block for Eta Visor (relationship, scope, evidenced outputs only).
3. **company-targets.md** — Second batch: embodied / robotics / drone ops companies (15–20 names).
4. **concept2.html** — Optional "Physical intent layer" card linking agent evals ↔ machine intent events (secondary asset only).

---

## Quick reference

| Item | Answer |
|------|--------|
| **Expansion sentence** | Same problem — messy human intent → structured machine action — in software agents and physical interfaces. |
| **Eta Visor** | Hands-free intent layer: gaze + IMU → confidence-gated events → ROS2 / MAVLink / logs. |
| **Software proof** | Quotely: agents, evals, 60→3 min quoting, deflection, fill rate. |
| **Pitch to** | Warehouse robotics, drone ops, industrial inspection, HMI / autonomy middleware. |
| **Role fit** | TPO / PM for agentic or embodied systems; founding PM at pre-seed–Series A ops-robotics. |
| **Identity** | One spine: technical product operator for operational AI. Eta extends, does not replace. |
