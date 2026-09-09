# Current State

Read `CONSTITUTION.md`, `TASK_QUEUE.md`, `ROADMAP.md`, and `MEMORY.md` first. Update this document at the end of every meaningful engineering or research cycle.

**Last updated:** 2026-09-09
**Active horizon:** Two-month founder build — research, product, and company in parallel

## Where we are today

AXIOM is a Python/FastAPI and Next.js research-platform repository whose initial wedge is mathematical intelligence: knowledge graph, ingestion, reasoning, verification, evaluation, and UI. Core engineering baselines and the researcher workspace exist. The new priority is to turn that foundation into a measurable, local-first scientific execution loop.

## Completed

- Operating contract and AXIOM Operating System under `.axiom/`.
- Research Workspace v1 and verification truthfulness controls.
- Core scientific/document/formal reasoning phases recorded in repository evidence.
- **2026-09-09:** Added `axiom/science_runtime/` local-first deterministic Lorenz experiment runtime.
- Added reproducible experiment records with explicit evidence tier `NUMERICAL_OBSERVATION`.
- Added paired-trajectory sensitivity experiment and deterministic rho sweep.
- Added optional Ollama planner adapter; no paid API is required for the scientific runtime.
- Added smoke tests and the two-month execution plan in `docs/TWO_MONTH_EXECUTION_PLAN.md`.

## Blocked

- No core engineering blocker.
- Local LLM quality depends on the user's available hardware/model; this is intentionally an optional acceleration path.
- External deployment and paid compute remain human-approved decisions.

## Highest priority

**S1-SCI-001:** Complete the Lorenz evidence ladder: parameter sweep, timestep sensitivity, convergence checks, independent numerical verifier, provenance persistence, and report generation.

## 60-day target

A bounded scientific question should flow through hypothesis → experiment design → deterministic execution → critique → verification → reproducible report. The system must never upgrade numerical observations into mathematical proof.

## Worktree integrity

Capability delta reports under `docs/capability_delta_*.md` should not be bulk-committed; milestone deltas only.
