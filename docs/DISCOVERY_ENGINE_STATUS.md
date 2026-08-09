# Discovery Engine Status

**Updated:** 2026-08-09  
**Branch:** `cursor/integrate-mainline-dc7e`  
**Package:** `axiom/discovery/`

## Audit summary (reuse vs build)

| Existing | Reused for |
|----------|------------|
| SKAI `detect_gaps` / conflicts | Gap → opportunity seeding |
| SEC sandbox + counterexample workflow | Pilot experiment + counterexample search |
| E&R discovery gate principles | No silent VERIFIED upgrades |
| FRCE campaigns | Optional `campaign_id` linkage |
| PaperQA untrusted wrapping / web fetch | Prior work on untrusted content |

| Missing before this work | Status now |
|--------------------------|------------|
| First-class Discovery object | **Implemented** |
| Opportunity scoring | **Implemented** |
| Competing hypotheses + QC | **Implemented** |
| Predictions | **Implemented** |
| Novelty assessment (conservative) | **Implemented** (local scan; default INSUFFICIENT_SEARCH) |
| Skeptical independent attack | **Implemented** |
| Persistent loop + API + UI | **Implemented** |
| Deterministic benchmarks + FDR trap | **Implemented** |
| Human approve/reject/pause/stop | **Implemented** (`POST /discovery/investigations/{id}/human`) |

## What works (executable)

- `Discovery` model with gated status transitions
- `DiscoveryEngine.create` → `run_cycle` stages: opportunities → hypotheses → pilot experiment → counterexample → independent attack → report
- API: `/discovery/*`
- UI: `/discovery` (linked from landing + research)
- Benchmarks: 8 deterministic cases via `/discovery/benchmarks/run`
- Explicit non-claims: `is_scientific_discovery_claim=False`, no Millennium attempt
- Tests: `tests/test_discovery_engine.py` (7 passing)

## Bugs fixed this cycle

1. **NO_COUNTEREXAMPLE substring trap** — `search_computational_counterexample` treated `NO_COUNTEREXAMPLE` as a hit because it contains `COUNTEREXAMPLE`. Fixed to require `COUNTEREXAMPLE_FOUND` or an exact `COUNTEREXAMPLE` line. Same fix in `axiom/experiment/discovery.py` signal detection.
2. **Hypothesis wipe on transition** — save before status transition after generating hypotheses.
3. **Trap markers** — known-false / FDR markers read from research question + knowledge context, not from hypothesis prose listing potential counterexamples.

## What is still partial

- External multi-engine literature novelty search (local SKAI only)
- Full formal proof bridge inside discovery cycle (FRCE/FMTP available separately)
- Rich discovery graph edges in EGS (IDs linked; full ontology expansion later)
- Live streaming of agent tool calls in UI
- Resource allocator / multi-strategy competition (scaffolded via competing hypotheses + attacks)

## Explicit honesty rules enforced

- Hypothesis ≠ fact
- Computational evidence ≠ proof
- Missing retrieval ≠ novelty
- VERIFIED requires explicit gate (`allow_verified=True`) — LLM cannot self-verify
- REFUTED cannot be casually resurrected
- No Millennium Prize attempts

## Benchmark posture

- 8 deterministic cases; false-discovery traps must not reach VERIFIED
- Measured FDR proxy on trap cases = 0.0 in suite

## Replit / env

Uses existing `AXIOM_DB_PATH`, `AXIOM_API_TOKEN`. No new secrets. Discovery store shares the AXIOM SQLite DB.
