# AXIOM Phase 12 — Autonomous Mathematical Discovery Engine

## Overview

Phase 12 transforms AXIOM into an autonomous discovery engine capable of generating candidate conjectures across algebraic, numerical, and logical domains, verifying them symbolically via SymPy, proving inequalities via Z3 SMT, and persisting learning metrics.

---

## Architecture

```
                       +------------------------+
                       | Conjecture Generator   |
                       +-----------+------------+
                                   |
                         Candidate Conjectures
                                   |
                     +-------------+-------------+
                     |                           |
                     v                           v
          +--------------------+       +--------------------+
          | SymPy Symbolic     |       | Z3 SMT Automated   |
          | Summation Engine   |       | Inequality Prover  |
          +---------+----------+       +---------+----------+
                    |                            |
                    v                            v
          Closed Form & Inductive       Counterexample Search
          Sample Verification            (SAT / UNSAT)
                    |                            |
                    +-------------+--------------+
                                  |
                                  v
                      +----------------------+
                      | Discovery Pipeline   |
                      | & Benchmark Logger   |
                      +----------------------+
```

---

## Capabilities

1. **Summation Discovery:** Automatically generates candidate series expressions $f(k)$ and derives exact closed-form algebraic solutions $\sum_{k=1}^n f(k)$, grounded with multi-sample inductive verification.
2. **SMT Automated Theorem Proving:** Verifies multi-variable algebraic inequalities using Z3 SMT solver, searching for counterexamples across integer and real domains.
3. **REST API Endpoint (`POST /discovery/run`):** Exposes discovery cycles to the frontend and autonomous agent callers.
4. **Deterministic Benchmarking:** 8 automated benchmarks verifying symbolic summation, inequality proving, and end-to-end cycle execution.

---

## REST API

### `POST /discovery/run`
Executes an autonomous discovery cycle.

**Response:**
```json
{
  "timestamp": "2026-08-22T12:24:00Z",
  "total_candidates": 7,
  "proved": 7,
  "disproved": 0,
  "results": [
    {
      "conjecture": {
        "id": "...",
        "formula_type": "SUMMATION",
        "expression_str": "2**k*k**3"
      },
      "status": "PROVED",
      "closed_form": "2*2**n*n**3 - 6*2**n*n**2 + 18*2**n*n - 26*2**n + 26",
      "verification_time_ms": 32.43
    }
  ]
}
```

---

## Verification

```bash
# Run unit tests
EMBEDDING_PROVIDER=test ENVIRONMENT=development .venv312/bin/python -m pytest tests/test_phase12_discovery.py -v

# Run 8-suite discovery benchmark
EMBEDDING_PROVIDER=test ENVIRONMENT=development .venv312/bin/python benchmarks/phase12_discovery_benchmark.py
```
