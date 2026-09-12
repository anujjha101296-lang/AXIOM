# Prioritized Task Queue

Read `CONSTITUTION.md`, `CURRENT_STATE.md`, `DECISION_FRAMEWORK.md`, `ROADMAP.md`, and `MEMORY.md`. This queue is the next-work source of truth; update it after each cycle.

## Ranking method

Tasks are ordered by severity and by the weighted score in `DECISION_FRAMEWORK.md`: impact, dependency unlock, scientific value, engineering value, prize-readiness impact, confidence, reversibility, and effort. P0 safety, integrity, data-loss, and supported-build failures always outrank the formula.

| Rank | ID | Task | Dependencies | Acceptance signal | Status |
|---:|---|---|---|---|---|
| 1 | S1-SCI-001 | Complete Lorenz evidence ladder: declared tolerances, sweep, timestep sensitivity, convergence, independent verifier, provenance, report. | Local scientific runtime | Reproducible evidence package with explicit numerical evidence tier and declared tolerance policy. | **Active** |
| 2 | S1-SCI-002 | Harden bounded research-loop state machine: planner → experiment designer → executor → critic → verifier, with persistence-ready run records and provider-neutral agent adapters. | S1-SCI-001 | A question produces a bounded, auditable sequence of executable experiments with explicit stop conditions. | **Active** |
| 3 | S1-SCI-004 | Integrate science runtime API into the FastAPI gateway and researcher workspace. | S1-SCI-002 | Authenticated API starts a bounded run and exposes run/evidence state to the UI. | **Advanced: API mounted, workspace shipped, CI green** |
| 4 | S1-SCI-006 | Persist and stream research lifecycle events incrementally. | S1-SCI-004 | Each state transition is recorded and the workspace can observe run progress without waiting for completion. | **Implemented: pending CI verification** |
| 5 | S1-SCI-005 | Add provider-neutral agent adapters: OpenAI Agents SDK + Ollama. | S1-SCI-002 | Interchangeable planners produce the same structured scientific plan contract; deterministic execution remains authoritative. | **Next** |
| 6 | S1-SCI-003 | Add AXIOM Scientific Intelligence Benchmark v0.1. | S1-SCI-001/002 | Quantitative benchmark with baseline, failure cases, and reproducibility metadata. | Planned |
| 7 | S1-SCI-007 | Move research-run persistence toward PostgreSQL/JSONB and artifact storage. | S1-SCI-006 | Durable multi-user research history without making vector search the source of truth. | Planned |
| 8 | P0-WEB | Create an honest public landing experience for the AI research workspace. | Existing Next.js UI | Responsive page distinguishes current capabilities from future vision. | In progress |
| 9 | R0-PLAN | Maintain researcher workflow, benchmark program, and monthly evidence review. | Existing repository evidence | Research plan names workflow, measurement, non-claims, and review cadence. | In progress |
| 10 | C0-PMO | Establish daily and weekly PMO cadence. | AOS | Operating document answers daily priorities, parallelism, blockers, and weekly shipping target. | In progress |
| 11 | H1-OBS | Add reproducible run/provenance records to scientific capability evaluations. | S1-SCI-001 | Result identifies inputs, runtime, configuration, and evidence tier. | Ready |

## Two-month operating rule

Prefer work that increases verified scientific capability over cosmetic UI. Every week must ship at least one research artifact, one product improvement, and one company-learning artifact.

## Queue protocol

Select the first unblocked task. If blocked, record the blocker in `CURRENT_STATE.md`, choose the next independent safe task, and preserve rank/reasoning. Add new work only with an acceptance signal, dependencies, evidence source, and a link to a capability or opportunity in `KNOWLEDGE_GRAPH.md`.
