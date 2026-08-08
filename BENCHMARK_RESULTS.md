# Benchmark Results

**Last updated:** 2026-08-08  
**Evidence tier:** measured (core suite) / partial (e2e)

## Core test suite

| Suite | Command | Result | Notes |
|-------|---------|--------|-------|
| Core unit/integration | `pytest tests/ --ignore=tests/e2e -q` | 183 pass | Primary CI gate |
| S0-E4 evidence gate | `pytest tests/test_s0_e4_evidence_gate.py -q` | pass | Evidence metadata regression |
| SCEP / EPIC-002 | `pytest tests/test_eval_api.py tests/test_evaluation_platform.py -q` | pass | Capability + prize readiness |
| Operating system | `pytest tests/test_operating_system.py -q` | 5/5 | Governance artifacts |
| GCP | `make gcp-benchmark` | Tier 0 compliant | Campaign framework |

## SCEP capability benchmarks

Run: `python3 -m axiom.evaluation.run_benchmarks` or `POST /eval/run`

| Dimension | Evidence state (typical) | Notes |
|-----------|--------------------------|-------|
| mathematical_reasoning | measured | Algebra/calculus cases |
| proof_verification | **simulated** | No Lean4 compiler in default env |
| conjecture_generation | measured | |
| knowledge_quality | measured | Requires DB |
| counterexample_search | measured | |
| research_planning | measured | |
| literature_synthesis | measured | Requires DB |
| research_productivity | measured | Requires DB |

Aggregate evidence tier after benchmark run: **simulated** (weakest dimension = proof_verification).

## E2E suite

| Suite | Result | Status |
|-------|--------|--------|
| Full including e2e | 334/360 | 26 failures — MDE gap (TD-001) |

## Regressions

None recorded for core gate since S0-E4 evidence integration.

## How to refresh

```bash
pytest tests/ --ignore=tests/e2e -q
python3 -m axiom.evaluation.run_benchmarks
make gcp-benchmark
```

Update this file after each CEL cycle that changes benchmarks or test baselines.
