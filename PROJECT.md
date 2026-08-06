# Project: AXIOM — Scientific Capability Evaluation Platform (SCEP - EPIC-002)

## Architecture
AXIOM Scientific Capability Evaluation Platform (SCEP - EPIC-002) is the objective measurement system for AXIOM Labs. Inspired by AlphaFold's evaluation-first philosophy, SCEP measures whether every engineering sprint improves scientific capability across 8 core dimensions and 6 Clay Millennium Prize Problems.

- `docs/scientific_capability_framework.md`: Formal taxonomy L0–L5 for 8 dimensions, objective rubrics, composite score formula (R1).
- `axiom/evaluation/frameworks/capability.py`: Capability dimension enum, weights, L0-L5 thresholds, level names, composite calculation (R1).
- `axiom/evaluation/benchmarks/suite.py`: Runnable benchmark suite for 8 dimensions, ≥5 categories, ≥3 test cases each, running in < 2 mins total, scores in [0, 1] (R2).
- `axiom/evaluation/frameworks/prize_readiness.py`: Scored readiness model for 6 Clay Millennium Prize Problems, prerequisite map, milestones, confidence intervals, grounded in benchmark results (R3).
- `axiom/evaluation/reporting/delta_report.py`: Capability Delta Report generator producing JSON & Markdown reports (`docs/capability_delta_TIMESTAMP.md`) formatted strictly per spec (R4).
- `axiom/evaluation/run_benchmarks.py`: CLI runner with `--compare-previous` flag, exit code 0 (pass/no regression) / exit code 1 (regression > 5%), saving to SQLite `eval_results` and `eval_runs` tables (R5).
- `axiom/services/api_gateway/routes/eval_api.py`: FastAPI REST router at `/eval/*` exposing `/scores`, `/run`, `/history`, `/prize-readiness` (R5).
- `docs/audit/EPIC_002_audit.md`: Independent audit document by Department J (Chief Skeptic) & Department I (Independent Audit) flagging optimistic assumptions, gameable benchmarks, ungrounded readiness scores (R6).

## Feature Inventory

| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Capability Framework Document | Formal taxonomy L0–L5 for 8 dimensions, evaluation rubrics, composite score formula | M1 | survey |
| 2 | Capability Framework Code Module | Python module `capability.py` with 8 dimensions, level thresholds, composite score calculator | M1 | survey |
| 3 | Benchmark Suite Core Categories | Benchmark runners for Algebra/Calculus, Theorem Reproduction, Proof Verification, Conjecture Novelty, Open Problem Decomposition | M2 | survey |
| 4 | Runnable Benchmark Expansion | Complete benchmark runners for Counterexample Search, Literature Synthesis, Research Productivity (<2 min total) | M2 | survey |
| 5 | Prize Readiness Scorer | Scored model for 6 Millennium Problems grounded in benchmark scores with confidence intervals | M3 | survey |
| 6 | SQLite DB Persistence | Database tables `eval_results`, `eval_runs`, and `eval_readiness` in SQLite store (`axiom.db`) | M3 | survey |
| 7 | Capability Delta Report Generator | Generator producing JSON & Markdown reports (`docs/capability_delta_TIMESTAMP.md`) matching exact spec | M4 | survey |
| 8 | Evaluation CLI Runner | CLI script `axiom/evaluation/run_benchmarks.py` with `--compare-previous` and exit codes (0/1) | M5 | survey |
| 9 | Evaluation REST API Endpoints | FastAPI endpoints `GET /eval/scores`, `POST /eval/run`, `GET /eval/history`, `GET /eval/prize-readiness` | M5 | survey |
| 10 | Independent Audit Layer Document | Department J & I audit document `docs/audit/EPIC_002_audit.md` flagging assumptions and ungrounded scores | M6 | survey |
| 11 | Comprehensive E2E Test Suite | Test suite verifying benchmarks, delta reports, API endpoints, CLI exit codes, and DB storage | M7 | survey |

## Milestones

| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | M1: Scientific Capability Framework | Framework document (`docs/scientific_capability_framework.md`) and code module (`capability.py`) | none | DONE |
| 2 | M2: Benchmark Suite Expansion & Tuning | Runnable benchmark suite with 8 dimensions, ≥5 categories, ≥3 cases each, < 2 min run limit | M1 | PLANNED |
| 3 | M3: Prize Readiness Engine & Storage | Scored model for 6 Millennium Problems grounded in benchmarks, SQLite `eval_results` table | M1, M2 | PLANNED |
| 4 | M4: Capability Delta Report Generator | JSON & Markdown report generator (`docs/capability_delta_TIMESTAMP.md`) matching spec | M2, M3 | PLANNED |
| 5 | M5: Evaluation API & CLI Runner | REST endpoints (`/eval/*`), CLI runner (`run_benchmarks.py --compare-previous`) exiting 0/1 | M3, M4 | PLANNED |
| 6 | M6: Independent Audit Layer | Independent audit document at `docs/audit/EPIC_002_audit.md` (Dept J & I) | M1..M5 | PLANNED |
| 7 | M7: E2E Integration & Verification | Dual Track E2E test suite, regression checks, CLI exit code tests, forensic audit | M1..M6 | PLANNED |

## Interface Contracts

### Benchmark Suite ↔ Capability Framework
- Input: `run_all_benchmarks() -> Dict[str, float]`
- Output: `CapabilitySnapshot(scores, composite_score, timestamp)`

### Benchmark Suite ↔ Prize Readiness Engine
- Input: `CapabilitySnapshot`
- Output: `Dict[str, PrizeReadinessScore]` (for 6 Millennium Problems: Riemann, P vs NP, Navier-Stokes, Yang-Mills, BSD, Poincaré)

### Delta Report Generator ↔ Storage / CLI
- Input: `current_snapshot: CapabilitySnapshot, prev_snapshot: Optional[CapabilitySnapshot], current_readiness, prev_readiness`
- Output: `CapabilityDeltaReport(markdown_output: str, json_output: dict, regression_detected: bool)`

### CLI Runner ↔ System Environment
- Execution: `python axiom/evaluation/run_benchmarks.py [--db PATH] [--compare-previous]`
- Exit Codes: `0` (pass / no regression), `1` (regression > 5% on any dimension)

## Code Layout
- `docs/`: `scientific_capability_framework.md`, `capability_delta_TIMESTAMP.md`, `audit/EPIC_002_audit.md`
- `axiom/evaluation/`:
  - `frameworks/capability.py`: 8 dimensions, L0–L5 level taxonomy, thresholds, composite formula
  - `frameworks/prize_readiness.py`: 6 Millennium Problems, prerequisite maps, confidence intervals
  - `benchmarks/suite.py`: Runnable benchmark implementations for all 8 dimensions
  - `reporting/delta_report.py`: JSON & Markdown delta report generator
  - `run_benchmarks.py`: CLI runner with `--compare-previous` and exit codes (0/1)
- `axiom/services/api_gateway/routes/eval_api.py`: REST router mounted at `/eval/*`
- `tests/`: `test_evaluation_platform.py`, `test_eval_api.py`, `test_scep_e2e.py`
