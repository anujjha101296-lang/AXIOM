# Current State

Read `CONSTITUTION.md`, `TASK_QUEUE.md`, `ROADMAP.md`, and `MEMORY.md` first. Update this document at the end of every meaningful engineering or research cycle.

**Last updated:** 2026-08-06
**Active horizon:** Continuous Engineering — H1-OBS provenance records

## Where we are today

AXIOM is a Python/FastAPI and Next.js research platform. **S0-E4 EPIC-002 Evidence Integration Gate** is complete: all capability scores expose `evidence_state`, `benchmark_count`, and `limitations`. Engineering Governance System operational (`make engineering-health`).

## Completed

- Operating contract committed as `6dca714` (`VISION.md`, root engineering/architecture contract, and Sprint 0 roadmap).
- AXIOM Operating System initialized under `.axiom/`.
- **S0-E2 (core):** Test toolchain restored — **171/171** core tests pass (`pytest tests/ --ignore=tests/e2e`).
- **S0-E3:** Verification truthfulness audit — `axiom/core/verification/truthfulness.py`.
- **Research Workspace v1:** End-to-end vertical slice at `/research`.
- **Engineering Governance System:** `axiom/governance/` — collectors, council, health reports, CI workflow.
- **S0-E4:** EPIC-002 evidence gate — `axiom/evaluation/frameworks/evidence.py`, gated `/eval/*` API, `docs/S0-E4_evidence_gate.md`.

## Latest Engineering Health Scores (2026-08-06)

| Score | Value |
|-------|------:|
| Engineering Health | 70 |
| Product Health | 28 |
| Research Capability | 20 |
| Technical Debt | 95 (higher = more debt) |
| Security | 26 |
| Performance | 70 |
| Developer Experience | 67 |
| Repository Maturity | 60 |

## Blocked

- None for core engineering baseline.

## Highest priority

**H1-OBS** — Add reproducible run/provenance records to scientific capability evaluations (per `TASK_QUEUE.md` rank 7). Depends on S0-E4 (complete).

## Worktree integrity

Capability delta reports under `docs/capability_delta_*.md` should not be bulk-committed; milestone deltas only.
