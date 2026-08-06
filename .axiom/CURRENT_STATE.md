# Current State

Read `CONSTITUTION.md`, `TASK_QUEUE.md`, `ROADMAP.md`, and `MEMORY.md` first. Update this document at the end of every meaningful engineering or research cycle.

**Last updated:** 2026-08-06
**Active horizon:** Milestone 006 — Golden Demo (v0.5-demo)

## Where we are today

AXIOM is a Python/FastAPI and Next.js research-platform repository whose initial wedge is mathematical intelligence: knowledge graph, ingestion, reasoning, verification, evaluation, and UI. **Milestone 006 — Golden Demo** delivers a five-minute, self-explanatory demonstration at `/demo` for researchers, investors, and partners. Prior milestones include Research Workspace (EM-001/MVP-0), Autonomous Research Loop v1 (M005), and Sprint 0 baseline (S0-E2/E3 complete; S0-E4 open).

**Engineering checkpoint (2026-08-06):** See `MASTER_PROGRESS.md`, `ROADMAP_STATUS.md`, `ENGINEERING_SCORECARD.md`. Overall platform ~46%; Golden Demo is presentation-ready.

## Completed

- Operating contract committed as `6dca714` (`VISION.md`, root engineering/architecture contract, and Sprint 0 roadmap).
- AXIOM Operating System initialized under `.axiom/`.
- Three-track execution initiated: Research capability, researcher-workspace product, and company/PMO foundation now progress in parallel.
- **S0-E2 (core):** Test toolchain restored — `pytest.py` moved to `scripts/standalone_test_runner.py`, `prize_readiness.py` syntax fixed, ruff config consolidated in `pyproject.toml`, CORS origins parsing fixed, httpx pinned `<0.28`, MDE router mounted.
- **Test baseline (2026-08-06):** `159/159` core tests pass (`pytest tests/ --ignore=tests/e2e`). Full suite: `334/360`; 26 e2e failures documented (MDE API surface gap).
- **Research Workspace v1:** End-to-end vertical slice — create projects, upload PDFs, extract text, generate summaries, save structured notes, FTS search, resume sessions. API `/research/*`, UI `/research`, demo script `scripts/demo_research_workspace.sh`.
- **S0-E3:** Verification truthfulness audit — `axiom/core/verification/truthfulness.py`; API responses expose `evidence_mode` and `formally_proven`; simulated/SMT/heuristic paths cannot claim `TIER_2_PROVEN`.
- **EM-001 Research Workspace (production):** Projects CRUD, PDF upload/parse/store, notes with tags, FTS search, paper Q&A with saved conversations, session resume. UI at `/research`.
- **MVP-0 stabilization:** Register/login API + UI (`/login`), JWT auth, UX fixes (loading, empty states, errors, a11y), `AXIOM_API_TOKEN` settings fix, `MVP_READINESS.md`, `scripts/demo_mvp_workflow.sh`. Core tests: **166/166** pass.
- **Milestone 005 — Autonomous Research Loop v1:** `axiom/research_loop/` — 8 role workers, failure memory, claim classification, historical benchmarks, `ResearchLoopEngine`, API `/research-loop/*`, UI `/research/runs`, demo `scripts/demo_research_loop.sh`. Core tests: **182/182** pass.
- **Milestone 006 — Golden Demo:** `/demo` UI with auto-play, guided tour, evidence graph, research tree, timeline; API `/demo/*`; sample dataset; presenter assets in `docs/demo/`. Tag `v0.5-demo`. Core tests: **187/187** pass.

## Blocked

- None for core engineering baseline.

## Highest priority

**S0-E4** — EPIC-002 integration gate: all capability scores must expose evidence state, benchmark count, and stated limitations (per `TASK_QUEUE.md` rank 6). **H1-OBS** (provenance records) follows immediately after S0-E4.

## Worktree integrity

Capability delta reports under `docs/capability_delta_*.md` should not be bulk-committed; milestone deltas only.
