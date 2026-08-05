# Organizational Knowledge Graph

Read `CONSTITUTION.md`, `RESEARCH.md`, `PRODUCT.md`, `CAPABILITIES.md`, `PRIZE_TRACK.md`, and `MEMORY.md`.

## Purpose

This is the human-readable index to AXIOM's organizational knowledge. The implementation may evolve from Markdown to a graph store, but every link must retain provenance and an evidence tier.

## Node schema

| Node type | Required fields |
|---|---|
| Evidence | source, date, provenance, quality tier, limitations |
| Hypothesis | claim, rationale, expected signal, falsifier, owner |
| Experiment | method, inputs, configuration, outcome, reproducibility |
| Capability | maturity, code/tests/benchmarks, limitations, next proof point |
| Decision | alternatives, evidence, rationale, review date |
| Opportunity | user/problem, market evidence, value hypothesis, status |
| Artifact | path/commit, purpose, integrity status |

## Edge schema

Use `supports`, `contradicts`, `tests`, `depends_on`, `implements`, `measures`, `supersedes`, `derived_from`, and `blocked_by`. A claim without an evidence edge is an assumption.

## Seed links

- `Artifact: 6dca714` **implements** the operating-contract baseline.
- `Capability: formal verification adapters` **blocked_by** actual supported-runtime compiler validation.
- `Experiment: EPIC-002 evaluation framework integration` **depends_on** the Sprint 0 runtime baseline.

Add durable knowledge here; log chronological events and full decision history in `MEMORY.md`.
