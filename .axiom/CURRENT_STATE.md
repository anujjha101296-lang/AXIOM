# Current State

Read `CONSTITUTION.md`, `TASK_QUEUE.md`, `ROADMAP.md`, and `MEMORY.md` first. Update this document at the end of every meaningful engineering or research cycle.

**Last updated:** 2026-09-12
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
- Dedicated authenticated FastAPI science-runtime router for bounded research, run snapshots/events, and benchmark execution; router is mounted in the API gateway.
- Science API contract tests covering the mounted router and bounded POST surface.
- Next.js `/research/science` workspace for launching bounded investigations and viewing hypothesis, state transitions, evidence, critic verdicts, hashes, and benchmark results.
- One-time router-mount workflow removed after successful integration.
- CI dependency installation aligned more closely with the repository `pyproject.toml` runtime requirements.
- `docs/AXIOM_TECHNICAL_EVOLUTION.md` defining the target agent, data, backend, frontend, observability, security, and evaluation architecture.
- Root README rewritten to distinguish current evidence from future claims and remove unsupported production/build assertions.
- Optional Ollama planner remains available; LLMs are accelerators, not sources of scientific truth.
- **S1-SCI-006 implemented:** every research-loop transition can be persisted immediately as an ordered append-only event with monotonic sequence IDs.
- **Live research API implemented:** asynchronous run queue endpoint plus authenticated Server-Sent Events stream with replay cursor and terminal event.
- **Workspace live mode implemented:** the science workspace launches the async run and refreshes its run snapshot as lifecycle events arrive, so progress no longer depends on waiting for completion.

## Architecture direction

- **Scientific runtime:** deterministic Python scientific tools remain the source of numerical truth.
- **Agent runtime:** provider-neutral orchestration first; OpenAI Agents SDK can be an optional intelligence layer with agents, tools, handoffs, guardrails, sessions, human-in-the-loop, and tracing.
- **Backend:** retain FastAPI for APIs and domain services; move durable research-run persistence toward PostgreSQL with JSONB/event records and optional pgvector rather than making a vector database the system of record.
- **Frontend:** retain the existing Next.js App Router research workspace and evolve it around evidence-first run views, experiment timelines, provenance, and benchmark dashboards rather than a generic chat UI.
- **Observability:** adopt structured run IDs, transition events, tool-call provenance, latency/cost metrics, and agent traces.

## Verification status

- Repository changes are committed to `main`.
- GitHub Actions previously verified the scientific runtime suite at **17 passed** and the database/UI integration on the preceding green run.
- A new CI run was triggered by the live-event changes and is currently the authoritative verification check; its initial state was queued, so this milestone is **implemented but not yet CI-verified**.
- Scientific evidence remains numerical; convergence, solver cross-checks, and critic gates do not constitute formal proof of chaos.

## Blocked / constraints

- No core engineering blocker identified.
- Local LLM quality depends on available hardware/model; optional by design.
- Vercel deployment access is not currently authorized through the connected deployment tool, so production deployment has not been attempted.
- External deployment and paid compute remain human-approved decisions.

## Highest priority

**Next:** S1-SCI-005 — wire provider-neutral planner adapters for OpenAI Agents SDK and Ollama into the existing structured scientific-plan contract, with deterministic execution and evidence verification remaining authoritative.

In parallel, complete the Lorenz evidence ladder (S1-SCI-001), harden the research-loop guarantees (S1-SCI-002), and then build the quantitative Scientific Intelligence Benchmark v0.1 (S1-SCI-003).

## 60-day target

A bounded scientific question should flow through hypothesis → experiment design → deterministic execution → critique → verification → reproducible report. The system must never upgrade numerical observations into mathematical proof.

## Worktree integrity

Capability delta reports under `docs/capability_delta_*.md` should not be bulk-committed; milestone deltas only.
