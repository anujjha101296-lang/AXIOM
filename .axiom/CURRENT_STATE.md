# Current State

Read `CONSTITUTION.md`, `TASK_QUEUE.md`, `ROADMAP.md`, and `MEMORY.md` first. Update this document at the end of every meaningful engineering or research cycle.

**Last updated:** 2026-08-08
**Active horizon:** AXIOM Operating System v1.0 — Continuous Evolution Loop

## Where we are today

AXIOM operates as a **self-improving research organization** governed by the Continuous Evolution Loop (`.axiom/OPERATING_SYSTEM.md`). Work flows through seven nested layers — strategic (monthly), engineering (daily), research (per campaign), product (per release), capability (weekly), learning (continuous), and frontier (GCP tiers).

The repository is the organizational memory. Prompts do not advance the mission; evidence, benchmarks, and state updates do.

## Operating system (v1.0)

| Layer | Cadence | Key artifact |
|------:|---------|--------------|
| 1 Strategic | Monthly | `.axiom/templates/MONTHLY_STRATEGIC_REVIEW.md` |
| 2 Engineering | Daily | `.axiom/TASK_QUEUE.md`, `.axiom/ENGINEERING.md` |
| 3 Research | Per campaign | `GRAND_CHALLENGE_PROGRAM.md`, GCP engine |
| 4 Product | Per release | `.axiom/PRODUCT.md` |
| 5 Capability | Weekly | SCEP benchmarks, `.axiom/NORTH_STAR_METRICS.md` |
| 6 Learning | Continuous | `.axiom/MEMORY.md` |
| 7 Frontier | Per GCP tier | `READINESS_GATES.md` |

Entry point: `AXIOM_OPERATING_SYSTEM.md` → `.axiom/OPERATING_SYSTEM.md`

## Completed

- Operating contract committed as `6dca714` (`VISION.md`, root engineering/architecture contract, and Sprint 0 roadmap).
- AXIOM Operating System initialized under `.axiom/`.
- Three-track execution initiated: Research capability, researcher-workspace product, and company/PMO foundation now progress in parallel.
- **S0-E2 (core):** Test toolchain restored — `pytest.py` moved to `scripts/standalone_test_runner.py`, `prize_readiness.py` syntax fixed, ruff config consolidated in `pyproject.toml`, CORS origins parsing fixed, httpx pinned `<0.28`, MDE router mounted.
- **Test baseline (2026-08-06):** `159/159` core tests pass (`pytest tests/ --ignore=tests/e2e`). Full suite: `334/360`; 26 e2e failures documented (MDE API surface gap).
- **Research Workspace v1:** End-to-end vertical slice — create projects, upload PDFs, extract text, generate summaries, save structured notes, FTS search, resume sessions. API `/research/*`, UI `/research`, demo script `scripts/demo_research_workspace.sh`.
- **S0-E3:** Verification truthfulness audit — `axiom/core/verification/truthfulness.py`; API responses expose `evidence_mode` and `formally_proven`; simulated/SMT/heuristic paths cannot claim `TIER_2_PROVEN`.
- **EM-001 Research Workspace (production):** Projects CRUD, PDF upload/parse/store, notes with tags, FTS search, paper Q&A with saved conversations, session resume. UI at `/research`.
- **Grand Challenge Program (GCP):** Six-tier challenge registry, campaign management, readiness gates, `/gcp/*` API — `GRAND_CHALLENGE_PROGRAM.md`.
- **AXIOM Operating System v1.0:** Continuous Evolution Loop, seven layers, north star metrics, repository map — `AXIOM_OPERATING_SYSTEM.md`, `.axiom/OPERATING_SYSTEM.md`.
- **S0-E4 (EPIC-002 evidence gate):** `EvidenceState` on capability snapshots, prize readiness, and `/eval/*` APIs — `docs/S0-E4_evidence_gate.md`.
- **CEL v1:** Master loop (`.axiom/CEL.md`), scorecards (`TECH_DEBT.md`, `BENCHMARK_RESULTS.md`, `ENGINEERING_SCORECARD.md`, `PRODUCT_SCORECARD.md`), `scripts/cel_health_check.py`.
- **H1-OBS:** Unified `run_provenance` table and `/provenance` API for SCEP evaluation runs — `docs/H1-OBS_run_provenance.md`.
- **TSS-1:** Trust, Security & Safety Loop — `.axiom/TSS.md`, security scorecards, production guard, optional route auth, secret scanner — `SECURITY_STATUS.md`.
- **E&R-1:** Evidence & Reproducibility Loop — claim registry, discovery gate, provenance graph, reproduction engine, `/evidence/*` API — `EVIDENCE_STATUS.md`.
- **SIMR-1:** Scientific Intelligence & Model Routing — model/tool registries, capability graph, router, research compiler, `/routing/*` API — `MODEL_REGISTRY.md`.
- **FMTP-1:** Formal Mathematics & Theorem-Proving — prover registry, formalization pipelines, proof search, compilation gate, `/formal/*` API — `FORMAL_MATH_STATUS.md`.
- **SEC-1:** Scientific Experimentation & Compute — experiment kernel, sandbox, lifecycle, `/experiments/*` API — `EXPERIMENT_ENGINE.md`.

## Blocked

- **GCP-2:** First Tier 1 campaign requires Layer 1 strategic approval.

## Highest priority

**P0-WEB** — Honest public landing experience linking to `/research` workspace. **GCP-2** remains ready pending founder strategic approval.

## Worktree integrity

Capability delta reports under `docs/capability_delta_*.md` should not be bulk-committed; milestone deltas only.
