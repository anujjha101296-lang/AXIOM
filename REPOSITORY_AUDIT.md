# AXIOM Labs — Repository Audit

**Auditor role:** Chief Technology Officer (onboarding)  
**Audit date:** 2026-08-06  
**Repository:** AXIOM — Autonomous eXploration of Ideas, Observations & Models  
**Version:** 0.2.0  
**Branch audited:** `main` @ `ee12816` (plus working-tree inspection)

---

## Executive summary

AXIOM is a **substantial early-stage research-engineering monorepo** with a Python/FastAPI backend (~79 source files, ~20K LOC), a Next.js 16 frontend, an extensive pytest suite (~350 test functions across 16 files), and a mature **operating system** under `.axiom/`. The repository's ambition — an AI workspace for frontier mathematical and scientific research with formal verification and objective capability measurement — is reflected in real code, not only documentation.

However, the repository **cannot currently claim a trustworthy engineering baseline**. Three independent P0 defects prevent `make test` and CI from running reliably: a root-level `pytest.py` that shadows the real pytest package, a syntax error in `axiom/evaluation/prize_readiness.py`, and a misconfigured `ruff.toml`. Until these are fixed and a full test run is recorded, all "tests passing" claims in agent artifacts and gate documents are **unverified**.

The highest-priority engineering task is **S0-E2 (revised): restore a green, reproducible test baseline** — not feature expansion.

---

## 1. Repository inventory

### 1.1 Scale and structure

| Metric | Value |
|--------|-------|
| Total files (excl. `.git`) | ~697 |
| Python source files (`axiom/`) | 79 across 32 directories |
| Test files (`tests/`) | 17 Python files |
| UI source (`ui/src/`) | 4 files (App Router: landing + workspace) |
| Documentation (`docs/`) | ~180 Markdown files |
| Agent artifacts (`.agents/`) | 312 files across ~50 agent directories |
| Commits on `main` | 14 |
| Approximate Python + TS LOC | ~24,300 |

### 1.2 Top-level layout

```
/workspace
├── axiom/              # Python platform (core, mip, evaluation, workflow, services)
├── ui/                 # Next.js 16 + React 19 frontend
├── tests/              # pytest suite (unit, integration, e2e, mip)
├── docs/               # Architecture, API, audits, 180 capability delta reports
├── .axiom/             # AXIOM Operating System (constitution, state, queue, contracts)
├── .agents/            # Multi-agent orchestration handoffs and briefings
├── .github/workflows/  # CI (lint+test), CD (API image), security audit
├── deploy/             # Prometheus scrape config only
├── research/           # Research operating plan
├── scripts/            # deploy.sh
├── Dockerfile          # API multi-stage image (Python 3.11-slim)
├── docker-compose.yml  # API + UI + Prometheus + Grafana (partially broken)
├── pyproject.toml      # Poetry spec, pytest/coverage/mypy config
├── pytest.py           # ⚠️ Custom test runner — shadows real pytest
└── [contracts]         # VISION.md, ENGINEERING.md, ARCHITECTURE.md, roadmap.md
```

### 1.3 Git state at audit time

| Item | Status |
|------|--------|
| Branch | `main` (audit branch: `cursor/cto-repository-audit-dc7e`) |
| Modified | `benchmark_results.json` |
| Untracked | 16 new `docs/capability_delta_*.md` files |
| `poetry.lock` | **Missing** — non-reproducible Python installs |
| Remote branches | `origin/main` only |

### 1.4 Commit history (chronological)

| Commit | Summary |
|--------|---------|
| `ee12816` | Initial AXIOM import |
| `d2bfe25` | Sprint 0 — production foundation |
| `4b10300` | Sprint 3 — verification improvements |
| `9b35c2a` | EPIC-001 — Mathematical Intelligence Platform |
| `6dca714` | Engineering operating contract |
| `18b1669` | AXIOM Operating System (`.axiom/`) |
| `1dd87a1` | Session entry point (`AGENTS.md`) |
| `209059a` | Research operating plan |
| `8f54266` | PMO operating cadence |
| `a5df231` | EPIC-002 — Scientific Capability Evaluation Platform |
| `366294d` | Scientific capability + PMO rules |
| `9bebf1e` | Marketing homepage, workspace UI, YC draft, blog post |

---

## 2. What exists

### 2.1 Backend platform (`axiom/`)

| Subsystem | Path | Maturity | Evidence |
|-----------|------|----------|----------|
| **Epistemic Graph Store (EGS)** | `core/knowledge_graph/` | Prototype | SQLite + NetworkX, v4 migrations, Pydantic schemas, tests |
| **Literature ingestion** | `core/parser/` | Prototype | arXiv tarball download, regex LaTeX extraction |
| **Reasoning** | `core/reasoning/` | Prototype | MCTS proof search, hypothesis engine, self-improvement loop |
| **Verification** | `core/verification/` | Prototype | Z3 SMT gateway, Lean 4 exporter |
| **Symbolic math** | `core/symbolic/` | Prototype | SymPy engine with pure-Python fallback |
| **Theorem retrieval (MDE)** | `core/retrieval/` | Prototype | Formula canonicalization, AST scoring |
| **Working memory** | `core/memory/` | Prototype | In-process session state |
| **Event bus** | `core/events/` | Prototype | In-process async pub/sub |
| **MIP (EPIC-001)** | `mip/` | Prototype | Knowledge ontology, Lean/Coq/Isabelle generators, conjecture engine, millennium strategy trees, episodic memory, verification consensus |
| **Evaluation (EPIC-002/SCEP)** | `evaluation/` | Experimental | 8-dimension capability framework, benchmark suite, prize readiness engine, delta reports, CLI runner |
| **Workflow engine** | `workflow/` | Prototype | DAG scheduler, parallel executor, SQLite persistence, 5 worker types — **router not mounted** |
| **API gateway** | `services/api_gateway/` | Prototype | FastAPI, Bearer auth, CORS, metrics; mounts MIP + eval routers |
| **Model gateway** | `services/model_gateway/` | Prototype | OpenAI/Gemini client with SQLite cache and mock fallback |
| **Observability** | `observability/` | Prototype | Structured JSON logging, in-process Prometheus metrics |
| **Configuration** | `config/` | Operational | Pydantic-settings, `.env.example` with 22 variables |

### 2.2 API surface

**Mounted and reachable:**

- System: `/health`, `/ready`, `/metrics`, `/events`, `/self-improve`
- Discovery: `/ingest`, `/query` (stub), `/hypothesize`, `/graph`
- Verification: `/verify/conjecture`, `/verify/proof`
- Memory: `/memory/context`, `/memory/reset`, `/memory/problem`
- Benchmark (legacy): `/benchmark/prize-readiness`
- MIP: `/mip/*` (12 endpoints — largely unauthenticated)
- Evaluation: `/eval/*` (4 endpoints — unauthenticated)

**Implemented but not mounted:**

- `/workflows/*` — full workflow CRUD, run/pause/resume/cancel (`routes/workflow_router.py`)
- `/mde/*` — theorem retrieval (`routes/mde.py`)

### 2.3 Frontend (`ui/`)

| Item | Status |
|------|--------|
| Framework | Next.js 16.3, React 19.2, TypeScript 5, Tailwind CSS v4 |
| Pages | `/` (marketing landing), `/workspace` (interactive research canvas) |
| API integration | 4 endpoints hardcoded to `localhost:8000` (ignores `NEXT_PUBLIC_API_URL`) |
| Components | None — all UI inline in page files (~1,100 LOC) |
| Waitlist form | Non-functional stub |
| Docker | **No `ui/Dockerfile`** — compose stack cannot build UI |

### 2.4 Test suite (`tests/`)

| Category | Files | Approx. tests | Notes |
|----------|-------|---------------|-------|
| Core API/reasoning | 4 | ~40 | Blocked by conftest import chain |
| Epistemic layer / MDE ontology | 2 | ~30 | Schema, migrations, FK constraints |
| Verification improvements | 1 | ~15 | NRA SMT, polynomial identities |
| Legacy benchmark (SCB) | 1 | ~10 | 5-dimension pre-SCEP scorer |
| SCEP / EPIC-002 | 3 | 22 | **Verified passing** in isolation (Python 3.12) |
| MIP | 2 | ~64 | EPIC-001 department suite |
| E2E (MDE features F1–F21) | 4 | ~226 | Many helpers embedded in test files, not production code |

### 2.5 Documentation and governance

| Document | Purpose | Quality |
|----------|---------|---------|
| `.axiom/CONSTITUTION.md` | Governing principles, read order, human-approval gates | Excellent |
| `.axiom/CURRENT_STATE.md` | Operational state (last updated 2026-08-05) | Good — **stale on runtime blocker** |
| `.axiom/TASK_QUEUE.md` | Ranked executable work | Good |
| `.axiom/ROADMAP.md` | Three-track adaptive roadmap | Good |
| `VISION.md`, `ENGINEERING.md`, `ARCHITECTURE.md` | Durable contracts | Good |
| `docs/architecture.md`, `docs/api.md` | Component topology and REST reference | Good but partially stale |
| `docs/scientific_capability_framework.md` | Ratified SCF v1.0 (8 dimensions, L0–L5) | Excellent |
| `docs/audit/EPIC_002_audit.md` | Independent audit with 5 active findings | Excellent |
| `TEST_INFRA.md` | 640-line MDE test methodology spec | Comprehensive |
| `TEST_READY.md` | SCEP sign-off (17/17) | Claims unverified at repo level |
| `.agents/` (312 files) | Agent orchestration artifacts | Valuable history, not operational truth |

### 2.6 Infrastructure and CI/CD

| Component | Status |
|-----------|--------|
| API Dockerfile | Working (Python 3.11-slim, non-root, healthcheck) |
| CD to GHCR | Working — pushes `axiom-api` image on `main` |
| CI lint + test | **Broken** — `ruff.toml` format error |
| UI CI | **Missing** |
| Docker Compose full stack | **Broken** — missing UI Dockerfile, Grafana provisioning |
| Prometheus | Config present, scrapes API metrics |
| Grafana | Referenced but provisioning directory missing |
| Lean 4 in Docker | Not installed despite config references |
| `poetry.lock` | Missing |
| Pre-commit hooks | Configured but `make setup` does not install them |

---

## 3. What is missing

### 3.1 Engineering baseline (P0)

| Gap | Impact |
|-----|--------|
| Green full test suite | No trustworthy regression signal |
| `poetry.lock` or pinned requirements | Non-reproducible dependency resolution |
| Working `make test` / CI | Cannot gate merges |
| UI Dockerfile + Grafana provisioning | Full-stack deploy broken |
| UI CI pipeline | Frontend regressions undetected |
| Mounted workflow and MDE routers | Implemented capability unreachable via HTTP |
| `POST /query` implementation | Advertised retrieval endpoint returns empty results |
| `mip/counterexample/` and `mip/proof/` | Empty packages; E2E tests expect functionality |
| Lean 4 / Coq / Isabelle in CI or Docker | All formal verification is simulation |
| Persistent `baseline_epic001` eval snapshot | Delta comparisons drift (audit Finding 4) |
| PR template | Referenced in CONTRIBUTING, absent |
| Dependabot / Renovate | No automated dependency updates |

### 3.2 Product (Track B)

| Gap | Impact |
|-----|--------|
| Functional waitlist / lead capture | Landing page CTA is a stub |
| API URL configuration in UI | Docker env var ignored |
| Auth token mismatch | UI defaults `test_token`, backend expects `axiom-dev-token` |
| Remaining API surfaces in UI | `/hypothesize`, `/eval/*`, `/mip/*` not exposed |
| User onboarding, docs site | No product documentation beyond API reference |
| Measured user validation | Zero recorded early-user conversations |

### 3.3 Research integrity (Track A)

| Gap | Impact |
|-----|--------|
| Compiler-backed proof verification | Structural simulation only |
| Dynamic benchmark parameterization | Static cases vulnerable to memorization |
| `estimated=True` metadata on fallback scores | Synthetic floors inflate capability claims |
| Live zeta zero verification suite | RH readiness marked DISPUTED in audit |
| Corpus-scale ingest quality metrics | arXiv parser precision/recall unmeasured |
| Reproducible run/provenance records | Evaluation runs lack full provenance chain |

### 3.4 Company (Track C)

| Gap | Impact |
|-----|--------|
| Production TLS / reverse proxy | No HTTPS configuration |
| Secret management | Default credentials in compose and `.env.example` |
| Real GitHub URL on landing page | Points to `https://github.com` placeholder |
| Institutional pilot readiness | No security questionnaire, SOC2 path, or data handling policy |

---

## 4. Technical debt

### 4.1 Critical (P0 — blocks trustworthy engineering)

| ID | Debt | Location | Risk |
|----|------|----------|------|
| TD-01 | Root `pytest.py` shadows real pytest | `/pytest.py` | `make test`, `python -m pytest` fail silently or collect 0 tests |
| TD-02 | Syntax error in legacy prize scorer | `axiom/evaluation/prize_readiness.py:77` | `def score_all((self)` — blocks conftest import chain |
| TD-03 | `ruff.toml` uses `[tool.ruff]` not `[ruff]` | `/ruff.toml` | CI lint job fails before tests run |
| TD-04 | Formal verification simulation without tier enforcement | `evaluation/benchmarks/suite.py`, `mip/formal/*` | False `TIER_2_PROVEN` claims possible |
| TD-05 | `eval()` on user equation strings | `core/verification/smt_gateway.py` | Code injection on untrusted input |

### 4.2 High (P1 — architectural integrity)

| ID | Debt | Location | Risk |
|----|------|----------|------|
| TD-06 | Dual prize-readiness systems | `prize_readiness.py` (legacy 5-dim) vs `frameworks/prize_readiness.py` (EPIC-002 8-dim) | Inconsistent scores across `/benchmark` and `/eval` |
| TD-07 | Dual working memory | `core/memory/` vs `mip/memory/` | Fragmented session state |
| TD-08 | DB path inconsistency | `settings.db_path` vs `AXIOM_DB_PATH` in MIP router | Split-brain data |
| TD-09 | Unmounted API routers | `workflow_router.py`, `mde.py` | Dead code paths, test/production drift |
| TD-10 | E2E test helpers not in production | `tests/e2e/*.py` | Tests validate imaginary APIs |
| TD-11 | SQLite with 2 uvicorn workers | `Dockerfile` CMD | Concurrency corruption under load |
| TD-12 | Auth split | MIP/eval unauthenticated; core routes Bearer-only | Inconsistent security model |

### 4.3 Medium (P2 — maintainability)

| ID | Debt | Location | Risk |
|----|------|----------|------|
| TD-13 | 180 capability delta reports (16 untracked) | `docs/capability_delta_*.md` | Repo bloat, signal-to-noise collapse |
| TD-14 | 312 agent artifact files | `.agents/` | Onboarding noise; not gitignored |
| TD-15 | Documentation drift | CONTRIBUTING (80% coverage, strict mypy) vs pyproject (70%, loose) | Misleading contributor expectations |
| TD-16 | `ResearcherWorker` stub generation | `workflow/workers/researcher.py` | Fake research output |
| TD-17 | `VerificationConsensus` keyword heuristics | `mip/verification/consensus.py` | Shallow verification |
| TD-18 | No `npm audit` / failing security CI | `.github/workflows/security.yml` | Vulnerabilities never block merges |

### 4.4 Low (P3 — polish)

| ID | Debt | Location |
|----|------|----------|
| TD-19 | Default `ui/README.md` is create-next-app boilerplate | `ui/README.md` |
| TD-20 | External Google Fonts CDN dependency | `ui/src/app/layout.tsx` |
| TD-21 | Codecov upload tokenless | `.github/workflows/ci.yml` |
| TD-22 | EPIC_002_SPEC.md naming collision | Root spec vs SCEP both called EPIC-002 |

---

## 5. Architectural risks

| Risk | Severity | Description | Mitigation direction |
|------|----------|-------------|---------------------|
| **False verification claims** | Critical | Lean/Coq/Isabelle absent → structural simulation can pass invalid proofs | Enforce `TIER_1_SIMULATED` cap; require compiler exit 0 for `TIER_2_PROVEN` |
| **Benchmark gaming** | High | Static test cases in `suite.py` (`mr_001`–`mr_010`) | Dynamic parameterization with random seeds |
| **Synthetic score inflation** | High | Empty DB triggers fallback baselines (~0.30–0.40 floors) | `estimated=True` flag; lock `baseline_epic001` |
| **Test/production divergence** | High | ~226 E2E specs reference unmounted routes and test-embedded helpers | Mount routers or delete/migrate tests to match production |
| **Monolith scaling** | Medium | Single SQLite file, in-process event bus, no queue | Accept for MVP; plan Postgres + job queue before multi-user |
| **Agent-generated artifact trust** | Medium | GATE_STATUS.md claims PASS; repo cannot run full suite | Re-verify all gates after baseline fix |
| **Capability delta noise** | Medium | 180 reports, many +0% deltas | Archive to artifact store; commit only milestone deltas |
| **Security defaults in production path** | Medium | `axiom-dev-token`, `axiom-admin` Grafana password in compose | Fail deploy on default secrets; use secret manager |

---

## 6. Dependency and runtime matrix

| Component | Declared | CI | Docker | Cloud agent VM |
|-----------|----------|-----|--------|----------------|
| Python | ^3.10 | 3.11 | 3.11-slim | 3.12.3 |
| FastAPI | ^0.100 | pip float | pinned in Dockerfile | installed |
| Pydantic | ^2.5 | pip float | pinned | v2 |
| Next.js | 16.3.0 | not tested | N/A (no Dockerfile) | not tested |
| Z3 | ^4.12 | pip | pip | available |
| Lean 4 | config only | absent | absent | absent |
| Coq / Isabelle | code only | absent | absent | absent |

---

## 7. Verification performed during audit

| Check | Result |
|-------|--------|
| Read `.axiom/` operating contracts (all 14 files) | Complete |
| Read root contracts (`VISION`, `ENGINEERING`, `ARCHITECTURE`, `roadmap`) | Complete |
| Inventory all 697 non-git files | Complete |
| Inspect all 79 `axiom/` Python modules (via structure + key file reads + subagent analysis) | Complete |
| Inspect all 17 test files and 4 e2e suites | Complete |
| Inspect UI (4 source files) | Complete |
| Inspect CI/CD (3 workflows), Dockerfile, compose | Complete |
| Inspect 312 `.agents/` artifacts (pattern + key orchestrator files) | Complete |
| Sample 180 `docs/capability_delta_*` reports | Pattern verified |
| Run SCEP tests in isolation | **22/22 passed** |
| Run full `pytest tests/` | **Failed** — pytest shadowing + conftest syntax error |
| Run `ruff check` | **Failed** — `ruff.toml` format |
| Python version check | 3.12.3 available (supersedes stale 3.9.6 blocker in `.axiom/CURRENT_STATE.md`) |

---

## 8. Highest-priority engineering task

### S0-E2 (revised): Restore a trustworthy, reproducible test baseline

**Why this outranks everything else:** Without a green CI and `make test`, no capability score, gate status, sprint completion claim, or audit finding resolution can be verified. The organization's constitution explicitly requires evidence over theater.

**Acceptance criteria:**

1. Remove or rename root `pytest.py` so the real pytest package is importable from the repository root.
2. Fix syntax error in `axiom/evaluation/prize_readiness.py:77`.
3. Fix `ruff.toml` section headers (`[ruff]` not `[tool.ruff]`).
4. Add `poetry.lock` or `requirements-lock.txt` for reproducible installs.
5. Run full `pytest tests/ -v --cov=axiom --cov-fail-under=70` on Python 3.11+ and record results in `.axiom/MEMORY.md`.
6. Fix or quarantine failing tests with documented owners (do not delete failing tests silently).
7. Restore CI to green on `main`.

**Estimated scope:** Small diff (3–5 file fixes) + test triage. The hard part is honestly recording what passes vs. what was previously claimed.

---

## 9. Audit conclusions

**Strengths:**

- Genuine technical depth — this is not a slide-deck repo.
- Evaluation-first culture codified in SCF, SCEP, and independent audit.
- Operating system (`.axiom/`) provides durable organizational memory.
- Three-track execution model (Research / Product / Company) is coherent.
- EPIC-001 (MIP) and EPIC-002 (SCEP) represent real, testable subsystems.

**Weaknesses:**

- Engineering baseline is broken despite documented "complete" gate statuses.
- Significant gap between test specifications (~350 tests, 226 MDE E2E specs) and production API surface.
- Formal verification is largely simulated; prize readiness scores must be treated as internal hypotheses only.
- Infrastructure for full-stack deploy and CI is incomplete.

**Recommendation to leadership:** Do not authorize external scientific claims, investor-facing capability numbers, or production deployment until S0-E2 is complete and S0-E3 (verification truthfulness audit) passes with regression tests.

---

*This audit is read-only. No code was modified. Operational state documents (`.axiom/CURRENT_STATE.md`, `.axiom/TASK_QUEUE.md`) should be updated after S0-E2 completion.*
