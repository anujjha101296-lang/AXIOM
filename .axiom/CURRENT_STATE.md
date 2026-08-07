# Current State

Read `CONSTITUTION.md`, `TASK_QUEUE.md`, `ROADMAP.md`, and `MEMORY.md` first. Update this document at the end of every meaningful engineering or research cycle.

**Last updated:** 2026-08-07
**Active horizon:** Frontier Research Platform — H1-OBS provenance complete; autonomous research next

## Where we are today

AXIOM is a Python/FastAPI research platform. **H1-OBS Evaluation Provenance Records** now link every SCEP and RVP run to auditable inputs, runtime, configuration, environment, and evidence tier. RVP operational (266 problems). S0-E4 evidence gate complete. Engineering Governance operational.

## Completed

- **S0-E2/E3/E4:** Test baseline, verification truthfulness, EPIC-002 evidence gate.
- **Engineering Governance System:** `make engineering-health`, council reviews, health reports.
- **Research Validation Program:** `axiom/research_validation/` — stages 0–6, known-answer dataset (266 problems), capability scoring, pipeline artifacts, reproducibility, dashboard, API, `make research-validation`.
- **H1-OBS:** Unified `run_provenance` table, `/provenance/*` API, SCEP+RVP integration — see `docs/H1-OBS_run_provenance.md`.
- **Verification review:** `VERIFIED_CAPABILITIES.md`, `IMPLEMENTATION_MATRIX.md`, `PRODUCT_READINESS.md`, `RESEARCH_READINESS.md`.
- **Core tests:** **189/189** pass (`pytest tests/ --ignore=tests/e2e`).

## Blocked

- None for provenance infrastructure.

## Highest priority

**Mount workflow API + merge research loop** — unlock autonomous research (Program 3). See `FRONTIER_RESEARCH_PLATFORM.md`.

## Worktree integrity

Capability delta reports under `docs/capability_delta_*.md` should not be bulk-committed; milestone deltas only.
