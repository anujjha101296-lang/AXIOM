# Project: SCEP (Scientific Capability Evaluation Platform — EPIC-002)

## Architecture
- **Framework Module**: `axiom/evaluation/frameworks/capability.py` — Defines 8 capability dimensions (`mathematical_reasoning`, `proof_verification`, `conjecture_generation`, `knowledge_quality`, `counterexample_search`, `research_planning`, `literature_synthesis`, `research_productivity`), level taxonomy (L0–L5), evaluation rubrics, dimension weights, and composite score computation.
- **Benchmark Suite**: `axiom/evaluation/benchmarks/suite.py` — Runnable benchmark runner executing 8 suites covering the 5 required categories with $\ge 3$ test cases each, returning normalized scores in $[0, 1]$ in $<2$ seconds total.
- **Prize Readiness Engine**: `axiom/evaluation/frameworks/prize_readiness.py` — Dynamic, evidence-grounded readiness models for all 6 Clay Millennium Prize Problems with prerequisite capability DAGs, milestones, confidence intervals, and gap identification.
- **Delta Report Generator**: `axiom/evaluation/reporting/delta_report.py` — Generates structured Capability Delta Reports in JSON (`benchmark_results.json`) and Markdown (`docs/capability_delta_TIMESTAMP.md`) matching the exact required format from `ORIGINAL_REQUEST.md`.
- **API & CLI Integration**: `axiom/services/api_gateway/routes/eval_api.py` and `axiom/evaluation/run_benchmarks.py` — REST endpoints (`/eval/scores`, `/eval/run`, `/eval/history`, `/eval/prize-readiness`), SQLite table persistence (`eval_runs`, `eval_readiness`, `eval_results`), and CLI execution with `--compare-previous` exit codes (0 for pass / no regression, 1 for regression > 5%).
- **Independent Audit Layer**: `docs/audit/EPIC_002_audit.md` — Formal audit by Chief Skeptic (Dept J) and Independent Audit (Dept I) documenting unbacked estimates, compiler simulation fallbacks, gaming risks, and grounding status.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Scientific Capability Framework (SCF) | Taxonomy L0–L5 for 8 dimensions, rubrics, composite formula | M1 | R1 |
| 2 | Runnable Benchmark Suite | $\ge 5$ categories, $\ge 3$ cases each, $<2$ min total runtime, score in $[0,1]$ | M2 | R2 |
| 3 | Prize Readiness Engine | Scored readiness models for 6 Millennium Problems grounded in benchmark data | M3 | R3 |
| 4 | Capability Delta Report Generator | JSON & Markdown reports showing % change, readiness delta, exact format compliance | M4 | R4 |
| 5 | Evaluation API & CLI Runner | REST `/eval/*` endpoints, SQLite storage, `run_benchmarks.py --compare-previous` (exit 0 / 1) | M5 | R5 |
| 6 | Independent Audit Layer | Chief Skeptic (Dept J) & Audit (Dept I) findings document at `docs/audit/EPIC_002_audit.md` | M6 | R6 |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Scientific Capability Framework | `docs/scientific_capability_framework.md`, `capability.py` | None | PLANNED |
| M2 | Benchmark Suite | `axiom/evaluation/benchmarks/suite.py`, 8 benchmark categories | M1 | PLANNED |
| M3 | Prize Readiness Engine | `axiom/evaluation/frameworks/prize_readiness.py`, 6 Clay problems | M1, M2 | PLANNED |
| M4 | Capability Delta Report Generator | `axiom/evaluation/reporting/delta_report.py`, format validation | M1, M2, M3 | PLANNED |
| M5 | Evaluation API & CLI Runner | `eval_api.py`, `run_benchmarks.py --compare-previous`, DB persistence | M1–M4 | PLANNED |
| M6 | Independent Audit Layer | `docs/audit/EPIC_002_audit.md`, Dept I & Dept J findings | M1–M5 | PLANNED |

## Interface Contracts
### Evaluation Engine ↔ API Gateway
- `GET /eval/scores`: Returns `{"composite_score": float, "dimensions": {dim_name: {"score": float, "level": int, "estimated": bool}}}`
- `POST /eval/run`: Executes benchmark suite, returns `BenchmarkRunResponse` with run ID, composite score, execution time, and status.
- `GET /eval/history`: Returns list of past `BenchmarkRunSummary` records from SQLite.
- `GET /eval/prize-readiness`: Returns `{"problems": {prob_id: {"name": str, "readiness_score": float, "readiness_integer": int, "confidence_interval": [float, float], "status": str, "grounded_evidence": dict}}}`

### CLI Runner ↔ Database & System
- `run_benchmarks.py`: Options `--compare-previous`, `--db`, `--output-json`, `--output-md`.
- Exit 0: Execution succeeds and composite capability drop is $\le 5\%$.
- Exit 1: Execution fails or any capability dimension regression is $> 5\%$.

## Code Layout
- `docs/scientific_capability_framework.md` — SCF framework taxonomy and formulas
- `docs/audit/EPIC_002_audit.md` — Independent Audit document
- `axiom/evaluation/frameworks/capability.py` — Framework dimensions and levels
- `axiom/evaluation/frameworks/prize_readiness.py` — Prize readiness model
- `axiom/evaluation/benchmarks/suite.py` — Benchmark suites and runner
- `axiom/evaluation/reporting/delta_report.py` — Markdown & JSON delta report generator
- `axiom/evaluation/run_benchmarks.py` — CLI runner script
- `axiom/services/api_gateway/routes/eval_api.py` — FastAPI evaluation routes
- `tests/test_evaluation_platform.py` — Unit & integration tests
- `tests/test_scep_e2e.py` — End-to-end evaluation tests
