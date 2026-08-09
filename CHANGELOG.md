# Changelog

All notable changes to AXIOM are documented in this file.

Format: [Semantic Versioning](https://semver.org/)

---

## [Unreleased]

### SEC — Scientific Experimentation & Compute Loop (2026-08-09)
- **SEC v1:** `.axiom/SEC.md`, experiment engine docs, sandbox security
- **Experiment kernel:** lifecycle, versioned store, hypothesis linking
- **Sandbox:** static analysis, subprocess isolation, timeouts
- **Integrity gate:** computational evidence ≠ proof or scientific fact
- **API:** `/experiments/*` routes with optional authentication
- **Plugins:** VLSI research interface stub
- **Health check:** `scripts/sec_health_check.py`, `make sec-health`
- **Tests:** `tests/test_experiment_sec.py` (13 tests)

### FMTP — Formal Mathematics & Theorem-Proving Loop (2026-08-09)
- **FMTP v1:** `.axiom/FMTP.md`, formal math status reports, millennium readiness update
- **Prover registry:** Lean4, Coq, Isabelle, SMT, SymPy with installation status
- **Pipelines:** informal → formal, formal → informal, proof search, compilation gate
- **Counterexample engine:** SMT modular + randomized testing
- **Failure memory:** proof failures with repair suggestions
- **Millennium gate:** blocks premature prize campaigns
- **API:** `/formal/*` routes with optional authentication
- **Health check:** `scripts/fmtp_health_check.py`, `make fmtp-health`
- **Tests:** `tests/test_formal_math.py` (17 tests)

### SIMR — Scientific Intelligence & Model Routing (2026-08-08)
- **SIMR v1:** `.axiom/SIMR.md`, model/tool registries, capability graph, routing policy docs
- **Model registry:** 5 models with capability scores and fallback chains
- **Tool registry:** Scientific tools + workflow workers with TSS risk classes
- **Router:** Problem profiling, strategy generation, verification-aware selection
- **Research compiler:** Problem → capability graph → execution plan
- **Failure memory:** Model failure tracking and adaptive deprioritization
- **API:** `/routing/*` routes with optional authentication
- **Integration:** Research Q&A uses router instead of hardcoded model
- **Health check:** `scripts/simr_health_check.py`, `make simr-health`
- **Tests:** `tests/test_simr_routing.py` (14 tests)

### E&R — Evidence & Reproducibility Loop (2026-08-08)
- **E&R v1:** `.axiom/ERL.md`, evidence/reproducibility/verification status reports
- **Claim registry:** SQLite `er_*` tables with versioned claims and provenance graph
- **Discovery gate:** status upgrades and discovery labels require evidence and verification
- **API:** `/evidence/*` routes with optional authentication
- **Reproduction:** `compare_provenance_runs()` integrated with H1-OBS provenance
- **Health check:** `scripts/erl_health_check.py`, `make erl-health`
- **Tests:** `tests/test_evidence_registry.py` (12 tests)

### TSS — Trust, Security & Safety Loop (2026-08-08)
- **TSS v1:** `.axiom/TSS.md`, security scorecards, incident runbook
- **Production guard:** blocks insecure production startup; audits config on API boot
- **Optional route auth:** `/eval`, `/gcp`, `/provenance` (enable via env in production)
- **Secret scanner:** `scripts/tss_security_check.py`, `make tss-security`
- **Agent safety:** `ToolRiskClass` + prompt-injection heuristics

### H1-OBS — Run Provenance (2026-08-08)
- **Unified provenance:** `run_provenance` SQLite table for SCEP evaluation runs
- **API:** `GET /provenance/runs`, `GET /provenance/runs/{type}/{id}`, `GET /eval/runs/{id}`
- **Integration:** `POST /eval/run` and CLI benchmark runner record provenance automatically
- **Tests:** `tests/test_run_provenance.py` (9 tests)

### CEL — Continuous Evolution Loop (2026-08-08)
- **S0-E4 evidence gate:** `EvidenceState` enum; capability snapshots and prize readiness expose `evidence_tier`, `benchmark_count`, and `limitations`
- **CEL artifacts:** `.axiom/CEL.md`, `TECH_DEBT.md`, `BENCHMARK_RESULTS.md`, `ENGINEERING_SCORECARD.md`, `PRODUCT_SCORECARD.md`
- **Health check:** `scripts/cel_health_check.py`, `make cel-health`
- **Tests:** `tests/test_s0_e4_evidence_gate.py`

### AXIOM Operating System v1.0
- Added `.gitignore`, `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`
- Added Pydantic `BaseSettings` configuration system (`axiom/config/settings.py`)
- Added structured JSON logging via `structlog` (`axiom/observability/logger.py`)
- Added Prometheus metrics endpoint (`axiom/observability/metrics.py`, `GET /metrics`)
- Added in-process async event bus (`axiom/core/events/bus.py`)
- Added JWT + RBAC authentication with roles: `RESEARCHER`, `ADMIN`, `READONLY`
- Added database migrations with `proof_lineage` table
- Added `Makefile` with `setup`, `dev`, `test`, `lint`, `docker-build`, `docker-up` targets
- Added multi-stage `Dockerfile` and `docker-compose.yml`
- Added GitHub Actions CI/CD workflows (lint, test, security scan, build)
- Added `.env.example` for secrets management
- Added `tests/conftest.py` shared fixtures
- Added `docs/architecture.md` and `docs/api.md`

### Sprint 2 — Autonomous Discovery Loop
- **R1. Hypothesis Engine (HYP)**: Generates DUAL, BOUND, COMPLEX, GENERAL, COMPOSE conjectures from EGS verified claims
- **R2. Prize Readiness Scorer (PRS)**: Scores AXIOM against all 7 Millennium Prize Problems across 5 capability dimensions
- **R3. Self-Improvement Loop (SIL)**: Audits 10 subsystems and auto-generates prioritised `roadmap.md`
- **R4. Working Memory (MEM)**: Session-scoped store for active hypotheses, failures, open questions
- **R5. Scientific Benchmark (SCB)**: 5-dimension pytest benchmark suite
- Added API endpoints: `/hypothesize`, `/memory/context`, `/memory/reset`, `/memory/problem`, `/self-improve`, `/benchmark/prize-readiness`

### Sprint 1 — Core Platform Foundation
- **EIE**: arXiv LaTeX parser extracting theorems, lemmas, definitions, citations
- **EGS**: SQLite epistemic graph store with NetworkX export
- **LRK**: Lean 4 theorem exporter
- **AVT**: Z3 SMT modular arithmetic and real inequality verifier
- **MCTS**: Monte Carlo Tree Search algebraic proof solver
- **API Gateway**: FastAPI REST gateway with JWT auth
- **UI**: Next.js spatial canvas knowledge graph dashboard
- 16 passing integration tests

---

## [0.1.0] — Sprint 1 Initial Release

- Core platform established
- 16/16 tests passing
