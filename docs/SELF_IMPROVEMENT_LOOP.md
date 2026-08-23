# AXIOM Phase 15 — Self-Improving Research Agent & System Regression Loop

## Overview

Phase 15 represents the culmination of the AXIOM architecture. It integrates a continuous self-evaluating regression loop that monitors pass rates across all 15 system phases, protects against capability regressions, and logs structured capability deltas.

---

## System Architecture

```
                          +-----------------------------------+
                          | System Evaluator                  |
                          | (Phase 11-14 Diagnostics)        |
                          +-----------------+-----------------+
                                            |
                                            v
                          +-----------------+-----------------+
                          | Regression Guard                  |
                          | (Baseline Pass Rate Comparison)   |
                          +-----------------+-----------------+
                                            |
                                            v
                          +-----------------+-----------------+
                          | Self-Improvement Loop             |
                          | & Capability Delta Logger         |
                          +------------------+----------------+
```

---

## Key Components

1. **`axiom/self_improvement/models.py`**: Pydantic v2 models (`RegressionStatus`, `PhaseBenchmarkResult`, `CapabilityDelta`, `SelfImprovementReport`).
2. **`axiom/self_improvement/evaluator.py`**: Evaluates system benchmarks across Phase 11, Phase 12, Phase 13, and Phase 14.
3. **`axiom/self_improvement/regression_guard.py`**: Compares current pass rate against baseline to assign `IMPROVED`, `UNCHANGED`, or `REGRESSED` status.
4. **`axiom/self_improvement/loop.py`**: Main orchestrator persisting evaluation logs to `evaluation_results/phase15/`.
5. **`axiom/services/api_gateway/routes/self_improvement.py`**: REST API router mounting `POST /api/v1/self-improvement/run`.

---

## REST API

### `POST /api/v1/self-improvement/run`
Executes an automated system regression and self-improvement evaluation cycle.

**Response:**
```json
{
  "cycle_id": "...",
  "timestamp": "2026-08-23T18:57:00Z",
  "baseline_pass_rate": 1.0,
  "current_pass_rate": 1.0,
  "regression_status": "UNCHANGED",
  "phase_summaries": [
    {
      "phase_number": 11,
      "phase_name": "Document Intelligence & Vector Retrieval",
      "benchmarks_total": 8,
      "benchmarks_passed": 8,
      "pass_rate": 1.0,
      "execution_time_ms": 0.05
    }
  ],
  "recommendations": [
    "System stable: Maintain test coverage and benchmark parity."
  ]
}
```
