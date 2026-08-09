# Organizational Memory Ledger

Read `CONSTITUTION.md`, `CURRENT_STATE.md`, `TASK_QUEUE.md`, `DECISION_FRAMEWORK.md`, and `KNOWLEDGE_GRAPH.md`. This ledger is append-only except for correcting factual errors with an explicit correction note.

## Recording protocol

Record decisions, experiments, failures, benchmarks, architecture changes, commits, customer learnings, proof attempts, and rejected ideas. Each record includes date, type, summary, evidence/artifacts, outcome, limitations, and links to the knowledge graph. Never store secrets, private credentials, sensitive personal data, or unapproved customer data.

## Entries

### 2026-08-09 — Operating system — AXIOM-MASTER-001 installed

- **Summary:** Replaced isolated “next feature” prompting with continuous autonomous execution under `.axiom/MASTER_DIRECTIVE.md`. Wired `AGENTS.md` + `CONSTITUTION.md`. Created `AXIOM_STATE.md` documenting that 25+ draft PRs never landed on `main` is the primary organizational failure mode.
- **Artifacts:** `.axiom/MASTER_DIRECTIVE.md`, `AXIOM_STATE.md`, `.axiom/MERGE_ORDER.md`, updated `AGENTS.md`, `CONSTITUTION.md`, `TASK_QUEUE.md`, `CURRENT_STATE.md`.
- **Decision:** Product-first YC MVP + research loop wedge; do not reinvent coding-agent / app-builder / general-API stacks; stop opening orphan research-loop PRs until LAND-1 / FOUNDER-MERGE resolve.
- **Founder gate:** Authorize merge of draft PR chain #17→#26 (or squash tip).
- **Next:** LAND-1 (land P0-WEB + OS), then MVP-AUTH.

### 2026-08-06 — Product milestone — EM-001 Research Workspace (production)

- **Summary:** Shipped production-ready researcher workflow: project organization, PDF pipeline, notes with tags, FTS search, paper Q&A with persisted conversations, session resume.
- **Artifacts:** `axiom/research/qa.py`, conversation tables, `/research/projects/{id}/ask`, UI chat at `/research`.
- **Evidence:** `159/159` core tests; `scripts/demo_research_workspace.sh` completes full workflow including Q&A.
- **Next:** S0-E4 EPIC-002 integration gate.

### 2026-08-06 — Engineering — S0-E3 verification truthfulness audit

- **Summary:** Centralized evidence-mode labeling so simulated, SMT-bounded, heuristic, and compiler-backed verification cannot claim formal proof status.
- **Artifacts:** `axiom/core/verification/truthfulness.py`; updated `/verify/*` and `/mip/formal/compile`, `/mip/verify/claim` responses; `tests/test_verification_truthfulness.py`.
- **Evidence:** `pytest tests/ --ignore=tests/e2e` → 154 passed; regression tests assert `formally_proven: false` for simulated Lean and SMT modular paths.
- **Limitation:** MIP consensus `final_verdict` may still be `VERIFIED` from heuristic checks; `formally_proven` flag distinguishes formal proof.
- **Next:** S0-E4 EPIC-002 integration gate.

### 2026-08-06 — Product milestone — Research Workspace v1

- **Summary:** Shipped first complete researcher vertical slice: projects, PDF upload/extraction, summaries, structured notes, FTS search, session resume.
- **Artifacts:** `axiom/research/`, `/research` API routes, `ui/src/app/research/page.tsx`, `tests/test_research_workspace.py`, `scripts/demo_research_workspace.sh`, `docs/api.md` Research section.
- **Evidence:** `pytest tests/test_research_workspace.py` → 10 passed; core suite `144/144`; demo script completes end-to-end against live API.
- **Fixes:** Reserved `LogRecord` keys (`name`, `filename`) in structured logging caused 500/404 on create/upload; corrected to `project_name` / `document_filename`.
- **Limitation:** Summaries use model gateway with extractive fallback; blank/scanned PDFs return 422; UI requires bearer token in dev.
- **Next:** S0-E3 verification truthfulness audit.

### 2026-08-06 — Engineering baseline — S0-E2 core complete

- **Summary:** Restored trustworthy core test baseline after three P0 toolchain defects.
- **Changes:** Moved `pytest.py` → `scripts/standalone_test_runner.py`; fixed `prize_readiness.py` syntax; consolidated ruff config in `pyproject.toml`; fixed CORS comma-separated env parsing; pinned `httpx<0.28`; mounted MDE router; fixed e2e TestClient auth headers.
- **Evidence:** `pytest tests/ --ignore=tests/e2e` → 134 passed, 0 failed (Python 3.12.3). Full suite: 334 passed, 26 e2e failed.
- **Limitation:** 26 e2e tests fail because MDE conjecture/counterexample endpoints exist only in test modules, not production API. Coverage ~54%.
- **Next:** S0-E3 verification truthfulness audit.

### 2026-08-05 — Architecture decision — operating contract

- **Summary:** AXIOM moved from prompt-led execution toward a repository-native operating system.
- **Artifact:** commit `6dca714`; root `VISION.md`, `ENGINEERING.md`, `ARCHITECTURE.md`, and `roadmap.md`.
- **Rationale:** persistent state and evidence improve continuity, prioritization, and review across sessions.
- **Limitation:** documents guide workers but do not replace human authority or executable automation.

### 2026-08-05 — Baseline failure — unsupported runtime

- **Summary:** full pytest collection fails under the available Python 3.9.6 runtime.
- **Evidence:** Pydantic cannot evaluate existing `str | None` annotations; `pyproject.toml` declares Python `^3.10`.
- **Decision:** prioritize provision of a Python 3.10+ runtime before integrating EPIC-002 work.
- **Links:** `CURRENT_STATE.md`, `TASK_QUEUE.md` S0-E2, `ARCHITECTURE.md`.

### 2026-08-05 — Constitution initialization

- **Summary:** `.axiom/` was created as the operating source of truth for sessions.
- **Outcome:** durable contracts, current state, queue, roadmap governance, capability map, knowledge schema, and memory protocol now exist.
- **Next review:** after Sprint 0 E2 test baseline is available.

### 2026-08-05 — Strategy decision — three parallel tracks

- **Summary:** AXIOM will advance Research, Product, and Company tracks together instead of waiting for a finished artificial scientist before validating product and company assumptions.
- **Product position:** the initial public offering is an AI workspace for frontier mathematical and scientific research, with explicit limits and evidence-backed claims.
- **Rationale:** early user learning improves product clarity and informs the research-capability roadmap; research rigor remains a non-negotiable foundation.
- **Current action:** start a landing experience, an initial researcher-workflow/benchmark plan, and a PMO cadence alongside the Python 3.10+ baseline task.
