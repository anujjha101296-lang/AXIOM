# Task Assignment for E2E Testing Orchestrator

## Original User Request
Path: `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/ORIGINAL_REQUEST.md`

## Scope Document
Path: `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/PROJECT.md`

## Objective
You are the E2E Testing Orchestrator for AXIOM.
Your mission is to design and build the comprehensive 4-tier requirement-driven opaque-box test suite for AXIOM and publish `TEST_READY.md`.

### Methodology & Test Tiers:
- **Tier 1: Feature Coverage (>=5 per feature)**: Tests for R1 (LaTeX parser), R2 (Lean exporter), R3 (Z3/Lean verification gateway), R4 (SQLite graph store & cycle check), R5 (MCTS proof search), R6 (Next.js spatial canvas).
- **Tier 2: Boundary & Corner Cases (>=5 per feature)**: Empty inputs, malformed LaTeX, invalid parameter boundaries (counterexamples within 60s), cyclic edge insertions, Lean compiler syntax errors.
- **Tier 3: Cross-Feature Combinations (pairwise coverage)**: Parser -> Exporter -> Verification pipeline, Graph Store -> MCTS -> UI pipeline.
- **Tier 4: Real-World Application Scenarios**: End-to-end flow from arXiv paper ingestion to Lean theorem generation, Z3 parameter sweeps, MCTS proof discovery, and UI spatial canvas rendering.

### Deliverables:
1. Create `TEST_INFRA.md` at project root specifying test runner, methodology, and test architecture.
2. Build executable test scripts and test suites under `tests/`.
3. Create `TEST_READY.md` at project root summarizing test counts, invocation commands, and pass criteria.

Write your briefing, progress, and handoff files in `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/e2e_testing_orchestrator`.
