# Model Benchmarks

**Last updated:** 2026-08-08  
**Loop:** SIMR (Scientific Intelligence & Model Routing)

## Status

| Benchmark category | Source | Status |
|-------------------|--------|--------|
| Mathematical reasoning | SCEP `mathematical_reasoning` | ✅ Integrated via model benchmark scores |
| Proof verification | SCEP `proof_verification` | ⚠️ Static scores in registry |
| Literature synthesis | SCEP `literature_synthesis` | ⚠️ Static scores in registry |
| Research planning | SCEP `research_planning` | ⚠️ Static scores in registry |
| Coding | Model registry | ⚠️ Static scores |
| Active benchmarking | Automated re-evaluation | ⚠️ Planned |

## Policy

Benchmark scores in the model registry are initial estimates. Active benchmarking (SIMR §11) will update scores from SCEP runs correlated with routing decisions.

## Regression detection

Defer to SCEP delta reports (`axiom/evaluation/reporting/delta_report.py`) and `make cel-health`.

## Refresh

```bash
make simr-health
make cel-health
```
