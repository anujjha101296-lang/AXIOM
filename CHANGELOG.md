# Changelog

All notable changes to AXIOM are documented in this file.

Format: [Semantic Versioning](https://semver.org/)

---

## [Unreleased]

### P0-WEB — Honest Public Landing Page (2026-08-09)
- Replaced mock metrics and fake terminal output with verified platform facts
- Capability disclosure: Available now / Early access / Planned tiers
- Removed dead waitlist form; primary CTA links to `/research` workspace
- Health gate section documents executable `make *-health` checks
- Landing page is a static server component (no client interactivity errors)
- Updated metadata in `layout.tsx` for honest early-access positioning

### Sprint 0 — Production Foundation
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
