# AXIOM Architecture Contract

`docs/architecture.md` describes the current component topology. This document defines the architectural direction and the rules for evolving it.

## System purpose

AXIOM is a research-engineering platform that turns evidence into bounded, inspectable technical work. The first implementation focus is mathematical intelligence, but its core patterns must remain usable by later scientific and engineering domains.

## Current topology

```text
Clients / UI
    ↓
FastAPI API Gateway ── authentication, validation, metrics
    ↓
Domain services ── ingest, knowledge, reasoning, verification, evaluation
    ↓
Storage and external tools ── SQLite/graph, model providers, Z3, Lean/Coq/Isabelle
```

The platform separates four concerns:

| Layer | Responsibility | Must not do |
|---|---|---|
| Interfaces | HTTP/UI input and output, auth, schema validation | Embed domain or persistence rules |
| Domain capability | Research logic, search, scoring, planning, verification orchestration | Depend directly on request globals or UI state |
| Evidence and state | Provenance, graph entities, runs, evaluations, audit history | Claim a result is stronger than its evidence |
| Adapters | Databases, subprocess provers, model APIs, queues | Leak provider-specific behavior through the domain API |

## Result integrity model

Every material result must carry enough metadata to answer:

- What claim or output was produced?
- What source inputs, tool versions, configuration, and run identifier produced it?
- Was it generated, heuristically checked, simulated, independently checked, or formally compiled?
- Can it be reproduced, challenged, or invalidated?

Only an actual successful compiler/prover invocation may create a `formally_verified` result. Fallback validation must remain explicitly `simulated` or `heuristic`.

## Evolution rules

- Add a reusable domain capability before adding a one-off endpoint.
- Prefer additive, reversible schema migrations with explicit versioning and rollback reasoning.
- Define model-provider interfaces so tests can run without live credentials.
- Promote a research prototype to a supported feature only after it has acceptance tests, observability, error behavior, and a clear evidence boundary.
- Do not make prize-readiness or scientific-value scores authoritative unless backed by recorded benchmarks and stated limitations.

## Current baseline (2026-08-06)

- **Runtime:** Python 3.11 in CI and Docker; minimum Python 3.10
- **Tests:** `make test-core` — 200+ core tests pass; e2e suite documents MDE API gaps
- **Coverage:** ≥70% on `axiom/` package (enforced in CI)

See `ARCHITECTURE_DECISION_RECORDS/0002-python-310-runtime-baseline.md` for the runtime decision.
