# AXIOM Repository Structure

Reference for contributors. For onboarding steps, see `CONTRIBUTOR_GUIDE.md`.

---

## Top-Level Layout

| Path | Purpose |
|------|---------|
| `axiom/` | Python application (installable package) |
| `ui/` | Next.js frontend |
| `tests/` | pytest test suite |
| `docs/` | Human documentation, ADRs, demo assets |
| `.axiom/` | Operating system — state, queue, roadmap (read before major work) |
| `demo/` | Golden Demo sample dataset (not runtime code) |
| `scripts/` | Shell utilities and demos |
| `deploy/` | Prometheus/Grafana config fragments |
| `.github/` | CI/CD workflows, PR template, Dependabot |

---

## Python Package (`axiom/`)

### `axiom/config/`
- `settings.py` — Pydantic `BaseSettings`; reads `.env`
- Single source for `DB_PATH`, `JWT_SECRET_KEY`, `CORS_ORIGINS`, etc.

### `axiom/core/`
Mathematical intelligence primitives (EPIC-001 foundation).

| Submodule | Responsibility |
|-----------|----------------|
| `knowledge_graph/` | SQLite + NetworkX epistemic graph |
| `parser/` | arXiv/LaTeX parsing |
| `reasoning/` | MCTS, hypothesis engine, self-improvement |
| `memory/` | Session working memory |
| `verification/` | SMT gateway, Lean exporter, **truthfulness** |
| `retrieval/` | Theorem retrieval engine (MDE backend) |
| `events/` | Internal event bus |

### `axiom/services/`
HTTP and external adapters.

| Submodule | Responsibility |
|-----------|----------------|
| `api_gateway/` | FastAPI app, route modules, auth |
| `model_gateway/` | LLM client with mock fallback |

**Route modules** (`api_gateway/routes/`):
- `research.py` — Research Workspace
- `research_loop.py` — Autonomous loop
- `demo.py` — Golden Demo (public)
- `mip.py`, `mde.py`, `eval_api.py`, `auth_api.py`, `workflow_router.py`

### `axiom/research/`
Research Workspace vertical slice: projects, PDF extract, notes, FTS, Q&A, sessions.

### `axiom/research_loop/`
Milestone 005 closed-loop orchestration: workers, failure memory, benchmarks.

### `axiom/workflow/`
Generic DAG workflow engine (used by research loop). **Needs more tests** — see `tests/test_workflow_models.py`.

### `axiom/evaluation/`
SCEP (EPIC-002): benchmark suites, capability scoring, prize readiness.

### `axiom/mip/`
Mathematical Intelligence Platform: knowledge, formal adapters, conjecture, strategy.

### `axiom/demo/`
Curated Golden Demo payload — **Demo Mode only**, not live inference.

### `axiom/modes.py`
Demo vs Research operation mode contracts.

### `axiom/observability/`
Structured logging (`logger.py`) and Prometheus metrics (`metrics.py`).

---

## Frontend (`ui/`)

| Path | Route | Mode |
|------|-------|------|
| `src/app/page.tsx` | `/` | Landing |
| `src/app/demo/` | `/demo` | **Demo Mode** |
| `src/app/research/` | `/research` | **Research Mode** |
| `src/app/research/runs/` | `/research/runs` | **Research Mode** |
| `src/app/login/` | `/login` | Auth |
| `src/app/workspace/` | `/workspace` | Graph canvas (partial) |
| `src/components/OperationModeBanner.tsx` | — | Mode honesty banner |
| `src/lib/api.ts` | — | API helpers |
| `src/lib/modes.ts` | — | Mode type definitions |

---

## Tests (`tests/`)

| Pattern | Purpose |
|---------|---------|
| `test_*.py` | Core unit/integration (CI gate) |
| `e2e/test_*.py` | Extended API surface tests |
| `conftest.py` | Shared fixtures (`empty_store`, `seeded_store`) |
| `mip/test_mip_all.py` | MIP integration tests |

**CI runs:** `tests/` excluding `tests/e2e/`.

---

## Configuration Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | Poetry metadata, pytest, ruff, mypy, coverage |
| `Makefile` | Developer command shortcuts |
| `.env.example` | Environment variable template |
| `docker-compose.yml` | Local stack orchestration |
| `Dockerfile` | API container (UI Dockerfile pending) |

---

## Documentation Map

| Doc | Audience |
|-----|----------|
| `CONTRIBUTOR_GUIDE.md` | New engineers (day 1) |
| `CONTRIBUTING.md` | Commit/PR conventions |
| `ARCHITECTURE_DECISION_RECORDS/` | Design decision history |
| `docs/MODES.md` | Demo vs Research policy |
| `docs/OBSERVABILITY.md` | Logging and metrics |
| `docs/SECURITY.md` | Security review checklist |
| `.axiom/CURRENT_STATE.md` | Live project status |
