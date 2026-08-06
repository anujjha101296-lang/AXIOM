# Original User Request

## Initial Request — 2026-08-04T21:54:52+05:30

Drive orchestration of AXIOM based on ORIGINAL_REQUEST.md
Build and complete the AXIOM AI Scientific Discovery Platform according to PROJECT.md specifications:
- M1: Graph Store & Ingestion (EGS & EIE) - SQLite store, cycle detection, LaTeX AST parser, ingestion API
- M2: Logical Exporter & Verification (LRK & AVT) - Lean 4 AST exporter, SMT/Z3 counterexample gateway, Lean checker
- M3: MCTS Proof Search & Discovery (DRSP) - MCTS tactic search engine, autonomous discovery loop
- M4: Spatial Canvas UI & API Integration (UI) - Next.js spatial canvas, REST & WebSocket streaming endpoints
Ensure full test coverage, robust verification, formal integrity auditing, and end-to-end verification.

## 2026-08-05T18:44:00+05:30

<USER_REQUEST>
Design and implement the Mathematical Discovery Engine (MDE) inside AXIOM. The MDE is the core subsystem responsible for mathematical research, ontology, theorem retrieval, formal proof verification, conjecture generation, counterexample search, symbolic mathematics, and mathematical memory.

Working directory: `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom`
Integrity mode: benchmark

## Project Context
The existing AXIOM repository contains:
- `axiom/core/knowledge_graph/` — SQLite epistemic store (EGS)
- `axiom/core/parser/arxiv_parser.py` — LaTeX theorem/citation parser
- `axiom/core/verification/smt_gateway.py` — Z3 SMT gateway
- `axiom/core/verification/lean_exporter.py` — Lean 4 exporter
- `axiom/core/reasoning/mcts.py` — MCTS algebraic proof search
- `axiom/services/api_gateway/main.py` — FastAPI REST gateway

## Requirements

### R1. Mathematical Ontology (Team A)
Extend the EGS schema and ontology to support mathematical objects, definitions, theorems, lemmas, proofs, corollaries, conjectures, open problems, and equivalent statements.

### R2. Theorem Retrieval & Dependency Discovery (Team B)
Implement a retrieval system to discover relevant mathematical theorems, proof dependencies, and equivalent formulations based on syntactic and semantic matches.

### R3. Formal Proof Architecture (Team C & Team I)
Design and implement formal proof checkers and script generators for Lean 4, Coq, and Isabelle. Verify all proofs through subprocess compiler validation.

### R4. Conjecture Generation & Hypothesis Scorer (Team D)
Implement an autonomous conjecture generator that discovers new mathematical conjectures from patterns, ranks hypotheses, and discards weak conjectures.

### R5. Counterexample Search Gateway (Team E)
Design computational, symbolic (Z3/SMT), and probabilistic search systems to find counterexamples for invalid mathematical claims.

### R6. Symbolic Mathematics Interfaces (Team F)
Integrate interfaces for exact symbolic computation (e.g. SymPy) supporting exact mathematical operations and avoiding numerical approximations.

### R7. Research Strategy Planner (Team G)
Design a research strategy module to plan mathematical research, decompose open problems, identify missing lemmas, and prioritize proof attempts.

### R8. Mathematical Memory & Snapshotting (Team H)
Implement a persistent mathematical memory store that logs failed/successful proofs, research paths, dead ends, equivalent formulations, and useful transformations.

### R9. Independent Verification & Architecture Review (Team I & Team J)
Implement independent reasoning review layers that verify all verification chains and cross-check SMT/MCTS results. Critique and simplify the complete MDE architecture.

### R10. Deliverables & Documentation
Provide:
- Monorepo repository integration
- Database migrations for the expanded EGS schema
- FastAPI microservice endpoints and APIs
- Exhaustive test suite (unit and integration tests)
- Sprint breakdown, implementation order, GitHub issues, and acceptance criteria
- A detailed prize alignment report evaluating contribution to the Riemann Hypothesis (zeta zeros).

---

## Target Verification Domain
The engine must be verified on:
1. **Basic Number Theory & Algebraic Identities:** Commutativity, binomial expansion, prime factorization lemmas.
2. **Riemann Hypothesis / Analytic Number Theory:** Zeta zero tracking, complex zeros of the zeta function, and Dirichlet series representations.

---

## Acceptance Criteria

### EGS Ontological Schema & Migrations
- [ ] SQLite database migrations run successfully and create tables for `mathematical_objects`, `definitions`, `equivalent_statements`, and `memory_snapshots`.
- [ ] Nodes representing open problems and conjectures can be linked via `EQUIVALENT_TO`, `DEPENDS_ON`, and `PROVES` edges in the graph.

### Theorem Retrieval & Dependency Search
- [ ] `GET /mde/retrieval` fetches relevant theorems and equivalent formulations for a target formula with a confidence score.
- [ ] Dependencies are correctly resolved and returned as a logical dependency DAG.

### Formal Proof & Compiler Verification
- [ ] `POST /mde/proof/compile` takes Lean 4, Coq, or Isabelle code templates and runs validation. If the compiler is not present, it gracefully simulates checks and logs warning diagnostics.
- [ ] Tactic generation successfully outputs valid Mathlib statements for algebraic identities.

### Conjecture & Counterexample Gateways
- [ ] `POST /mde/conjectures/generate` proposes candidate claims and ranks them by a mathematical novelty score.
- [ ] `POST /mde/counterexample/search` performs computational Z3 parameter sweeps and exact SymPy solving to identify counterexamples.

### Memory & Research Strategy
- [ ] Mathematical memory tracks failed proof attempts, ensuring that the same failed tactics are not repeated during proof search.
- [ ] Research strategy API exposes a hierarchical decomposition of a target open problem (like the Riemann Hypothesis) into lemmas.

### Prize Alignment & Evaluation
- [ ] A final report (`docs/mde_prize_alignment.md`) details MDE's capability gaps and recommendations for future scientific discovery subsystems.
</USER_REQUEST>

## 2026-08-06T05:51:32Z

<USER_REQUEST>
The host server has restarted. Please resume execution of the Mathematical Discovery Engine (MDE) milestone executions. Keep in mind the new strategic paradigm shift:
- We operate in 3 parallel tracks: Track A (Research: Artificial Scientist), Track B (Product: Research workspace UI), Track C (Company: GTM, website, YC preparation).
- Align all work with the PMO dashboard priorities.
- Run tests and verify milestones against the SCEP evaluation runner.
</USER_REQUEST>

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

