# PMOS in a feature factory

How this toolkit helps when the org optimizes for **output** (tickets closed, features shipped, roadmap theater) over **outcomes** (jobs done, metrics moved, decisions owned).

PMOS does not fix a broken operating model. It gives **you** a portable system so you can ship without becoming the slop, and leave with evidence.

## What a feature factory looks like

- Roadmap is a commitment list, not a strategy
- "Why" is answered with "the CEO asked" or "competitor has it"
- PRDs are Jira tickets with extra steps
- No time for discovery; research is "check analytics once"
- Success = shipped on date; impact reviewed never
- PMs are project coordinators with a nicer title
- Decisions happen in Slack and evaporate

Sound familiar? PMOS is built for exactly this — Jarrell's thread assumes situational tweaks per company.

## How PMOS still helps

### 1. Personal operating system (the org doesn't need one)

Everything lives in **your** repo: `context/`, `decisions/`, `products/`. You don't need permission to run BMC in week one or log DACI in a markdown file. The factory's chaos doesn't block your clarity.

### 2. Minimum viable rigor (minutes, not meetings)

| Situation | PMOS move | Time |
|-----------|-----------|------|
| Random feature lands on you | ICE score it; write 3-line problem in PRD | 15 min |
| Stakeholder wants "yes" today | DACI: who is Approver? get it on paper | 10 min |
| Build starts Monday, no spec | Lightweight PRD — problem, scope, metric | 30 min |
| "Why are we building this?" | One mock press release headline test | 20 min |
| Quarterly date is immovable | Planning timeline — milestones only | 20 min |

You look aligned and fast. You're also not lying to yourself.

### 3. Decision log = career insurance

`decisions/` captures what was decided, who approved, and what evidence existed. When the feature flops or gets blamed on product:

- You have a timestamped record
- Interview stories write themselves (STAR from real decisions)
- You can show you raised risks without blocking the business

Feature factories hate process. They respect **one-page receipts**.

### 4. KPI tree when leadership only counts features

If the org won't define success, **you** define it in `products/<name>/metrics.md` + `06-kpi-tree.md`:

- Pick one north-star branch leadership vaguely cares about (retention, revenue, activation)
- Link your feature to a leaf metric before build
- After ship: did the branch move? Document yes/no in metrics file

This is how you stop being "the person who ships things" and become "the person who ships things **and knows if they worked**."

See [Thiago Brum — Product Metrics 101](../references.md) — written partly for PMs trapped in feature-factory mode.

### 5. JTBD and story map as stealth discovery

No research budget? Three customer calls + `08-jtbd.md`. Support ticket themes count.

Story map (`05-story-map.md`) exposes when the factory is shipping **horizontal slices of nothing** — features that don't complete a user journey. One diagram in a review: "We're shipping stage 2 tasks without stage 1 working." Hard to argue with the backbone.

### 6. ICE stops infinite prioritization theater

Feature factories love debate because debate feels like work. ICE (`09-ice-prioritization.md`) forces a score and a top 3. You move. If they override your ranking, log it in `decisions/` and ship their pick — with the score visible.

### 7. Roadmap as translation layer

You may not control the roadmap. You **can** maintain `products/<name>/roadmap.md` as your honest now/next/later:

- **Now:** what the factory committed to (high confidence)
- **Next:** what you'd do if outcomes mattered
- **Later:** inspiration so you don't lose the plot

Stakeholder narrative section = one paragraph you can paste into whatever deck they use. Same truth, their format.

### 8. Context files for fast re-orientation

Feature factories burn PMs out. `context/<company>/` means when you come back from vacation or land in a new squad, you don't re-learn politics from scratch. Portable if you leave.

### 9. BMC for "should I even be here?"

`01-business-model-canvas.md` answers whether the **business** makes sense — not whether your sprint board is full. Weak value prop + expensive sales motion + feature checklist roadmap = structural slop. Useful career signal, not just a workshop exercise.

## What PMOS will not do

- Change incentives that reward shipping over learning
- Replace executive sponsorship for outcome-based roadmaps
- Win political fights with better templates alone
- Turn a coordinator role into a strategy role without org buy-in

## Practical stance

| Do | Don't |
|----|-------|
| Run minimum viable artifacts on every non-trivial bet | Block shipping to enforce full PMOS ceremony |
| Log decisions and metrics for **your** record | Expect the factory to adopt your folder structure |
| Use PR/FAQ and JTBD to sanity-check bad bets | Die on every hill — pick 1–2 outcome fights per quarter |
| Export to Notion/Slides when stakeholders need visibility | Maintain two conflicting truths (personal vs public) |
| Build interview portfolio from `decisions/` + metrics | Stay two years without updating resume truth |

## Suggested weekly rhythm (30 min total)

| Day | Action |
|-----|--------|
| Monday | `workspace/weekly-plan.md` — top 3 outcomes (not tickets) |
| Per feature kickoff | PRD problem + metric row, or ICE if backlog item |
| Per stakeholder conflict | DACI or decision log stub |
| Friday | One line in metrics file: what moved, what didn't |

## Related

- [First 30 days](../onboarding/first-30-days.md) — same checklist works in a factory; week 3 "small win" is critical for credibility
- [ORGANIZATION.md](../ORGANIZATION.md) — which template when you're time-boxed
- [references.md](../references.md) — metrics depth when the factory won't teach it

---

*PMOS is portable by design. The factory doesn't have to improve for your practice to.*
