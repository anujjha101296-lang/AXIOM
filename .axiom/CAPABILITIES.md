# Capability Map

Read `CONSTITUTION.md`, `RESEARCH.md`, `ENGINEERING.md`, `ROADMAP.md`, `PRIZE_TRACK.md`, and `KNOWLEDGE_GRAPH.md`.

## Capability maturity model

`Idea → prototype → measured → reproducible → independently verified → operationally reliable`

Only measured or stronger capabilities may influence planning as evidence. Each entry links to code, tests, benchmarks, provenance, limitations, and an owner or review status.

## Current capability inventory

| Capability | Current maturity | Evidence / limitation | Next proof point |
|---|---|---|---|
| Epistemic graph and knowledge storage | Prototype | SQLite/NetworkX implementation and tests exist; completeness unmeasured. | Reproducible provenance and migration baseline. |
| Mathematical ingest and parsing | Prototype | arXiv/LaTeX parsing code exists; corpus-scale quality unmeasured. | Benchmark extraction precision/recall. |
| Formal verification adapters | Prototype | Lean/Coq/Isabelle adapters include fallback simulation. | Actual compiler-backed tests and unambiguous result status. |
| Reasoning and hypothesis generation | Prototype | MCTS and conjecture modules exist; research utility unmeasured. | Fixed benchmark and comparison to baselines. |
| Scientific capability evaluation | Experimental | Uncommitted EPIC-002 framework exists. | Supported-runtime tests and evidence audit. |

Do not promote maturity without an artifact in `KNOWLEDGE_GRAPH.md` and a dated entry in `MEMORY.md`.
