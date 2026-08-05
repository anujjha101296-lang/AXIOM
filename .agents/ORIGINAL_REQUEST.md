# Original User Request

## Initial Request — 2026-08-04T16:20:06Z

<USER_REQUEST>
A continuously improving AI Scientific Discovery Platform (AXIOM) capable of parsing mathematical papers, exporting proof templates, executing SMT checks, running MCTS proof searches, and displaying results in an interactive Next.js dashboard.

Working directory: `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom`
Integrity mode: development

## Requirements

### R1. Epistemic Ingest & Parser (EIE)
Ingest LaTeX archives from arXiv, parsing theorem statements, lemmas, definitions, and bibliographic citations into a structured JSON graph format.

### R2. Logical Reasoning & Proof Exporter (LRK)
Automatically translate parsed LaTeX theorem/lemma statements and concept definitions into compilable Lean 4 theorem declarations.

### R3. Verification & SMT Gateway (AVT)
Integrate with Z3/SMT solvers to run parameter sweeps seeking counterexamples for conjectures, and local Lean 4 compilers to check proof script correctness.

### R4. Graph Store & Storage (EGS)
SQLite-backed database service storing entities and logical dependency edges with circular reference checks.

### R5. Autonomous Discovery Loop & MCTS Proof Search (DRSP)
Implement Monte Carlo Tree Search (MCTS) to explore Lean proof tactics and run continuous loop cycles managing candidate evaluations.

### R6. Spatial Canvas Dashboard (UI)
Build a Next.js/React frontend application displaying the scientific knowledge graph, nodes, citation lineages, and verification statuses on an interactive spatial canvas.

## Acceptance Criteria

### Ingestion Validation
- [ ] Parse LaTeX source documents correctly, extracting >95% of math environments and citation keys.

### Translation & Proof Search
- [ ] Translate extracted claims into Lean 4 format, compiling declarations with 0 syntax errors.
- [ ] Run MCTS proof searches to compile valid proofs for simple algebra lemmas.

### Verification Guard
- [ ] Identify and flag counterexamples for invalid parameter boundaries inside claims within 60 seconds.
- [ ] Ensure that only proofs that compile successfully in the Lean 4 compiler are designated as verified.

### Front-End Dashboard
- [ ] Launch a Next.js frontend showing an interactive node-link representation of the SQLite knowledge graph.
</USER_REQUEST>

## 2026-08-04T16:19:46Z

<USER_REQUEST>
You are the Project Orchestrator for AXIOM (AI Scientific Discovery Platform).

Original user request: /Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/ORIGINAL_REQUEST.md
Project root working directory: /Users/itachiuchiha/.gemini/antigravity/scratch/axiom
Your agent working directory: /Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/orchestrator

Please resume and drive the full orchestration of AXIOM to completion:
1. Re-read /Users/itachiuchiha/.gemini/antigravity/scratch/axiom/PROJECT.md and workspace files in .agents/orchestrator/ (BRIEFING.md, plan.md, progress.md, context.md).
2. Spawn/coordinate milestone sub-orchestrators or workers for Milestones 1 to 4 (LaTeX Ingestion & SQLite Graph, Lean Exporter & SMT Verification Gateway, MCTS Discovery Loop, Next.js Spatial Canvas UI).
3. Ensure all acceptance criteria in ORIGINAL_REQUEST.md are thoroughly tested and verified.
4. Keep .agents/orchestrator/progress.md updated.
5. When all work is done and verified, send a message to Sentinel (parent) claiming project completion with a summary of delivered components.
</USER_REQUEST>

## 2026-08-04T16:26:51Z

<USER_REQUEST>
You are the Project Orchestrator for the AXIOM project.
Your source of requirements is `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/ORIGINAL_REQUEST.md`.
Project root directory is `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom`.
Your agent directory is `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/orchestrator`.

Your job is to orchestrate, plan, dispatch tasks, and execute the complete implementation of AXIOM according to the requirements and acceptance criteria in ORIGINAL_REQUEST.md:
- R1: Epistemic Ingest & Parser (EIE)
- R2: Logical Reasoning & Proof Exporter (LRK)
- R3: Verification & SMT Gateway (AVT)
- R4: Graph Store & Storage (EGS)
- R5: Autonomous Discovery Loop & MCTS Proof Search (DRSP)
- R6: Spatial Canvas Dashboard (UI)

Ensure you maintain your `plan.md` and `progress.md` inside `.agents/orchestrator/` throughout the process. When all milestones are complete and verified, send a completion report back to Sentinel claiming project victory.
</USER_REQUEST>

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
