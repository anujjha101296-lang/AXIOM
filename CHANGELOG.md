# Changelog

All notable changes to AXIOM are documented in this file.

Format: [Semantic Versioning](https://semver.org/)

---

## [Unreleased]

### INTEGRATE — Tip integration (2026-08-09)
- Combined VFACTORY research tip with MASTER-OS, P0-WEB, and MVP-AUTH
- Chosen merge strategy: tip integration (not bottom-up of 10 PRs)

### AXIOM-MASTER-001 — Continuous Autonomous Execution (2026-08-09)
- Installed `.axiom/MASTER_DIRECTIVE.md` as binding engineering execution law
- Wired `AGENTS.md` and `.axiom/CONSTITUTION.md` to continuous-loop operation
- Added `AXIOM_STATE.md` honest system snapshot and `.axiom/MERGE_ORDER.md`

### P0-WEB — Honest Public Landing Page (2026-08-09)
- Replaced mock metrics and dead waitlist with verified capability disclosure
- Primary CTA to `/research`; static Next.js server component

### MVP-AUTH — Signup / Login (2026-08-09)
- `axiom/identity/` + `/auth/signup|/login|/me` + `/login` UI
- JWT accepted by `verify_token`; static token still works
- Limitation: project owner isolation deferred

### VFACTORY — Verification Factory (2026-08-09)
- **VFACTORY v1:** Capability registry (15 capabilities), test pyramid runners, verification scoring
- **User journeys:** A (research workspace), B (campaign), C (formal math), D (sandbox recovery)
- **Multi-agent roles:** 12 logical verification roles (controlled workers, not unlimited agents)
- **Orchestrator:** discover → test → score → update registry continuous loop
- **API:** `/vfactory/*` routes with optional authentication
- **Health check:** `scripts/vfactory_health_check.py`, `make vfactory-health`
- **Governance:** `VERIFICATION_STATUS.md`, `VERIFICATION_MATRIX.md`, `REGRESSION_LOG.md`, `E2E_STATUS.md`
- **Tests:** `tests/test_vfactory.py` (14 tests)

### MASTER — Build & Evolution Loop Audit (2026-08-09)
- **Capability matrix:** `AXIOM_CAPABILITY_MATRIX.md` — full implementation truth audit
- **Target architecture:** `AXIOM_TARGET_ARCHITECTURE.md`
- **Master loop directive:** `.axiom/MASTER_LOOP.md`
- **httpx pin fix:** TestClient compatibility restored (281 core tests pass)
- **Workflow API mounted:** `/workflows/*` with optional auth
- **Discovery query:** `/query` wired to SKAI synthesis (no longer empty stub)
- **CEL health:** PASS (281 tests)

### SKAI — Scientific Knowledge Acquisition & Intelligence Loop (2026-08-09)
- **SKAI v1:** `.axiom/SKAI.md`, knowledge acquisition docs, graph spec
- **Knowledge graph:** entities, relations, conflicts, gaps with full provenance
- **Source quality engine:** explicit tier ranking and reliability scores
- **Structure extraction:** LaTeX environments and text patterns
- **Bridge:** EGS ↔ E&R ↔ SKAI unified acquisition
- **Conflict detection:** opposing positions with resolution tracking
- **Gap detection:** research opportunities from graph analysis
- **Literature saturation:** honest coverage estimation
- **Reasoning-aware retrieval:** by research requirements, not embeddings
- **FRCE integration:** literature track wired to SKAI orchestrator
- **API:** `/skai/*` routes with optional authentication
- **Health check:** `scripts/skai_health_check.py`, `make skai-health`
- **Tests:** `tests/test_skai_knowledge.py` (12 tests)

### FRCE — Frontier Research Campaign Engine (2026-08-09)
- **FRCE v1:** `.axiom/FRCE.md`, campaign engine docs, orchestration architecture
- **Campaign kernel:** state machine, research graph, graduated contribution levels
- **Orchestrator:** connects SIMR, SEC, FMTP, E&R, GCP in research cycles
- **Pivot mechanism:** continue/pivot/escalate/pause/abandon after each cycle
- **Human gates:** novel claims, counterexamples, formal proofs, resource thresholds
- **Memory:** campaign memory + global compounding with provenance
- **Challenge ladder:** levels 0–9 with evidence-based advancement
- **API:** `/frce/*` routes with optional authentication
- **Health check:** `scripts/frce_health_check.py`, `make frce-health`
- **Tests:** `tests/test_frce_campaign.py` (14 tests)

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
