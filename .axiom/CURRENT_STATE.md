# Current State

Read `CONSTITUTION.md`, `TASK_QUEUE.md`, `ROADMAP.md`, and `MEMORY.md` first. Update this document at the end of every meaningful engineering or research cycle.

**Last updated:** 2026-08-06
**Active horizon:** Research Validation Program (RVP) — staged scientific validation

## Where we are today

AXIOM is a Python/FastAPI research platform. **Research Validation Program (RVP)** is operational with 266 known-answer problems, 10-dimension Research Capability Score, discovery pipeline outputs, replay, and dashboard API (`/rvp/*`). S0-E4 evidence gate complete. Engineering Governance System operational.

## Completed

- **S0-E2/E3/E4:** Test baseline, verification truthfulness, EPIC-002 evidence gate.
- **Engineering Governance System:** `make engineering-health`, council reviews, health reports.
- **Research Validation Program:** `axiom/research_validation/` — stages 0–6, known-answer dataset (266 problems), capability scoring, pipeline artifacts, reproducibility, dashboard, API, `make research-validation`.
- **Core tests:** **176/176** pass (`pytest tests/ --ignore=tests/e2e`).

## Blocked

- None for RVP infrastructure validation.

## Highest priority

**H1-OBS** — Add reproducible run/provenance records linking RVP and SCEP evaluation runs (see `NEXT_RESEARCH_TARGETS.md`).

## Worktree integrity

Capability delta reports under `docs/capability_delta_*.md` should not be bulk-committed; milestone deltas only.
