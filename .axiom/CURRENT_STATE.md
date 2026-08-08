# Current State

Read `CONSTITUTION.md`, `TASK_QUEUE.md`, `ROADMAP.md`, and `MEMORY.md` first. Update this document at the end of every meaningful engineering or research cycle.

**Last updated:** 2026-08-08
**Active horizon:** AXIOM Cognitive Architecture (ACA) — permanent model-agnostic reasoning

## Where we are today

AXIOM is a Python/FastAPI research platform with a **three-layer governance stack**:

1. **ACA** (`axiom/cognitive/`) — permanent 9-layer cognitive architecture; models interchangeable
2. **SME** (`axiom/scientific_method/`) — mandatory 10-phase scientific method for research workflows
3. **H1-OBS** — provenance records for SCEP, RVP, SME, and ACA runs

Workflow creation requires completed SME session. All reasoning delegates through ACA layer adapters to existing subsystems (no duplication).

## Completed

- **S0-E2/E3/E4:** Test baseline, verification truthfulness, EPIC-002 evidence gate.
- **Engineering Governance System:** `make engineering-health`, council reviews, health reports.
- **Research Validation Program:** 266 known-answer problems, capability scoring, dashboard, API.
- **H1-OBS:** Unified `run_provenance` table, `/provenance/*` API.
- **Scientific Method Engine (SME):** 10-phase mandatory workflow, `/sme/*` API, workflow gate — `docs/SME_scientific_method_engine.md`.
- **AXIOM Cognitive Architecture (ACA):** 9-layer permanent reasoning model, `/aca/*` API, model provider abstraction — `docs/ACA_cognitive_architecture.md`.
- **Workflow API:** `/workflows/*` mounted with SME gate.
- **Core tests:** **209/209** pass (`pytest tests/ --ignore=tests/e2e`).

## Blocked

- None for ACA/SME infrastructure.

## Highest priority

**Research loop merge** — wire long-horizon discovery through ACA → SME → Workflow pipeline. See `FRONTIER_RESEARCH_PLATFORM.md`.

## Worktree integrity

Capability delta reports under `docs/capability_delta_*.md` should not be bulk-committed; milestone deltas only.
