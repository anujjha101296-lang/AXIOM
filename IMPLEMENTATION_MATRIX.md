# AXIOM Implementation Matrix

**Verification date:** 2026-08-07  
**Branch:** `cursor/axiom-verification-review-dc7e`  
**Legend:** ✅ Fully implemented · ⚠️ Partial · 🔬 Prototype · 📐 Architecture only · ❌ Not present

---

## Summary Matrix

| # | Capability | Status | Source (primary) | API surface | UI | Tests | Benchmarks |
|---|------------|--------|------------------|-------------|-----|-------|------------|
| 1 | API Gateway & health | ✅ | `axiom/services/api_gateway/main.py` | `/health`, `/ready`, `/metrics` | — | 5+ | — |
| 2 | Authentication (Bearer) | ⚠️ | `auth.py` | Protected routes only; no `/auth/*` | — | Partial | — |
| 3 | Epistemic Knowledge Graph | ✅ | `axiom/core/knowledge_graph/` | `GET /graph` | — | 5 | EPIC-002 dim |
| 4 | arXiv ingestion | ⚠️ | `axiom/core/parser/` | `POST /ingest` | — | Indirect | — |
| 5 | Query (discovery) | 🔬 | `main.py` | `POST /query` (empty results) | — | — | — |
| 6 | SMT verification | ✅ | `axiom/core/verification/smt_gateway.py` | `POST /verify/conjecture` | — | 10+ | EPIC-002 dim |
| 7 | MCTS + Lean export | ✅ | `mcts.py`, `lean_exporter.py` | `POST /verify/proof` | — | 6+ | EPIC-002 dim |
| 8 | Hypothesis engine | ✅ | `hypothesis_engine.py` | `POST /hypothesize` | — | 6 | EPIC-002 dim |
| 9 | Working memory | ✅ | `working_memory.py` | `/memory/*` | — | Yes | — |
| 10 | Self-improvement loop | ✅ | `self_improvement.py` | `POST /self-improve` | — | Yes | — |
| 11 | Legacy prize readiness | ✅ | `evaluation/prize_readiness.py` | `GET /benchmark/prize-readiness` | — | 10 | Inline |
| 12 | MIP (full platform) | ✅ | `axiom/mip/` | `/mip/*` (14 endpoints) | — | 64 | — |
| 13 | EPIC-002 / SCEP eval | ✅ | `axiom/evaluation/` | `/eval/*` (4 endpoints) | — | 37 | composite 0.944 |
| 14 | S0-E4 evidence gate | ✅ | `frameworks/evidence.py` | Fields on `/eval/*` | — | 5 | measured |
| 15 | MDE theorem retrieval | ⚠️ | `core/retrieval/engine.py` | `GET /mde/retrieval` only | — | 18 | — |
| 16 | Research workspace | ⚠️ | `axiom/research/` | `/research/*` (15+ routes) | page only | 15 | — |
| 17 | Model gateway | ⚠️ | `services/model_gateway/client.py` | Used by research QA | — | Mocked | — |
| 18 | Research Validation (RVP) | ✅ | `axiom/research_validation/` | `/rvp/*` (7 endpoints) | — | 6 | 96.2% pass |
| 19 | Engineering governance | ✅ | `axiom/governance/` | CLI/Makefile | — | 6 | Health 70.2 |
| 20 | Workflow engine | 📐 | `axiom/workflow/` | **Not mounted** | — | 0 | — |
| 21 | Research loop | ❌ | — | 404 | — | 0 | — |
| 22 | Web UI (Next.js) | 🔬 | `ui/src/app/` | None wired | 3 pages | 0 | Build fails |
| 23 | Observability | ✅ | `axiom/observability/` | `/metrics`, `/events` | — | Indirect | — |
| 24 | Event bus | ✅ | `axiom/core/events/bus.py` | `GET /events` | — | — | — |
| 25 | SymPy engine | ✅ | `axiom/core/symbolic/` | Internal | — | E2E partial | — |
| 26 | Docker / Compose | ⚠️ | `docker-compose.yml` | — | — | — | — |
| 27 | CI (governance) | ⚠️ | `.github/workflows/governance.yml` | — | — | — | — |

---

## Status Definitions (applied)

| Status | Criteria used in this matrix |
|--------|------------------------------|
| **Fully implemented** | Source exists, API/CLI callable, tests pass, demonstrated in verification |
| **Partial** | Core logic exists but API surface incomplete, tenancy missing, or demo blocked |
| **Prototype** | Stub/minimal implementation or UI without working integration |
| **Architecture only** | Substantial code exists but not exposed or not testable end-to-end |
| **Not present** | No source on verified branch |

---

## API Mounting Inventory

Verified routers in `main.py`:

| Router | Prefix | Mounted |
|--------|--------|---------|
| MIP | `/mip` | ✅ |
| Eval | `/eval` | ✅ |
| MDE | `/mde` | ✅ (1 route) |
| Research | `/research` | ✅ |
| RVP | `/rvp` | ✅ |
| Workflow | `/workflows` | ❌ |
| Auth | `/auth` | ❌ |
| Research loop | `/research-loop` | ❌ |

Inline routes in `main.py`: `/health`, `/ready`, `/metrics`, `/events`, `/graph`, `/ingest`, `/query`, `/verify/*`, `/hypothesize`, `/memory/*`, `/self-improve`, `/benchmark/prize-readiness`

---

## Test Coverage Matrix

| Area | Test file(s) | Count | Pass (verified) |
|------|-------------|------:|----------------:|
| Core (excl. e2e) | `tests/test_*.py`, `tests/mip/` | 176+ | **176/176** |
| E2E | `tests/e2e/*.py` | 226 | **200/226** |
| MIP | `tests/mip/test_mip_all.py` | 64 | **64/64** |
| Governance | `tests/test_governance.py` | 6 | **6/6** |
| RVP | `tests/test_research_validation.py` | 6 | **6/6** |
| Eval / S0-E4 | `test_eval_api`, `test_s0_e4_*`, `test_evaluation_platform`, `test_scep_e2e`, `test_benchmark` | 37 | **37/37** |
| Research workspace | `tests/test_research_workspace.py` | 15 | **15/15** |
| Verification | `tests/test_verification_*.py` | 14 | **14/14** |
| Workflow | — | 0 | — |
| UI | — | 0 | — |

**E2E failure cluster (26):** Primarily MDE API surface gap, tier3/tier4 autonomous discovery pipelines, and auth/error-handling scenarios expecting routes not mounted on this branch.

---

## Benchmark & Score Matrix

| System | Metric | Value | Source |
|--------|--------|------:|--------|
| EPIC-002 | Composite capability score | 0.944 | `POST /eval/run` |
| EPIC-002 | Weakest dimension | literature_synthesis (0.6) | `/eval/scores` |
| EPIC-002 | Regressions vs prior | 2 (knowledge_quality, literature_synthesis) | `benchmark_results.json` |
| RVP | Known-answer problems | 266 | `data/known_answer_problems.json` |
| RVP | Overall pass rate | 96.2% | `BENCHMARK_RESULTS.md` |
| RVP | Stage 0 mean score | 1.000 | `BENCHMARK_RESULTS.md` |
| RVP | Stage 1 mean score | 0.651 | `BENCHMARK_RESULTS.md` |
| RVP | Capability composite | 0.705 | `CAPABILITY_SCORE.md` |
| Governance | Engineering health | 70.2 | `ENGINEERING_HEALTH.md` |
| Governance | Product health | 31.1 | `PRODUCT_HEALTH.md` |
| Governance | Research capability | 20.4 | `RESEARCH_HEALTH.md` |
| Governance | Security score | 26.0 | `ENGINEERING_HEALTH.md` |

---

## UI Component Matrix

| Page | Path | Build | API wired | Status |
|------|------|-------|-----------|--------|
| Landing | `/` | ❌ Fail | No | 🔬 Prototype |
| Research | `/research` | Not isolated | No | 🔬 Prototype |
| Workspace | `/workspace` | Not isolated | No | 🔬 Prototype |
| Login | `/login` | — | — | ❌ Not present |
| Demo | `/demo` | — | — | ❌ Not present |

---

## External Tooling Dependencies

| Tool | Required by | Installed (verified env) | Impact |
|------|-------------|--------------------------|--------|
| Lean 4 | MIP formal, proof export | ❌ | Simulated compile |
| Coq (`coqc`) | MIP formal | ❌ | Simulated |
| Isabelle | MIP formal | ❌ | Simulated |
| Z3 | SMT gateway | ✅ (via library) | Working |
| LLM backend | Research QA, RVP | Not configured | Mock/heuristic |
| arXiv API | Ingestion | Network | Live fetch fragile |

---

## Branch Divergence Notes

| Component | On verified branch | Elsewhere |
|-----------|-------------------|-----------|
| Research loop | ❌ Absent | `origin/cursor/milestone-005-research-loop-dc7e` |
| Workflow HTTP API | Code only | Router not in `main.py` |
| MDE full API | 1 route | E2E expects full surface |

---

*Matrix reflects verified state only. Status counts: 14 fully implemented, 7 partial, 2 prototype, 3 architecture-only/absent as major capabilities.*
