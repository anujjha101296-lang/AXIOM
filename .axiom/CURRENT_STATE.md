# Current State

Read `CONSTITUTION.md`, `TASK_QUEUE.md`, `ROADMAP.md`, and `MEMORY.md` first. Update this document at the end of every meaningful engineering or research cycle.

**Last updated:** 2026-08-08
**Active horizon:** AXIOM Research Kernel — permanent execution engine for research workflows

## Where we are today

AXIOM is a Python/FastAPI research platform with a **four-layer governance stack**:

1. **ACA** (`axiom/cognitive/`) — permanent 9-layer cognitive architecture; models interchangeable
2. **Research Kernel** (`axiom/research_kernel/`) — permanent 10-stage execution engine; domain plugins
3. **SME** (`axiom/scientific_method/`) — mandatory 10-phase scientific method for research workflows
4. **H1-OBS** — provenance records for SCEP, RVP, SME, ACA, and kernel runs

Workflow creation requires completed SME session. Research runs execute through the kernel, which delegates to ACA, SME, and workflow subsystems without duplication.

## Completed

- **S0-E2/E3/E4:** Test baseline, verification truthfulness, EPIC-002 evidence gate.
- **Engineering Governance System:** `make engineering-health`, council reviews, health reports.
- **Research Validation Program:** 266 known-answer problems, capability scoring, dashboard, API.
- **H1-OBS:** Unified `run_provenance` table, `/provenance/*` API.
- **Scientific Method Engine (SME):** 10-phase mandatory workflow, `/sme/*` API, workflow gate — `docs/SME_scientific_method_engine.md`.
- **AXIOM Cognitive Architecture (ACA):** 9-layer permanent reasoning model, `/aca/*` API, model provider abstraction — `docs/ACA_cognitive_architecture.md`.
- **Research Kernel:** 10-stage permanent execution engine, 3 domain plugins (math, CS, VLSI), `/kernel/*` API — `RESEARCH_KERNEL.md`, `PLUGIN_API.md`, `KERNEL_ARCHITECTURE.md`.
- **Workflow API:** `/workflows/*` mounted with SME gate.
- **Core tests:** **220/220** pass (`pytest tests/ --ignore=tests/e2e`).

## Blocked

- None for ACA/SME infrastructure.

## Highest priority

**Research loop merge** — wire long-horizon discovery through Kernel → ACA → SME → Workflow pipeline. See `FRONTIER_RESEARCH_PLATFORM.md`.

## Worktree integrity

Capability delta reports under `docs/capability_delta_*.md` should not be bulk-committed; milestone deltas only.
