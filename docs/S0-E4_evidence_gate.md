# S0-E4 — EPIC-002 Evidence Integration Gate

**Status:** Complete (2026-08-06)  
**Task ID:** S0-E4  
**Acceptance:** Evidence state, benchmark count, and limitations tested and documented on all capability scores.

---

## What changed

Every capability dimension score now exposes:

| Field | Type | Description |
|-------|------|-------------|
| `evidence_state` | string | `measured`, `simulated`, `estimated`, `baseline`, or `unavailable` |
| `benchmark_count` | int | Number of benchmark cases contributing to the score |
| `limitations` | list[str] | Stated limitations (minimum one per dimension) |
| `estimated` | bool | True when score is not fully measured |
| `confidence` | float | Statistical confidence in the score |

## API behavior

- `GET /eval/scores` — Returns evidence-gated scores. Empty database yields `evidence_state: baseline` with `benchmark_count: 0`.
- `POST /eval/run` — Runs benchmarks and persists evidence-gated snapshot to SQLite.
- `GET /eval/prize-readiness` — Includes `limitations` and `evidence_state` per problem.

## Proof verification honesty

Proof verification benchmarks use structural simulation (`evidence_state: simulated`). Limitations explicitly state that simulated passes do not constitute formal proof.

## Code locations

- `axiom/evaluation/frameworks/capability.py` — `EvidenceState`, `DimensionScore` fields
- `axiom/evaluation/frameworks/evidence.py` — Gate helpers, shared `run_all_capability_benchmarks()`
- `axiom/services/api_gateway/routes/eval_api.py` — Gated API responses
- `tests/test_s0_e4_evidence_gate.py` — Acceptance tests

## How to verify

```bash
pytest tests/test_s0_e4_evidence_gate.py tests/test_eval_api.py -v
python3 -m axiom.evaluation.run_benchmarks --db /tmp/axiom_eval.db
```

## Unlocks

**H1-OBS** — Reproducible run/provenance records can now attach to evidence-gated evaluation runs.
