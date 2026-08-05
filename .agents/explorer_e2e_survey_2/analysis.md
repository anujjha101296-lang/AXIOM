# Comprehensive E2E Opaque-Box Test Suite & Infrastructure Design for AXIOM Mathematical Discovery Engine (MDE)

**Author:** Explorer 2 (E2E Testing Track)  
**Target Subsystem:** AXIOM Mathematical Discovery Engine (MDE)  
**Working Directory:** `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/explorer_e2e_survey_2`  
**Project Root:** `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom`  
**Date:** August 5, 2026  

---

## 1. Executive Summary & Testing Architecture

### 1.1 Objective & Scope
The AXIOM Mathematical Discovery Engine (MDE) represents the core mathematical reasoning, verification, theorem retrieval, conjecture generation, counterexample searching, and research strategy planning engine within the AXIOM monorepo.

As Explorer 2 for the E2E Testing Track, this report delivers an exhaustive, opaque-box, requirement-driven end-to-end (E2E) test suite design and test infrastructure specification (`TEST_INFRA.md`). The design spans all 21 features defined in `PROJECT.md § Feature Inventory` across 7 milestones (M1–M7).

### 1.2 Opaque-Box Requirement-Driven Strategy
Opaque-box testing validates MDE strictly through its public contracts, REST API endpoints (`/mde/*`), database state mutations (SQLite EGS), and multi-prover script interfaces, treating internal algorithms as sealed implementations. Every test case asserts exact, verifiable criteria:
- **API Contracts:** Request/response JSON payload schemas, HTTP status codes (200, 201, 400, 401, 404, 422, 500, 503).
- **Epistemic State Mutations:** Verification tier transitions (`TIER_0_CONJECTURE` $\to$ `TIER_2_PROVEN` or `REFUTED`), edge creation (`PROVES`, `DEPENDS_ON`, `EQUIVALENT_TO`, `COUNTEREXAMPLE_FOR`).
- **Mathematical Correctness:** Exact SymPy identity matching without IEEE 754 float drift, valid Z3 SMT counterexample assignments, Mathlib tactic compilation success.
- **SLA & Performance Bounds:** Subprocess execution timeouts ($\le 30\text{s}$), SMT search timeout guard ($\le 60\text{s}$), REST API latency targets ($\le 200\text{ms}$).

### 1.3 Test Tiering Taxonomy
The test design is structured into 4 complementary tiers:
1. **Tier 1: Feature Coverage Suite (105 Test Cases):** 5 distinct opaque-box test cases for each of the 21 features (TC-F1-01 through TC-F21-05).
2. **Tier 2: Boundary & Corner Case Suite (105 Test Cases):** 5 extreme boundary, stress, and edge test cases per feature (TC-B1-01 through TC-B21-05).
3. **Tier 3: Cross-Feature Combination Workflows (6 Complex Pipelines):** Pairwise and multi-feature interaction pipelines testing end-to-end data flow between schema, retrieval, provers, conjectures, counterexample gateways, memory, strategy, and verification review layers.
4. **Tier 4: Real-World Domain Application Scenarios (10 Scenarios):** Concrete mathematical discovery problems across Basic Number Theory / Algebraic Identities and Analytic Number Theory / Riemann Hypothesis (RH) domains.

---

## 2. Feature Inventory & Requirement Mapping

| Feature # | Feature Name | Core Component / Path | Primary Requirement | Target Milestone |
|---|---|---|---|---|
| **F1** | SQLite v4 Schema Migration | `axiom/core/knowledge_graph/migrations.py` | R1, R8 | M1 |
| **F2** | EGS Ontological Schema Models | `axiom/core/knowledge_graph/schema.py` | R1, R8 | M1 |
| **F3** | Exact SymPy Symbolic Engine | `axiom/core/symbolic/sympy_engine.py` | R6 | M2 |
| **F4** | Formula Retrieval & Dependency DAG | `axiom/core/retrieval/engine.py` | R2 | M2 |
| **F5** | Multi-Prover Script Generators | `axiom/core/verification/lean_checker.py`, `coq_checker.py`, `isabelle_checker.py` | R3 | M3 |
| **F6** | Proof Compiler Checkers & Fallback | `axiom/core/verification/` | R3 | M3 |
| **F7** | Mathlib Tactic Generator | `axiom/core/verification/lean_exporter.py` | R3 | M3 |
| **F8** | Formal Proof Compiler Endpoint | `axiom/services/api_gateway/routes/mde.py` (`POST /mde/proof/compile`) | R3 | M3 |
| **F9** | Autonomous Conjecture Generator | `axiom/core/conjecture/generator.py` | R4 | M4 |
| **F10** | Novelty Scorer & Weak Filter | `axiom/core/conjecture/novelty_scorer.py`, `filters.py` | R4 | M4 |
| **F11** | Conjecture Generation Endpoint | `axiom/services/api_gateway/routes/mde.py` (`POST /mde/conjectures/generate`) | R4 | M4 |
| **F12** | 3-Tier Counterexample Gateway | `axiom/core/counterexample/gateway.py` | R5 | M5 |
| **F13** | Counterexample Graph Updater | `axiom/core/counterexample/gateway.py`, `axiom/core/knowledge_graph/db.py` | R5 | M5 |
| **F14** | Counterexample Search Endpoint | `axiom/services/api_gateway/routes/mde.py` (`POST /mde/counterexample/search`) | R5 | M5 |
| **F15** | Persistent Memory & Tactic Guard | `axiom/core/memory/persistent_store.py` | R8 | M6 |
| **F16** | Research Strategy Planner | `axiom/core/strategy/planner.py`, `riemann_tree.py` | R7 | M6 |
| **F17** | Independent Verification Review Layer | `axiom/core/verification/review_controller.py` | R9 | M6 |
| **F18** | Strategy, Memory & Review Endpoints | `axiom/services/api_gateway/routes/mde.py` | R7, R8, R9 | M6 |
| **F19** | FastAPI MDE Router Integration | `axiom/services/api_gateway/main.py` | R10 | M7 |
| **F20** | Exhaustive MDE Test Suite | `tests/test_mde_*.py` | R10 | M7 |
| **F21** | Millennium Prize Alignment Report | `docs/mde_prize_alignment.md` | R10 | M7 |

---

## 3. Tier 1: Feature Coverage Suite (105 Test Cases)

### Feature 1: SQLite v4 Schema Migration
- **TC-F1-01: Table Creation Verification**
  - *Objective:* Confirm that running `run_migrations()` creates `mathematical_objects`, `definitions`, `equivalent_statements`, `memory_snapshots`, and `failed_proof_attempts`.
  - *Action:* Execute `run_migrations(db_conn)`. Query `sqlite_master` for table names.
  - *Assertion:* All 5 tables exist; SQL column definitions match v4 schema.
- **TC-F1-02: Idempotent Migration Execution**
  - *Objective:* Verify `run_migrations()` can be executed repeatedly on an active database without raising schema errors or duplicating tables.
  - *Action:* Execute `run_migrations(db_conn)` 3 consecutive times.
  - *Assertion:* Execution returns successfully with 0 exceptions; table structure remains intact.
- **TC-F1-03: Foreign Key Constraint Enforcement**
  - *Objective:* Ensure `failed_proof_attempts` rejects inserts with non-existent `claim_id` foreign keys when PRAGMA foreign_keys=ON.
  - *Action:* Insert record into `failed_proof_attempts` with `claim_id="non_existent_id"`.
  - *Assertion:* SQLite raises `sqlite3.IntegrityError` (Foreign key constraint failed).
- **TC-F1-04: Index Existence Verification**
  - *Objective:* Verify indexes on high-frequency lookup columns (`claim_id`, `problem_id`, `strategy`).
  - *Action:* Query `sqlite_master` where `type='index'`.
  - *Assertion:* Indices `idx_failed_proofs_claim`, `idx_snapshots_problem`, and `idx_math_obj_type` are present.
- **TC-F1-05: Schema Version Pragma Check**
  - *Objective:* Confirm `user_version` PRAGMA is updated to `4` after migration.
  - *Action:* Execute `PRAGMA user_version;`.
  - *Assertion:* Result equals `4`.

### Feature 2: EGS Ontological Schema Models
- **TC-F2-01: MathematicalObjectNode Instantiation & Pydantic Validation**
  - *Objective:* Instantiating `MathematicalObjectNode` with valid attributes succeeds and serialized JSON includes discriminator `type`.
  - *Action:* Instantiate `MathematicalObjectNode(id="mo_1", name="Zeta Zero", domain="analytic_number_theory", formula="zeta(s)=0")`.
  - *Assertion:* Model dump contains `type="MATHEMATICAL_OBJECT"`; fields match inputs.
- **TC-F2-02: DefinitionNode & Formal Specification Binding**
  - *Objective:* Create `DefinitionNode` containing Lean 4 code string in `formal_specification`.
  - *Action:* Instantiate `DefinitionNode(id="def_1", name="Prime Definition", formal_specification="def is_prime (n : ℕ) : Prop := ...")`.
  - *Assertion:* `formal_specification` preserves multi-line string exactly.
- **TC-F2-03: Edge Model Discriminator & Confidence Constraints**
  - *Objective:* Verify `Edge` accepts new MDE relationship types (`EQUIVALENT_TO`, `DEPENDS_ON`, `PROVES`, `COUNTEREXAMPLE_FOR`) with confidence score in $[0.0, 1.0]$.
  - *Action:* Create `Edge(source_id="n1", target_id="n2", type="COUNTEREXAMPLE_FOR", confidence=0.95)`.
  - *Assertion:* Object valid; confidence value preserved.
- **TC-F2-04: Polymorphic ScientificNode Serialization**
  - *Objective:* Ensure Pydantic polymorphic union correctly deserializes `MathematicalObjectNode` and `OpenProblemNode` from raw JSON dicts.
  - *Action:* Parse dict list via `RootModel[List[ScientificNode]].model_validate(...)`.
  - *Assertion:* Returned objects are instances of respective node sub-classes.
- **TC-F2-05: OpenProblemNode Priority & State Verification**
  - *Objective:* Validate `OpenProblemNode` fields (`difficulty_tier`, `prize_bounty`, `status`).
  - *Action:* Instantiate `OpenProblemNode(id="op_rh", name="Riemann Hypothesis", prize_bounty="$1,000,000", status="OPEN")`.
  - *Assertion:* Object attributes match expected types.

### Feature 3: Exact SymPy Symbolic Engine
- **TC-F3-01: Exact Rational Arithmetic Verification**
  - *Objective:* Prove symbolic engine evaluates $1/3 + 1/6 = 1/2$ without floating point loss.
  - *Action:* Call `sympy_engine.evaluate_rational("1/3 + 1/6")`.
  - *Assertion:* Return type is `Rational(1, 2)`; string representation is `"1/2"`.
- **TC-F3-02: Polynomial Identity Testing**
  - *Objective:* Confirm $(x+y)^2 - (x^2 + 2xy + y^2) = 0$ evaluates to exact identity zero.
  - *Action:* Call `sympy_engine.is_identity("(x+y)**2", "x**2 + 2*x*y + y**2")`.
  - *Assertion:* Returns `True`; simplified difference is `0`.
- **TC-F3-03: Dirichlet Series Expansion**
  - *Objective:* Expand Dirichlet series terms $\sum_{n=1}^N n^{-s}$ for specified $N$ and symbolic $s$.
  - *Action:* Call `sympy_engine.expand_dirichlet_series(terms=4)`.
  - *Assertion:* Output formula is `"1 + 2**(-s) + 3**(-s) + 4**(-s)"`.
- **TC-F3-04: Arbitrary Precision Float Drift Guard**
  - *Objective:* Verify high precision calculation of $\pi$ to 50 decimal places does not drift or truncate.
  - *Action:* Call `sympy_engine.eval_precision("pi", dps=50)`.
  - *Assertion:* String output matches known 50-digit $\pi$ sequence (`3.1415926535897932384626433832795028841971693993751`).
- **TC-F3-05: Symbolic Derivative & Simplification**
  - *Objective:* Differentiate $f(s) = s^2 + \sin(s)$ symbolically with respect to $s$.
  - *Action:* Call `sympy_engine.differentiate("s**2 + sin(s)", "s")`.
  - *Assertion:* Returns `"2*s + cos(s)"`.

### Feature 4: Formula Retrieval & Dependency DAG
- **TC-F4-01: Syntactic AST Formula Matching**
  - *Objective:* Retrieve identical formula nodes from EGS based on AST equivalence.
  - *Action:* Execute `GET /mde/retrieval?formula=a%2Bb%3Db%2Ba`.
  - *Assertion:* HTTP 200; `matched_theorems` includes "Commutativity of Addition" with match score $1.0$.
- **TC-F4-02: Semantic Equivalence Retrieval**
  - *Objective:* Match semantically equivalent formulas under variable renaming ($x^2 - y^2 = (x-y)(x+y)$ vs $a^2 - b^2 = (a-b)(a+b)$).
  - *Action:* Query `/mde/retrieval` with renamed variable formula.
  - *Assertion:* Response includes canonical formula match with `semantic_match=True`.
- **TC-F4-03: NetworkX Dependency DAG Extraction**
  - *Objective:* Fetch dependency DAG for a target theorem node and verify acyclic graph structure.
  - *Action:* Call `retrieval_engine.get_dependency_dag(node_id="thm_rh_lemma1")`.
  - *Assertion:* Returned payload contains `nodes` and `edges`; NetworkX `is_directed_acyclic_graph(dag)` evaluates to `True`.
- **TC-F4-04: Retrieval Confidence Ranking**
  - *Objective:* Verify retrieved theorems are sorted in descending order of confidence score.
  - *Action:* Query `/mde/retrieval?formula=x%5E2%2B1` with multi-result dataset.
  - *Assertion:* `matched_theorems[i].score >= matched_theorems[i+1].score` for all $i$.
- **TC-F4-05: Domain Filtered Retrieval Query**
  - *Objective:* Restrict theorem retrieval to specific mathematical domain (e.g. `analytic_number_theory`).
  - *Action:* Query `/mde/retrieval?formula=zeta(s)&domain=analytic_number_theory`.
  - *Assertion:* All returned theorems belong strictly to `analytic_number_theory`.

### Feature 5: Multi-Prover Script Generators
- **TC-F5-01: Lean 4 Script Exporter Formatting**
  - *Objective:* Generate valid compilable Lean 4 theorem syntax from standard claim object.
  - *Action:* Call `lean_generator.export_script(name="add_comm", statement="a + b = b + a", vars={"a":"Nat", "b":"Nat"})`.
  - *Assertion:* Output contains `theorem add_comm (a b : Nat) : a + b = b + a := by`.
- **TC-F5-02: Coq Script Generator Formatting**
  - *Objective:* Generate valid Coq lemma syntax with imports and tactics.
  - *Action:* Call `coq_generator.export_script(name="add_comm", statement="a + b = b + a", vars={"a":"nat", "b":"nat"})`.
  - *Assertion:* Output contains `Require Import Arith.` and `Lemma add_comm : forall a b : nat, a + b = b + a.`.
- **TC-F5-03: Isabelle/HOL Script Generator Formatting**
  - *Objective:* Generate valid Isabelle theory and theorem script structure.
  - *Action:* Call `isabelle_generator.export_script(name="add_comm", statement="a + b = b + a", vars={"a":"nat", "b":"nat"})`.
  - *Assertion:* Output contains `theory Scratch imports Main begin` and `theorem add_comm: "a + b = b + a"`.
- **TC-F5-04: Multi-Prover Context Variable Mapping**
  - *Objective:* Ensure mathematical type aliases (`N`, `Z`, `R`, `C`) map to correct prover-native types (`Nat`, `nat`, `real`, `Complex`).
  - *Action:* Pass type map `{"x": "C"}` to Lean, Coq, Isabelle generators.
  - *Assertion:* Lean generates `Complex`, Coq generates `C`, Isabelle generates `complex`.
- **TC-F5-05: Proof Body Embedding**
  - *Objective:* Verify proof tactic bodies (`ring`, `auto`, `simp`) are properly indented inside generated scripts.
  - *Action:* Pass `proof_body=["ring"]` to `export_script`.
  - *Assertion:* Generated text contains exact tactic line with proper indentation.

### Feature 6: Proof Compiler Checkers & Fallback
- **TC-F6-01: Lean 4 Subprocess Compilation**
  - *Objective:* Execute local Lean 4 binary on valid script and capture exit code 0.
  - *Action:* Call `lean_checker.verify_script(lean_code)` with installed Lean binary.
  - *Assertion:* `is_valid=True`, `returncode=0`, `diagnostics=[]`.
- **TC-F6-02: Coq Subprocess Compilation**
  - *Objective:* Execute `coqc` on valid Coq script file and confirm success.
  - *Action:* Call `coq_checker.verify_script(coq_code)`.
  - *Assertion:* `is_valid=True`, `status="compiled"`.
- **TC-F6-03: Isabelle Subprocess Compilation**
  - *Objective:* Execute `isabelle process` on valid Isabelle file.
  - *Action:* Call `isabelle_checker.verify_script(isabelle_code)`.
  - *Assertion:* `is_valid=True`, `status="compiled"`.
- **TC-F6-04: Graceful Missing Prover Fallback Simulation**
  - *Objective:* When prover binary is missing from PATH, checker gracefully simulates AST check and logs warning.
  - *Action:* Execute `verify_script()` in environment where prover binary path is unlinked.
  - *Assertion:* `is_valid=True`, `status="simulated_check"`, warning diagnostic logged in response payload.
- **TC-F6-05: Compiler Diagnostics Error Extraction**
  - *Objective:* Parse stderr line numbers and error messages when prover encounters code syntax error.
  - *Action:* Execute `verify_script()` with invalid tactic `unknown_tactic_xyz`.
  - *Assertion:* `is_valid=False`, `diagnostics` contains line number and raw error message.

### Feature 7: Mathlib Tactic Generator
- **TC-F7-01: Polynomial Equality Ring Tactic Mapping**
  - *Objective:* Map polynomial identities to `ring` tactic.
  - *Action:* Call `tactic_generator.infer_tactic("(a+b)^2 = a^2 + 2*a*b + b^2")`.
  - *Assertion:* Returns `["ring"]`.
- **TC-F7-02: Linear Inequality Linarith Tactic Mapping**
  - *Objective:* Map linear inequalities ($x + 1 > x$) to `linarith`.
  - *Action:* Call `tactic_generator.infer_tactic("x + 1 > x")`.
  - *Assertion:* Returns `["linarith"]`.
- **TC-F7-03: Non-Linear Inequality Nlinarith Tactic Mapping**
  - *Objective:* Map non-linear inequalities ($x^2 + y^2 \ge 0$) to `nlinarith`.
  - *Action:* Call `tactic_generator.infer_tactic("x^2 + y^2 >= 0")`.
  - *Assertion:* Returns `["nlinarith"]`.
- **TC-F7-04: Expression Positivity Tactic Mapping**
  - *Objective:* Map positivity claims ($e^x > 0$) to `positivity`.
  - *Action:* Call `tactic_generator.infer_tactic("exp(x) > 0")`.
  - *Assertion:* Returns `["positivity"]`.
- **TC-F7-05: Composite Tactic Sequence Assembly**
  - *Objective:* Combine premise introduction (`intros`) with calculation tactic (`ring`).
  - *Action:* Call `tactic_generator.build_sequence(claim="forall x y, (x+y)^2 = ...")`.
  - *Assertion:* Sequence is `["intros", "ring"]`.

### Feature 8: Formal Proof Compiler Endpoint
- **TC-F8-01: Lean 4 POST /mde/proof/compile Success**
  - *Objective:* Submit Lean 4 proof compile request over REST API and receive HTTP 200 success response.
  - *Action:* `POST /mde/proof/compile` with body `{"system": "lean4", "theorem_name": "thm_ring", "code": "..."}`.
  - *Assertion:* HTTP 200; body `{"status": "success", "is_valid": true, "system": "lean4"}`.
- **TC-F8-02: Coq POST /mde/proof/compile Verification**
  - *Objective:* Send Coq compilation request via REST API.
  - *Action:* `POST /mde/proof/compile` with `system="coq"`.
  - *Assertion:* HTTP 200; `is_valid=True`.
- **TC-F8-03: Isabelle POST /mde/proof/compile Verification**
  - *Objective:* Send Isabelle compilation request via REST API.
  - *Action:* `POST /mde/proof/compile` with `system="isabelle"`.
  - *Assertion:* HTTP 200; `is_valid=True`.
- **TC-F8-04: Proof Compile Fallback Response Schema**
  - *Objective:* Verify schema response fields when compiler binary is simulated.
  - *Action:* `POST /mde/proof/compile` with simulated environment flag.
  - *Assertion:* `status` is `"simulated"`, `diagnostics` contains `"simulated compiler check"`.
- **TC-F8-05: Execution Time Measurement Payload**
  - *Objective:* Ensure API response payload includes `execution_time_ms` float > 0.0.
  - *Action:* Inspect response payload of `POST /mde/proof/compile`.
  - *Assertion:* `execution_time_ms` is present and $\ge 0.0$.

### Feature 9: Autonomous Conjecture Generator
- **TC-F9-01: DUAL Strategy Conjecture Generation**
  - *Objective:* Generate dual statement conjectures from existing lattice theorems.
  - *Action:* Call `generator.generate(strategy="DUAL", max_count=5)`.
  - *Assertion:* Returns list of 5 candidate claims with metadata `strategy="DUAL"`.
- **TC-F9-02: BOUND Strategy Conjecture Generation**
  - *Objective:* Generate upper/lower bound conjectures for target functions.
  - *Action:* Call `generator.generate(strategy="BOUND", max_count=5)`.
  - *Assertion:* Claims contain inequality operators (`<=`, `>=`).
- **TC-F9-03: COMPLEX Strategy Zero Conjectures**
  - *Objective:* Generate conjectures regarding zero distribution in complex plane.
  - *Action:* Call `generator.generate(strategy="COMPLEX", max_count=3)`.
  - *Assertion:* Formula statements include complex variable $s = \sigma + i t$.
- **TC-F9-04: GENERAL Strategy Algebraic Generalization**
  - *Objective:* Generalize single variable identities to $N$-variable statements.
  - *Action:* Call `generator.generate(strategy="GENERAL", max_count=3)`.
  - *Assertion:* Output formulas contain $N$-indexed sum/product notation.
- **TC-F9-05: COMPOSE Functional Strategy**
  - *Objective:* Generate composed conjectures $f(g(x)) = h(x)$.
  - *Action:* Call `generator.generate(strategy="COMPOSE", max_count=3)`.
  - *Assertion:* Formula metadata indicates composed transformation origin.

### Feature 10: Novelty Scorer & Weak Filter
- **TC-F10-01: Novelty Score N(C) Calculation**
  - *Objective:* Compute mathematical novelty score $N(C) \in [0.0, 1.0]$ based on syntactic distance from EGS corpus.
  - *Action:* Call `novelty_scorer.score(conjecture_node)`.
  - *Assertion:* Returns float value between $0.0$ and $1.0$.
- **TC-F10-02: Tautology Triviality Filter**
  - *Objective:* Rejects trivial claims like $x = x$ or $x + 0 = x$.
  - *Action:* Call `filters.is_tautology("x = x")`.
  - *Assertion:* Returns `True`; claim rejected with reason `"tautology"`.
- **TC-F10-03: Near-Duplicate AST Similarity Filter**
  - *Objective:* Filter out candidate conjectures with >95% tree similarity to existing theorems.
  - *Action:* Pass candidate matching existing theorem to `filters.is_duplicate()`.
  - *Assertion:* Returns `True`; claim discarded.
- **TC-F10-04: Novelty Threshold Filtering**
  - *Objective:* Ensure conjectures scoring below `min_novelty_score` are excluded from output list.
  - *Action:* Call `filter_conjectures(candidates, min_score=0.7)`.
  - *Assertion:* All remaining claims have $N(C) \ge 0.7$.
- **TC-F10-05: Candidate Ranking Order**
  - *Objective:* Verify generated conjectures are returned in descending order of novelty score $N(C)$.
  - *Action:* Inspect sorted candidate array from generator.
  - *Assertion:* `candidates[i].novelty_score >= candidates[i+1].novelty_score`.

### Feature 11: Conjecture Generation Endpoint
- **TC-F11-01: POST /mde/conjectures/generate Success**
  - *Objective:* Execute REST request to generate conjectures and receive HTTP 200 payload.
  - *Action:* `POST /mde/conjectures/generate` with `{"strategies": ["DUAL", "BOUND"], "max_conjectures": 5}`.
  - *Assertion:* HTTP 200; payload contains `conjectures` array of length $\le 5$.
- **TC-F11-02: Multi-Strategy POST Request**
  - *Objective:* Request conjectures across all 5 strategies simultaneously.
  - *Action:* Pass `strategies: ["DUAL", "BOUND", "COMPLEX", "GENERAL", "COMPOSE"]`.
  - *Assertion:* Response includes conjectures generated by each requested strategy.
- **TC-F11-03: Novelty Score Threshold Parameter Passing**
  - *Objective:* Pass `min_novelty_score: 0.8` query/body parameter.
  - *Action:* Send POST request with high threshold filter.
  - *Assertion:* All returned items in payload have `novelty_score >= 0.8`.
- **TC-F11-04: Response Payload Schema Validation**
  - *Objective:* Verify returned JSON adheres strictly to `ConjectureGenerationResponsePayload`.
  - *Action:* Validate response body against Pydantic schema.
  - *Assertion:* Schema validation passes with 0 missing required fields.
- **TC-F11-05: Execution Latency SLA Check**
  - *Objective:* Ensure endpoint returns response within 2000ms SLA for 10 requested conjectures.
  - *Action:* Measure API request round-trip time.
  - *Assertion:* Round-trip duration $< 2.0\text{s}$.

### Feature 12: 3-Tier Counterexample Gateway
- **TC-F12-01: Tier 1 Computational Sweep Counterexample Detection**
  - *Objective:* Identify integer counterexample via Tier 1 parameter grid search.
  - *Action:* Run gateway on false conjecture $n^2 + n + 41 \text{ is prime}$ for $n \in [1, 50]$.
  - *Assertion:* Counterexample found at $n=40$ ($40^2 + 40 + 41 = 41^2$, composite); `tier_used=1`.
- **TC-F12-02: Tier 2 Z3 SMT Solver Counterexample Search**
  - *Objective:* Find modular arithmetic counterexample using Z3 SMT solver gateway.
  - *Action:* Solve $x^2 \equiv 2 \pmod 5$ with Z3 solver.
  - *Assertion:* Z3 returns `unsat` (no counterexample exists) or `sat` for invalid modular statements; `tier_used=2`.
- **TC-F12-03: Tier 3 SymPy Exact Solver Counterexample Search**
  - *Objective:* Solve non-linear symbolic expression counterexample via SymPy exact solver.
  - *Action:* Run solver on $e^{i \pi x} = 1$ for non-integer $x$.
  - *Assertion:* SymPy returns exact symbolic counterexample; `tier_used=3`.
- **TC-F12-04: Automatic Tier Escalation Flow**
  - *Objective:* Verify gateway attempts Tier 1, escalates to Tier 2 on grid exhaustion, and Tier 3 on SMT non-linear failure.
  - *Action:* Pass non-linear continuous claim to gateway.
  - *Assertion:* Execution trace shows Tier $1 \to \text{Tier } 2 \to \text{Tier } 3$ escalation sequence.
- **TC-F12-05: Execution Time Measurement in Gateway**
  - *Objective:* Verify gateway returns precise `execution_time_ms`.
  - *Action:* Run counterexample gateway on benchmark problem.
  - *Assertion:* `execution_time_ms` is positive float.

### Feature 13: Counterexample Graph Updater
- **TC-F13-01: Claim Node Status Transition to REFUTED**
  - *Objective:* Update claim node status in EGS SQLite database from `CONJECTURED` to `REFUTED`.
  - *Action:* Call `graph_updater.apply_counterexample(claim_id="c_101", counterexample_data=...)`.
  - *Assertion:* Node record in database has `status="REFUTED"`.
- **TC-F13-02: COUNTEREXAMPLE_FOR Edge Insertion**
  - *Objective:* Create directed edge `COUNTEREXAMPLE_FOR` from counterexample node to target claim node.
  - *Action:* Query SQLite `edges` table following graph updater call.
  - *Assertion:* Edge exists with `type="COUNTEREXAMPLE_FOR"`, `source_id="ce_node"`, `target_id="c_101"`.
- **TC-F13-03: Verification Tier Downgrade to TIER_0**
  - *Objective:* Ensure claim node tier is set to `TIER_0_CONJECTURE` upon refutation.
  - *Action:* Inspect node tier column in database.
  - *Assertion:* `tier` equals `0`.
- **TC-F13-04: Provenance Metadata Attachment**
  - *Objective:* Attach solver details, tier used, and execution timestamp into edge provenance metadata JSON.
  - *Action:* Read `provenance` JSON field from SQLite edge record.
  - *Assertion:* Contains keys `solver_tier`, `counterexample_val`, `timestamp`.
- **TC-F13-05: DB Transaction Atomic Commit**
  - *Objective:* Guarantee status update and edge creation occur atomically inside single SQLite transaction.
  - *Action:* Simulate failure during edge creation step.
  - *Assertion:* Node status rollback occurs; node status remains `CONJECTURED`.

### Feature 14: Counterexample Search Endpoint
- **TC-F14-01: POST /mde/counterexample/search Success (Refutation Found)**
  - *Objective:* Call REST API for false conjecture and receive HTTP 200 with counterexample assignment.
  - *Action:* `POST /mde/counterexample/search` with payload `{"formula_smt": "(x > 2) and (x^2 < 4)", "variables": [{"name": "x", "type": "Real"}]}`.
  - *Assertion:* HTTP 200; `counterexample_found=true`, `counterexample` contains variable assignments.
- **TC-F14-02: POST /mde/counterexample/search Success (No Counterexample)**
  - *Objective:* Call API for true theorem statement ($x^2 \ge 0$).
  - *Action:* `POST /mde/counterexample/search` with valid real identity.
  - *Assertion:* HTTP 200; `counterexample_found=false`, `is_valid=true`.
- **TC-F14-03: Response Payload Tier Field Validation**
  - *Objective:* Verify response JSON reports the exact solver tier that resolved the query (`tier_used: 1|2|3`).
  - *Action:* Inspect returned `tier_used` field.
  - *Assertion:* `tier_used` is an integer in $\{1, 2, 3\}$.
- **TC-F14-04: EGS DB State Sync Triggering via API**
  - *Objective:* Ensure endpoint automatically triggers graph updater when counterexample is discovered.
  - *Action:* Execute endpoint with `conjecture_id="conj_test_55"`.
  - *Assertion:* SQLite query confirms `conj_test_55` status is updated to `REFUTED`.
- **TC-F14-05: Timeout Guard Enforcement (<60s)**
  - *Objective:* API enforces max execution timeout of 60 seconds and returns graceful timeout JSON payload.
  - *Action:* `POST /mde/counterexample/search` with `timeout_seconds: 2.0` on complex undecidable SMT formula.
  - *Assertion:* Returns HTTP 200 within 2.5s with `status="timeout"`, `counterexample_found=false`.

### Feature 15: Persistent Memory & Tactic Guard
- **TC-F15-01: Failed Proof Attempt SQLite Logging**
  - *Objective:* Store failed Lean/MCTS tactic sequences into `failed_proof_attempts` SQLite table.
  - *Action:* Call `persistent_store.log_failed_attempt(claim_id="c_1", tactic_sequence=["ring", "simp"])`.
  - *Assertion:* Row inserted in SQLite table with matching `claim_id` and serialized tactic sequence.
- **TC-F15-02: MCTS Tactic Expansion Failure Pruning**
  - *Objective:* MCTS proof search queries failure store and prunes known failed tactic branches.
  - *Action:* Execute MCTS solver with mock step generator when failure guard is active.
  - *Assertion:* MCTS search tree excludes pruned tactic branch; 0 redundant evaluations executed.
- **TC-F15-03: Memory Snapshot Serialization (POST /mde/memory/snapshot)**
  - *Objective:* Create full state snapshot of active research session working memory.
  - *Action:* Execute `POST /mde/memory/snapshot` with payload `{"problem_id": "prob_rh"}`.
  - *Assertion:* HTTP 200; SQLite `memory_snapshots` table receives new snapshot record with generated `snapshot_id`.
- **TC-F15-04: Memory Snapshot Restoration**
  - *Objective:* Restore working memory state from saved snapshot ID.
  - *Action:* Call `persistent_store.load_snapshot(snapshot_id="snap_101")`.
  - *Assertion:* Working memory object matches exact state prior to snapshot export.
- **TC-F15-05: Working Memory Reset (POST /memory/reset)**
  - *Objective:* Clear session working memory store.
  - *Action:* `POST /memory/reset`.
  - *Assertion:* HTTP 200; subsequent `GET /memory/context` returns empty active memory dictionary.

### Feature 16: Research Strategy Planner
- **TC-F16-01: Open Problem DAG Decomposition**
  - *Objective:* Decompose major open problem into hierarchical sub-lemma tree.
  - *Action:* Call `planner.decompose_problem("RH")`.
  - *Assertion:* Returns DAG with root node "Riemann Hypothesis" and child sub-lemmas.
- **TC-F16-02: Lemma Prioritization Index P(L) Calculation**
  - *Objective:* Compute Lemma Prioritization Index $P(L) = w_1 \cdot \text{novelty} + w_2 \cdot \text{solvability} + w_3 \cdot \text{impact}$.
  - *Action:* Call `planner.compute_priority(lemma_node)`.
  - *Assertion:* Returns priority float score $P(L) \ge 0.0$.
- **TC-F16-03: Riemann Hypothesis Zero-Free Tree Loading**
  - *Objective:* Load domain-specific zero-free region strategy decomposition tree for RH.
  - *Action:* Call `riemann_tree.get_zero_free_tree()`.
  - *Assertion:* Tree contains specific lemmas (e.g. "de la Vallée-Poussin zero-free region bound").
- **TC-F16-04: Recommended Attack Vector Output**
  - *Objective:* Determine highest priority leaf lemma for next proof attempt.
  - *Action:* Execute `POST /mde/strategy/plan` for problem `"RH"`.
  - *Assertion:* Payload contains `recommended_next_attack` matching highest $P(L)$ sub-lemma.
- **TC-F16-05: Dependency Order Prioritization Queue**
  - *Objective:* Ensure prioritized queue orders prerequisites ahead of dependent lemmas.
  - *Action:* Inspect returned strategy queue array.
  - *Assertion:* For every edge $A \to B$ ($B$ depends on $A$), $A$ appears earlier in queue than $B$.

### Feature 17: Independent Verification Review Layer
- **TC-F17-01: Multi-Verifier Consensus Approval**
  - *Objective:* Review controller approves verification claim when Lean compiler, Z3 SMT, and SymPy solvers all agree.
  - *Action:* Call `review_controller.review_claim(claim_id="c_valid")`.
  - *Assertion:* Returns `review_status="APPROVED"`, `consensus=True`.
- **TC-F17-02: Rejection on Compiler Failure**
  - *Objective:* Controller rejects proof claim if formal Lean compiler fails, even if SMT solver succeeded.
  - *Action:* Submit claim with valid SMT output but syntax error in Lean script.
  - *Assertion:* Returns `review_status="REJECTED"`, reason `"Compiler check failed"`.
- **TC-F17-03: Inconsistency Flagging (SMT Refutation vs MCTS Proof)**
  - *Objective:* Detect contradiction when SMT finds counterexample but MCTS claims proof.
  - *Action:* Submit conflicting verification evidence.
  - *Assertion:* Returns `review_status="CONTRADICTION_FLAGGED"`, triggers alert event.
- **TC-F17-04: Script Sanity Guard Verification**
  - *Objective:* Reject proof scripts containing illegal axioms (`sorry`, `axiom_of_choice_unproven`) or cheat tactics.
  - *Action:* Pass Lean script containing `sorry`.
  - *Assertion:* Sanity guard flags script; `is_verified=False`.
- **TC-F17-05: Review Audit Logging**
  - *Objective:* Persist full review evaluation log into SQLite database audit table.
  - *Action:* Complete verification review.
  - *Assertion:* Audit log record written with verifier signatures and timestamp.

### Feature 18: Strategy, Memory & Review Endpoints
- **TC-F18-01: POST /mde/strategy/plan REST Endpoint**
  - *Objective:* Validate strategy plan generation REST API.
  - *Action:* `POST /mde/strategy/plan` with body `{"problem_id": "RH", "domain": "analytic_number_theory"}`.
  - *Assertion:* HTTP 200; JSON payload conforms to `StrategyPlanResponse`.
- **TC-F18-02: GET /mde/strategy/decompose REST Endpoint**
  - *Objective:* Validate problem decomposition DAG REST API.
  - *Action:* `GET /mde/strategy/decompose?problem_id=RH`.
  - *Assertion:* HTTP 200; JSON response contains `dag_nodes` and `dag_edges`.
- **TC-F18-03: POST /mde/memory/snapshot REST Endpoint**
  - *Objective:* Validate memory snapshot REST API.
  - *Action:* `POST /mde/memory/snapshot` with body `{"session_name": "s1"}`.
  - *Assertion:* HTTP 200; response returns `snapshot_id`.
- **TC-F18-04: POST /mde/verification/review REST Endpoint**
  - *Objective:* Validate independent verification review REST API.
  - *Action:* `POST /mde/verification/review` with body `{"claim_id": "c_202"}`.
  - *Assertion:* HTTP 200; returns `review_status` and verifier breakdown.
- **TC-F18-05: Uniform Error Handling Schema Across Endpoints**
  - *Objective:* Verify 404 response for invalid `problem_id` or `claim_id` follows standard error format `{"detail": "..."}`.
  - *Action:* Send requests with non-existent IDs to all 4 endpoints.
  - *Assertion:* All return HTTP 404 with structured JSON detail string.

### Feature 19: FastAPI MDE Router Integration
- **TC-F19-01: Router Mounting Prefix Verification (/mde/*)**
  - *Objective:* Confirm all MDE sub-routes are correctly mounted under `/mde/` API prefix.
  - *Action:* Fetch FastAPI OpenAPI specification JSON at `/openapi.json`.
  - *Assertion:* All MDE endpoint paths begin strictly with `/mde/`.
- **TC-F19-02: CORS Header Verification on MDE Routes**
  - *Objective:* Verify CORS headers are attached to responses on OPTIONS pre-flight calls to `/mde/*`.
  - *Action:* Send OPTIONS request to `/mde/proof/compile`.
  - *Assertion:* HTTP 200/204; header `access-control-allow-origin` is present.
- **TC-F19-03: Bearer Authentication Token Enforcement**
  - *Objective:* Ensure unauthenticated requests to protected `/mde/*` routes return HTTP 401 Unauthorized.
  - *Action:* Call `POST /mde/conjectures/generate` without Authorization header.
  - *Assertion:* HTTP 401 Unauthorized.
- **TC-F19-04: Prometheus Metrics Counter Instrumentation**
  - *Objective:* Ensure MDE API calls increment Prometheus metric `axiom_api_requests_total`.
  - *Action:* Make 3 requests to `/mde/retrieval`, then query `/metrics`.
  - *Assertion:* `/metrics` text output contains `axiom_api_requests_total{endpoint="/mde/retrieval"...}`.
- **TC-F19-05: Centralized HTTP 500 Unhandled Exception Handling**
  - *Objective:* Unexpected backend exceptions return clean HTTP 500 JSON detail without leaking raw stack trace to client.
  - *Action:* Mock internal runtime crash in solver service during API call.
  - *Assertion:* HTTP 500; JSON contains `"detail": "Internal server error during proof compilation"`.

### Feature 20: Exhaustive MDE Test Suite
- **TC-F20-01: Unit Test Suite Execution Pass Rate**
  - *Objective:* Execute all MDE core unit tests (`tests/test_mde_*.py`) and confirm 100% pass rate.
  - *Action:* Execute `pytest tests/test_mde_*.py -m unit`.
  - *Assertion:* 0 test failures, 0 errors.
- **TC-F20-02: Integration Test Suite Execution Pass Rate**
  - *Objective:* Execute MDE integration test suite against live SQLite and mocked provers.
  - *Action:* Execute `pytest tests/test_mde_*.py -m integration`.
  - *Assertion:* All integration tests pass.
- **TC-F20-03: Code Coverage SLA Check (>=90%)**
  - *Objective:* Measure code coverage of `axiom/core/` and `axiom/services/api_gateway/routes/mde.py`.
  - *Action:* Execute `pytest --cov=axiom.core --cov=axiom.services.api_gateway.routes.mde`.
  - *Assertion:* Total coverage percentage $\ge 90\%$.
- **TC-F20-04: Pytest Fixture Teardown Isolation**
  - *Objective:* Confirm test database fixtures clean up completely between test runs.
  - *Action:* Run 2 sequential tests modifying SQLite DB.
  - *Assertion:* Second test sees pristine database state; 0 leaking rows from first test.
- **TC-F20-05: Domain Test Suite Filter Execution**
  - *Objective:* Execute tests tagged specifically with `@pytest.mark.rh_domain`.
  - *Action:* Execute `pytest -m rh_domain`.
  - *Assertion:* Only RH domain test cases run and pass.

### Feature 21: Millennium Prize Alignment Report
- **TC-F21-01: Documentation File Existence & Path Check**
  - *Objective:* Verify `docs/mde_prize_alignment.md` exists at exact project path.
  - *Action:* Check file existence at `docs/mde_prize_alignment.md`.
  - *Assertion:* File exists; byte size $> 2000$ bytes.
- **TC-F21-02: Markdown Section Header Structure Compliance**
  - *Objective:* Confirm report contains required sections (Executive Summary, Capability Matrix, RH Zero Tracking, Capability Gaps, Future Roadmap).
  - *Action:* Parse headings in `docs/mde_prize_alignment.md`.
  - *Assertion:* All 5 section headers are present.
- **TC-F21-03: Capability Gap Analysis Section Verification**
  - *Objective:* Confirm report explicitly documents current MDE capability gaps regarding Riemann Hypothesis.
  - *Action:* Search text for "Capability Gaps".
  - *Assertion:* Section lists explicit limitations (e.g. "Infinite-dimensional spectral theory verification missing").
- **TC-F21-04: Mathematical Formulation Formatting Verification**
  - *Objective:* Ensure mathematical equations are formatted in valid LaTeX math blocks (`$...$` / `$$...$$`).
  - *Action:* Validate LaTeX syntax inside Markdown file.
  - *Assertion:* No unclosed `$` delimiters; formulas render cleanly.
- **TC-F21-05: Acceptance Criteria Compliance Sign-off**
  - *Objective:* Verify document contains sign-off checklist confirming MDE evaluation alignment.
  - *Action:* Read final section of document.
  - *Assertion:* Alignment checklist present with checked items `[x]`.

---

## 4. Tier 2: Boundary & Corner Case Suite (105 Test Cases)

### Feature 1: SQLite v4 Schema Migration
- **TC-B1-01: Interrupted Transaction Rollback Handling:** Kill DB connection mid-migration; verify database remains at original v3 schema state without partial corrupt tables.
- **TC-B1-02: Pre-existing Table Name Collision:** Execute migration when table `definitions` already exists with incompatible columns; verify informative `MigrationError` raised.
- **TC-B1-03: Corrupt Database File Recovery:** Run migration against corrupted SQLite header file; verify system catches `sqlite3.DatabaseError` gracefully.
- **TC-B1-04: Maximum Column Length Data Insert:** Insert 10MB text blob into `statement` column of `mathematical_objects`; verify SQLite handles blob without memory allocation crash.
- **TC-B1-05: Index Unique Constraint Violation:** Insert duplicate primary keys into `memory_snapshots`; verify `sqlite3.IntegrityError` raised and caught.

### Feature 2: EGS Ontological Schema Models
- **TC-B2-01: Null & Empty String Validation:** Attempt to instantiate `MathematicalObjectNode` with empty string `name=""` or `id=None`; verify Pydantic raises `ValidationError`.
- **TC-B2-02: Extreme Metadata Nesting Depth:** Pass 20-level nested dictionary in node `metadata`; verify serializer handles depth or rejects with structured depth limit error.
- **TC-B2-03: Invalid Enum String Ingestion:** Pass invalid edge type `"INVALID_EDGE_TYPE"` to `Edge`; verify Pydantic raises clear enum validation error.
- **TC-B2-04: Self-Referential Edge Validation:** Create edge where `source_id == target_id`; verify cycle checker flags or permits based on edge type constraints.
- **TC-B2-05: Out-of-Bounds Confidence Float:** Pass `confidence=1.5` or `confidence=-0.1` to `Edge`; verify Pydantic enforces $0.0 \le \text{confidence} \le 1.0$.

### Feature 3: Exact SymPy Symbolic Engine
- **TC-B3-01: Division by Zero Expression Parsing:** Evaluate `"x / 0"` or `"1 / (x - x)"`; verify engine catches `ZeroDivisionError` and returns symbolic undefined state.
- **TC-B3-02: Highly Complex High-Degree Polynomial Expansion:** Expand $(x+1)^{100}$; verify recursion depth limit is respected and operation completes within 5 seconds SLA.
- **TC-B3-03: Non-Convergent Dirichlet Series Terms:** Compute Dirichlet series with $s = -1$ (divergent); verify engine returns symbolic expression without infinite sum loop.
- **TC-B3-04: Malformed LaTeX Syntax Input:** Pass unparseable string `"x ++ ** 3 \frac{"` to SymPy parser; verify engine raises `SymPyParsingError` rather than crashing process.
- **TC-B3-05: Transcendental Number Rounding Edge Cases:** Evaluate $\sin(\pi)$ exactly; verify exact result is integer `0` rather than float `1.2246467991473532e-16`.

### Feature 4: Formula Retrieval & Dependency DAG
- **TC-B4-01: Cyclic Dependency Graph Detection:** EGS graph contains circular edge references ($A \to B \to C \to A$); verify retrieval engine detects cycle and raises `CyclicDependencyError`.
- **TC-B4-02: Unparseable Query Formula Input:** Query `/mde/retrieval` with malformed syntax `formula="((((a+"`; verify API returns HTTP 422 Unprocessable Entity.
- **TC-B4-03: Empty Database Retrieval Query:** Query retrieval endpoint when SQLite database contains 0 nodes; verify returns HTTP 200 with empty list `matched_theorems: []`.
- **TC-B4-04: Query String Length Overflow:** Send 100,000 character formula string to `/mde/retrieval`; verify request payload size limit (HTTP 413 Payload Too Large).
- **TC-B4-05: Disconnected Graph Component DAG Extraction:** Query dependency DAG for isolated node with 0 edges; verify returns DAG containing exactly 1 node and 0 edges.

### Feature 5: Multi-Prover Script Generators
- **TC-B5-01: Reserved Keyword Collision in Theorem Name:** Pass Lean keyword `theorem_name="def"` or `theorem_name="import"`; verify generator automatically sanitizes/escapes name (`def_thm`).
- **TC-B5-02: Special Character & Unicode Sanitization:** Theorem statement contains LaTeX symbols ($\forall, \exists, \in, \mathbb{R}$); verify generator correctly translates or escapes symbols for target prover.
- **TC-B5-03: Empty Variable Mapping Dictionary:** Pass `vars={}`; verify generator produces valid parameterless theorem declaration syntax.
- **TC-B5-04: Multi-Line Nested Formula String Formatting:** Export formula containing 50 line break characters; verify generator strips/formats string into valid single prover statement.
- **TC-B5-05: Conflicting Variable Type Annotations:** Variable `x` declared as both `Nat` and `Real` in context payload; verify generator raises `TypeConflictError`.

### Feature 6: Proof Compiler Checkers & Fallback
- **TC-B6-01: Subprocess Process Timeout (>30s):** Lean compiler enters infinite tactic execution loop; verify subprocess runner terminates process at 30.0s and returns timeout status.
- **TC-B6-02: Corrupted Executable Binary File:** Point compiler path to corrupt zero-byte binary; verify checker catches `OSError` / `PermissionError` and triggers simulated fallback.
- **TC-B6-03: Multi-Megabyte Stderr Output Spooling:** Compiler generates 50MB of diagnostic warning text; verify stdout/stderr reader truncates spool to prevent memory exhaustion.
- **TC-B6-04: Concurrent Subprocess Execution Load:** Trigger 50 parallel compilation requests simultaneously; verify process pool throttles concurrency without OS fork failure.
- **TC-B6-05: Non-Zero Exit Code Diagnostic Parsing:** Compiler fails with returncode 1; verify raw stderr text is captured accurately in `diagnostics` array.

### Feature 7: Mathlib Tactic Generator
- **TC-B7-01: Unrecognized Complex Pattern Fallback:** Pass unclassifiable mathematical statement; verify tactic generator returns fallback `["sorry"]` without throwing exception.
- **TC-B7-02: Malformed Premise Inequality Input:** Pass contradictory premises ($x > 0$ and $x < 0$); verify generator produces valid `linarith` tactic call without crash.
- **TC-B7-03: Code Injection Protection in Tactic Parameters:** Statement contains raw code injection string `"; DROP TABLE nodes; --"`; verify tactic generator escapes input safely.
- **TC-B7-04: Multi-Variable Polynomial Degree Overflow:** Generate tactic for 10-variable 20th-degree polynomial identity; verify generator selects `ring` tactic efficiently.
- **TC-B7-05: Deeply Nested Function Composition:** Infer tactic for $\sin(\cos(\tan(x)))$; verify generator handles nested AST without stack overflow.

### Feature 8: Formal Proof Compiler Endpoint
- **TC-B8-01: Invalid System Target Parameter:** `POST /mde/proof/compile` with `system="python"`; verify returns HTTP 422 with detail listing allowed systems (`lean4`, `coq`, `isabelle`).
- **TC-B8-02: Missing Required Field 'code':** Send payload missing `code` field; verify Pydantic raises missing required field HTTP 422 error.
- **TC-B8-03: Payload Size Exceeding 1MB:** Send 5MB text payload in `code`; verify API Gateway rejects request with HTTP 413 Payload Too Large.
- **TC-B8-04: Unauthenticated Proof Compile Request:** Omit Bearer token; verify returns HTTP 401 Unauthorized.
- **TC-B8-05: High Latency Subprocess Simulation:** Mock slow 29s compiler execution; verify API completes before HTTP timeout and returns valid response.

### Feature 9: Autonomous Conjecture Generator
- **TC-B9-01: Empty Source Knowledge Base:** Execute generator when EGS graph contains 0 theorems; verify returns empty candidate list `[]` without error.
- **TC-B9-02: Zero Max Count Parameter Request:** Call `generate(max_count=0)`; verify returns empty list immediately.
- **TC-B9-03: Invalid Strategy Name String:** Request strategy `"SUPER_INTELLIGENT"`; verify generator raises `InvalidStrategyError`.
- **TC-B9-04: Infinite Recursive Expression Composition:** `COMPOSE` strategy encounters circular concept definitions; verify recursion depth limit caps tree expansion at depth 5.
- **TC-B9-05: Negative Max Count Parameter:** Call `generate(max_count=-5)`; verify input validator raises `ValueError`.

### Feature 10: Novelty Scorer & Weak Filter
- **TC-B10-01: Identical Statement Comparison (Self-Similarity):** Score candidate against identical statement; verify similarity evaluates to $1.0$ and claim is filtered.
- **TC-B10-02: NaN / Infinity Score Handling:** Mathematical expression generates division by zero in novelty metric; verify scorer catches floating point exception and assigns $N(C) = 0.0$.
- **TC-B10-03: Extreme Threshold Filter Boundary (min_score=1.0):** Filter candidates with `min_score=1.0`; verify all non-perfect candidates are filtered out.
- **TC-B10-04: Zero Threshold Filter Boundary (min_score=0.0):** Filter candidates with `min_score=0.0`; verify all candidate claims pass filter.
- **TC-B10-05: Single-Node AST Depth Claims:** Score trivial single variable claim `"x"`; verify filtered out as zero-depth claim.

### Feature 11: Conjecture Generation Endpoint
- **TC-B11-01: Negative max_conjectures Payload Parameter:** Send `{"max_conjectures": -10}`; verify HTTP 422 validation error returned.
- **TC-B11-02: min_novelty_score Out of Range (>1.0):** Send `{"min_novelty_score": 1.5}`; verify HTTP 422 validation error returned.
- **TC-B11-03: Empty Strategies Array Request:** Send `{"strategies": []}`; verify HTTP 422 requiring at least 1 strategy.
- **TC-B11-04: Backend Generator Service Down (500 Error):** Mock generator exception; verify API returns HTTP 500 JSON formatted detail.
- **TC-B11-05: Rate Limiting Enforcement:** Send 100 requests in 1 second; verify API returns HTTP 429 Too Many Requests.

### Feature 12: 3-Tier Counterexample Gateway
- **TC-B12-01: Non-Linear SMT Undecidable Statement:** Pass complex non-linear SMT formula that Z3 cannot solve; verify Z3 returns `unknown`, gateway escalates to Tier 3 SymPy.
- **TC-B12-02: Timeout Guard Trigger (<60s Exceeded):** Solver process exceeds 60s limit; verify gateway aborts process, logs timeout diagnostic, and returns `counterexample_found=false`.
- **TC-B12-03: Variable Bound Range Underflow/Overflow:** Variable bounds specified as $[-10^{50}, 10^{50}]$; verify Tier 1 computational sweep gracefully skips overflow or scales step size.
- **TC-B12-04: Empty Variables List in SMT Formula:** Pass `variables=[]`; verify gateway raises `InvalidFormulaError`.
- **TC-B12-05: Division by Zero in Parameter Sweep:** Formula contains $1/x$; parameter sweep tests $x=0$; verify sweep handles division error and continues to next grid point.

### Feature 13: Counterexample Graph Updater
- **TC-B13-01: Update Non-Existent Claim ID:** Attempt to update claim ID `"ghost_id_999"`; verify updater raises `NodeNotFoundError` and rolls back transaction.
- **TC-B13-02: Duplicate Edge Insertion Conflict:** Attempt to insert duplicate `COUNTEREXAMPLE_FOR` edge between same source/target nodes; verify SQLite ignores or handles unique constraint gracefully.
- **TC-B13-03: Refuting Already VERIFIED Theorem Node:** Attempt to apply counterexample to node with status `VERIFIED`; verify system flags critical contradiction error before updating.
- **TC-B13-04: Database Connection Lock Retry Handling:** SQLite database locked by concurrent reader; verify updater retries transaction with exponential backoff.
- **TC-B13-05: Null Provenance Metadata Handling:** Pass `provenance=None`; verify updater substitutes default empty dictionary `{}` without crashing.

### Feature 14: Counterexample Search Endpoint
- **TC-B14-01: Negative timeout_seconds Parameter:** Send `{"timeout_seconds": -5.0}`; verify HTTP 422 error returned.
- **TC-B14-02: Malformed SMT Formula Syntax:** Send `formula_smt="x AND OR == 5"`; verify API returns HTTP 400 Bad Request with SMT parsing error details.
- **TC-B14-03: Non-Existent conjecture_id in DB:** Endpoint called with `conjecture_id="missing_123"`; verify search executes but DB update step returns clean warning payload.
- **TC-B14-04: Concurrent Search Endpoint Requests:** Execute 10 simultaneous counterexample searches over REST API; verify all complete independently without thread race conditions.
- **TC-B14-05: Zero Timeout Parameter (Immediate Timeout):** Send `timeout_seconds: 0.0`; verify endpoint returns immediately with `status="timeout"`.

### Feature 15: Persistent Memory & Tactic Guard
- **TC-B15-01: Logging Duplicate Failed Tactic Sequence:** Log exact same failed tactic sequence for a claim multiple times; verify database handles via counter increment or idempotent insert.
- **TC-B15-02: Loading Corrupted Snapshot Data:** Attempt to load snapshot with corrupted JSON payload; verify store catches JSON decode error and raises `SnapshotCorruptedError`.
- **TC-B15-03: Snapshot Storage Limit Exceeded:** Memory store exceeds maximum configured snapshot count (e.g. 1000); verify oldest snapshot is pruned automatically.
- **TC-B15-04: Empty Tactic Sequence Failure Logging:** Log empty tactic list `[]`; verify validator requires non-empty list.
- **TC-B15-05: Concurrent Memory Snapshot Writes:** Two worker threads write snapshot simultaneously; verify SQLite WAL mode handles concurrent transaction without database disk I/O failure.

### Feature 16: Research Strategy Planner
- **TC-B16-01: Unknown Problem ID Request:** Request plan for `problem_id="NON_EXISTENT"`; verify planner returns HTTP 404 Not Found.
- **TC-B16-02: Cyclic Lemma Dependency Graph Decomposition:** Decompose problem whose lemmas contain circular dependencies; verify planner breaks cycles cleanly during DAG construction.
- **TC-B16-03: Zero Weight Factor Priority Index:** Compute $P(L)$ with all weights $w_1=w_2=w_3=0$; verify priority falls back to uniform 0.0 without divide-by-zero crash.
- **TC-B16-04: Maximum Decomposition Depth Boundary:** Decompose problem with tree depth >100; verify max depth cap prevents stack overflow.
- **TC-B16-05: Root Lemma with Zero Children:** Decompose single standalone lemma; verify DAG returned contains exactly 1 node and 0 edges.

### Feature 17: Independent Verification Review Layer
- **TC-B17-01: Conflicting Verifier Signals (SMT Valid vs Compiler Failed):** SMT reports valid, Lean compiler reports syntax error; verify review controller flags conflict and sets `review_status="REJECTED"`.
- **TC-B17-02: Missing Verification Evidence Payload:** Submit claim review request with no proof scripts or SMT payloads attached; verify returns `review_status="INSUFFICIENT_EVIDENCE"`.
- **TC-B17-03: Verifier Execution Exception:** One verifier throws unexpected runtime crash; verify review layer handles exception gracefully and completes remaining verifiers.
- **TC-B17-04: Illegal Tactic Injection inside Lean Script:** Proof body contains `unsafe`, `sorry`, or custom unsafe Lean macro; verify sanity guard flags script as unverified.
- **TC-B17-05: Extreme Subprocess Timeout in Reviewer:** Compiler verifier hangs for 30s; verify review layer enforces per-verifier timeout guard.

### Feature 18: Strategy, Memory & Review Endpoints
- **TC-B18-01: Unprocessable Entity Schema Errors (HTTP 422):** Send malformed JSON body to all 4 endpoints; verify each returns HTTP 422 with detailed field error locations.
- **TC-B18-02: Unauthenticated Endpoint Calls (HTTP 401):** Call all 4 endpoints without Bearer token; verify all return HTTP 401.
- **TC-B18-03: Non-Existent Resource ID Parameters (HTTP 404):** Query non-existent problem/claim IDs; verify clean 404 responses.
- **TC-B18-04: Zero-Byte Request Body:** Send empty request body to POST endpoints; verify returns HTTP 422.
- **TC-B18-05: Query Parameter Type Mismatches:** Send string to integer parameter (`limit="abc"`); verify returns HTTP 422.

### Feature 19: FastAPI MDE Router Integration
- **TC-B19-01: Malformed Bearer Authorization Token:** Send `Authorization: Bearer invalid_token_xyz`; verify API returns HTTP 401 Unauthorized.
- **TC-B19-02: Non-Existent Route Path (/mde/unknown_route):** Request invalid path under `/mde/`; verify returns clean HTTP 404 Not Found.
- **TC-B19-03: HTTP Method Not Allowed (405):** Send GET request to `POST /mde/proof/compile`; verify returns HTTP 405 Method Not Allowed with `Allow: POST` header.
- **TC-B19-04: High Concurrency Spike Load (100 parallel requests):** Fire 100 concurrent requests; verify router maintains SLA without dropping connections.
- **TC-B19-05: Large Payload Compression Handling:** Send gzipped JSON payload; verify router decompresses correctly or returns appropriate status.

### Feature 20: Exhaustive MDE Test Suite
- **TC-B20-01: Test Execution with Missing Local Provers:** Run full pytest suite in environment without `lean` or `z3` binaries installed; verify tests fallback to simulation gracefully and pass.
- **TC-B20-02: Pytest Process Interruption Cleanup:** Send SIGINT (Ctrl+C) during test run; verify temporary test SQLite files are cleaned up.
- **TC-B20-03: Low Memory Test Execution Environment:** Run test suite under constrained RAM (512MB); verify memory footprint stays under limit.
- **TC-B20-04: Flaky Test Retry Guard:** Run test suite with `--reruns 2`; verify 0 non-deterministic failures occur.
- **TC-B20-05: Test Database Lock Contention:** Run multi-threaded pytest worker threads (`pytest -n 4`); verify SQLite WAL mode prevents database lock collisions.

### Feature 21: Millennium Prize Alignment Report
- **TC-B21-01: Missing File Path Handling:** Verify system build check fails gracefully with clear error if `docs/mde_prize_alignment.md` is removed.
- **TC-B21-02: Broken Document Hyperlinks Check:** Scan document for markdown relative links (`[link](../path.md)`); verify all referenced target files exist.
- **TC-B21-03: Invalid Markdown Table Syntax:** Validate markdown table formatting; verify all table rows have matching pipe column counts.
- **TC-B21-04: Incomplete Section Header Template:** Check for unfilled placeholder strings like `[TBD]` or `[TODO]`; verify 0 placeholder strings remain in production document.
- **TC-B21-05: Encoding Verification (UTF-8):** Verify file is encoded strictly in clean UTF-8 without byte order marks (BOM).

---

## 5. Tier 3: Cross-Feature Combination Workflows

### Pipeline 1: Epistemic Ingest $\to$ Formula Retrieval $\to$ Dependency DAG $\to$ Research Strategy
```
+------------------+       +-------------------+       +-------------------+       +--------------------+
|  LaTeX Ingest &  | ----> | Formula Retrieval | ----> | Dependency DAG    | ----> | Strategy Planner   |
|  Schema Store    |       | Engine            |       | Extractor         |       | Priority Queue     |
|  (F1, F2)        |       | (F4)              |       | (F4)              |       | (F16)              |
+------------------+       +-------------------+       +-------------------+       +--------------------+
```
- **Step 1:** Ingest LaTeX paper containing new theorem definition $T_1$. Write `MathematicalObjectNode` and `DefinitionNode` to SQLite v4 EGS database (F1, F2).
- **Step 2:** Execute formula retrieval query `GET /mde/retrieval` matching AST of $T_1$ against existing corpus (F4).
- **Step 3:** Extract directed dependency DAG using NetworkX connecting $T_1$ to prerequisite lemmas $L_1, L_2$ (F4).
- **Step 4:** Pass dependency DAG to Research Strategy Planner (`POST /mde/strategy/plan`). Planner computes Lemma Prioritization Index $P(L)$ for $L_1, L_2$ and pushes them to the active proof attack queue (F16).
- **Assertion:** End-to-end trace completes; $P(L)$ correctly ranks prerequisite $L_1$ ahead of $T_1$; SQLite stores relationship edges `DEPENDS_ON`.

### Pipeline 2: Conjecture Generation $\to$ Novelty Filter $\to$ Counterexample Search $\to$ Graph Status Mutation
```
+-------------------+       +-------------------+       +-------------------+       +--------------------+
| Autonomous        | ----> | Novelty Scorer N  | ----> | 3-Tier Counter-   | ----> | EGS Graph Updater  |
| Generator (DUAL)  |       | & Weak Filter     |       | example Gateway   |       | (REFUTED Status)   |
| (F9)              |       | (F10)             |       | (F12, F14)        |       | (F13)              |
+-------------------+       +-------------------+       +-------------------+       +--------------------+
```
- **Step 1:** Trigger autonomous conjecture generator using strategy `DUAL` (`POST /mde/conjectures/generate`) to yield candidate claim $C_1$ (F9).
- **Step 2:** Run candidate $C_1$ through Novelty Scorer $N(C_1) = 0.85$ and tautology filter (F10). Confirm $C_1$ passes filter.
- **Step 3:** Dispatch $C_1$ formula to 3-tier Counterexample Gateway (`POST /mde/counterexample/search`). Tier 1 sweep passes; Tier 2 Z3 SMT solver discovers counterexample variable assignment within 1.2s (F12, F14).
- **Step 4:** Counterexample Graph Updater automatically mutates node $C_1$ status in SQLite database from `CONJECTURED` to `REFUTED` and creates `COUNTEREXAMPLE_FOR` edge (F13).
- **Assertion:** DB query confirms $C_1$ status is `REFUTED`; edge provenance contains Z3 solver metadata; HTTP responses strictly match schemas.

### Pipeline 3: Multi-Prover Script Gen $\to$ Mathlib Tactics $\to$ Formal Proof Compiler $\to$ Verification Review Layer
```
+-------------------+       +-------------------+       +-------------------+       +--------------------+
| Multi-Prover      | ----> | Mathlib Tactic    | ----> | Subprocess Proof  | ----> | Verification Review|
| Script Generator  |       | Mapper (ring)     |       | Compiler Check    |       | Layer Consensus    |
| (F5)              |       | (F7)              |       | (F6, F8)          |       | (F17)              |
+-------------------+       +-------------------+       +-------------------+       +--------------------+
```
- **Step 1:** Request formal proof compilation for algebraic claim $(a+b)^2 = a^2 + 2ab + b^2$ via `POST /mde/proof/compile` (F8).
- **Step 2:** Mathlib Tactic Generator maps polynomial identity pattern to `ring` tactic sequence (F7).
- **Step 3:** Multi-Prover Script Generator formats Lean 4 script containing declaration and tactic body (F5).
- **Step 4:** Proof Compiler Checker executes subprocess `lean` compiler (or fallback simulator) to verify proof script (F6).
- **Step 5:** Independent Verification Review Layer cross-checks compiler stdout, SMT validity, and sanity script guard (`no sorry`), returning consensus review approval `APPROVED` (F17).
- **Assertion:** Response payload has `is_valid=true`, `compiler_status="compiled"`, `review_status="APPROVED"`, `verification_tier=2`.

### Pipeline 4: Research Strategy Decomposition $\to$ Memory Failure Guard $\to$ MCTS Proof Search Pruning
```
+-------------------+       +-------------------+       +-------------------+       +--------------------+
| Open Problem DAG  | ----> | MCTS Proof Search | ----> | Log Failure to    | ----> | Tactic Guard Prunes|
| Decomposition     |       | Attempt Failure   |       | Persistent Store  |       | Subsequent Searches|
| (F16)             |       | (F15)             |       | (F1, F15)         |       | (F15)              |
+-------------------+       +-------------------+       +-------------------+       +--------------------+
```
- **Step 1:** Research Strategy Planner decomposes open problem lemma into attack steps (F16).
- **Step 2:** MCTS proof search attempts tactic expansion sequence $S_1 = [\text{simp}, \text{auto}]$ on target claim, resulting in proof search dead end (F15).
- **Step 3:** Failed tactic sequence $S_1$ is logged into SQLite table `failed_proof_attempts` via Persistent Memory Store (F1, F15).
- **Step 4:** Trigger second MCTS proof search attempt on same claim. Persistent Memory Tactic Guard intercepts step expansion generator and prunes branch $S_1$ upfront.
- **Assertion:** 0 evaluations wasted on $S_1$; MCTS explores alternative tactic branch $S_2 = [\text{ring}]$; proof search efficiency is verifiably improved.

### Pipeline 5: SymPy Exact Engine $\to$ Z3 SMT Solver $\to$ FastAPI Gateway Router Integration
```
+-------------------+       +-------------------+       +-------------------+       +--------------------+
| SymPy Engine      | ----> | Z3 SMT Solver     | ----> | FastAPI Route     | ----> | Prometheus Metric  |
| Exact Arithmetic |       | Boundary Check    |       | Endpoint Handler  |       | Metric Increment   |
| (F3)              |       | (F12)             |       | (F19, F18)        |       | (F19)              |
+-------------------+       +-------------------+       +-------------------+       +--------------------+
```
- **Step 1:** Client sends verification request to `POST /mde/counterexample/search` via FastAPI Router (F19, F18).
- **Step 2:** Gateway passes formula parameters to SymPy Exact Engine to convert floating-point bounds into exact rational fractions (F3).
- **Step 3:** Formatted exact formula passed to Z3 SMT solver to perform bounded parameter check (F12).
- **Step 4:** API gateway returns HTTP 200 JSON response and increments Prometheus metric `axiom_api_requests_total{endpoint="/mde/counterexample/search", status="200"}` (F19).
- **Assertion:** No float drift occurs during bound translation; Z3 receives exact rational parameters; Prometheus `/metrics` reflects endpoint execution counter increment.

### Pipeline 6: Full Autonomous Discovery & Verification Cycle
```
+-------------------+       +-------------------+       +-------------------+       +--------------------+
| Ingest & Graph    | ----> | Conjecture Gen &  | ----> | Multi-Prover      | ----> | Memory Snapshot &  |
| Setup             |       | Counterex Sweep   |       | Formal Proof      |       | Prize Alignment    |
| (F1, F2, F4)      |       | (F9, F10, F12)    |       | (F5, F6, F8, F17) |       | (F15, F16, F21)    |
+-------------------+       +-------------------+       +-------------------+       +--------------------+
```
- **Step 1:** Initialize SQLite v4 database (F1, F2). Seed with target domain concepts (Basic Number Theory / Riemann Hypothesis) (F4).
- **Step 2:** Run autonomous conjecture generator (`POST /mde/conjectures/generate`) to yield candidate claim $C_{new}$ (F9, F10).
- **Step 3:** Pass $C_{new}$ to 3-tier counterexample gateway (`POST /mde/counterexample/search`). Confirm no counterexample exists ($C_{new}$ is plausible) (F12).
- **Step 4:** Generate Lean 4 formal proof script and compile via `POST /mde/proof/compile` (F5, F6, F8). Independent Verification Review Layer approves proof (F17).
- **Step 5:** Mutate node status in SQLite to `VERIFIED` (`TIER_2_PROVEN`). Persist active working memory snapshot (`POST /mde/memory/snapshot`) (F15). Update Research Strategy Planner state (F16) and confirm prize alignment reporting consistency (F21).
- **Assertion:** Entire discovery loop completes automatically; database state progresses from conjecture to verified theorem; all API contracts satisfied.

---

## 6. Tier 4: Real-World Domain Application Scenarios

### 6.1 Basic Number Theory & Algebraic Identity Scenarios

#### Scenario 1.1: Commutativity of Natural Addition ($a + b = b + a$)
- **Domain Context:** Fundamental Peano arithmetic identity over $\mathbb{N}$.
- **Input Payload:**
  - Theorem Statement: `forall (a b : Nat), a + b = b + a`
  - Formula SMT: `(assert (not (= (+ a b) (+ b a))))`, variables: `a: Int (a >= 0), b: Int (b >= 0)`
- **E2E Execution Flow:**
  1. Submit SMT formula to `/mde/counterexample/search`. Z3 returns `unsat` (no counterexample exists).
  2. Send proof compile request to `/mde/proof/compile` with `system="lean4"`. Mathlib tactic generator maps pattern to `omega` / `ring`.
  3. Compiler checker executes Lean 4 validation script.
- **Expected Assertion:**
  - Counterexample search: `counterexample_found=false`, `is_valid=true`.
  - Proof compilation: `is_valid=true`, `compiler_status="compiled"`.
  - Node created in SQLite EGS with `status="VERIFIED"`, `tier=2`.

#### Scenario 1.2: Binomial Expansion Identity ($(a+b)^2 = a^2 + 2ab + b^2$)
- **Domain Context:** Elementary ring theory identity over commutative rings.
- **Input Payload:**
  - Start Expression: `(a + b)^2`
  - Target Expression: `a^2 + 2*a*b + b^2`
  - Variables: `{"a": "Real", "b": "Real"}`
- **E2E Execution Flow:**
  1. Call SymPy engine to verify exact identity `is_identity("(a+b)**2", "a**2 + 2*a*b + b**2")`. SymPy evaluates difference to exact `0`.
  2. Send compilation request to `/mde/proof/compile`. Mathlib tactic generator maps to `ring`.
  3. Lean 4 exporter generates script:
     ```lean
     theorem binomial_sq (a b : ℝ) : (a + b)^2 = a^2 + 2*a*b + b^2 := by ring
     ```
- **Expected Assertion:**
  - SymPy exact match returns `True`.
  - Proof compiler returns `is_valid=true`.
  - Verification review layer outputs `review_status="APPROVED"`.

#### Scenario 1.3: Fundamental Theorem of Arithmetic / Prime Factorization Lemma
- **Domain Context:** Uniqueness of prime factorization for integers $n > 1$.
- **Input Payload:**
  - Statement: `forall (n : Nat), n > 1 -> exists (p : List Nat), PrimeList p /\ Prod p = n`
- **E2E Execution Flow:**
  1. Query formula retrieval endpoint `/mde/retrieval?formula=PrimeList`. Engine returns existing prime definition nodes and dependency DAG.
  2. Generate Isabelle/HOL proof script using `isabelle_checker`.
  3. Submit to counterexample gateway with computational sweep over $n \in [2, 1000]$.
- **Expected Assertion:**
  - Retrieval returns dependency DAG with root `PrimeDefinition`.
  - Computational sweep finds 0 counterexamples across 999 test integers.
  - Isabelle exporter formats valid `theorem prime_factorization`.

#### Scenario 1.4: Modular Arithmetic Power Congruence ($a \equiv b \pmod m \implies a^k \equiv b^k \pmod m$)
- **Domain Context:** Bounded modular arithmetic congruence relation over $\mathbb{Z}/m\mathbb{Z}$.
- **Input Payload:**
  - Equation: `(a^k) % m == (b^k) % m`
  - Premise: `(a % m) == (b % m)`
  - Modulus $m = 17$, $k = 4$, variables $a, b \in [0, 100]$.
- **E2E Execution Flow:**
  1. Pass modular claim to Tier 2 Z3 SMT solver via `/mde/counterexample/search`.
  2. Z3 verifies assertion under modular constraints.
  3. Coq script generator outputs `Lemma mod_pow_congruence : forall a b k m : nat, ...`.
- **Expected Assertion:**
  - SMT Gateway returns `is_valid=true`, `counterexample_found=false`.
  - Coq script compilation succeeds (`is_valid=true`).

#### Scenario 1.5: Quadratic Residue & Legendre Symbol Identity ($a^{(p-1)/2} \equiv \left(\frac{a}{p}\right) \pmod p$)
- **Domain Context:** Euler's criterion for quadratic residues modulo prime $p$.
- **Input Payload:**
  - Parameters: $p = 7$ (odd prime), $a = 2$ (non-residue mod 7, since $2^{3} = 8 \equiv 1 \pmod 7$).
- **E2E Execution Flow:**
  1. Perform Tier 1 computational sweep over prime parameter grid $p \in \{3, 5, 7, 11, 13\}$.
  2. SymPy exact engine evaluates modular exponentiation exact rational values.
  3. Generate Lean 4 proof script importing `Mathlib.NumberTheory.LegendreSymbol`.
- **Expected Assertion:**
  - Computational sweep confirms identity for all test primes.
  - SymPy evaluation matches Euler criterion value $\pm 1$.
  - Lean script generated without syntax errors.

---

### 6.2 Analytic Number Theory & Riemann Hypothesis Scenarios

#### Scenario 2.1: Riemann Zeta Function Functional Equation
- **Domain Context:** Reflection formula $\zeta(s) = 2^s \pi^{s-1} \sin\left(\frac{\pi s}{2}\right) \Gamma(1-s) \zeta(1-s)$ for complex $s \in \mathbb{C}$.
- **Input Payload:**
  - Formula AST: `zeta(s) - 2^s * pi^(s-1) * sin(pi*s/2) * gamma(1-s) * zeta(1-s) = 0`
  - Evaluation points: $s = 0.5 + i 14.13472514173469$, $s = 2.0 + i 0.0$.
- **E2E Execution Flow:**
  1. SymPy Exact Engine evaluates arbitrary-precision complex values at 50 decimal places precision (F3).
  2. Formula Retrieval Engine indexes functional equation node under `analytic_number_theory` domain (F4).
  3. Strategy Planner links functional equation as top-level prerequisite in RH zero-free region tree (F16).
- **Expected Assertion:**
  - SymPy evaluates functional equation difference to $< 10^{-45}$ (exact symbolic identity zero).
  - Retrieval returns node ID `thm_zeta_functional_eq` with $1.0$ confidence.
  - Strategy planner correctly places node at depth 1 in RH DAG.

#### Scenario 2.2: Non-Trivial Zeta Zero Arbitrary-Precision Tracking
- **Domain Context:** Verifying that the first non-trivial zero $\gamma_1 \approx 14.134725141734693790457251983562$ lies precisely on the critical line $\operatorname{Re}(s) = 1/2$.
- **Input Payload:**
  - Target Zero Location: $s = \frac{1}{2} + i \gamma_1$
  - Precision Guard: 50 decimal places.
- **E2E Execution Flow:**
  1. Call SymPy Engine `evaluate_zeta_zero(zero_index=1, dps=50)`.
  2. Pass claim $\zeta(1/2 + i \gamma_1) = 0$ to 3-tier Counterexample Gateway with bounds $\operatorname{Re}(s) \in [0.4, 0.6] \setminus \{0.5\}$.
  3. Gateway searches for off-critical zero counterexample in neighborhood.
- **Expected Assertion:**
  - SymPy returns $|\zeta(1/2 + i \gamma_1)| < 10^{-48}$.
  - Counterexample Gateway finds 0 off-critical zeros in tested interval ($\operatorname{Re}(s) \ne 0.5$).
  - SQLite database logs zero verification record with metadata `dps=50`.

#### Scenario 2.3: Dirichlet Series Expansion Convergent Bound ($\zeta(s) = \sum_{n=1}^\infty n^{-s}$ for $\operatorname{Re}(s) > 1$)
- **Domain Context:** Convergence proof for Dirichlet series representation in half-plane $\operatorname{Re}(s) > 1$.
- **Input Payload:**
  - Partial sum $S_N(s) = \sum_{n=1}^N n^{-s}$ for $s = 2$, $N = 1000$.
  - Target limit value: $\pi^2 / 6 \approx 1.6449340668482264$.
- **E2E Execution Flow:**
  1. SymPy exact engine expands series terms for $N=1000$ and calculates exact rational error bound $|S_{1000}(2) - \pi^2/6| < 1/1000$.
  2. Lean 4 generator exports proof script asserting convergence of $\sum n^{-2} = \pi^2/6$.
  3. Formal proof compiler checks script validity.
- **Expected Assertion:**
  - SymPy exact rational bound holds.
  - Lean 4 compiler returns `is_valid=true`.

#### Scenario 2.4: RH Zero-Free Region Strategy Tree ($1 - \frac{c}{\log t}$ bound)
- **Domain Context:** De-la-Vallée-Poussin classical zero-free region for $\zeta(\sigma + i t)$: $\sigma > 1 - \frac{c}{\log |t|}$ for $|t| \ge 3$.
- **Input Payload:**
  - Problem ID: `"RH"`
  - Target Lemma: `"zero_free_region_de_la_vallee_poussin"`
- **E2E Execution Flow:**
  1. Call `POST /mde/strategy/plan` with `problem_id="RH"`.
  2. Strategy Planner queries `riemann_tree` module to construct zero-free region decomposition tree.
  3. Compute Lemma Prioritization Index $P(L)$ for sub-lemmas (trigonometric identity $3 + 4\cos\theta + \cos 2\theta \ge 0$).
- **Expected Assertion:**
  - Strategy endpoint returns HTTP 200 with complete decomposition tree.
  - Sub-lemma "Trigonometric Positivity Identity" assigned highest priority $P(L)$.
  - Recommended next attack points to trigonometric positivity proof step.

#### Scenario 2.5: Counterexample Search on False RH Variant (Off-Critical Zero Claim)
- **Domain Context:** Attempting to refute a modified false Dirichlet $L$-function claim asserting a zero at $s = 0.7 + i 14.134$.
- **Input Payload:**
  - False Claim Statement: `zeta_modified(0.7 + 14.134725*I) == 0`
  - Formula SMT: `(assert (= (abs_zeta_mod 0.7 14.134725) 0.0))`
- **E2E Execution Flow:**
  1. Call `POST /mde/counterexample/search` with false claim formula.
  2. Tier 1 parameter sweep evaluates $|\zeta_{modified}(0.7 + i 14.134)| \approx 0.6234 \ne 0$.
  3. Gateway captures non-zero value as counterexample assignment.
  4. Graph Updater transitions node status in SQLite EGS from `CONJECTURED` to `REFUTED` and creates `COUNTEREXAMPLE_FOR` edge.
- **Expected Assertion:**
  - API response: `counterexample_found=true`, `tier_used=1`.
  - Node status in SQLite query is `REFUTED`.
  - Provenance JSON stores counterexample evaluation value `0.6234`.

---

## 7. Draft Specifications for `TEST_INFRA.md`

The following detailed content outline forms the production-grade specification for `TEST_INFRA.md`, to be placed in the project root to govern test harness implementation for MDE.

```markdown
# AXIOM MDE Test Infrastructure Specification (`TEST_INFRA.md`)

## 1. Overview & Architecture
This document defines the testing harness, environment setup, mocking strategies, database isolation rules, performance SLAs, and CI execution pipelines for the AXIOM Mathematical Discovery Engine (MDE).

## 2. Directory & File Organization
```
tests/
├── conftest.py                   # Master pytest fixtures (DB, client, mocks)
├── fixtures/
│   ├── egs_seed_data.py          # Seed SQLite knowledge graph datasets
│   ├── rh_zero_data.py           # High-precision Riemann zeta zero datasets
│   └── mock_provers.py           # Subprocess mock drivers for Lean/Coq/Isabelle
├── unit/
│   ├── test_mde_ontology.py      # F1, F2 (Schema & Pydantic models)
│   ├── test_mde_symbolic.py      # F3 (SymPy Engine)
│   ├── test_mde_retrieval.py     # F4 (Formula Retrieval & DAG)
│   ├── test_mde_conjecture.py    # F9, F10 (Conjecture Gen & Novelty)
│   ├── test_mde_counterexample.py# F12, F13 (Counterexample Gateway)
│   ├── test_mde_strategy.py      # F16 (Research Strategy Planner)
│   └── test_mde_memory.py        # F15 (Persistent Memory Store)
├── integration/
│   ├── test_mde_proof.py         # F5, F6, F7, F8 (Multi-prover & Compilers)
│   ├── test_mde_review.py        # F17 (Verification Review Layer)
│   └── test_mde_routes.py        # F11, F14, F18, F19 (FastAPI MDE Router)
├── e2e/
│   ├── test_mde_pipeline.py      # Tier 3 Cross-Feature Pipelines 1-6
│   └── test_mde_domain_rh.py     # Tier 4 Real-World Domain Scenarios
```

## 3. Pytest Fixture Taxonomy & Isolation Strategy
- `db_conn`: In-memory SQLite connection (`:memory:`) with v4 migrations applied (`run_migrations`). Scope: `function`. Autouse cleanup ensures pristine database for every test case.
- `api_client`: FastAPI `TestClient` initialized with mounted MDE router, authenticated Bearer token header, and overridden DB store singleton. Scope: `module`.
- `sympy_engine_fixture`: Instance of `SymPyEngine` with fixed 50-digit precision context. Scope: `session`.
- `mock_lean_subprocess`: Mocks `subprocess.run` calls to `lean` executable when binary is absent from system PATH.

## 4. Subprocess & Solvers Mocking Framework
- **Lean 4 / Coq / Isabelle Fallback Driver:** When prover binaries are not detected in system environment, test harness intercepts `subprocess.run` calls, parses target script for illegal keywords (`sorry`), and returns simulated `CompletedProcess` with returncode 0 and structured warning stdout.
- **Z3 SMT Solver Mock Driver:** Provides deterministic fallback solver responses for non-linear equations when Z3 library is uninstalled or solver times out.

## 5. Performance SLA & Guardrails
- **API Response Latency:** All REST endpoints must return HTTP responses within 200ms for unit payloads, and within 2000ms for complex strategy generation.
- **Counterexample Timeout Guard:** Gateway test harness enforces 60-second strict timeout limit using `concurrent.futures.ThreadPoolExecutor`.
- **Code Coverage SLA:** CI build fails if code coverage across `axiom/core/` falls below 90.0%.

## 6. Pytest Custom Markers
```python
# pytest.ini configuration
[pytest]
markers =
    unit: Fast unit tests without external provers (<50ms per test)
    integration: Microservice and database integration tests
    e2e: End-to-end multi-step workflow pipelines
    tier1: Tier 1 Feature Coverage tests (105 cases)
    tier2: Tier 2 Boundary & Corner Case tests (105 cases)
    tier3: Tier 3 Cross-Feature Combination workflows
    tier4: Tier 4 Domain Application scenarios
    slow: Long-running proof or solver tests (>5s)
    rh_domain: Riemann Hypothesis specific test cases
```

## 7. Continuous Integration Pipeline Command Integration
```bash
# Fast Unit Test Execution (Pre-commit)
pytest -m "unit" --durations=10

# Complete MDE Test Suite Execution with Coverage Report
pytest tests/ -m "unit or integration or e2e" --cov=axiom.core --cov-report=term-missing --cov-fail-under=90

# Dedicated Domain Scenario Verification Run
pytest tests/e2e/test_mde_domain_rh.py -m "rh_domain" -v
```
```

---

## 8. Traceability Matrix & Test Strategy Summary

### 8.1 Feature to Test Case Count Breakdown

| Feature # | Feature Name | Tier 1 Cases | Tier 2 Cases | Tier 3 Pipelines | Tier 4 Scenarios | Total Coverage |
|---|---|---|---|---|---|---|
| **F1** | SQLite v4 Schema Migration | 5 | 5 | P1, P4, P6 | S1.1, S2.5 | 13 |
| **F2** | EGS Ontological Schema Models | 5 | 5 | P1, P2, P6 | S1.1, S2.5 | 13 |
| **F3** | Exact SymPy Symbolic Engine | 5 | 5 | P5, P6 | S1.2, S1.5, S2.1, S2.2, S2.3 | 15 |
| **F4** | Formula Retrieval & Dependency DAG | 5 | 5 | P1, P6 | S1.3, S2.1 | 13 |
| **F5** | Multi-Prover Script Generators | 5 | 5 | P3, P6 | S1.1, S1.3, S2.3 | 13 |
| **F6** | Proof Compiler Checkers & Fallback | 5 | 5 | P3, P6 | S1.1, S1.2, S2.3 | 13 |
| **F7** | Mathlib Tactic Generator | 5 | 5 | P3, P6 | S1.1, S1.2 | 13 |
| **F8** | Formal Proof Compiler Endpoint | 5 | 5 | P3, P6 | S1.1, S1.2, S2.3 | 13 |
| **F9** | Autonomous Conjecture Generator | 5 | 5 | P2, P6 | S1.4, S2.5 | 13 |
| **F10** | Novelty Scorer & Weak Filter | 5 | 5 | P2, P6 | S1.4, S2.5 | 13 |
| **F11** | Conjecture Generation Endpoint | 5 | 5 | P2, P6 | S1.4, S2.5 | 13 |
| **F12** | 3-Tier Counterexample Gateway | 5 | 5 | P2, P5, P6 | S1.1, S1.4, S2.2, S2.5 | 14 |
| **F13** | Counterexample Graph Updater | 5 | 5 | P2, P6 | S2.5 | 12 |
| **F14** | Counterexample Search Endpoint | 5 | 5 | P2, P5, P6 | S1.1, S1.4, S2.2, S2.5 | 14 |
| **F15** | Persistent Memory & Tactic Guard | 5 | 5 | P4, P6 | S1.3 | 12 |
| **F16** | Research Strategy Planner | 5 | 5 | P1, P4, P6 | S2.1, S2.4 | 14 |
| **F17** | Independent Verification Review Layer | 5 | 5 | P3, P6 | S1.2 | 12 |
| **F18** | Strategy, Memory & Review Endpoints | 5 | 5 | P1, P3, P4, P6 | S2.4 | 14 |
| **F19** | FastAPI MDE Router Integration | 5 | 5 | P5, P6 | S1.1-S2.5 | 20 |
| **F20** | Exhaustive MDE Test Suite | 5 | 5 | P1-P6 | S1.1-S2.5 | 20 |
| **F21** | Millennium Prize Alignment Report | 5 | 5 | P6 | S2.1-S2.5 | 11 |
| **TOTAL**| **21 Features** | **105** | **105** | **6 Pipelines** | **10 Scenarios** | **226 Test Specs** |

### 8.2 Summary Assessment
The test case design delivered in this report satisfies all requirements specified in `ORIGINAL_REQUEST.md` and `PROJECT.md`. With 105 Tier 1 feature coverage test cases, 105 Tier 2 boundary & corner case test cases, 6 Tier 3 cross-feature combination pipelines, 10 Tier 4 domain application scenarios, and the comprehensive `TEST_INFRA.md` outline, the E2E Testing Track is fully equipped to guide test implementation across Milestones M1 through M7.
