# Current State

Read `CONSTITUTION.md`, `TASK_QUEUE.md`, `ROADMAP.md`, and `MEMORY.md` first. Update this document at the end of every meaningful engineering or research cycle.

**Last updated:** 2026-08-08
**Active horizon:** AXIOM Operating System v1.0 — Continuous Evolution Loop

## Where we are today

AXIOM operates as a **self-improving research organization** governed by the Continuous Evolution Loop (`.axiom/OPERATING_SYSTEM.md`). Work flows through seven nested layers — strategic (monthly), engineering (daily), research (per campaign), product (per release), capability (weekly), learning (continuous), and frontier (GCP tiers).

The repository is the organizational memory. Prompts do not advance the mission; evidence, benchmarks, and state updates do.

## Operating system (v1.0)

| Layer | Cadence | Key artifact |
|------:|---------|--------------|
| 1 Strategic | Monthly | `.axiom/templates/MONTHLY_STRATEGIC_REVIEW.md` |
| 2 Engineering | Daily | `.axiom/TASK_QUEUE.md`, `.axiom/ENGINEERING.md` |
| 3 Research | Per campaign | `GRAND_CHALLENGE_PROGRAM.md`, GCP engine |
| 4 Product | Per release | `.axiom/PRODUCT.md` |
| 5 Capability | Weekly | SCEP benchmarks, `.axiom/NORTH_STAR_METRICS.md` |
| 6 Learning | Continuous | `.axiom/MEMORY.md` |
| 7 Frontier | Per GCP tier | `READINESS_GATES.md` |

Entry point: `AXIOM_OPERATING_SYSTEM.md` → `.axiom/OPERATING_SYSTEM.md`

## Completed

- Operating contract committed as `6dca714` (`VISION.md`, root engineering/architecture contract, and Sprint 0 roadmap).
- AXIOM Operating System initialized under `.axiom/`.
- Three-track execution initiated: Research capability, researcher-workspace product, and company/PMO foundation now progress in parallel.
- **S0-E2 (core):** Test toolchain restored — `pytest.py` moved to `scripts/standalone_test_runner.py`, `prize_readiness.py` syntax fixed, ruff config consolidated in `pyproject.toml`, CORS origins parsing fixed, httpx pinned `<0.28`, MDE router mounted.
- **Test baseline (2026-08-06):** `159/159` core tests pass (`pytest tests/ --ignore=tests/e2e`). Full suite: `334/360`; 26 e2e failures documented (MDE API surface gap).
- **Research Workspace v1:** End-to-end vertical slice — create projects, upload PDFs, extract text, generate summaries, save structured notes, FTS search, resume sessions. API `/research/*`, UI `/research`, demo script `scripts/demo_research_workspace.sh`.
- **S0-E3:** Verification truthfulness audit — `axiom/core/verification/truthfulness.py`; API responses expose `evidence_mode` and `formally_proven`; simulated/SMT/heuristic paths cannot claim `TIER_2_PROVEN`.
- **EM-001 Research Workspace (production):** Projects CRUD, PDF upload/parse/store, notes with tags, FTS search, paper Q&A with saved conversations, session resume. UI at `/research`.
- **Grand Challenge Program (GCP):** Six-tier challenge registry, campaign management, readiness gates, `/gcp/*` API — `GRAND_CHALLENGE_PROGRAM.md`.
- **AXIOM Operating System v1.0:** Continuous Evolution Loop, seven layers, north star metrics, repository map — `AXIOM_OPERATING_SYSTEM.md`, `.axiom/OPERATING_SYSTEM.md`.

## Blocked

- None for core engineering baseline.

## Highest priority

**Execute the engineering loop (Layer 2):** Select highest-ROI task from `TASK_QUEUE.md`, implement with tests and benchmarks, update state. **First Tier 1 campaign** ("Foundations of Known-Answer Mathematical Reasoning") awaits human strategic approval in Layer 1 monthly review.

## Worktree integrity

Capability delta reports under `docs/capability_delta_*.md` should not be bulk-committed; milestone deltas only.
