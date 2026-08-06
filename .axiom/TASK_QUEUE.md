# Prioritized Task Queue

Read `CONSTITUTION.md`, `CURRENT_STATE.md`, `DECISION_FRAMEWORK.md`, `ROADMAP.md`, and `MEMORY.md`. This queue is the next-work source of truth; update it after each cycle.

## Ranking method

Tasks are ordered by severity and by the weighted score in `DECISION_FRAMEWORK.md`: impact, dependency unlock, scientific value, engineering value, prize-readiness impact, confidence, reversibility, and effort. P0 safety, integrity, data-loss, and supported-build failures always outrank the formula.

| Rank | ID | Task | Dependencies | Acceptance signal | Status |
|---:|---|---|---|---|---|
| 1 | S0-E2 | Provision and document Python 3.10+ runtime; align local setup, CI, and Docker where applicable; run full suite. | Runtime authority/environment | Test collection works under supported runtime; complete results recorded. | Blocked: supported interpreter unavailable |
| 2 | P0-WEB | Create an honest public landing experience for the AI research workspace. | Existing Next.js UI | Responsive, accessible page distinguishes current capabilities from future vision. | In progress |
| 3 | R0-PLAN | Establish the initial researcher workflow, benchmark program, and monthly evidence review. | Existing repository evidence | Research plan names workflow, measurement, non-claims, and review cadence. | In progress |
| 4 | C0-PMO | Establish daily and weekly PMO cadence. | AOS | Operating document answers daily priorities, parallelism, blockers, and weekly shipping target. | In progress |
| 5 | S0-E3 | Audit verification routes/models for simulation versus formal-proof truthfulness. | S0-E2 test baseline | Regression tests prove fallback results cannot claim formal verification. | Ready after S0-E2 |
| 6 | S0-E4 | Review and integrate EPIC-002 capability framework. | S0-E2, S0-E3 | Evidence state, benchmark count, and limitations tested and documented. | Deferred |
| 7 | H1-OBS | Add reproducible run/provenance records to scientific capability evaluations. | S0-E4 | A result can identify inputs, runtime, configuration, and evidence tier. | Deferred |

## Queue protocol

Select the first unblocked task. If blocked, record the blocker in `CURRENT_STATE.md`, choose the next independent safe task, and preserve rank/reasoning. Add new work only with an acceptance signal, dependencies, evidence source, and a link to a capability or opportunity in `KNOWLEDGE_GRAPH.md`.
