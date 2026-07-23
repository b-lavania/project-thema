

Great question. The scoring methodology in your roadmap (L1 task, L2 response shape, L3 rubric+grader, L4 harness with SD/kappa/over-award) is broadly applicable anywhere you need reliable, repeatable judgments from LLMs. Here are high‑leverage, general-purpose use cases, each with how to score them observably.

# Content generation and editing
- **Resume/cover letter rater**
  - Criteria: length caps; JD term coverage; 2+ concrete outcomes; avoids banned fog words; role selection plausibility.
  - Harness: edit rate after user review; ATS coverage; per-criterion kappa on a gold set.
- **Meeting summary → action log**
  - Criteria: includes decisions, owners, deadlines; ≤ N bullets; quotes 2 exact phrases as evidence.
  - Harness: SD across responses; over-award on verbose summaries; kappa vs human labels.
- **Spec/PRD critique**
  - Criteria: flags 3 risks; names metrics; proposes 2 tradeoffs; cites exact section lines.
  - Harness: disagreement taxonomy on each criterion.

## Worked example: Meeting summary → action log
- L1 Task: From transcript, produce (a) 4–7 bullets ≤ 12 words; (b) 3–5 actions with owner and due date; (c) one decision or “none” (8 min).
- L2 Response: `summary[]: string<=12w`; `actions[]: {action, owner(@name), due(YYYY-MM-DD)}`; `decision: {present: bool, text<=15w}`
- L3 Rubric (100): C1 Concision –10; C2 Decision captured –20; C3 Owners+due –20; C4 Action quality –20; C5 Evidence quotes (2) –10; C6 No hallucinations –10; C7 JSON/schema –10.
- L4 Harness: κ on C2–C4; SD on total; over‑award test with long owner‑less answers; gold n≈20; target κ≥0.75.

# Extraction and structuring
- **Invoice/receipt field extraction**
  - Criteria: exact-match vendor/date/total; checksum validation; currency normalization.
  - Harness: field-level precision/recall; per-field kappa; error taxonomy (parse vs OCR).
- **JD → structured fields**
  - Criteria: duties≥5, tools≥5; title seniority detected; location class (Canada/NA/global).
  - Harness: accuracy vs human gold; SD on “fit-lite” score; drift checks over time.
- **Entity/relationship extraction from text**
  - Criteria: unique entities list; relationship triples; source sentence quoted.
  - Harness: micro/macro F1; kappa on “is-relationship-valid”.

# Reasoning and planning
- **A/B test plan grader**
  - Criteria: hypothesis format; primary metric defined; power calc or sample size rule; stopping rule present.
  - Harness: per-criterion kappa; SD target; over-award on long rationale.
- **Root-cause analysis from logs**
  - Criteria: cites ≥2 metrics; proposes 1 testable hypothesis; names 1 confound; picks one action.
  - Harness: banded score agreement (low/med/high) vs SME.

# Code and data tasks
- **NL → SQL grader**
  - Criteria: compiles; returns expected rows on hidden tests; uses indexed columns; no SELECT *.
  - Harness: exact match on test suite; penalty for runtime > threshold; binary kappa on pass/fail.
- **Refactor/readability judge**
  - Criteria: tests pass; cyclomatic complexity reduced; function length ≤ N; docstring includes params/returns.
  - Harness: objective metrics (tests/complexity); human vs AI agreement on docstring sufficiency.

## Worked example: NL → SQL
- L1 Task: Given schema + NL query, write SQL; avoid SELECT *; ensure indexed predicate.
- L2 Response: `sql: string` (optional rationale ≤50 words; not graded).
- L3 Rubric (100): Hidden tests pass –60; Projected columns only –10; Indexed predicate –10; No Cartesian joins –10; Runtime under threshold –10.
- L4 Harness: Test suite + runtime budget; error taxonomy (syntax/semantics/perf); κ on pass/fail for borderline items.

# Safety, policy, and compliance
- **Redaction/PII scrubber**
  - Criteria: masks emails/phones/SSNs; preserves non-PII; no over-redaction of domain terms.
  - Harness: field-level precision/recall; policy kappa; over-block rate.
- **Policy-compliant support reply**
  - Criteria: cites KB link; includes next step; tone adherence; no promises outside policy.
  - Harness: per-criterion kappa; over-award on politeness-only.

# RAG and search
- **RAG answer judge (grounded QA)**
  - Criteria: includes citation span; all claims supported; no extraneous facts; ≤ N words.
  - Harness: groundedness accuracy; claim-level kappa; latency vs quality curve.
- **Retrieval/ranking eval**
  - Criteria: top-k contains gold doc; MRR/NDCG targets; diversity constraint met.
  - Harness: offline IR metrics; failure buckets (lexical vs semantic).

## Worked example: RAG grounded QA
- L1 Task: Answer only from provided docs. Include citations `{doc_id,start,end,quote}`. ≤120 words.
- L2 Response: `answer<=120w`; `citations[]` of exact spans.
- L3 Rubric (100): All claims supported –35; Span correctness –25; No extraneous facts –20; Brevity/structure –10; Direct answer –10.
- L4 Harness: Claim‑level accuracy; κ on “unsupported claim present?”; latency vs quality; drift alerts when corpus changes.

# Agents and tool-use
- **Tool-using agent adherence**
  - Criteria: follows step order; stops after success; includes tool output quotes; handles API error.
  - Harness: task success rate; step adherence kappa; injection-resistance pass rate.
- **Browsing task eval**
  - Criteria: visits source domain; captures required fields; cites URL; avoids prohibited domains.
  - Harness: success@k; policy violations; SD on total score.

# Product and go-to-market
- **Positioning/copy rewrites**
  - Criteria: ≤ 65-char headline; includes ICP; 1 value prop; avoids banned buzzwords.
  - Harness: compliance rate; inter-rater agreement on ICP correctness.
- **Email triage/classification**
  - Criteria: folder assignment; priority band; SLA suggestion.
  - Harness: confusion matrix; kappa on banded priority.

# How to apply the L1–L4 pattern quickly
- **L1 Task**: One coherent scenario + explicit deliverables + constraints (time, word caps, “choose one”).
- **L2 Response shape**: Prefer structured fields/templates/checklists; keep free text bounded.
- **L3 Rubric + grader**: 8–12 criteria, points sum to 100; each criterion has an observable definition and partial credit; anti-gaming (word caps, evidence quotes, neg/pos exemplars).
- **L4 Harness**: Track SD (discrimination), per-criterion kappa, over-award on verbosity, disagreement taxonomy, and a small human-labeled gold set for calibration.

# Why measure (principles)
- Discrimination (SD): spread scores so you can rank outputs. If everyone scores 67–71, you can’t choose.
- Reliability (κ): judge agrees with humans beyond chance. Target ≥0.75 on key criteria.
- Validity: score observable behavior, not prose length/tone.
- Anti‑gaming: word caps, required slots, evidence quotes, negative exemplars.

# Core metrics (quick reference)
- SD (standard deviation): aim 12–15 on 100‑pt scales post‑redesign.
- Cohen’s κ: `(Po−Pe)/(1−Pe)`. Track Gwet’s AC1 if prevalence is skewed.
- Precision/Recall/F1 (extraction): Micro overall; Macro to surface rare fields.
- MAE / Pearson r: for numeric totals/continuous grading.
- Over‑award rate: verbose‑but‑unsupported passes; target <15%.
- Time↔score correlation (r): ensure “slow ≠ smart”.

# Gold set creation (60‑minute recipe)
1. Sample 40–60 diverse items (difficulty/length/domain stratified).
2. Draft a 1‑page rubric with observable anchors + partial credit.
3. Calibrate 10 items together → refine anchors.
4. Double‑label 20–30 items; compute κ/criterion; note disagreements.
5. Save JSONL with evidence quotes for each label (teaches the grader).

Example gold JSONL line
```
{
  "id": "ms_0031",
  "input": {"meeting_notes": "..."},
  "response": {"summary": "...", "actions": ["..."]},
  "human_scores": {"C1": 2, "C2": 1, "C3": 1},
  "human_total": 74,
  "evidence": {"C1": "Quoted: 'Decide ...'", "C2": "Owner: @ana by Fri"},
  "rater": "bl",
  "version": "meeting_actionlog_v1"
}
```

# Instrumentation schema (log each run)
```
{
  "harness": "<name>@<version>",
  "bundle_hash": "<prompt+rubric+grader hash>",
  "input_id": "<gold or live id>",
  "model": "<provider/model>",
  "latency_ms": 0,
  "tokens": {"prompt": 0, "completion": 0},
  "response": {"...": "..."},
  "ai_scores": {"C1": 2, "C2": 1},
  "ai_total": 78,
  "ai_evidence": {"C1": "Quoted span ..."},
  "human_scores": {"C1": 2, "C2": 2},
  "human_total": 85,
  "run_at": "<ISO8601>"
}
```

# Calibration loop
1. Rubric v1: 8–12 observable criteria (sum=100).
2. Label gold (n=50); compute κ/criterion; rewrite weak anchors.
3. Grader context: rubric JSON/table + 2–3 scored exemplars (high/low) + “quote evidence”.
4. Tune grader; holdout n=20 → κ≥0.70; revise to κ≥0.75.
5. Freeze bundle hash; weekly drift check (κ/SD on n≥30).

# Anti‑gaming controls
- Word caps on free text (e.g., mission ≤120 words).
- Required slots/checklists; grade presence explicitly.
- Evidence quoting before awarding each point.
- Negative exemplar (long/fluffy) that scores 0.
- Forced choice: “Choose exactly one option (A/B/C)”.

# Acceptance thresholds (rules of thumb)
- κ≥0.75 on ≥70% of criteria; none <0.60 without mitigation.
- SD≥12 on 100‑pt scales (useful rank‑ordering).
- Extraction: micro‑F1≥0.92 on critical fields; over‑award <15%.

# Fast starters tailored to your stack
- **JD→Fit Lite auto-rater**: Turn your heuristic fit into a rubric with explanation + coverage meter; calibrate on 50 JDs you’ve hand-labeled.
- **Resume quality gates v2**: Redesign `resume_quality_review` to emit per-criterion JSON and run a small kappa study on 20 outputs.
- **RAG answer judge**: For any docs you use, add a grader that requires citations and measures groundedness vs human labels.

# Reporting pattern (what to show users)
- Per‑criterion scores with 1‑line evidence quotes.
- Total score + band (0–59 Weak, 60–79 Adequate, 80–100 Strong).
- Short “why this score” explanation (avoid generic prose).
- Version tag (harness@version, bundle hash).

# Common failure modes → fixes
- Length bias → word caps + evidence quotes + negative exemplar.
- Prevalence skew (κ drop) → balance labels; show Gwet’s AC1 with κ.
- Rubric drift → freeze version; log bundle hash; weekly diffs.
- Overfitting gold → holdout 20%; rotate exemplars; refresh quarterly.
- Domain drift → disagreement taxonomy; retrain anchors.

# Quick‑start grader scaffold
```
SYSTEM: Strict rubric grader. Do not award points for length/tone. Quote exact evidence before awarding each point.

RUBRIC (JSON or table): [C1..Cn with observable anchors and points]

CALIBRATION EXAMPLE — HIGH: <response> + per‑criterion scores
CALIBRATION EXAMPLE — LOW: <response> + per‑criterion scores

USER:
Response to grade:
{{response}}

OUTPUT (JSON): {"criterion_scores": {"C1": 2, ...}, "total": 84, "evidence": {"C1": "Quoted: ..."}}
```

# Checklist (print and keep at desk)
- [ ] L1: One coherent scenario + constraints
- [ ] L2: Response shape is gradable (templates/fields)
- [ ] L3: 8–12 observable criteria, sum=100, anti‑gaming in prompt
- [ ] L4: SD, κ, over‑award, disagreement taxonomy wired
- [ ] Gold: n≥50; double‑label 20%; κ≥0.75 on key criteria
- [ ] Bundle hash logged; weekly drift check

# Suggested practice plan (1 week each)
- Week 1: Meeting summary → action log harness
- Week 2: JD structuring accuracy harness
- Week 3: RAG grounded QA harness
- Week 4: A/B test plan grader

If you pick 2–3 you want to implement first, I can help you write the L1 task, L2 response schema, L3 rubric+grader prompt, and an L4 mini-harness with targets (SD, kappa) and a 20-item gold set.