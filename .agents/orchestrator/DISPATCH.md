# Dispatch Log

## 2026-08-06T05:55:00Z

<USER_REQUEST>
Build the **Scientific Capability Evaluation Platform (SCEP)** for AXIOM Labs — the objective measurement system that determines whether every engineering sprint actually makes AXIOM a better scientist. This is an independent evaluation organization, not a feature team.

Working directory: `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom`
Integrity mode: development

## Context

AXIOM is an AI Scientific Discovery Platform targeting the Clay Millennium Prize Problems. EPIC-001 built the Mathematical Intelligence Platform (`axiom/mip/`). EPIC-002 builds the **evaluation system** that measures whether all future epics actually improve scientific capability.

This system is inspired by AlphaFold's evaluation-first philosophy: build the evaluation framework before optimizing features.

Existing codebase at `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom` includes:
- `axiom/mip/` — Mathematical Intelligence Platform (Dept A–H)
- `axiom/core/` — Knowledge graph, parser, verification, MCTS
- `axiom/evaluation/prize_readiness.py` — Basic prize readiness scorer
- `axiom/services/api_gateway/main.py` — FastAPI gateway
- `tests/` — Existing test suite

## Requirements

### R1. Scientific Capability Framework (SCF)
Define a formal, multi-dimensional capability framework with measurable levels. It must cover: mathematical reasoning, proof verification, conjecture generation, knowledge quality, research planning, counterexample search, literature synthesis, and research productivity. Each dimension must have: capability level taxonomy (L0–L5), evaluation rubrics with objective criteria, and a composite score formula.

### R2. Benchmark Suite
Implement a runnable benchmark suite with at minimum: undergraduate algebra/calculus problems (auto-gradable), published theorem reproduction tests, proof verification benchmarks, conjecture novelty benchmarks, and open problem decomposition benchmarks. Each benchmark must produce a numeric score in [0, 1] and must run in under 2 minutes.

### R3. Prize Readiness Engine
For each of the 6 Clay Millennium Prize Problems, implement a scored readiness model with: prerequisite capability map, measurable milestones, current evidence-based score in [0, 1], confidence interval, and identified capability gaps. Scores must be grounded in benchmark results — not estimated.

### R4. Capability Delta Report Generator
Implement a system that, given two benchmark snapshots (before/after a sprint), produces a structured Capability Delta Report showing: per-dimension score changes (%), prize readiness changes (problem × score delta), regression flags, weakest capability identification, and recommended next Epic. Output as both JSON and human-readable Markdown.

### R5. Evaluation API & Automated Runner
Expose a REST API (`/eval/*`) in the existing FastAPI gateway and a CLI runner (`axiom/evaluation/run_benchmarks.py`) that: runs all benchmarks against the live system, stores results in the `eval_results` SQLite table, computes all scores, generates a delta report vs. the previous run, and exits with code 0 (no regression) or 1 (regression detected).

### R6. Independent Audit Layer
The Chief Skeptic (Department J) and Independent Audit (Department I) must flag: optimistic assumptions in scores without supporting benchmark evidence, any benchmark that can be gamed by self-assessment, and any prize readiness score computed without concrete test evidence. All audit findings must be written to `docs/audit/EPIC_002_audit.md`.

## Acceptance Criteria

### Scientific Capability Framework
- [ ] Framework document exists at `docs/scientific_capability_framework.md` with L0–L5 levels for ≥8 dimensions
- [ ] Composite score formula is defined and computable from benchmark outputs

### Benchmark Suite
- [ ] `python axiom/evaluation/run_benchmarks.py` exits 0 and produces `benchmark_results.json`
- [ ] ≥5 runnable benchmark categories with ≥3 test cases each
- [ ] All benchmarks complete in < 2 minutes total

### Prize Readiness Engine
- [ ] All 6 Millennium Problems have scored readiness entries in the database
- [ ] Each score is justified by at least one benchmark measurement (not estimated)
- [ ] `GET /eval/prize-readiness` returns structured JSON for all 6 problems

### Capability Delta Report
- [ ] Running benchmarks twice produces a delta report comparing the two runs
- [ ] Delta report shows per-dimension % change and per-problem prize readiness delta
- [ ] Report saved to `docs/capability_delta_TIMESTAMP.md`

### Evaluation API
- [ ] `GET /eval/scores` returns current capability scores for all dimensions
- [ ] `POST /eval/run` triggers benchmark run and returns results
- [ ] `GET /eval/history` returns last 10 benchmark run summaries

### Regression Guard
- [ ] `run_benchmarks.py --compare-previous` exits 1 when any dimension drops > 5%
- [ ] Regression report names the specific failing dimension and score delta

## Important: Capability Delta Report Format

Every Epic completion must produce a report in this format:

```
EPIC-002 COMPLETE

Capability Delta

Knowledge Understanding
+12%

Proof Verification
+8%

Research Planning
+6%

Conjecture Generation
+4%

Counterexample Search
+0%

Prize Readiness

Riemann
31 → 34

P vs NP
28 → 30

Navier-Stokes
26 → 28

Weakest Capability
Automated Lemma Discovery

Highest Priority
Build Formal Proof & Lemma Discovery Platform

Recommended Next Epic
EPIC-003
```

After completing every task, generate: Code, Tests, Documentation, Review, Improvements. Continue automatically until EPIC-002 is complete.
</USER_REQUEST>
