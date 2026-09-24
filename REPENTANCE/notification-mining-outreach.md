# Notification Mining Outreach — Ops-AI Target Lane

Upgrade to the static outreach motion in [`company-targets.md`](company-targets.md) and [`execution-scoreboard.md`](execution-scoreboard.md). Same targets, same templates skeleton — but every message is triggered by a fresh public signal from the target company, sent while the signal is still warm.

**Core idea:** response rate on founder outreach depends mostly on *relevance at moment of contact*. A static hypothesis is always somewhat relevant. A message sent 48 hours after the founder announced a raise, shipped a feature, or posted about the exact bottleneck is maximally relevant — because the problem is already top-of-mind for *them*.

---

## Signal taxonomy — what counts as a notification

Four classes, ranked by outreach value:

| Class | Signals | Why it matters | Where found |
|---|---|---|---|
| 💰 **Money events** | New raise (Seed→A→B), bridge round, notable lead investor | New capital = hiring mandate + budget. Founders are in announce-mode and most responsive in the 72h after announcing. | TechCrunch, Crunchbase, press page, founder LinkedIn |
| 🧑‍💼 **Team events** | PM / Founding PM / AI-eng job postings, new Head of Product hire, headcount jump 10→20 | A posted PM role is an explicit buy signal. A new product leader is a peer-level conversation. | Careers page, LinkedIn Jobs, LinkedIn people changes |
| 🚀 **Product events** | Changelog entries, new feature pages, model/agent launches, app updates, Product Hunt | Direct evidence of roadmap direction — lets you attach your hypothesis to something they *just* built or missed. | Site `/changelog`, `/blog`, app stores, PH |
| 🎙️ **Voice events** | Founder LinkedIn posts, podcast appearances, conference talks | Reveals what the founder thinks the bottleneck IS — lets you agree, sharpen, or respectfully push using their own framing. | LinkedIn, podcast apps, conference agendas |

**Rule:** money/team events *open windows*. Product/voice events give you the *hook language*. Best messages combine one window-opener + one hook.

---

## Triage — signal → action mapping

| Priority | Trigger | Action |
|---|---|---|
| 🔥 **Hot** | Round announced in-lane · PM role posted at target · founder post naming your exact bottleneck · launch in your sub-vertical | Personalize fully, send within **48h**. Bump ahead of scheduled batch. Cap: ≤10/day (LinkedIn limits + quality floor). |
| 🌡️ **Warm** | Changelog item adjacent to hypothesis · new product-leadership hire · podcast/talk appearance | Queue into next Wed–Thu batch with signal-specific opener. |
| 🧊 **Cold** | Generic marketing content · minor UI tweaks · unrelated vertical news | Log only. Use static hypothesis template as fallback. |

Never manufacture familiarity. If the only signal is weak, the static template from the scoreboard is the honest move.

---

## Collection stack — three tiers, start at Tier 1 this week

### Tier 1 — Manual sweep, $0 (START HERE)

- **Google Alerts:** one alert per company — `"<company>" (funding OR raises OR launches OR Series)` — weekly digest email. Set once for all 40+ in [`company-targets.md`](company-targets.md), runs forever.
- **LinkedIn:** follow every Batch-1 founder; bell-icon post notifications for those 15 only. Company-page follows for the rest.
- **Monday sweep (30 min):** for each Batch-1 company, check site `/blog` or `/changelog`, recent LinkedIn posts, and LinkedIn Jobs for PM/product roles.

Cost: ~45 min/week total. Captures ~80% of the value.

### Tier 2 — Semi-automated (week 2+, only if Tier 1 held two straight weeks)

- **RSS aggregation:** pipe each company's blog/changelog RSS into one Feedly folder → single daily digest.
- **HUNT-AGENT extension:** the scraper package already has SerpAPI search ([`HUNT-AGENT/`](../HUNT-AGENT/)). Add a signal-scan mode: per target company, query `site:<domain> (changelog OR blog OR "now shipping")` plus `"<company>" funding announcement`, dump results as leads. Run weekly, triage during Monday sweep.

### Tier 3 — Full automation (ONLY after ~50 signal-triggered sends prove the lift)

- Cron'd careers-page scraping with week-over-week diffing (new PM title = team event).
- LLM classification pass: score each collected item hot/warm/cold against the company's `hypothesis:` field in `CRM/data/companies.yaml`; write flagged activities into `tempus.db`.

**Operating-system guardrail** (see [`02-operating-system.md`](02-operating-system.md)): jumping to Tier 3 before earning it is the insight-high escape hatch — building the machine instead of doing the reps. Tier 1 for two full weeks minimum. The sweep *is* the boring rep.

---

## Message conversion — signal → outreach

Formula: **[signal ack, 1 line] → [reframe toward their direction] → [1 Quotely proof] → [specific ask]**

### Product event (changelog/launch)

> Saw [Company] shipped [feature] last week — congrats. My read: [feature] attacks [surface problem], but the bottleneck underneath is usually [hypothesis from target list]. I built the CV+OR version of this at Quotely — 60min→3min job costing. Worth 15 minutes?

### Money event (raise)

> Congrats on the [round] — [lead investor] backing logistics AI says the thesis is landing. As you scale past [stage], [bottleneck hypothesis] is usually the first thing that breaks. I shipped production CV+OR quoting at Quotely (60min→3min, ~93% fill). Open to comparing notes?

### Team event (PM role posted) — strongest signal

> Noticed you're hiring a [role]. Before you settle for a generalist PM: I've already shipped [the exact system the JD describes] in live last-mile ops at Quotely — 60min→3min costing, ~93% fill. If that role owns quoting/dispatch outcomes, I'm worth a call even if it closes internally.

### Voice event (founder post/podcast)

> [Founder] — your point on [topic] matches what I hit building Quotely's AI layer: [one-line agreement + addition]. In my experience [voice/intake/pricing AI] breaks on [structured handoff / exception routing / trust], not demos. Would value pushing on this with you.

**Hard rules (unchanged from scoreboard):** no resume in first message · one proof metric max · lead with *their* signal, not your bio · Series-A → founder, Series-B → Head of Product / VP Eng.

---

## Cadence integration — slots into the existing scoreboard week

| Day | Existing block | Notification-mining addition |
|---|---|---|
| **Mon** | Pipeline review | +30 min Signal Sweep: collect + triage past week's notifications; flag 🔥 hot |
| **Tue** | HUNT ATS scrape | Add any newly posted PM roles at targets to `company-targets.md` |
| **Wed–Thu** | 5 touches/day | 🔥 Hot-signal sends FIRST (inside 48h window), then standard batch |
| **Fri** | Artifact + review | Log replies by signal class; update status column in targets |

---

## Metrics & feedback loop

Tag every send in CRM with:

- `signal_class`: `money` | `team` | `product` | `voice` | `static_fallback`
- `signal_age_days`: days between signal event and send

After **~50 signal-triggered sends (~2–3 weeks)**, compare reply rates by class:

- Signal-triggered reply rate **≥1.5×** static rate → keep going, consider Tier 2.
- **<1.5×** → simplify: keep Google Alerts + Monday sweep, revert to static template. Kill the machinery, keep the habit.

Sanity math: 25 touches/week baseline; expect roughly a third of tracked companies to produce ≥1 warm-or-hot signal per month → 5–8 signal-triggered sends displacing static ones weekly once warm. A 2–3× reply lift on timely founder outreach is the realistic target band.

---

## First session checklist (~60 min, do today)

1. ☐ Google Alerts for every company in `company-targets.md` (~25 min)
2. ☐ Follow + bell-icon all 15 Batch-1 founders on LinkedIn (~15 min)
3. ☐ Bookmark `/blog`, `/changelog`, `/careers` for the Batch-1 15 (~10 min)
4. ☐ Add `signal_class` + `signal_age_days` tagging convention to CRM outreach logging (~5 min)
5. ☐ Run first sweep; send first 2 signal-based messages Wednesday

---

*Cross-links: [Company targets](company-targets.md) · [90-day scoreboard](execution-scoreboard.md) · [Grizzly Hunt](GrizzlyHunt.md) · [Operating system](02-operating-system.md)*
