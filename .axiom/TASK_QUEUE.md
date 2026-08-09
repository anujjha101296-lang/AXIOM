# Prioritized Task Queue

Read `CONSTITUTION.md`, `CURRENT_STATE.md`, `DECISION_FRAMEWORK.md`, `ROADMAP.md`, and `MEMORY.md`. This queue is the next-work source of truth; update it after each cycle.

## Ranking method

Tasks are ordered by severity and by the weighted score in `DECISION_FRAMEWORK.md`: impact, dependency unlock, scientific value, engineering value, prize-readiness impact, confidence, reversibility, and effort. P0 safety, integrity, data-loss, and supported-build failures always outrank the formula.

| Rank | ID | Task | Dependencies | Acceptance signal | Status |
|---:|---|---|---|---|---|
| 1 | S0-E2 | Provision and document Python 3.10+ runtime; align local setup, CI, and Docker where applicable; run full suite. | Runtime authority/environment | Test collection works under supported runtime; complete results recorded. | **Complete (core):** 134/134 core tests pass; 26 e2e failures documented |
| 2 | P0-WEB | Create an honest public landing experience for the AI research workspace. | Existing Next.js UI | Responsive, accessible page distinguishes current capabilities from future vision. | **Ready — highest priority** |
| 3 | R0-PLAN | Establish the initial researcher workflow, benchmark program, and monthly evidence review. | Existing repository evidence | Research plan names workflow, measurement, non-claims, and review cadence. | In progress |
| 4 | C0-PMO | Establish daily and weekly PMO cadence. | AOS | Operating document answers daily priorities, parallelism, blockers, and weekly shipping target. | In progress |
| 5 | S0-E3 | Audit verification routes/models for simulation versus formal-proof truthfulness. | S0-E2 test baseline | Regression tests prove fallback results cannot claim formal verification. | **Complete** |
| 6 | S0-E4 | Review and integrate EPIC-002 capability framework. | S0-E2, S0-E3 | Evidence state, benchmark count, and limitations tested and documented. | **Complete** — see `docs/S0-E4_evidence_gate.md` |
| 7 | GCP-1 | Grand Challenge Program — six-tier campaign framework with readiness gates. | S0-E4 | 15+ challenges, campaign API, gates, 4 docs, Tier 1 campaign recommended. | **Complete** — see `GRAND_CHALLENGE_PROGRAM.md` |
| 8 | GCP-2 | Execute first Tier 1 campaign ("Foundations of Known-Answer Mathematical Reasoning"). | FRCE-1 | 2-week bounded campaign; >= 2/3 challenges pass; journal + checkpoints. | **Ready — requires Layer 1 strategic approval** |
| 9 | OS-1 | AXIOM Operating System v1.0 — Continuous Evolution Loop codified. | GCP-1 | 7 layers, metrics, repo map, templates, constitution update. | **Complete** — see `AXIOM_OPERATING_SYSTEM.md` |
| 10 | CEL-1 | CEL master loop, scorecards, and health check. | OS-1, S0-E4 | `.axiom/CEL.md`, scorecards, `make cel-health` passes. | **Complete** |
| 11 | H1-OBS | Add reproducible run/provenance records to scientific capability evaluations. | S0-E4 | A result can identify inputs, runtime, configuration, and evidence tier. | **Complete** — see `docs/H1-OBS_run_provenance.md` |
| 12 | TSS-1 | Trust, Security & Safety Loop — continuous security evaluation. | H1-OBS | TSS docs, production guard, secret scan, optional route auth. | **Complete** — see `SECURITY_STATUS.md` |
| 13 | E&R-1 | Evidence & Reproducibility Loop — provenance, claims, reproduction. | TSS-1, H1-OBS | Claim registry, discovery gate, `/evidence/*`, `make erl-health` passes. | **Complete** — see `EVIDENCE_STATUS.md` |
| 14 | SIMR-1 | Scientific Intelligence & Model Routing — model/tool selection. | E&R-1, SCEP | Model/tool registries, router, `/routing/*`, `make simr-health` passes. | **Complete** — see `MODEL_REGISTRY.md` |
| 15 | FMTP-1 | Formal Mathematics & Theorem-Proving Loop. | SIMR-1, MIP | Prover registry, formalization, proof search, `/formal/*`, `make fmtp-health` passes. | **Complete** — see `FORMAL_MATH_STATUS.md` |
| 16 | SEC-1 | Scientific Experimentation & Compute Loop. | FMTP-1, TSS | Experiment kernel, sandbox, `/experiments/*`, `make sec-health` passes. | **Complete** — see `EXPERIMENT_ENGINE.md` |
| 17 | FRCE-1 | Frontier Research Campaign Engine — connect all loops. | SEC-1, E&R-1, SIMR-1, FMTP-1, GCP-1 | Campaign orchestrator, `/frce/*`, `make frce-health` passes. | **Complete** — see `FRONTIER_CAMPAIGN_ENGINE.md` |
| 18 | SKAI-1 | Scientific Knowledge Acquisition & Intelligence Loop. | FRCE-1, E&R-1 | Knowledge graph, acquisition, `/skai/*`, `make skai-health` passes. | **Complete** — see `KNOWLEDGE_ACQUISITION.md` |

## Queue protocol

Select the first unblocked task. If blocked, record the blocker in `CURRENT_STATE.md`, choose the next independent safe task, and preserve rank/reasoning. Add new work only with an acceptance signal, dependencies, evidence source, and a link to a capability or opportunity in `KNOWLEDGE_GRAPH.md`.
