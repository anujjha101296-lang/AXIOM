# Current State

Read `CONSTITUTION.md`, `TASK_QUEUE.md`, `ROADMAP.md`, and `MEMORY.md` first. Update this document at the end of every meaningful engineering or research cycle.

**Last updated:** 2026-08-08
**Active horizon:** Scientific Method Engine (SME) — mandatory research workflow governance

## Where we are today

AXIOM is a Python/FastAPI research platform. **Scientific Method Engine (SME)** now governs every autonomous research task through 10 mandatory phases. Workflow creation requires a completed SME session. H1-OBS provenance records SCEP, RVP, and SME runs. RVP operational (266 problems). Engineering Governance operational.

## Completed

- **S0-E2/E3/E4:** Test baseline, verification truthfulness, EPIC-002 evidence gate.
- **Engineering Governance System:** `make engineering-health`, council reviews, health reports.
- **Research Validation Program:** `axiom/research_validation/` — stages 0–6, known-answer dataset (266 problems), capability scoring, pipeline artifacts, reproducibility, dashboard, API, `make research-validation`.
- **H1-OBS:** Unified `run_provenance` table, `/provenance/*` API, SCEP+RVP+SME integration — see `docs/H1-OBS_run_provenance.md`.
- **Scientific Method Engine (SME):** `axiom/scientific_method/` — 10-phase mandatory workflow, `/sme/*` API, workflow gate, `make sme-benchmark` — see `docs/SME_scientific_method_engine.md`.
- **Workflow API:** `/workflows/*` mounted with SME gate (requires completed `sme_session_id`).
- **Verification review:** `VERIFIED_CAPABILITIES.md`, `IMPLEMENTATION_MATRIX.md`, `PRODUCT_READINESS.md`, `RESEARCH_READINESS.md`.
- **Core tests:** **199/199** pass (`pytest tests/ --ignore=tests/e2e`).

## Blocked

- None for SME infrastructure.

## Highest priority

**Research loop merge** — wire long-horizon discovery orchestration through SME-gated workflows. See `FRONTIER_RESEARCH_PLATFORM.md`.

## Worktree integrity

Capability delta reports under `docs/capability_delta_*.md` should not be bulk-committed; milestone deltas only.
