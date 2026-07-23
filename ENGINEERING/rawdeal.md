# AI Task & Prompt Design: Cross-Platform Workflow Automation

**Design a high-fidelity AI task prompt and scoring rubric for a complex multi-tool productivity scenario** *(Not yet saved)*

---

## Instructions & Overview

You are a Senior Product Manager on the AI Task & Prompt Design team at WorkflowIQ, a B2B SaaS company that builds AI-powered evaluation and simulation platforms. Your company's clients – Fortune 500 HR departments and top-tier consulting firms – use your platform to assess PM candidates through realistic, tool-based task simulations. You have been asked to architect a new assessment module that tests a candidate's ability to design an AI-driven cross-platform automation spanning Google Calendar, Gmail, Mixpanel, and Slack.

This case study evaluates your ability to:

1. Analyze product and user data to identify the right task design
2. Write a production-quality prompt specification
3. Build a defensible scoring rubric
4. Anticipate edge cases in AI-generated evaluation workflows

### Recommended Steps

* **Step 1:** Read the full scenario, data exhibits, and stakeholder context carefully.
* **Step 2:** Work through the Situation Analysis and Key Issues sections.
* **Step 3:** Design your prompt specification and rubric architecture.
* **Step 4:** Finalize your recommendation and confidence assessment.

### Tips for Strong Responses

* Ground your answers in the specific data provided – reference metrics, user quotes, and platform statistics.
* Think like a prompt engineer **AND** a product manager: your task design must be both technically sound and user-centric.
* Strong answers will address how the rubric handles ambiguity and partial credit in open-ended responses.
* Consider how an LLM auto-grader would interpret your rubric criteria – vague language reduces grading reliability.

---

## Scoring Rubric

Scored across five dimensions: Analytical Rigor (25%), Strategic Thinking (25%), Quantitative Skills (20%), Communication Clarity (15%), and Creativity & Insight (15%). **Total: 100 points.**

### 1. Analytical Rigor (25%)

*Accurate diagnosis of root causes using specific data from exhibits; logical routing from problem symptoms to causes.*

* **Weak:** Vague or generic analysis; does not reference exhibit data; misidentifies root causes.
* **Adequate:** References some data but analysis is surface-level; identifies obvious issues without exploring interactions.
* **Strong:** Cites specific metrics (SD = 8.3, kappa = 0.58, 45% over-award rate); connects dots across data to refute vague language; explains interactions.
* **Excellent:** Synthesizes multi-exhibit data into a coherent diagnostic framework; identifies non-obvious systemic interactions (e.g., how time-on-task metrics validate or reduce over-rewarding); framework clearly underpins subsequent design choices.

### 2. Strategic Thinking (25%)

*Quality of task prompt design and rubric architecture; alignment between design choices and stated problems; feasibility of delivery plan.*

* **Weak:** Task prompt is generic or unrealistic; rubric criteria use subjective language case explicitly warned against; no delivery plan.
* **Adequate:** Task prompt includes all four tools but scenario lacks complexity; rubric has some observable anchors; delivery plan is vague.
* **Strong:** Task prompt creates compounding complexity that naturally separates candidates; rubric criteria are specific and auto-grader friendly; delivery plan sequences pipeline stages logically within 60 days.
* **Excellent:** Task prompt features a genuine analytical focus that only strong candidates will navigate successfully; rubric includes explicit anti-gaming measures (e.g., word count caps); required behavioral/structural delivery plan minimizes urgency for the identified risks; de-scoping strategy is credible.

### 3. Quantitative Skills (20%)

*Appropriate use of metrics and data; understanding of statistical concepts (kappa, standard deviation, correlation); quantitative reasoning in rubric design.*

* **Weak:** Ignores or misinterprets quantitative data; confuses correlation with causation; no numeric targets in rubric.
* **Adequate:** References key metrics correctly; understands kappa conceptually; rubric includes some numeric thresholds.
* **Strong:** Uses SD, kappa, and time-on-task data to justify specific design decisions; rubric anchors include concrete quantifiable performance indicators; proposes realistic target metrics for the new module.
* **Excellent:** Demonstrates deep understanding of how metric granularity affects score variance; proposes a reverse-reward plan with specific thresholds for success/failure and separates statistical power requirements for pilot evaluations.

### 4. Communication Clarity (15%)

*Writing quality of the task prompt template; clarity and precision of rubric language; logical structure of arguments.*

* **Weak:** Disorganized response; task prompt would confuse candidates; rubric language is ambiguous.
* **Adequate:** Responses are readable but require some parsing; task prompt is functional but not polished; rubric is understandable.
* **Strong:** Task prompt text is production-ready.
* **Excellent:** Task prompt is publication-ready with no ambiguity; rubric could be handed directly to a prompt engineer for auto-grader implementation; structures arguments to exceptionally frame the language.

### 5. Creativity & Insight (15%)

*Originality of scenario design; non-obvious insights in analysis; innovative approaches to the discrimination and kappa problems.*

* **Weak:** Scenario is trivial (schedule a meeting and send an email task); no novel insights.
* **Adequate:** Scenario has some interesting elements but follows predictable patterns; one minor insight beyond the obvious.
* **Strong:** Scenario includes a creative tension or trade-off that makes the task genuinely challenging; identifies at least one non-obvious technical item (e.g., how time-on-task data could inform automated scoring).
* **Excellent:** Scenario design is genuinely novel.

---

### Assessment Categories

`AI Task & Prompt Design` `Product Management` `Rubric Engineering` `Psychometrics & Assessment Design` `Cross-Platform Workflow Tools`

### Quick Navigation

* Section 1: Situation Analysis
* Section 2: Task Prompt Design
* Section 3: Rubric Architecture
* Section 4: Strategic Recommendation & Risk Assessment

---

**Case Study** | **Hard** | **100 Points**

## Workflow Orchestration Challenge — Task & Rubric Architecture

WorkflowIQ's Multi-Tool PM Assessment track is underperforming on two critical dimensions: score discrimination (SD of only 8.3 on a 100-point scale) and human-AI grading alignment (Kappa = 0.58 vs. target >= 0.75). Three enterprise accounts worth $1.2M in combined ARR have given a 60-day ultimatum. You have been tasked with designing the "Workflow Orchestration Challenge," a flagship 30-minute task module that tests a mid-to-senior PM candidate's ability to orchestrate a realistic workflow across Google Calendar, Gmail, Mixpanel, and Slack. Your deliverable is the task prompt specification, rubric architecture, and strategic rationale for your design choices.

> **CONTEXT:** Use the data exhibits, stakeholder priorities, and auto-grader performance metrics provided in the materials section. Your answers should reflect deep familiarity with prompt engineering best practices, psychometric principles of assessment design, and the practical realities of building AI-scorable evaluation tasks.

---

## Background Materials

WorkflowIQ was founded in 2020 and serves 87 enterprise clients. The platform's core value proposition is "realistic task simulations that predict on-the-job performance better than interviews." The AI Task & Prompt Design team (6 PMs, 3 prompt engineers, 2 psychometriceans) ships ~12 new task modules per quarter. Each module goes through a 4-stage pipeline: (1) Scenario Design, (2) Prompt Specification & Rubric Authoring, (3) LLM Auto-Grader Calibration, and (4) Human Rater Validation.

Three months ago, the team launched a "Multi-Tool PM Assessment" track targeting senior PM hires. It includes tasks that simulate real workflows across productivity tools. Early adoption has been strong (41 enterprise clients activated the track), but quality metrics are concerning.

### Client Feedback Summary (from 23 post-assessment debrief calls):

* 74% of hiring managers said the tasks "felt realistic" but "didn't separate great candidates from good ones."
* 61% said rubric scores clustered too tightly – the middle 60% of candidates scored between 67 and 71 out of 100.
* 3 clients (including a FAANG company and a top-5 consulting firm) threatened to churn unless task difficulty and rubric discrimination improved within 60 days.
* Candidates themselves rated the tasks 4.1/5 on realism but only 2.8/5 on "intellectual challenge."

### Auto-Grader Performance (last 90 days, Multi-Tool track):

* Human-AI grading agreement (Cohen's kappa): 0.58 (Target: >= 0.75)
* Primary disagreement driver: open-ended "strategy rationale" fields where the rubric used subjective language like "demonstrates strong thinking."
* The auto-grader over-awarded points for verbose but shallow responses 45% of the time.

### The New Module Brief:

Your VP of Product has tasked you with designing a flagship task module called "Workflow Orchestration Challenge." The candidate being assessed is a mid-to-senior PM (3-7 years experience) who must demonstrate proficiency with Calendar, Gmail, Mixpanel, and Slack in an integrated scenario. The task must:

* Be completable in 30 minutes by the assessed candidate.
* Include at least one quantitative analysis component (Mixpanel data interpretation).
* Require the candidate to draft at least one artifact (e.g., a Slack message, an email, a calendar invite with agenda).
* Be scorable by the LLM auto-grader with a target Cohen's kappa >= 0.75.
* Discriminate effectively between the 50th and 90th percentile candidates.

*You must now design the task prompt, define the rubric, and defend your architectural decisions.*

---

## Key Data Points

| Metric | Value |
| --- | --- |
| Enterprise Clients (Total) | 87 |
| Multi-Tool Track Clients (Active) | 41 |
| Candidates Assessed (Multi-Tool, Last 90 Days) | 2,047 |
| Median Candidate Score | 67/100 |
| Score Standard Deviation | 8.3 points |
| Human-AI Kappa (Current) | 0.58 |
| Human-AI Kappa (Target) | ≥ 0.75 |
| Auto-Grader Over-Award Rate (Verbose Responses) | 45% |
| Client Churn Risk (60-Day Deadline) | 3 accounts ($1.2M ARR) |
| Candidate Realism Rating | 4.1 / 5.0 |
| Candidate Challenge Rating | 2.8 / 5.0 |
| New Module Time Budget (Candidate) | 30 minutes |
| Current Quarterly Module Shipping Rate | 12 modules |
| Team Composition | 6 PMs, 3 Prompt Engineers, 2 Psychometriceans |

---

## Data Exhibits

### EXHIBIT A: SCORE DISTRIBUTION

Current Multi-Tool track scores are approximately normal with mean 67, SD 8.3. The 25th percentile score is 61, the 75th percentile score is 73. Only 4% of candidates score above 85. The bottom 10% score below 55. Hiring managers report that candidates scoring 62-71 (the middle 60%) are "indistinguishable" in debrief sessions.

### EXHIBIT B: AUTO-GRADER DISAGREEMENT ANALYSIS

Of 412 flagged disagreements in the last 90 days, 67% occurred on text area fields with rubric criteria containing words like "strong," "clear," "thoughtful," or "demonstrates understanding." Only 11% of disagreements occurred on fields with criteria referencing specific, observable outputs (e.g., "Includes at least 3 data points," "addresses both stakeholder groups by name"). Select-type and rating-type fields had 97% agreement.

### EXHIBIT C: CANDIDATE TIME-ON-TASK DATA

Average completion time for current multi-tool tasks is 22.4 minutes (target: 30 min). Candidates in the top decile spend an average of 28.1 minutes. Candidates in the bottom quartile spend an average of 16.7 minutes. Time-on-task correlates with final score at r = 0.41.

### EXHIBIT D: STAKEHOLDER PRIORITIES