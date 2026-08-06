# Plan — EPIC-002 Scientific Capability Evaluation Platform (SCEP)

## Objective
Drive complete end-to-end design, implementation, benchmark evaluation, verification, and audit of EPIC-002 SCEP for AXIOM.

## Roadmap & Milestones

### Phase 0: Survey & Codebase Mapping
- Dispatch 3 parallel Explorers / Spec Miners to analyze existing codebase (`axiom/mip/`, `axiom/evaluation/`, `axiom/services/api_gateway/`, `tests/`) and extract detailed specifications for requirements R1–R6.

### Phase 1: Milestone Decomposition & Project Blueprint
- Formulate `PROJECT.md` at `.agents/orchestrator/PROJECT.md` specifying architecture, feature inventory, milestone breakdown (M1–M6), interface contracts, and code layout.

### Phase 2: Dual Track Execution
- **Track 1: E2E Testing Suite (E2E Testing Orchestrator)**: Build requirement-driven opaque-box test suite for `/eval/*` endpoints, `run_benchmarks.py`, delta reports, regression exits, and DB storage.
- **Track 2: Implementation Track**:
  - **M1: Scientific Capability Framework (SCF)**: Taxonomy L0–L5 for ≥8 dimensions, evaluation rubrics, composite score formula (`docs/scientific_capability_framework.md`).
  - **M2: Runnable Benchmark Suite**: ≥5 categories with ≥3 test cases each (algebra/calculus, theorem reproduction, proof verification, conjecture novelty, open problem decomposition), complete in < 2 mins, score in [0,1].
  - **M3: Prize Readiness Engine**: Scored readiness models for all 6 Clay Millennium Prize Problems with prerequisite map, milestones, confidence intervals, grounded in benchmarks (`GET /eval/prize-readiness`).
  - **M4: Capability Delta Report Generator**: JSON & Markdown reports showing % change per dimension, prize readiness delta, regression flags, weakest capability, recommended next epic (`docs/capability_delta_TIMESTAMP.md`).
  - **M5: Evaluation REST API & CLI Runner**: `/eval/*` API endpoints, SQLite `eval_results` integration, `run_benchmarks.py --compare-previous` with exit codes 0 and 1.
  - **M6: Independent Audit Layer**: Chief Skeptic (Dept J) & Audit (Dept I) report (`docs/audit/EPIC_002_audit.md`).

### Phase 3: Hardening & Final Gate Verification
- Run full test suite, verify CLI exit codes (0 for pass/no regression, 1 for regression > 5%), run forensic auditor, verify all acceptance criteria and document formatting.
- Report completion to Sentinel parent.
