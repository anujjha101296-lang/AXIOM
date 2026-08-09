# S0-E4 — EPIC-002 Evidence Gate

## Purpose

Ensure all capability and prize-readiness scores carry explicit evidence quality metadata so simulated, estimated, and baseline values cannot be mistaken for independently verified measurements.

## Evidence states

| State | Meaning |
|-------|---------|
| `measured` | Score derived from executed benchmark cases |
| `simulated` | Benchmark ran but formal verification path is simulated (no Lean/Coq compiler) |
| `estimated` | Partial benchmark coverage or heuristic estimation |
| `baseline` | Placeholder when no benchmark run exists |
| `unavailable` | No score or zero benchmark cases |

Aggregate evidence tier uses the **weakest** dimension state (minimum rank).

## Surfaces

- `CapabilitySnapshot.to_dict()` — `evidence_tier`, `limitations`, per-dimension `evidence_state` and `benchmark_count`
- `POST /eval/run` — returns `evidence_tier` and `limitations`
- `GET /eval/scores` — baseline fallback labeled `baseline` when DB empty
- `PrizeReadinessScore.to_dict()` — `evidence_tier`, `benchmark_count`, `limitations`
- `python3 -m axiom.evaluation.run_benchmarks` — persists evidence metadata in SQLite JSON

## Key modules

- `axiom/evaluation/frameworks/capability.py` — `EvidenceState`, `derive_evidence_state`, `rollup_evidence_tier`
- `axiom/evaluation/frameworks/prize_readiness.py` — `_enrich_prize_evidence`
- `axiom/services/api_gateway/routes/eval_api.py` — API integration

## Validation

```bash
pytest tests/test_s0_e4_evidence_gate.py tests/test_eval_api.py -q
python3 -m axiom.evaluation.run_benchmarks
```

## Known limitations

- Proof verification benchmarks use simulated Lean4 checks when compilers are absent.
- Prize readiness formulas remain EPIC-001 weighted models; evidence gate labels honesty, not proof of prize progress.
