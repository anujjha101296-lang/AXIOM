# AXIOM Phase 14 — Hypothesis & Scientific Reasoning Engine Architecture

## 1. Overview
AXIOM Phase 14 introduces the **Scientific Reasoning Layer**. Rather than presenting AI model outputs as verified facts, Phase 14 structures research questions and gaps into testable hypotheses with explicit falsifiers, scientific critiques, observable predictions, and structured verification plans.

---

## 2. Canonical Domain Model & Status Lifecycle

### Hypothesis Model (`hypotheses`)
- **`Hypothesis`**: Core scientific proposition (`id`, `project_id`, `question_id`, `gap_id`, `claim`, `motivation`, `assumptions`, `verification_strategy`, `status`, `confidence_score`, `rationale`).
- **Controlled Status Lifecycle**:
  $$\text{PROPOSED} \longrightarrow \text{UNDER\_REVIEW} \longrightarrow \begin{cases} \text{SUPPORTED} \\ \text{WEAKLY\_SUPPORTED} \\ \text{CONTRADICTED} \\ \text{FALSIFIED} \\ \text{INCONCLUSIVE} \\ \text{RETIRED} \end{cases}$$
  Candidate hypotheses are NEVER automatically promoted from `PROPOSED` to `SUPPORTED` without verified evidence.

### Predictions & Falsifiers (`hypothesis_predictions`)
- **`HypothesisPrediction`**: Observable condition, expected outcome, measurement metric, and explicit falsifying observation.

### Scientific Critique (`hypothesis_critiques`)
- **`HypothesisCritique`**: Evaluates hypotheses for logical consistency, unsupported assumptions, scope errors, circular reasoning, and unfalsifiability (`VALID`, `NEEDS_REVISION`, `UNFALSIFIABLE`, `CONTRADICTED`, `INSUFFICIENT_EVIDENCE`).

### Verification Plans (`verification_plans`)
- **`VerificationPlan`**: Formulates structured, reproducible testing procedures (`question`, `hypothesis_summary`, `required_evidence`, `predictions`, `method`, `data_sources`, `success_criteria`, `failure_criteria`, `limitations`).

---

## 3. Bounded Scientific Reasoning Loop
$$\text{RESEARCH QUESTION} \longrightarrow \text{KNOWLEDGE GRAPH} \longrightarrow \text{GAPS} \longrightarrow \text{HYPOTHESIS GENERATION} \longrightarrow \text{CRITIC} \longrightarrow \text{FALSIFICATION SEARCH} \longrightarrow \text{REVISION} \longrightarrow \text{RANKING} \longrightarrow \text{VERIFICATION PLAN}$$

Loops operate under strict step limits and budget controls.

---

## 4. REST API Endpoints
- `POST /api/v1/hypothesis/generate`: Formulate candidate hypotheses & verification plan for a question.
- `GET /api/v1/hypothesis/project/{project_id}`: List all project hypotheses with predictions and critiques.

---

## 5. Database Schema & Alembic Migration
- Alembic Migration: `e4f56185a741_add_phase14_hypothesis_reasoning_tables.py`
- Relational tables with foreign key cascades to `projects.id` and index `project_id` and `status`.
