# AXIOM Contributor Guide

Welcome. This guide helps a new engineer clone AXIOM, understand the repository, and contribute productively **within one day**.

**Read first:** `.axiom/CONSTITUTION.md` → `.axiom/CURRENT_STATE.md` → this document.

---

## Day 1 Checklist

| Step | Time | Action |
|------|------|--------|
| 1 | 15 min | Clone, run `make setup`, copy `.env.example` → `.env` |
| 2 | 15 min | Read [Repository structure](#repository-structure) and [Architecture](#architecture-at-a-glance) |
| 3 | 20 min | Run `make test-core` and `make dev` — confirm API at http://localhost:8000/docs |
| 4 | 15 min | Run UI: `make dev-ui` — visit `/demo` (Demo Mode) and `/research` (Research Mode) |
| 5 | 20 min | Read `docs/MODES.md` — understand Demo vs Research honesty policy |
| 6 | 30 min | Pick a [good first issue](#good-first-contributions) area; read relevant ADR in `docs/adr/` |
| 7 | — | Open a PR using the template; ensure `make check` passes |

---

## Prerequisites

| Tool | Version | Verify |
|------|---------|--------|
| Python | 3.10+ (3.11 recommended) | `python3 --version` |
| Node.js | 18+ | `node --version` |
| npm | 9+ | `npm --version` |
| git | 2.x | `git --version` |
| make | any | `make help` |

Optional: Docker (for `make docker-up`), Lean 4 (for formal proof adapters).

---

## Quick Start

```bash
git clone https://github.com/anujjha101296-lang/AXIOM.git
cd AXIOM
make setup
cp .env.example .env   # edit JWT_SECRET_KEY for local dev

# Terminal 1 — API
make dev

# Terminal 2 — tests (core suite, ~3s)
make test-core

# Terminal 3 — UI (optional)
make setup-ui && make dev-ui
```

**Verify:** `curl http://localhost:8000/health` → `{"status":"ok"}`

---

## Repository Structure

```
AXIOM/
├── axiom/                    # Python application package
│   ├── config/               # Pydantic settings (settings.py)
│   ├── core/                 # Domain: graph, parser, reasoning, verification
│   ├── demo/                 # Golden Demo curated data (Demo Mode only)
│   ├── evaluation/           # SCEP benchmarks, prize readiness
│   ├── mip/                  # Mathematical Intelligence Platform
│   ├── modes.py              # Demo vs Research mode contracts
│   ├── observability/        # Logging + Prometheus metrics
│   ├── research/             # Research Workspace (PDF, notes, Q&A)
│   ├── research_loop/        # Autonomous research loop v1
│   ├── services/
│   │   ├── api_gateway/      # FastAPI app + route modules
│   │   └── model_gateway/    # LLM client (mock fallback)
│   └── workflow/             # Generic workflow DAG engine
├── ui/                       # Next.js 16 frontend
├── tests/                    # pytest suite
│   ├── conftest.py           # Shared fixtures
│   ├── test_*.py             # Core unit/integration tests
│   └── e2e/                  # Extended MDE API tests (26 known failures)
├── docs/
│   ├── adr/                  # Architecture Decision Records
│   ├── demo/                 # Golden Demo presenter assets
│   └── MODES.md              # Demo vs Research policy
├── .axiom/                   # Operating system (state, queue, roadmap)
├── scripts/                  # Demo and utility scripts
├── .github/workflows/        # CI/CD
├── Makefile                  # Developer commands (start here)
├── pyproject.toml            # Python deps, pytest, ruff, coverage
└── docker-compose.yml        # API + UI + Prometheus + Grafana
```

See `docs/REPOSITORY_STRUCTURE.md` for module-level detail.

---

## Architecture at a Glance

```
Clients (Next.js UI)
        ↓
FastAPI API Gateway  — auth, validation, /metrics
        ↓
Domain services      — research, research_loop, mip, evaluation, workflow
        ↓
SQLite + adapters    — graph store, ModelClient, Z3, Lean/Coq
```

**Key boundaries:**
- **Interfaces** (`services/api_gateway/routes/`) — HTTP only; no business logic
- **Domain** (`core/`, `research/`, `mip/`) — logic; no UI imports
- **Evidence** — verification truthfulness (`core/verification/truthfulness.py`)
- **Modes** — Demo (`/demo`) vs Research (`/research`); see `docs/MODES.md`

**ADRs:** Important design decisions live in `ARCHITECTURE_DECISION_RECORDS/`. Read before changing auth, verification labels, or mode contracts.

---

## Development Commands

```bash
make help           # All targets
make setup          # Python deps
make setup-ui       # npm install in ui/
make dev            # API with hot reload (:8000)
make dev-ui         # Next.js (:3000)
make test-core      # Fast core tests (excludes e2e)
make test-e2e       # Extended e2e (known failures documented)
make test-coverage  # Coverage report (≥70% required)
make lint           # ruff check
make lint-fix       # ruff auto-fix
make format         # ruff format
make type-check     # mypy
make check          # lint + type-check + test-core
make profile        # Performance profile of core tests
make security-audit # pip-audit dependency scan
make docker-up      # Full stack
make clean          # Remove caches
```

---

## Testing

### Core suite (required for every PR)

```bash
make test-core
# Equivalent: PYTHONPATH=. pytest tests/ --ignore=tests/e2e -v
```

**Current baseline:** 193+ tests pass. CI enforces ≥70% coverage on `axiom/`.

### E2E suite (optional / in progress)

```bash
make test-e2e
```

26 failures document the MDE API surface gap — not a blocker for Research Workspace changes. See `MASTER_PROGRESS.md`.

### Writing tests

| Type | Location | Marker |
|------|----------|--------|
| Unit | `tests/test_<module>.py` | — |
| Integration | same file or `test_*_integration.py` | `@pytest.mark.integration` |
| Slow | — | `@pytest.mark.slow` |
| E2E | `tests/e2e/` | `@pytest.mark.e2e` |

Use fixtures from `tests/conftest.py`. Tests use in-memory SQLite via `DB_PATH=:memory:`.

---

## Code Standards

- **Python 3.10+** with type hints on public APIs
- **Pydantic v2** for request/response models
- **ruff** for lint + format (`make lint`, `make format`)
- **Conventional commits:** `feat(scope):`, `fix(scope):`, `docs:`, `test:`, `ci:`
- **Scope examples:** `research`, `demo`, `workflow`, `api`, `ui`, `ci`
- **No secrets** in code — use `.env` (gitignored)
- **No capability inflation** — label simulated/heuristic results honestly

---

## Operation Modes (Required Reading)

AXIOM has two user-facing modes. **Never confuse them.**

| Mode | Route | Scientific capability? |
|------|-------|------------------------|
| Demo Mode | `/demo` | **No** — curated presentation data |
| Research Mode | `/research`, `/research/runs` | Yes — with uncertainty |

When touching UI or API responses, preserve mode banners and disclaimers. See `docs/MODES.md` and ADR-0003.

---

## CI/CD Pipeline

| Workflow | Trigger | What it does |
|----------|---------|--------------|
| `ci.yml` | push/PR to `main`, `cursor/**`, etc. | ruff, mypy, core tests, coverage, UI build |
| `security.yml` | push to `main`, weekly | pip-audit + npm audit |
| `cd.yml` | push to `main`, tags | Docker image to GHCR |

**Before pushing:** `make check` locally.

---

## Observability

- **Logging:** `from axiom.observability.logger import get_logger`
- **Metrics:** `GET /metrics` (Prometheus text format)
- **Config:** `LOG_LEVEL`, `LOG_FORMAT` (json | console)

See `docs/OBSERVABILITY.md`.

---

## Security

- Never commit `.env`, API keys, or JWT secrets
- Use `AXIOM_API_TOKEN` and `JWT_SECRET_KEY` from environment
- Run `make security-audit` before releases
- Report vulnerabilities per `docs/SECURITY.md`

---

## Good First Contributions

Low-risk areas for new contributors:

1. **Tests** — `tests/test_workflow_models.py`, observability, edge cases
2. **Docs** — fix stale references, improve API docs in `docs/api.md`
3. **Technical debt** — e2e skip markers, lint fixes, type hints
4. **S0-E4** — EPIC-002 evidence state on eval scores (see `.axiom/TASK_QUEUE.md`)
5. **UI polish** — Research Mode banners, accessibility, loading states

**Avoid without discussion:** auth/tenancy changes, verification tier labeling, prize-readiness scoring.

---

## Pull Request Process

1. Branch from `main`: `cursor/<topic>-dc7e` or `fix/<topic>`
2. Keep PRs focused — one concern per PR
3. Run `make check`
4. Fill in `.github/pull_request_template.md`
5. Update docs if you change public behavior
6. Update `.axiom/CURRENT_STATE.md` only for significant engineering cycles

---

## Getting Help

| Question | Where to look |
|----------|---------------|
| What should I work on? | `.axiom/TASK_QUEUE.md` |
| Current project state? | `.axiom/CURRENT_STATE.md` |
| Why was X designed this way? | `ARCHITECTURE_DECISION_RECORDS/` |
| API reference? | http://localhost:8000/docs or `docs/api.md` |
| Demo vs Research? | `docs/MODES.md` |
| Engineering rules? | `ENGINEERING.md`, `.axiom/ENGINEERING.md` |

---

## Related Documents

- `CONTRIBUTING.md` — commit format and code standards (summary)
- `docs/REPOSITORY_STRUCTURE.md` — detailed module map
- `ARCHITECTURE_DECISION_RECORDS/` — ADR index
- `docs/OBSERVABILITY.md` — logging and metrics
- `docs/SECURITY.md` — security review checklist
- `MASTER_PROGRESS.md` — engineering checkpoint status
