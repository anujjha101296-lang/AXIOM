# Current State

Read `CONSTITUTION.md`, `TASK_QUEUE.md`, `ROADMAP.md`, and `MEMORY.md` first. Update this document at the end of every meaningful engineering or research cycle.

**Last updated:** 2026-08-08
**Active horizon:** Grand Challenge Program — permanent research campaign framework

## Where we are today

AXIOM is a Python/FastAPI research platform. EPIC-001 (MIP), EPIC-002 (SCEP), and the Research Workspace are committed. The **Grand Challenge Program** (`axiom/grand_challenge/`) provides a six-tier campaign framework from toy reasoning to frontier readiness assessment.

## Completed

- Operating contract committed as `6dca714` (`VISION.md`, root engineering/architecture contract, and Sprint 0 roadmap).
- AXIOM Operating System initialized under `.axiom/`.
- Three-track execution initiated: Research capability, researcher-workspace product, and company/PMO foundation now progress in parallel.
- **S0-E2 (core):** Test toolchain restored — `pytest.py` moved to `scripts/standalone_test_runner.py`, `prize_readiness.py` syntax fixed, ruff config consolidated in `pyproject.toml`, CORS origins parsing fixed, httpx pinned `<0.28`, MDE router mounted.
- **Test baseline (2026-08-06):** `159/159` core tests pass (`pytest tests/ --ignore=tests/e2e`). Full suite: `334/360`; 26 e2e failures documented (MDE API surface gap).
- **Research Workspace v1:** End-to-end vertical slice — create projects, upload PDFs, extract text, generate summaries, save structured notes, FTS search, resume sessions. API `/research/*`, UI `/research`, demo script `scripts/demo_research_workspace.sh`.
- **S0-E3:** Verification truthfulness audit — `axiom/core/verification/truthfulness.py`; API responses expose `evidence_mode` and `formally_proven`; simulated/SMT/heuristic paths cannot claim `TIER_2_PROVEN`.
- **EM-001 Research Workspace (production):** Projects CRUD, PDF upload/parse/store, notes with tags, FTS search, paper Q&A with saved conversations, session resume. UI at `/research`.
- **Grand Challenge Program (GCP):** Six-tier challenge registry, campaign management, readiness gates, `/gcp/*` API — `GRAND_CHALLENGE_PROGRAM.md`, `CHALLENGE_REGISTRY.md`, `READINESS_GATES.md`, `ROADMAP_ALIGNMENT.md`.

## Blocked

- None for core engineering baseline.

## Highest priority

**First Tier 1 campaign** — "Foundations of Known-Answer Mathematical Reasoning" (see `GRAND_CHALLENGE_PROGRAM.md`). Execute bounded campaign before Tier 2 paper reproduction.

## Worktree integrity

Capability delta reports under `docs/capability_delta_*.md` should not be bulk-committed; milestone deltas only.
