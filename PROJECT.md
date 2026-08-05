# Project: AXIOM — Mathematical Discovery Engine (MDE)

## Architecture
AXIOM Mathematical Discovery Engine (MDE) is a core scientific discovery subsystem integrated into AXIOM monorepo.
- `axiom/core/knowledge_graph`: SQLite Relational Store, v4 Ontological Schema Migration (`mathematical_objects`, `definitions`, `equivalent_statements`, `memory_snapshots`, `failed_proof_attempts`), Pydantic models (R1, R8).
- `axiom/core/symbolic`: SymPy exact computation engine eliminating IEEE 754 float drift, arbitrary-precision zeta zero tracking, exact integer/rational arithmetic (R6).
- `axiom/core/retrieval`: Syntactic & semantic formula AST matching engine, NetworkX dependency DAG extractor (R2).
- `axiom/core/verification`: Multi-prover architecture (Lean 4, Coq, Isabelle script generators & checkers with fallback simulation), Mathlib tactic generator, Independent Verification Review Layer (R3, R9).
- `axiom/core/conjecture`: Autonomous conjecture generator (DUAL, BOUND, COMPLEX, GENERAL, COMPOSE strategies), Mathematical Novelty Scorer N(C), weak conjecture tautology/similarity filter (R4).
- `axiom/core/counterexample`: Multi-tier search gateway (Tier 1 Computational Sweep -> Tier 2 Z3 SMT Solver -> Tier 3 SymPy Exact Solver) with <60s timeout guard and EGS graph status update (R5).
- `axiom/core/strategy`: Research strategy planner, hierarchical open problem decomposition (Riemann Hypothesis zero-free region tree), Lemma Prioritization Index P(L) (R7).
- `axiom/core/memory`: Persistent working memory snapshotting, MCTS failure guard pruning known failed tactics (R8).
- `axiom/services/api_gateway/routes/mde.py`: FastAPI router providing `/mde/*` REST API microservices (R10).
- `docs/mde_prize_alignment.md`: Clay Millennium Prize alignment report evaluating MDE capabilities against Riemann Hypothesis (R10).

## Feature Inventory

| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | SQLite v4 Schema Migration | Create `mathematical_objects`, `definitions`, `equivalent_statements`, `memory_snapshots`, `failed_proof_attempts` tables | M1 | survey |
| 2 | EGS Ontological Schema Models | Pydantic models (`MathematicalObjectNode`, `DefinitionNode`, `OpenProblemNode`, `ConjectureNode`) and edges (`EQUIVALENT_TO`, `DEPENDS_ON`, `PROVES`) | M1 | survey |
| 3 | Exact SymPy Symbolic Engine | Exact rational arithmetic, polynomial identity testing, Dirichlet series expansion, float drift guard | M2 | survey |
| 4 | Formula Retrieval & Dependency DAG | Syntactic/semantic formula matching, NetworkX dependency DAG extraction, `GET /mde/retrieval` | M2 | survey |
| 5 | Multi-Prover Script Generators | Generate formal proof scripts for Lean 4, Coq, and Isabelle/HOL | M3 | survey |
| 6 | Proof Compiler Checkers & Fallback | Subprocess checkers for `lean`, `coqc`, `isabelle` with fallback AST simulation & warning diagnostics | M3 | survey |
| 7 | Mathlib Tactic Generator | Map algebraic identity patterns to specialized Mathlib tactics (`ring`, `linarith`, `nlinarith`, `positivity`) | M3 | survey |
| 8 | Formal Proof Compiler Endpoint | REST endpoint `POST /mde/proof/compile` executing formal proof compilation | M3 | survey |
| 9 | Autonomous Conjecture Generator | Candidate claim generator with 5 strategies (`DUAL`, `BOUND`, `COMPLEX`, `GENERAL`, `COMPOSE`) | M4 | survey |
| 10 | Novelty Scorer & Weak Filter | Mathematical Novelty Scorer N(C) and weak conjecture filter (tautology & similarity checks) | M4 | survey |
| 11 | Conjecture Generation Endpoint | REST endpoint `POST /mde/conjectures/generate` | M4 | survey |
| 12 | 3-Tier Counterexample Gateway | Parameter sweep -> Z3 SMT -> SymPy exact solver with <60s timeout guard | M5 | survey |
| 13 | Counterexample Graph Updater | Transition node status to `REFUTED` and insert `COUNTEREXAMPLE_FOR` edge in EGS SQLite store | M5 | survey |
| 14 | Counterexample Search Endpoint | REST endpoint `POST /mde/counterexample/search` | M5 | survey |
| 15 | Persistent Memory & Tactic Guard | Persistent SQLite snapshot store and MCTS tactic expansion failure pruning guard | M6 | survey |
| 16 | Research Strategy Planner | Open problem DAG decomposition, Lemma Prioritization Index P(L), Riemann Hypothesis zero-free tree | M6 | survey |
| 17 | Independent Verification Review Layer | Multi-verifier review layer cross-checking SMT vs MCTS vs Compiler, script sanity guard | M6 | survey |
| 18 | Strategy, Memory & Review Endpoints | Endpoints `POST /mde/strategy/plan`, `GET /mde/strategy/decompose`, `POST /mde/memory/snapshot`, `POST /mde/verification/review` | M6 | survey |
| 19 | FastAPI MDE Router Integration | Router `axiom/services/api_gateway/routes/mde.py` mounted at `/mde/*` on main app | M7 | survey |
| 20 | Exhaustive MDE Test Suite | Unit and integration tests covering Basic Number Theory & Riemann Hypothesis domains | M7 | survey |
| 21 | Millennium Prize Alignment Report | Documentation report `docs/mde_prize_alignment.md` evaluating RH capabilities | M7 | survey |

## Milestones

| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | M1: EGS Mathematical Ontology & Migrations | SQLite v4 schema migration and Pydantic node/edge schema models (R1, R8-Schema) | none | PLANNED |
| 2 | M2: Symbolic Math Interface & Theorem Retrieval Engine | SymPy exact computation engine, syntactic/semantic formula matching, dependency DAG, `GET /mde/retrieval` (R2, R6) | M1 | PLANNED |
| 3 | M3: Multi-Prover Formal Proof Architecture | Lean 4, Coq, Isabelle script generators & checkers with fallback simulation, Mathlib tactics, `POST /mde/proof/compile` (R3) | M1 | PLANNED |
| 4 | M4: Autonomous Conjecture Generation & Novelty Scorer | Pattern generator strategies, Novelty Scorer N(C), weak conjecture filter, `POST /mde/conjectures/generate` (R4) | M2 | PLANNED |
| 5 | M5: Multi-Tier Counterexample Search Gateway | 3-tier gateway (Sweep -> Z3 -> SymPy), <60s timeout, EGS status update to `REFUTED`, `POST /mde/counterexample/search` (R5) | M2, M3 | PLANNED |
| 6 | M6: Research Strategy, Memory Store & Verification Review | Persistent memory snapshotting, MCTS failure pruning guard, Research Strategy Planner (RH tree), Verification Review layer (R7, R8-Logic, R9) | M3, M4, M5 | PLANNED |
| 7 | M7: API Router Integration, Test Suite & Prize Alignment Report | FastAPI `/mde/*` router mounting, unit/integration test suite, `docs/mde_prize_alignment.md` (R10) | M6 | PLANNED |

## Interface Contracts

### EGS ↔ Retrieval
- Input: `target_formula: str, domain: Optional[str]`
- Output: `RetrievalResponsePayload(query_formula, canonical_form, matched_theorems, equivalent_formulations, dependency_dag)`

### Symbolic ↔ Counterexample
- Input: `formula_smt: str, variables: List[VariableBound], timeout_seconds: float`
- Output: `CounterexampleSearchResponse(is_valid, counterexample_found, counterexample, tier_used, execution_time_ms)`

### Multi-Prover ↔ Verification
- Input: `system: str, theorem_name: str, code: str, context: Dict`
- Output: `ProofCompileResponse(system, theorem_name, is_valid, status, diagnostics, execution_time_ms)`

### Strategy ↔ Memory
- Input: `problem_id: str, domain: str`
- Output: `StrategyPlanResponse(problem_id, root_lemma_id, total_lemmas, prioritized_queue, recommended_next_attack)`

## Code Layout
- `axiom/core/knowledge_graph/`: `schema.py`, `db.py`, `migrations.py`
- `axiom/core/symbolic/`: `sympy_engine.py`
- `axiom/core/retrieval/`: `engine.py`
- `axiom/core/verification/`: `lean_checker.py`, `coq_checker.py`, `isabelle_checker.py`, `review_controller.py`
- `axiom/core/conjecture/`: `generator.py`, `novelty_scorer.py`, `filters.py`
- `axiom/core/counterexample/`: `gateway.py`, `computational_sweep.py`
- `axiom/core/strategy/`: `planner.py`, `riemann_tree.py`
- `axiom/core/memory/`: `persistent_store.py`, `working_memory.py`
- `axiom/services/api_gateway/routes/`: `mde.py`
- `docs/`: `mde_prize_alignment.md`
- `tests/`: `test_mde_ontology.py`, `test_mde_retrieval.py`, `test_mde_proof.py`, `test_mde_conjecture.py`, `test_mde_counterexample.py`, `test_mde_strategy.py`, `test_mde_review.py`, `test_mde_pipeline.py`
