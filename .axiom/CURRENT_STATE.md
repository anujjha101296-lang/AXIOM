# Current State

Read `CONSTITUTION.md`, `TASK_QUEUE.md`, `ROADMAP.md`, and `MEMORY.md` first. Update this document at the end of every meaningful engineering or research cycle.

**Last updated:** 2026-08-05
**Active horizon:** Three-track foundation — research, product, and company

## Where we are today

AXIOM is a Python/FastAPI and Next.js research-platform repository whose initial wedge is mathematical intelligence: knowledge graph, ingestion, reasoning, verification, evaluation, and UI. EPIC-001 is committed. An EPIC-002 scientific-capability evaluation framework exists as uncommitted work and has not yet been integrated.

## Completed

- Operating contract committed as `6dca714` (`VISION.md`, root engineering/architecture contract, and Sprint 0 roadmap).
- AXIOM Operating System initialized under `.axiom/`.
- Three-track execution initiated: Research capability, researcher-workspace product, and company/PMO foundation now progress in parallel.

## Blocked

- The discovered Python runtime is 3.9.6, while `pyproject.toml` requires Python 3.10+. API test collection fails in Pydantic on Python 3.9's unsupported `str | None` evaluation.
- A Python 3.10+ runtime (local, CI, or Docker) must be made available before a trustworthy full-suite baseline can be reported.

## Highest priority

**S0-E2: establish and document a Python 3.10+ supported runtime, then rerun the full test suite.** This remains the technical baseline blocker; independent Product, Research, and PMO work is active in parallel. See `TASK_QUEUE.md` and root `roadmap.md`.

## Worktree integrity

Existing uncommitted files under `axiom/evaluation/` and `docs/scientific_capability_framework.md` predate this AOS work and must not be overwritten. Their integration is gated on the supported-runtime baseline.
