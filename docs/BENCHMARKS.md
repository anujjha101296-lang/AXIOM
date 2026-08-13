# AXIOM Benchmark Commands

## Overview

AXIOM Phase 8 provides a scientific evaluation platform with reproducible benchmarks.
All benchmark commands are run from the repository root.

## Python Environment

```bash
# Use the project's virtual environment
.venv312/bin/python3 benchmarks/run_benchmarks.py --suite all
```

## Available Benchmark Suites

| Suite | Command | What it measures |
|-------|---------|-----------------|
| Retrieval | `--suite retrieval` | Hit@K, Recall@K, MRR using TF-IDF similarity |
| Grounding | `--suite grounding` | Evidence retrieval, claim support, citation validity |
| Agent | `--suite agent` | State machine correctness, budget compliance, cancellation |
| All | `--suite all` | All three suites |

## Running Benchmarks

### Run all benchmarks (recommended)
```bash
.venv312/bin/python3 benchmarks/run_benchmarks.py --suite all
```

### Run individual suites
```bash
# Retrieval only
.venv312/bin/python3 benchmarks/run_benchmarks.py --suite retrieval

# Grounding and citation only
.venv312/bin/python3 benchmarks/run_benchmarks.py --suite grounding

# Research agent only
.venv312/bin/python3 benchmarks/run_benchmarks.py --suite agent
```

### Establish regression baseline
```bash
.venv312/bin/python3 benchmarks/run_benchmarks.py --suite all --save-baseline
```

### Compare against baseline (regression detection)
```bash
.venv312/bin/python3 benchmarks/run_benchmarks.py --suite all --compare-baseline
```

### Fail CI pipeline if regression detected
```bash
.venv312/bin/python3 benchmarks/run_benchmarks.py --suite all --compare-baseline --fail-on-regression
```

### Show capability claims
```bash
.venv312/bin/python3 benchmarks/run_benchmarks.py --suite all --show-claims
```

## Running Tests

```bash
# Run Phase 8 evaluation tests only
.venv312/bin/python3 -m pytest tests/test_evaluation.py -v

# Run full test suite (Phases 1-8)
.venv312/bin/python3 -m pytest tests/ -v --tb=short
```

## Output Files

All results are stored in `evaluation_results/`:

```
evaluation_results/
├── baseline.json              # Regression baseline (saved with --save-baseline)
├── capability_claims.json     # Capability claims updated with measured values
├── latest_summary.json        # Summary of most recent run
└── <run_id>/
    ├── results.json           # Full run results with all metrics
    └── regression.json        # Regression comparison (if --compare-baseline used)
```

## Reproducibility

Every run records:
- `run_id`: Unique identifier
- `timestamp`: ISO 8601 UTC timestamp
- `git_commit`: Short hash of current HEAD
- `git_branch`: Current branch name
- `python_version`: Python interpreter version
- `benchmark_version`: Benchmark dataset version (currently 1.0)
- `configuration`: CLI arguments used

To reproduce a run from an existing results file:
1. Check out the git commit: `git checkout <git_commit>`
2. Use the same Python version
3. Run: `.venv312/bin/python3 benchmarks/run_benchmarks.py --suite <suite>`

## Benchmark Datasets

Datasets are version-controlled in `benchmarks/data/`:

| File | Version | Description |
|------|---------|-------------|
| `retrieval_corpus.json` | 1.0 | 3 docs, 6 chunks, 5 queries with known relevant chunk IDs |
| `grounding_cases.json` | 1.0 | 5 cases: fully supported, partial, none, conflicting, distractor |
| `agent_tasks.json` | 1.0 | 7 controlled tasks for agent state machine evaluation |

## Benchmark Metrics

### Retrieval Benchmark
- **Hit@K**: 1 if any relevant chunk is in top-K, else 0
- **Recall@K**: Fraction of relevant chunks found in top-K
- **MRR**: Mean Reciprocal Rank — where did the first correct chunk appear?

### Grounding Benchmark
- **Citation Validity Rate**: % of citations where source exists and was retrieved
- **Citation Coverage**: % of relevant chunks that were cited
- **Unsupported Citation Rate**: % of citations pointing to non-retrieved chunks

### Agent Benchmark
- **Task Completion Rate**: % of tasks reaching expected final state
- **Budget Compliance Rate**: % of tasks that respected all budget limits
- **State Machine Validity**: % of executions with valid state transitions only

## Known Limitations

See `docs/LIMITATIONS.md` for the full limitations document.
