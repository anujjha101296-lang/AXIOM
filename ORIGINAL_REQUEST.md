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
