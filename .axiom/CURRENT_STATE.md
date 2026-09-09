# Current State

Read `CONSTITUTION.md`, `TASK_QUEUE.md`, `ROADMAP.md`, and `MEMORY.md` first. Update this document at the end of every meaningful engineering or research cycle.

**Last updated:** 2026-09-09
**Active horizon:** Two-month founder build — research, product, and company in parallel

## Where we are today

AXIOM is a Python/FastAPI and Next.js research-platform repository whose initial wedge is mathematical intelligence: knowledge graph, ingestion, reasoning, verification, evaluation, and UI. Core engineering baselines and the researcher workspace exist. The active priority is a measurable, local-first scientific execution loop.

## Completed

- Operating contract and AXIOM Operating System under `.axiom/`.
- Research Workspace v1 and verification truthfulness controls.
- Core scientific/document/formal reasoning phases recorded in repository evidence.
- **2026-09-09:** Added `axiom/science_runtime/` local-first deterministic Lorenz experiment runtime.
- Added reproducible experiment records with explicit evidence tier `NUMERICAL_OBSERVATION`.
- Added paired-trajectory sensitivity experiment and deterministic rho sweep.
- Added timestep convergence and an independent midpoint-integrator cross-check.
- Added structured `axiom.science.evidence.v1` bundles with provenance, limitations, and content hashing.
- Added reproducible Markdown report generation and CLI flags for evidence export.
- Added science-runtime tests and included them in the existing CI test command.
- Added optional Ollama planner adapter; no paid API is required for the scientific runtime.
- Added smoke tests and the two-month execution plan in `docs/TWO_MONTH_EXECUTION_PLAN.md`.

## Verification status

- Code and tests have been committed to `main`.
- **Local execution of the new test suite has not yet been independently run in this environment**, so passing status is not claimed here.
- GitHub Actions should provide the authoritative clean-environment CI signal after the latest commits are processed; the existing CI workflow currently installs dependencies and runs its Python test command.
- The scientific evidence remains numerical; convergence and independent integration checks do not constitute formal proof of chaos.

## Blocked

- No core engineering blocker.
- Local LLM quality depends on the user's available hardware/model; this is intentionally an optional acceleration path.
- Vercel deployment access is not currently authorized through the connected deployment tool, so production deployment has not been attempted.
- External deployment and paid compute remain human-approved decisions.

## Highest priority

**S1-SCI-001:** Finish the Lorenz evidence ladder by validating the parameter sweep, provenance/report outputs, fresh-environment CI execution, and a fixed benchmark artifact.

## 60-day target

A bounded scientific question should flow through hypothesis → experiment design → deterministic execution → critique → verification → reproducible report. The system must never upgrade numerical observations into mathematical proof.

## Worktree integrity

Capability delta reports under `docs/capability_delta_*.md` should not be bulk-committed; milestone deltas only.
