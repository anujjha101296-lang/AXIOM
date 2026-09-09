# Current State

Read `CONSTITUTION.md`, `TASK_QUEUE.md`, `ROADMAP.md`, and `MEMORY.md` first. Update this document at the end of every meaningful engineering or research cycle.

**Last updated:** 2026-09-09
**Active horizon:** Two-month founder build — research, product, and company in parallel

## Where we are today

AXIOM is a Python/FastAPI and Next.js research platform whose initial wedge is mathematical intelligence and computational physics. The active priority is a measurable, local-first scientific execution loop that can later be driven by provider-neutral AI agents.

## Completed / newly advanced

- Operating contract and AXIOM Operating System under `.axiom/`.
- Research Workspace v1 and verification truthfulness controls.
- Core scientific/document/formal reasoning phases recorded in repository evidence.
- Deterministic Lorenz scientific runtime with explicit `NUMERICAL_OBSERVATION` evidence tier.
- Paired-trajectory sensitivity experiment and deterministic rho sweep.
- Timestep convergence and independent midpoint-integrator cross-check.
- Structured `axiom.science.evidence.v1` bundles with provenance, limitations, and content hashing.
- Reproducible Markdown report generation and CLI evidence export.
- Deterministic scientific critic with explicit numerical-evidence acceptance gates.
- Fixed Lorenz benchmark contract.
- Bounded research-loop state machine: planner → hypothesis → design → execute → critic → verify/repeat → complete/fail.
- Typed research question, hypothesis, experiment-plan, transition, and run records.
- Parameter allowlists and explicit experiment budgets so the autonomous loop fails closed rather than executing unbounded work.
- End-to-end deterministic research-loop test contract and CLI research entrypoint.
- Dedicated authenticated FastAPI science-runtime router for bounded research and benchmark execution; gateway mounting remains the next integration step.
- `docs/AXIOM_TECHNICAL_EVOLUTION.md` defining the target agent, data, backend, frontend, observability, security, and evaluation architecture.
- CI strengthened to run the complete `tests/science_runtime` suite and database regression, with current Actions/setup-node/setup-python major versions and Node 20.
- Root README rewritten to distinguish current evidence from future claims and remove unsupported production/build assertions.
- Optional Ollama planner remains available; LLMs are accelerators, not sources of scientific truth.

## Architecture direction

- **Scientific runtime:** deterministic Python scientific tools remain the source of numerical truth.
- **Agent runtime:** provider-neutral orchestration first; OpenAI Agents SDK can be an optional intelligence layer with agents, tools, handoffs, guardrails, sessions, human-in-the-loop, and tracing.
- **Backend:** retain FastAPI for APIs and domain services; move durable research-run persistence toward PostgreSQL with JSONB/event records and optional pgvector rather than making a vector database the system of record.
- **Frontend:** retain the existing Next.js App Router research workspace and evolve it around evidence-first run views, experiment timelines, provenance, and benchmark dashboards rather than a generic chat UI.
- **Observability:** adopt structured run IDs, transition events, tool-call provenance, latency/cost metrics, and agent traces.

## Verification status

- Repository changes are committed to `main`.
- **Local execution of the new test suite has not yet been independently run in this environment**, so passing status is not claimed.
- CI configuration now explicitly targets the scientific runtime and database tests; actual green status must be confirmed from the resulting workflow run.
- A visible Vercel check is pending on the latest workflow-related commit; deployment access remains separately constrained.
- Scientific evidence remains numerical; convergence, solver cross-checks, and critic gates do not constitute formal proof of chaos.

## Blocked / constraints

- No core engineering blocker identified.
- Local LLM quality depends on available hardware/model; optional by design.
- Vercel deployment access is not currently authorized through the connected deployment tool, so production deployment has not been attempted.
- External deployment and paid compute remain human-approved decisions.

## Highest priority

**S1-SCI-001 + S1-SCI-002:** finish the Lorenz evidence ladder and harden the bounded research loop with real tolerance semantics, robust independent verification, durable run/provenance storage, and provider-neutral agent adapters.

**Next product integration:** mount the science API into the gateway, persist research runs/events, then connect the existing Next.js workspace to live research-run state.

## 60-day target

A bounded scientific question should flow through hypothesis → experiment design → deterministic execution → critique → verification → reproducible report. The system must never upgrade numerical observations into mathematical proof.

## Worktree integrity

Capability delta reports under `docs/capability_delta_*.md` should not be bulk-committed; milestone deltas only.
