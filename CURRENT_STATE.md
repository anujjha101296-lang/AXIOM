# AXIOM Labs — Current State

**Document type:** CTO onboarding snapshot (repository-level)  
**Date:** 2026-08-06  
**Supersedes for audit purposes:** `.axiom/CURRENT_STATE.md` (2026-08-05) on runtime blocker status  
**Authoritative operational source:** `.axiom/` directory for day-to-day execution

---

## One-line summary

AXIOM is a **real but unverified** research-engineering platform at v0.2.0 with substantial Python backend, prototype UI, and evaluation infrastructure — blocked from claiming engineering baseline by three fixable P0 defects in the test toolchain.

---

## Organization and mission

| Item | State |
|------|-------|
| Entity | AXIOM Labs |
| Mission | Build systems that measurably increase humanity's ability to solve hard problems |
| Initial wedge | Mathematical intelligence (knowledge graph, formal verification, capability evaluation) |
| First product thesis | AI workspace for frontier mathematical and scientific research |
| Execution model | Three parallel tracks: Research (A), Product (B), Company (C) |
| Governance | `.axiom/CONSTITUTION.md` — humans retain authority over external/irreversible actions |

---

## Repository health dashboard

| Signal | Status | Evidence |
|--------|--------|----------|
| Code exists and is substantial | ✅ | 79 Python files, ~24K LOC, 14 commits |
| Operating system initialized | ✅ | 14 files in `.axiom/` |
| Engineering contracts committed | ✅ | `VISION.md`, `ENGINEERING.md`, `ARCHITECTURE.md`, `roadmap.md` |
| Full test suite runnable | ❌ | `pytest.py` shadow + `prize_readiness.py` syntax error |
| CI green | ❌ | `ruff.toml` format blocks lint job |
| Docker full stack | ❌ | Missing `ui/Dockerfile`, Grafana provisioning |
| Formal verification real | ❌ | Lean/Coq/Isabelle not installed; simulation active |
| SCEP evaluation framework | ✅ (isolated) | 22/22 SCEP tests pass when run individually |
| UI functional for demo | ✅ (local) | Landing page + workspace canvas with 4 API integrations |
| Production deployable | ❌ | Multiple infrastructure gaps |
| External user validation | ❌ | No recorded users or conversations |

---

## What is built and working (verified this audit)

### Backend

- FastAPI gateway with health, readiness, metrics, and Swagger docs
- Epistemic Graph Store with versioned SQLite migrations (v4)
- arXiv paper ingestion with LaTeX parsing
- Z3 SMT counterexample verification (with grid fallback)
- MCTS proof search with Lean 4 script export
- Hypothesis/conjecture generation engine
- MIP platform: knowledge ontology, formal script generators, conjecture strategies, millennium problem decomposition, episodic memory, verification consensus
- SCEP: 8-dimension capability framework, benchmark suite, prize readiness engine, delta report generator, `/eval/*` API
- Workflow engine with DAG scheduler (code complete, router unmounted)
- Model gateway with OpenAI/Gemini/mock support

### Frontend

- Marketing landing page with feature grid, roadmap, mission, metrics
- Research workspace with force-directed knowledge graph, ingest panel, SMT verify, MCTS proof search

### Infrastructure

- API Docker image builds and pushes to GHCR
- Prometheus scrape configuration
- Makefile with dev/test/lint/docker targets
- `.env.example` with 22 configuration variables

### Governance and documentation

- AXIOM Operating System (constitution, task queue, roadmap, domain contracts)
- Scientific Capability Framework v1.0 (ratified)
- Independent EPIC-002 audit with 5 active findings
- Research operating plan, PMO cadence, YC application draft

---

## What is blocked

### P0 — Engineering baseline (S0-E2, revised)

The original blocker (Python 3.9.6) is **resolved** in the cloud agent environment (Python 3.12.3 available). Three new blockers prevent a trustworthy baseline:

| Blocker | File | Fix complexity |
|---------|------|----------------|
| Root `pytest.py` shadows real pytest | `/pytest.py` | Trivial (rename) |
| Syntax error in legacy prize scorer | `axiom/evaluation/prize_readiness.py:77` | Trivial (one character) |
| `ruff.toml` wrong section header | `/ruff.toml` | Trivial (rename section) |

Until fixed: `make test`, `make lint`, and CI are non-functional. All prior "gate PASS" claims are unverified.

### P0 — Verification truthfulness (S0-E3)

Blocked on S0-E2. Simulation fallbacks can produce results indistinguishable from formal proofs without tier enforcement.

### P1 — EPIC-002 integration gate (S0-E4)

Blocked on S0-E2 and S0-E3. Legacy and SCEP prize readiness systems coexist with inconsistent semantics.

---

## Active workstreams (from `.axiom/TASK_QUEUE.md`)

| Rank | ID | Task | Status |
|------|-----|------|--------|
| 1 | S0-E2 | Python 3.10+ runtime + full test suite | **Blocked** (revised blockers above) |
| 2 | P0-WEB | Public landing experience | In progress (landing page exists; waitlist stub) |
| 3 | R0-PLAN | Researcher workflow + benchmark program | In progress |
| 4 | C0-PMO | PMO cadence | In progress |
| 5 | S0-E3 | Verification truthfulness audit | Ready after S0-E2 |
| 6 | S0-E4 | EPIC-002 integration gate | Deferred |
| 7 | H1-OBS | Evaluation provenance records | Deferred |

---

## Capability maturity (honest assessment)

| Capability | Maturity | Limitation |
|------------|----------|------------|
| Epistemic graph storage | Prototype | No corpus-scale validation |
| Literature ingestion | Prototype | Regex parsing; precision/recall unknown |
| SMT verification | Prototype | Works for bounded cases; `eval()` security risk |
| Lean proof export | Prototype | Compilation usually simulated |
| MCTS proof search | Prototype | Regex rewrites, not Mathlib-informed |
| MIP formal adapters | Prototype | Lean/Coq/Isabelle simulation fallback |
| Conjecture generation | Prototype | Template strategies; novelty unmeasured |
| Scientific capability evaluation | Experimental | SCEP framework complete; baseline unverified |
| Prize readiness scoring | Experimental | Audit-grounded RH score: 38/100 (DISPUTED) |
| Research workspace UI | Prototype | 4 of 30+ API endpoints integrated |
| Workflow automation | Idea | Engine built; not exposed via API |
| Production deployment | Idea | API image only; no UI, no TLS |

---

## Git and artifact state

| Item | Value |
|------|-------|
| Branch | `main` @ `ee12816` |
| Modified files | `benchmark_results.json` |
| Untracked files | 16 `docs/capability_delta_*.md` |
| Total capability delta reports | 180 (repo bloat risk) |
| Agent artifacts | 312 files in `.agents/` |
| Database | `axiom.db` (147 KB, present in workspace) |

---

## Test status (audit-verified)

| Suite | Result | Method |
|-------|--------|--------|
| SCEP (`test_evaluation_platform` + `test_scep_e2e` + `test_eval_api`) | **22/22 passed** | Individual file execution, Python 3.12 |
| Full `pytest tests/` | **Not runnable** | pytest shadowing |
| Core API tests | **Not run** | conftest blocked by syntax error |
| E2E MDE tests (~226) | **Not run** | Not in CI |
| MIP tests (~64) | **Not run** | conftest blocked |

---

## Security posture

| Control | Status |
|---------|--------|
| Auth on core API routes | Bearer token (default: `axiom-dev-token`) |
| Auth on MIP/eval routes | **None** |
| Secrets in source | Grafana password in compose; JWT placeholder in `.env.example` |
| Input sanitization | Pydantic validation; `eval()` in SMT is exception |
| TLS | Not configured |
| Security CI gate | Non-blocking (`pip-audit \|\| true`) |

---

## Key decisions needed from leadership

| Decision | Options | Urgency |
|----------|---------|---------|
| Authorize S0-E2 fix sprint | Yes / defer | **Immediate** — blocks all engineering credibility |
| Deprecate legacy prize scorer | Yes / fix in place | High — causes import failures |
| Mount workflow + MDE routers | Yes / defer / delete | Medium — after baseline |
| Commit capability delta reports | Milestone only / gitignore / archive | Medium — repo hygiene |
| Authorize Lean 4 in Docker (EPIC-003) | Yes / defer | Medium — resolves CRITICAL audit finding |
| External positioning | Wait for baseline / proceed with landing | Low — landing exists as internal draft |

---

## Highest priority

**S0-E2 (revised): Restore a trustworthy, reproducible test baseline.**

Fix the three P0 toolchain defects, run the full suite, record honest results, restore CI to green. No feature work, no capability claims, no external positioning until this is complete.

See `NEXT_90_DAYS.md` for the full engineering sequence.

---

## Document relationships

| Document | Role |
|----------|------|
| `.axiom/CURRENT_STATE.md` | Operational source of truth (update after each cycle) |
| `CURRENT_STATE.md` (this file) | CTO audit snapshot; may diverge until reconciled |
| `REPOSITORY_AUDIT.md` | Full repository inventory and debt register |
| `ARCHITECTURE_AUDIT.md` | System topology, risks, and architectural decisions |
| `NEXT_90_DAYS.md` | Prioritized engineering and product plan |

---

*Last verified: 2026-08-06 by CTO onboarding audit. No code was modified during this assessment.*
