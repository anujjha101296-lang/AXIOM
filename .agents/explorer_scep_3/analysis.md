# Architectural Design & Verification Analysis: SCEP R5 & R6

**Project**: AXIOM Scientific Capability Evaluation Platform (EPIC-002 SCEP)  
**Author**: Explorer 3  
**Target Domain**: R5 (Evaluation API & CLI Runner) and R6 (Independent Audit Layer)  
**Date**: 2026-08-06  

---

## 1. Executive Summary & Scope

The Scientific Capability Evaluation Platform (SCEP) serves as the objective measurement backbone of AXIOM Labs, ensuring that every engineering iteration yields measurable scientific capability growth rather than vanity feature accumulation.

This document provides the full architectural design, code topology analysis, and verification constraints for:
1. **R5 — Evaluation API & Automated Runner**: Restful API endpoints (`/eval/scores`, `/eval/run`, `/eval/history`, `GET /eval/prize-readiness`) hosted within FastAPI (`axiom/services/api_gateway/routes/eval_api.py`), the standalone CLI runner (`axiom/evaluation/run_benchmarks.py`), database persistence (`eval_runs`, `eval_readiness`, `eval_results`), regression guard mechanics (`--compare-previous` with exit code `0` for pass / exit code `1` for >5% regression), and delta report formatting.
2. **R6 — Independent Audit Layer**: Analysis of audit governance by Department I (Independent Audit) and Department J (Chief Skeptic), detailed breakdown of audit findings in `docs/audit/EPIC_002_audit.md`, grounding status for all 6 Clay Millennium Prize Problems, and risk mitigation directives for platform integrity.

---

## 2. Requirement R5: Evaluation API & Automated CLI Runner

### 2.1 Code Topology & System Architecture

The evaluation subsystem is located under `axiom/evaluation/` and integrated into the API Gateway at `axiom/services/api_gateway/routes/eval_api.py`.

```
axiom/
├── evaluation/
│   ├── __init__.py
│   ├── run_benchmarks.py               # CLI benchmark runner entrypoint
│   ├── prize_readiness.py              # Baseline prize readiness scorer
│   ├── frameworks/
│   │   ├── capability.py               # CapabilitySnapshot, DimensionScore, level classification
│   │   └── prize_readiness.py          # Evidence-based PrizeReadinessEngine (6 Clay Problems)
│   ├── benchmarks/
│   │   └── suite.py                    # Runnable benchmark test suites (MR, PV, CG, KQ, RP)
│   └── reporting/
│       └── delta_report.py             # CapabilityDeltaReport generator & Markdown formatter
└── services/
    └── api_gateway/
        ├── main.py                     # App lifespan, includes eval_router
        └── routes/
            └── eval_api.py             # REST endpoints (/eval/*)
```

### 2.2 CLI Runner Design (`axiom/evaluation/run_benchmarks.py`)

#### Invocation Interface
```bash
python3 -m axiom.evaluation.run_benchmarks [--db PATH] [--compare-previous]
```

#### Execution Workflow
1. **Database Initialization**: `init_db(db_path)` ensures the SQLite schema is active (`eval_runs` and `eval_readiness` tables).
2. **Benchmark Execution**: Calls 5 runnable benchmark suites in sequence:
   - `run_math_reasoning_benchmarks()`
   - `run_proof_verification_benchmarks()`
   - `run_conjecture_benchmarks(db_path)`
   - `run_knowledge_quality_benchmarks(db_path)`
   - `run_research_planning_benchmarks()`
3. **Estimation Integration**: Appends score placeholders for unbacked dimensions (`counterexample_search` = 0.35, `literature_synthesis` = 0.40, `research_productivity` = 0.50), explicitly marked as `estimated=True`.
4. **Snapshot Construction**: Instantiates `CapabilitySnapshot`, calculates composite score $S_{\text{composite}} = \sum_{d} w_d \cdot S_d$.
5. **Prize Readiness Calculation**: Invokes `PrizeReadinessEngine().compute_all(scores_map)` across all 6 Millennium Prize problems.
6. **Persistence**: Saves snapshot and readiness data to SQLite using `save_run()`.
7. **Delta Reporting**: Calls `generate_delta_report()`, comparing against previous run (`get_latest_run(db_path)`). Writes output to stdout, `docs/capability_delta_{run_id}.md`, and `benchmark_results.json`.
8. **Regression Evaluation**: If `--compare-previous` is supplied and `report.regression_detected` is `True` (i.e. any dimension drops by > 5% or 0.05), prints regression details and exits with **code 1**. Otherwise, exits with **code 0**.

### 2.3 Database Schema Design (`eval_runs`, `eval_readiness`, `eval_results`)

To meet storage and audit requirements, the evaluation subsystem manages SQLite schema tables:

```sql
-- Main snapshot table storing overall benchmark run metadata
CREATE TABLE IF NOT EXISTS eval_runs (
    run_id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    composite_score REAL NOT NULL,
    json_data TEXT NOT NULL
);

-- Detailed prize readiness scores per problem for each run
CREATE TABLE IF NOT EXISTS eval_readiness (
    run_id TEXT NOT NULL,
    problem_id TEXT NOT NULL,
    score REAL NOT NULL,
    json_data TEXT NOT NULL,
    PRIMARY KEY (run_id, problem_id)
);

-- Unified results table (R5 Specification Alignment)
CREATE TABLE IF NOT EXISTS eval_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    dimension_name TEXT NOT NULL,
    raw_score REAL NOT NULL,
    classified_level INTEGER NOT NULL,
    is_estimated BOOLEAN NOT NULL DEFAULT 0,
    metrics_json TEXT NOT NULL
);
```

### 2.4 REST API Specifications (`axiom/services/api_gateway/routes/eval_api.py`)

All endpoints are hosted under router prefix `/eval`:

| HTTP Method | Path | Description | Request Body | Response Format | Status Code |
|-------------|------|-------------|--------------|-----------------|-------------|
| `GET` | `/eval/scores` | Retrieves latest capability scores for all 8 dimensions | None | `Dict[str, DimensionDetail]` | `200 OK` |
| `POST` | `/eval/run` | Triggers benchmark execution synchronously, computes scores, updates DB & returns delta report | None | `BenchmarkRunResponse` | `200 OK` / `500 Error` |
| `GET` | `/eval/history` | Retrieves historical summary for up to last 10 benchmark runs | None | `List[RunSummary]` | `200 OK` |
| `GET` | `/eval/prize-readiness` | Computes & ranks prize readiness scores for all 6 Clay Millennium Problems | None | `List[PrizeReadinessScoreDict]` | `200 OK` |

#### Endpoint Implementation Breakdown
- `GET /eval/scores`: Reads latest JSON from `eval_runs`. If database is empty, returns predefined L0–L2 baseline defaults.
- `POST /eval/run`: Runs benchmark suites, saves snapshot, computes delta report, writes markdown to `docs/capability_delta_{run_id}.md`, and returns detailed response containing composite score, readiness breakdown, weakest capability, highest engineering priority, and regression flag.
- `GET /eval/history`: Queries `eval_runs` (`SELECT run_id, timestamp, composite_score FROM eval_runs ORDER BY timestamp DESC LIMIT 10`).
- `GET /eval/prize-readiness`: Loads current dimension scores, passes them to `PrizeReadinessEngine()`, returns sorted list by readiness score.

### 2.5 Capability Delta Report & Strict Specification Compliance

The delta report generator (`generate_delta_report`) produces human-readable Markdown matching the exact specification:

```markdown
EPIC-002 COMPLETE

Capability Delta

Knowledge Understanding
+12%

Proof Verification
+8%

Research Planning
+6%

Conjecture Generation
+4%

Counterexample Search
+0%

Prize Readiness

Riemann
31 → 34

P vs NP
28 → 30

Navier–Stokes
26 → 28

Weakest Capability
Automated Lemma Discovery

Highest Priority
Build Formal Proof & Lemma Discovery Platform

Recommended Next Epic
EPIC-003
```

---

## 3. Requirement R6: Independent Audit Layer & Chief Skeptic Review

### 3.1 Governance Framework (Department I & Department J)

The Independent Audit Layer enforces scientific integrity across AXIOM. 
- **Department I (Independent Audit)**: Audits proof verification grounding, database persistence, baseline integrity, and live execution compliance.
- **Department J (Chief Skeptic)**: Audits scoring assumptions, guards against benchmark overfitting/gaming, and flags ungrounded claim estimations.

All findings are documented in `docs/audit/EPIC_002_audit.md`.

### 3.2 Key Audit Findings Matrix

| Finding ID | Department | Risk Level | Description | Mandatory Audit Directive |
|------------|------------|------------|-------------|---------------------------|
| **Finding 1** | Dept J | **HIGH** | 3 of 8 dimensions (Counterexample Search: 0.35, Literature Synthesis: 0.40, Research Productivity: 0.50) are unbacked constant estimates. | Mark dimensions as `estimated=True`. Flag composite scores containing estimates with lower confidence. |
| **Finding 2** | Dept I | **CRITICAL** | Proof verification benchmarks (`_simulate_lean4_check`) use simulation fallback when Lean4 binary is missing. Risk of gaming syntax without mathematical proof. | Prohibit certification of Level L3+ Proof Verification capability without live compiler verification. |
| **Finding 3** | Dept J | **MEDIUM** | Mathematical Reasoning suite has 10 static questions; self-improvement loops could overfit/memorize answers. | Mandate randomized parameter seeding in benchmark generators for future sprints. |
| **Finding 4** | Dept I | **LOW** | On empty DB runs, delta report uses synthetic baseline comparison which could artificially inflate progress. | Hardcode post-EPIC-001 run as permanent baseline snapshot in SQLite database. |

### 3.3 Millennium Prize Problem Grounding Assessment

The `PrizeReadinessEngine` maps capability scores to readiness across all 6 Clay Millennium Problems:

$$\text{Readiness}_{\text{RH}} = 0.35 \cdot S_{\text{MR}} + 0.30 \cdot S_{\text{PV}} + 0.20 \cdot S_{\text{LS}} + 0.15 \cdot S_{\text{CE}}$$

#### Grounding Audit Table (`docs/audit/EPIC_002_audit.md`)

| Problem | Score | Active Grounding Evidence | Audit Status | Audit Rationale |
|---------|-------|---------------------------|--------------|-----------------|
| **Riemann Hypothesis** | 0.3805 | MR (0.90), PV (0.71), LS (0.40), CE (0.35) | **DISPUTED** | LS and CE are hardcoded estimates without test suite backing. |
| **P vs NP** | 0.2858 | MR (0.90), PV (0.71), RP (0.80) | **VERIFIED** | Prerequisites map directly to active runnable benchmarks. |
| **Navier–Stokes** | 0.4025 | MR (0.90), PV (0.71) | **VERIFIED** | Grounded in MR and PV benchmark measurements. |
| **Birch & Swinnerton-Dyer** | 0.3268 | MR (0.90), PV (0.71) | **VERIFIED** | Grounded in active benchmark suite measurements. |
| **Yang–Mills** | 0.2891 | MR (0.90), PV (0.71) | **VERIFIED** | Grounded in active benchmark suite measurements. |
| **Hodge Conjecture** | 0.2573 | MR (0.90), PV (0.71) | **VERIFIED** | Grounded in active benchmark suite measurements. |

---

## 4. Verification Constraints & Engineering Specifications

### 4.1 Execution Time Budget (< 2 Minutes)
- Total benchmark run execution time must remain under **120 seconds** (2 minutes).
- Benchmark suite execution in `run_benchmarks.py` currently finishes in ~1.2 seconds across 37 total test cases.

### 4.2 Test Coverage Requirements
The test suite in `tests/test_evaluation_platform.py` and `tests/test_scep_e2e.py` verifies:
1. **Level Classification**: Correct threshold boundaries for L0 through L5 across all dimensions.
2. **Composite Score Math**: Exact weighted sum calculation $S_{\text{composite}} = \sum w_d \cdot S_d$.
3. **Prize Readiness Grounding**: Correlation between underlying benchmark dimension scores and prize readiness outputs.
4. **Delta Report Format**: Markdown format output validation.
5. **SQLite Database Persistence**: Transactional integrity of `eval_runs` and `eval_readiness`.
6. **API Endpoints**: FastHTTP execution tests for `/eval/scores`, `/eval/run`, `/eval/history`, and `/eval/prize-readiness`.

---

## 5. Architectural Recommendations for Implementation & EPIC-003 Handoff

1. **Schema Standardization**: Ensure `eval_results` table is created alongside `eval_runs` to support individual dimension record queries.
2. **Compiler Sandbox Integration**: Resolve Department I Finding 2 by adding Lean 4 compiler binary check hooks to elevate certification from simulated to formally compiled.
3. **Dynamic Benchmark Seeding**: Address Department J Finding 3 by generating randomized algebraic expressions at runtime.
4. **Zeta Zero Benchmark Implementation**: Resolve the **DISPUTED** audit status of Riemann Hypothesis by replacing constant estimates in Counterexample Search with mpmath zeta zero verification tests.
