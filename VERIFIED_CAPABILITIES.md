# AXIOM Verified Capabilities

**Verification date:** 2026-08-07  
**Branch verified:** `cursor/axiom-verification-review-dc7e` (based on `cursor/research-validation-program-dc7e`)  
**Method:** Source inspection, automated test execution, API workflow demonstration, and `make` target execution. No planned features are included.

---

## Executive Summary

| Category | Fully implemented | Partial | Prototype | Architecture only |
|----------|------------------:|--------:|----------:|------------------:|
| Platform & API | 4 | 2 | 0 | 1 |
| Knowledge & Reasoning | 5 | 3 | 1 | 0 |
| Evaluation & Governance | 3 | 0 | 0 | 0 |
| Research Product | 2 | 2 | 1 | 2 |
| **Total (major capabilities)** | **14** | **7** | **2** | **3** |

**Test evidence (executed 2026-08-07):**

| Suite | Result |
|-------|--------|
| `pytest tests/ --ignore=tests/e2e` | **176 passed** |
| `pytest tests/e2e` | **200 passed, 26 failed** |
| `pytest tests/mip/test_mip_all.py` | **64 passed** |
| `make engineering-health` | Exit 0 — reports generated |
| `make research-validation` | Exit 0 — Stage 0 batch 10/10 pass |
| `npm run build` (ui/) | **Failed** — landing page prerender error |

---

## 1. API Gateway & Platform Infrastructure

**Status:** Fully implemented

### Source files
- `axiom/services/api_gateway/main.py`
- `axiom/config/settings.py`
- `axiom/observability/logger.py`, `axiom/observability/metrics.py`
- `axiom/core/knowledge_graph/migrations.py`

### APIs
| Endpoint | Auth | Verified |
|----------|------|----------|
| `GET /health` | No | 200 |
| `GET /ready` | No | 200 (DB ping) |
| `GET /metrics` | No | 200 (Prometheus text) |
| `GET /events` | Bearer | Implemented |
| `GET /docs`, `GET /redoc` | No | OpenAPI available |

### UI components
None (server-only).

### Tests
- `tests/test_api.py` (5 tests)
- Middleware exercised across e2e suites

### Benchmark results
- Cold import ~552ms (from governance collector)

### Known limitations
- Single-process in-memory event bus; not distributed.
- SQLite as default persistence; no multi-tenant partitioning at gateway level.

### Workflow demonstration
```
GET /health → 200 {"status":"healthy"}
GET /ready  → 200 {"status":"ready","database":"connected"}
GET /metrics → 200 Prometheus exposition format
```

---

## 2. Authentication & Authorization

**Status:** Partially implemented

### Source files
- `axiom/services/api_gateway/auth.py`

### APIs
| Capability | Mounted | Verified |
|------------|---------|----------|
| Static Bearer token (`AXIOM_API_TOKEN`) | Yes | 401 without token; 200 with valid token |
| JWT helpers (`create_jwt`, `decode_jwt`) | Library only | Not exposed via HTTP |
| RBAC (`require_role`) | Library only | Not wired to routes |
| `POST /auth/login` | **No** | 404 |
| `POST /auth/register` | **No** | 404 |

### UI components
None.

### Tests
- `tests/test_api.py::test_auth_success`
- E2E auth expectations partially unmet (`test_f19_tc03_bearer_token_authentication` fails)

### Benchmark results
N/A

### Known limitations
- Default token `axiom-dev-token` if env unset.
- JWT secret defaults to insecure value (Pydantic warning observed).
- No user registry, session management, or per-user data scoping in research store.

---

## 3. Epistemic Knowledge Graph (EGS)

**Status:** Fully implemented

### Source files
- `axiom/core/knowledge_graph/db.py`
- `axiom/core/knowledge_graph/schema.py`
- `axiom/core/knowledge_graph/migrations.py`

### APIs
| Endpoint | Auth | Verified |
|----------|------|----------|
| `GET /graph` | Bearer | 200 — exports nodes/edges |

### UI components
- `ui/src/app/workspace/page.tsx` — static/marketing workspace page; **not wired** to live graph API.

### Tests
- `tests/test_epistemic_layer.py` (5 tests)
- Seeded fixtures in `tests/conftest.py`

### Benchmark results
- Knowledge quality dimension score: 0.8 (EPIC-002 latest run)

### Known limitations
- Empty graph on fresh DB; population requires ingest or manual node creation.
- No graph visualization UI connected to API.

### Workflow demonstration
```
GET /graph (Bearer test_token) → 200 {"nodes":[],"edges":[]}  # fresh DB
```

---

## 4. arXiv Ingestion & Paper Parsing

**Status:** Partially implemented

### Source files
- `axiom/core/parser/arxiv_parser.py`
- `axiom/core/parser/semantic_tracker.py`

### APIs
| Endpoint | Auth | Verified |
|----------|------|----------|
| `POST /ingest` | Bearer | Endpoint exists; live arXiv fetch failed in demo |

### UI components
None.

### Tests
- Covered indirectly in e2e mock scenarios
- `tests/test_reasoning_pipeline.py`

### Benchmark results
N/A

### Known limitations
- **Live demo failure:** `POST /ingest` with `arxiv_id: 9901042` returned 500 — arXiv 404 for that ID in verification environment.
- Network-dependent; no offline fixture mode on the HTTP endpoint.
- `POST /query` returns empty results array (stub).

### Workflow demonstration
```
POST /ingest {"arxiv_id":"9901042"} → 500 (arXiv source not found)
```

---

## 5. SMT Counterexample Verification (Z3)

**Status:** Fully implemented (with simulation caveats)

### Source files
- `axiom/core/verification/smt_gateway.py`
- `axiom/core/verification/truthfulness.py`
- `axiom/core/symbolic/sympy_engine.py`

### APIs
| Endpoint | Auth | Verified |
|----------|------|----------|
| `POST /verify/conjecture` | Bearer | Implemented; schema requires `variables` as list (not dict) |

### UI components
None.

### Tests
- `tests/test_verification_truthfulness.py` (10 tests)
- `tests/test_reasoning_pipeline.py`
- E2E tier3/tier4 scenarios (some fail on broader pipeline expectations)

### Benchmark results
- Counterexample search dimension: 1.0 (EPIC-002)

### Known limitations
- SMT modular checks never assign TIER_2 formal proof (by design).
- Request schema mismatch caused 422 in ad-hoc demo when `variables` sent as object.

---

## 6. MCTS Proof Search & Lean Export

**Status:** Fully implemented (compiler simulation when Lean absent)

### Source files
- `axiom/core/reasoning/mcts.py`
- `axiom/core/verification/lean_exporter.py`

### APIs
| Endpoint | Auth | Verified |
|----------|------|----------|
| `POST /verify/proof` | Bearer | Implemented |

### UI components
None.

### Tests
- `tests/test_reasoning_pipeline.py`
- `tests/test_verification_truthfulness.py`

### Benchmark results
- Proof verification dimension: 1.0 (EPIC-002; simulated when Lean missing)

### Known limitations
- Lean 4 binary not installed in verification environment — returns "simulated compile success".
- Simulated passes explicitly marked `evidence_mode: simulated`, `formally_proven: false`.

---

## 7. Hypothesis Generation Engine

**Status:** Fully implemented

### Source files
- `axiom/core/reasoning/hypothesis_engine.py`

### APIs
| Endpoint | Auth | Verified |
|----------|------|----------|
| `POST /hypothesize` | Bearer | 200 — 0 hypotheses on empty graph |

### UI components
None.

### Tests
- `tests/test_reasoning_pipeline.py`

### Benchmark results
- Conjecture generation dimension: 1.0 (EPIC-002)

### Known limitations
- Returns zero hypotheses when EGS has no seed patterns (verified on empty DB).

---

## 8. Working Memory & Self-Improvement

**Status:** Fully implemented

### Source files
- `axiom/core/memory/working_memory.py`
- `axiom/core/reasoning/self_improvement.py`

### APIs
| Endpoint | Auth | Verified |
|----------|------|----------|
| `GET /memory/context` | Bearer | Implemented |
| `POST /memory/reset` | Bearer | Implemented |
| `POST /memory/problem` | Bearer | Implemented |
| `POST /self-improve` | Bearer | Implemented |

### UI components
None.

### Tests
- `tests/test_reasoning_pipeline.py`
- `tests/test_benchmark.py`

### Benchmark results
N/A (self-improve produces `roadmap.md` artifact)

### Known limitations
- Working memory is in-process only; not persisted across restarts unless snapshotted via MIP.

---

## 9. Legacy Prize Readiness Endpoint

**Status:** Fully implemented (superseded by EPIC-002 `/eval/prize-readiness`)

### Source files
- `axiom/evaluation/prize_readiness.py`

### APIs
| Endpoint | Auth | Verified |
|----------|------|----------|
| `GET /benchmark/prize-readiness` | Bearer | Implemented |

### Tests
- `tests/test_benchmark.py`

### Known limitations
- Parallel surface to EPIC-002; two prize-readiness APIs exist.

---

## 10. Mathematical Intelligence Platform (MIP)

**Status:** Fully implemented (formal compilers simulated)

### Source files
- `axiom/mip/` (knowledge, formal, conjecture, strategy, memory, verification)
- `axiom/services/api_gateway/routes/mip.py`

### APIs (all verified mounted)
| Endpoint | Verified |
|----------|----------|
| `POST /mip/knowledge/ingest` | Yes |
| `GET /mip/knowledge/lookup` | Yes |
| `GET /mip/knowledge/domain/{domain}` | Yes — 200, count=0 on empty DB |
| `POST /mip/formal/generate` | Yes |
| `POST /mip/formal/compile` | Yes |
| `POST /mip/conjecture/generate` | Yes — 200, 5 conjectures |
| `GET /mip/conjecture/ranked` | Yes |
| `POST /mip/strategy/plan` | Yes |
| `GET /mip/strategy/decompose/{problem_id}` | Yes |
| `GET /mip/strategy/roadmap` | Yes |
| `GET /mip/memory/context` | Yes |
| `POST /mip/memory/snapshot` | Yes |
| `GET /mip/memory/failed_tactics/{theorem_id}` | Yes |
| `POST /mip/verify/claim` | Yes |

### UI components
None.

### Tests
- `tests/mip/test_mip_all.py` — **64 passed**
- `tests/mip/validate_mip.py`

### Benchmark results
N/A (MIP-specific benchmarks not separate from EPIC-002)

### Known limitations
- Lean 4, Coq, Isabelle not installed — formal compile endpoints simulate success.
- `mip_conjectures` table missing on fresh DB — conjectures generated but not persisted (warning logged).
- Domain queries return empty without prior ingest.

### Workflow demonstration
```
POST /mip/conjecture/generate {"count":2} → 200 (5 conjectures returned)
GET /mip/knowledge/domain/algebra → 200 {"count":0,"entities":[]}
```

---

## 11. Scientific Capability Evaluation Platform (EPIC-002 / SCEP)

**Status:** Fully implemented

### Source files
- `axiom/evaluation/frameworks/evidence.py` (S0-E4 evidence gate)
- `axiom/evaluation/frameworks/capability.py`
- `axiom/evaluation/frameworks/prize_readiness.py`
- `axiom/evaluation/benchmarks/suite.py`
- `axiom/evaluation/reporting/delta_report.py`
- `axiom/services/api_gateway/routes/eval_api.py`

### APIs
| Endpoint | Auth | Verified |
|----------|------|----------|
| `GET /eval/scores` | No | 200 — 8 dimensions with `evidence_state` |
| `GET /eval/prize-readiness` | No | 200 — 6 Millennium problems ranked |
| `GET /eval/history` | No | 200 |
| `POST /eval/run` | No | 200 — composite **0.944** |

### UI components
None (scores referenced on landing page copy only).

### Tests
- `tests/test_eval_api.py` (5 tests)
- `tests/test_evaluation_platform.py` (9 tests)
- `tests/test_s0_e4_evidence_gate.py` (5 tests)
- `tests/test_scep_e2e.py` (8 tests)
- `tests/test_benchmark.py` (10 tests)

### Benchmark results
Latest verified run (`POST /eval/run`, 2026-08-07):

| Dimension | Score | evidence_state | benchmark_count |
|-----------|------:|----------------|----------------:|
| mathematical_reasoning | 1.0 | measured | 10 |
| proof_verification | 1.0 | measured | 10 |
| conjecture_generation | 1.0 | measured | 10 |
| knowledge_quality | 0.8 | measured | 10 |
| counterexample_search | 1.0 | measured | 10 |
| research_planning | 1.0 | measured | 10 |
| literature_synthesis | 0.6 | measured | 10 |
| research_productivity | 1.0 | measured | 10 |
| **Composite** | **0.944** | | |

Delta report: `benchmark_results.json`

### Known limitations
- Benchmarks use symbolic/heuristic checks, not competition-level problem solving.
- Literature synthesis and knowledge quality regressions detected vs prior snapshot.
- Scores stored in SQLite `eval_runs` table; no cross-run provenance linking (H1-OBS gap).

---

## 12. Mathematical Discovery Engine (MDE)

**Status:** Partially implemented

### Source files
- `axiom/core/retrieval/engine.py`
- `axiom/services/api_gateway/routes/mde.py`

### APIs
| Endpoint | Mounted | Verified |
|----------|---------|----------|
| `GET /mde/retrieval` | Yes | 200 — returns matched theorems for `x^2+y^2=z^2` |
| Other MDE routes expected by e2e | **No** | 26 e2e failures reference missing MDE surface |

### Tests
- `tests/test_mde_ontology.py` (18 tests)
- E2E MDE scenarios — many fail

### Benchmark results
N/A

### Known limitations
- Only retrieval endpoint mounted; e2e suite expects broader MDE API (problems, claims, snapshots).
- Requires `query_formula` parameter (not `query`).

### Workflow demonstration
```
GET /mde/retrieval?query_formula=x^2+y^2=z^2 → 200 (matched theorems including thm_add_comm)
```

---

## 13. Research Workspace

**Status:** Partially implemented

### Source files
- `axiom/research/store.py`, `schema.py`, `migrations.py`
- `axiom/research/pdf_extractor.py`, `summarizer.py`, `qa.py`
- `axiom/services/api_gateway/routes/research.py`
- `axiom/services/model_gateway/client.py`

### APIs
| Endpoint | Auth | Verified |
|----------|------|----------|
| `POST /research/projects` | Bearer | 201 |
| `GET /research/projects` | Bearer | Yes |
| `GET/PUT /research/projects/{id}` | Bearer | Yes |
| `POST /research/projects/{id}/documents/upload` | Bearer | PDF only — 400 for `.txt` |
| `POST /research/projects/{id}/documents/{doc_id}/summarize` | Bearer | Yes (requires PDF) |
| `POST /research/projects/{id}/ask` | Bearer | 422 without uploaded PDF |
| `GET /research/search` | Bearer | 200 |
| Notes, conversations, sessions | Bearer | Implemented in routes |

### UI components
- `ui/src/app/research/page.tsx` — present; not verified wired to API in this review.

### Tests
- `tests/test_research_workspace.py` — **15 tests** (pass when run in isolation)

### Benchmark results
N/A

### Known limitations
- **PDF-only upload** — text files rejected with 400.
- Q&A requires at least one PDF document.
- No per-user tenancy; shared SQLite store.
- ModelClient may return mock responses without configured LLM backend.

### Workflow demonstration
```
POST /research/projects → 201
POST .../documents/upload (text/plain) → 400 "Only PDF files are supported"
POST .../ask → 422 "Upload at least one PDF before asking questions"
GET /research/search?q=Wiles → 200 []
```

---

## 14. Research Validation Program (RVP)

**Status:** Fully implemented

### Source files
- `axiom/research_validation/` (models, dataset, engine, scoring, store, dashboard, pipeline, reproducibility, reports)
- `axiom/services/api_gateway/routes/research_validation.py`
- `data/known_answer_problems.json` (266 problems)
- `scripts/run_research_validation.py`

### APIs
| Endpoint | Verified |
|----------|----------|
| `GET /rvp/stages` | 200 — stages 0–6 |
| `GET /rvp/problems` | Yes |
| `GET /rvp/dashboard` | 200 after first run (requires `rvp_runs` table) |
| `POST /rvp/runs` | 200 — 10 runs Stage 0 |
| `GET /rvp/runs/{run_id}` | Yes |
| `POST /rvp/runs/replay` | Yes |
| `POST /rvp/reports/generate` | Yes |

### UI components
None.

### Tests
- `tests/test_research_validation.py` — **6 passed**

### Benchmark results (`make research-validation`, 2026-08-07)
- Dataset: **266** known-answer problems
- Stage 0 batch: **10/10 passed**, mean answer score **1.000**
- Overall success rate: **96.2%** (52 runs) per `BENCHMARK_RESULTS.md`
- Research Capability composite: **~0.705** per `CAPABILITY_SCORE.md`

### Known limitations
- `/rvp/dashboard` crashes with `no such table: rvp_runs` on completely uninitialized DB until first `POST /rvp/runs`.
- Stage 1 mean answer score 0.651 — 2 failures below threshold.
- LLM-backed runs expected to improve reasoning/literature dimensions (stated in reports, not verified with live LLM in this review).

### Workflow demonstration
```
GET /rvp/stages → 200
POST /rvp/runs {"stages":[0],"max_problems_per_stage":5} → 200 (10 runs)
GET /rvp/dashboard → 200
```

---

## 15. Engineering Governance System

**Status:** Fully implemented

### Source files
- `axiom/governance/` (9 collectors, council, scoring, reports)
- `scripts/run_engineering_review.py`

### APIs
None (CLI/Makefile driven).

### UI components
None.

### Tests
- `tests/test_governance.py` — **6 passed**

### Benchmark results (`make engineering-health`, 2026-08-07)

| Score | Value |
|-------|------:|
| Engineering Health | 70.2 |
| Product Health | 31.1 |
| Research Capability | 20.4 |
| Technical Debt | 95.0 |
| Security | 26.0 |

Reports: `ENGINEERING_HEALTH.md`, `PRODUCT_HEALTH.md`, `RESEARCH_HEALTH.md`, `TECH_DEBT_BOARD.md`, `TOP_25_PRIORITIES.md`

### Known limitations
- Scores are heuristic composites from collectors, not external audits.
- CI workflow `.github/workflows/governance.yml` exists but not re-run in this verification.

---

## 16. Workflow Engine

**Status:** Architecture only (code exists, not mounted)

### Source files
- `axiom/workflow/` (engine, executor, scheduler, workers, checkpoints, artifacts)
- `axiom/services/api_gateway/routes/workflow_router.py`

### APIs
| Endpoint | Mounted |
|----------|---------|
| `/workflows/*` | **No** — verified 404 |

### Tests
- No dedicated `tests/test_workflow*.py` found.
- Demo script: `axiom/workflow/demos/gnn_paper_research.py`

### Known limitations
- Router documented but not included in `main.py`.
- Cannot be exercised via HTTP in current deployment.

---

## 17. Research Loop

**Status:** Not present on verified branch

### Source files
- `axiom/research_loop/` — **directory absent** on this branch

### APIs
| Endpoint | Verified |
|----------|----------|
| `/research-loop/runs` | 404 |

### Known limitations
- Implementation exists only on separate branch (`origin/cursor/milestone-005-research-loop-dc7e` per prior investigation); not part of verified codebase.

---

## 18. Web UI (Next.js)

**Status:** Prototype

### Source files
- `ui/src/app/page.tsx` — landing/marketing
- `ui/src/app/research/page.tsx`
- `ui/src/app/workspace/page.tsx`
- `ui/src/app/layout.tsx`

### APIs
None consumed in verified build.

### Tests
None found.

### Build verification
```
npm run build → FAILED
Error: Event handlers cannot be passed to Client Component props (page "/")
```

### Known limitations
- Production build fails on landing page.
- No `/login`, `/demo`, or live API integration pages verified.
- Three static/marketing routes only.

---

## 19. Observability

**Status:** Fully implemented

### Source files
- `axiom/observability/logger.py`
- `axiom/observability/metrics.py`
- `axiom/core/events/bus.py`

### APIs
- `GET /metrics` — Prometheus format
- `GET /events` — recent event bus history (auth required)

### Tests
Exercised via API middleware in integration tests.

### Known limitations
- In-process metrics only; Grafana provisioning incomplete per governance report.

---

## Demonstrated Workflows Summary

| Workflow | Steps verified | Result |
|----------|----------------|--------|
| EPIC-002 benchmark | `POST /eval/run` → `GET /eval/scores` | **Pass** — composite 0.944 |
| RVP Stage 0 | `POST /rvp/runs` → `GET /rvp/dashboard` | **Pass** |
| MDE retrieval | `GET /mde/retrieval?query_formula=...` | **Pass** |
| MIP conjecture | `POST /mip/conjecture/generate` | **Pass** (no DB persist) |
| Research project CRUD | `POST /research/projects` | **Pass** |
| Research PDF Q&A | upload → summarize → ask | **Blocked** — PDF required |
| arXiv ingest | `POST /ingest` | **Fail** — arXiv 404 for test ID |
| Workflow engine | `GET /workflows` | **Not mounted** — 404 |
| UI production build | `npm run build` | **Fail** |

---

*This document reports only verified implementation as of 2026-08-07. Re-run `pytest`, `make engineering-health`, `make research-validation`, and API smoke tests to refresh evidence.*
