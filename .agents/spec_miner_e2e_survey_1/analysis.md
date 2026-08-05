# Specification Mining & E2E Test Criteria Report
**Project**: AXIOM — Mathematical Discovery Engine (MDE)  
**Agent**: `spec_miner_e2e_survey_1`  
**Date**: 2026-08-05  

---

## Executive Summary

This report establishes the authoritative end-to-end (E2E) specifications, data schemas, API contracts, error behaviors, edge cases, and pass/fail criteria for all **21 features** of the AXIOM Mathematical Discovery Engine (MDE). The specifications were mined by auditing existing codebase components (`axiom/core/`, `axiom/services/api_gateway/`), `PROJECT.md`, and `ORIGINAL_REQUEST.md`.

---

## Features Discovered

| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | Ontology | SQLite v4 Schema Migration | Run idempotent DB migrations creating `mathematical_objects`, `definitions`, `equivalent_statements`, `memory_snapshots`, `failed_proof_attempts` tables | `conn: sqlite3.Connection` | None (DB DDL updated, version recorded in `_schema_migrations`) | `sqlite3.OperationalError` on lock/corruption | `PROJECT.md` & `axiom/core/knowledge_graph/migrations.py` |
| 2 | Ontology | EGS Ontological Schema Models | Pydantic node/edge schema models (`MathematicalObjectNode`, `DefinitionNode`, `OpenProblemNode`, `ConjectureNode`, `EQUIVALENT_TO`, `DEPENDS_ON`, `PROVES`, `COUNTEREXAMPLE_FOR`) | Data dict / JSON payload | Validated Pydantic model instance | `pydantic.ValidationError` on missing/invalid fields | `PROJECT.md` & `axiom/core/knowledge_graph/schema.py` |
| 3 | Symbolic | Exact SymPy Symbolic Engine | Exact rational arithmetic, polynomial identity testing, Dirichlet series expansion, float drift guard | `expr_str: str`, `variables: List[str]` | `SymPyEngineResult(is_identical: bool, simplified_expr: str, exact_val: Optional[str])` | `sympy.SymPyError`, `ZeroDivisionError`, `ValueError` on float drift | `PROJECT.md` & `axiom/core/symbolic/` |
| 4 | Retrieval | Formula Retrieval & Dependency DAG | Syntactic/semantic AST formula matching, NetworkX dependency DAG extraction, endpoint `GET /mde/retrieval` | `target_formula: str`, `domain: Optional[str]`, `top_k: int` | `RetrievalResponsePayload(query_formula, canonical_form, matched_theorems, dependency_dag)` | HTTP 400 on malformed syntax; empty list on un-indexed formula | `PROJECT.md` & `axiom/core/retrieval/` |
| 5 | Prover | Multi-Prover Script Generators | Code template generators for Lean 4 (`theorem ... := by`), Coq (`Theorem ... Proof. ... Qed.`), and Isabelle/HOL (`theorem ... imports Main begin ... end`) | `system: str`, `theorem_name: str`, `statement: str`, `variables: Dict[str, str]`, `proof_body: Optional[str]` | Generated script string in target proof language | `ValueError` on unsupported system string | `PROJECT.md` & `axiom/core/verification/` |
| 6 | Prover | Proof Compiler Checkers & Fallback | Subprocess checkers executing local `lean`, `coqc`, `isabelle` with fallback AST simulation & warning diagnostics | `system: str`, `script_content: str`, `timeout_seconds: float` | `CompilerCheckResult(is_valid: bool, status: str, diagnostics: str, is_simulated: bool)` | Timeout >10s returns `status="TIMEOUT"`; missing CLI binary sets `is_simulated=True` | `PROJECT.md` & `axiom/core/verification/` |
| 7 | Prover | Mathlib Tactic Generator | Maps statement patterns to Lean 4 / Mathlib tactics (`ring`, `linarith`, `nlinarith`, `positivity`, `norm_num`, `rfl`, `sorry`) | `statement: str`, `variables: Dict[str, str]` | Tactic string (e.g. `"ring"`, `"linarith"`, `"norm_num"`) | Returns `"sorry"` on unrecognized pattern | `PROJECT.md` & `axiom/core/verification/lean_exporter.py` |
| 8 | Prover | Formal Proof Compiler Endpoint | REST endpoint `POST /mde/proof/compile` executing script generation, temp file writing, and compiler check | JSON payload (`system`, `theorem_name`, `statement`, `variables`, `proof_body`) | HTTP 200 OK with `ProofCompileResponse(system, theorem_name, is_valid, status, diagnostics)` | HTTP 401 Unauthorized; HTTP 422 Unprocessable Entity; HTTP 400 on invalid prover | `PROJECT.md` & `axiom/services/api_gateway/routes/mde.py` |
| 9 | Conjecture | Autonomous Conjecture Generator | Candidate claim generator with 5 strategies (`DUAL`, `BOUND`, `COMPLEX`, `GENERAL`, `COMPOSE`) | `domain: str`, `seed_nodes: List[ScientificNode]`, `strategy_mask: Optional[List[str]]` | `List[ConjectureCandidate]` | Generates default baseline candidates if seed nodes empty | `PROJECT.md` & `axiom/core/conjecture/` |
| 10 | Conjecture | Novelty Scorer & Weak Filter | Mathematical Novelty Scorer N(C) and weak conjecture filter (tautology & similarity checks) | `candidate: ConjectureCandidate`, `existing_conjectures: List[ConjectureCandidate]` | `NoveltyAssessment(score: float, is_accepted: bool, rejection_reason: Optional[str])` | Score = 0.0, `is_accepted = False` on parse error | `PROJECT.md` & `axiom/core/conjecture/` |
| 11 | Conjecture | Conjecture Generation Endpoint | REST endpoint `POST /mde/conjectures/generate` | JSON payload (`domain`, `max_conjectures`, `min_novelty`, `strategies`) | HTTP 200 OK (`status: "success"`, `count: int`, `conjectures: List[dict]`) | HTTP 401 Unauthorized; HTTP 422 on invalid parameters | `PROJECT.md` & `axiom/services/api_gateway/routes/mde.py` |
| 12 | Counterexample | 3-Tier Counterexample Gateway | Cascading 3-tier solver (Tier 1 Sweep -> Tier 2 Z3 SMT -> Tier 3 SymPy Exact) with <60s timeout guard | `claim_statement: str`, `variables: List[VariableBound]`, `timeout_seconds: float` | `CounterexampleSearchResult(is_valid, counterexample_found, counterexample, tier_used)` | Timeout >60s returns `status="TIMEOUT"`, `counterexample_found=False` | `PROJECT.md` & `axiom/core/counterexample/` |
| 13 | Counterexample | Counterexample Graph Updater | Transitions node status to `REFUTED` and inserts `COUNTEREXAMPLE_FOR` edge in EGS SQLite store | `store: EpistemicStore`, `claim_id: str`, `counterexample_data: Dict[str, Any]` | `updated_node: ScientificNode`, `new_edge: Edge` | `ValueError` if `claim_id` does not exist in store | `PROJECT.md` & `axiom/core/counterexample/` |
| 14 | Counterexample | Counterexample Search Endpoint | REST endpoint `POST /mde/counterexample/search` | JSON payload (`claim_id`, `statement`, `variables`, `update_graph`) | HTTP 200 OK (`is_valid`, `counterexample_found`, `counterexample`, `tier_used`, `graph_updated`) | HTTP 401 Unauthorized; HTTP 422 on bad payload; 504 on timeout | `PROJECT.md` & `axiom/services/api_gateway/routes/mde.py` |
| 15 | Memory | Persistent Memory & Tactic Guard | SQLite memory snapshotting and MCTS tactic expansion failure pruning guard | `claim_id: str`, `tactic_sequence: List[str]`, `failure_reason: str` | `is_pruned: bool` (for guard); snapshot dict (for store) | `ValueError` on corrupt JSON snapshot load | `PROJECT.md` & `axiom/core/memory/` |
| 16 | Strategy | Research Strategy Planner | Open problem DAG decomposition, Lemma Prioritization Index P(L), Riemann Hypothesis zero-free tree | `problem_id: str`, `domain: str` | `StrategyPlanResponse(problem_id, root_lemma_id, prioritized_queue, recommended_next_attack)` | `KeyError` or default template fallback on unknown `problem_id` | `PROJECT.md` & `axiom/core/strategy/` |
| 17 | Review | Independent Verification Review Layer | Multi-verifier review layer cross-checking SMT vs MCTS vs Compiler, script sanity guard | `claim_id: str`, `smt_result: Optional[dict]`, `mcts_result: Optional[dict]`, `compiler_result: Optional[dict]` | `VerificationReviewResult(consensus_status, is_verified, confidence_score, conflict_detected)` | `conflict_detected=True`, `status=UNDER_REVIEW` on verifier mismatch | `PROJECT.md` & `axiom/core/verification/` |
| 18 | Router | Strategy, Memory & Review Endpoints | Endpoints `POST /mde/strategy/plan`, `GET /mde/strategy/decompose`, `POST /mde/memory/snapshot`, `POST /mde/verification/review` | JSON payloads for strategy, memory, review APIs | HTTP 200 OK with schema-compliant JSON payloads | HTTP 401 Unauthorized; HTTP 422 Unprocessable Entity | `PROJECT.md` & `axiom/services/api_gateway/routes/mde.py` |
| 19 | Router | FastAPI MDE Router Integration | Router `axiom/services/api_gateway/routes/mde.py` mounted at `/mde/*` on main FastAPI application | Inbound HTTP requests to `/mde/*` | Routed HTTP response from MDE handlers | HTTP 404 Not Found if path unmounted | `PROJECT.md` & `axiom/services/api_gateway/main.py` |
| 20 | Testing | Exhaustive MDE Test Suite | Unit and integration tests covering Basic Number Theory & Riemann Hypothesis domains | Pytest test command execution | Clean pass output across unit & integration tests | Assert errors or unhandled exceptions | `PROJECT.md` & `tests/` |
| 21 | Documentation | Millennium Prize Alignment Report | Technical report `docs/mde_prize_alignment.md` evaluating RH capabilities | N/A (Markdown document file) | Markdown report at `docs/mde_prize_alignment.md` | Missing file or empty document | `PROJECT.md` & `docs/mde_prize_alignment.md` |

---

## Detailed Specifications & Pass/Fail Criteria

### Feature 1: SQLite v4 Schema Migration
- **Module Path**: `axiom/core/knowledge_graph/migrations.py`
- **Tables Created**:
  1. `mathematical_objects` (`id` TEXT PK, `symbol` TEXT, `domain` TEXT, `properties` TEXT, `metadata` TEXT, `created_at` TEXT)
  2. `definitions` (`id` TEXT PK, `term` TEXT, `formal_def` TEXT, `domain` TEXT, `created_at` TEXT)
  3. `equivalent_statements` (`id` TEXT PK, `statement_a_id` TEXT, `statement_b_id` TEXT, `proof_reference` TEXT, `confidence` REAL, `created_at` TEXT)
  4. `memory_snapshots` (`id` INTEGER PK AUTOINCREMENT, `session_id` TEXT, `snapshot` TEXT, `created_at` TEXT)
  5. `failed_proof_attempts` (`id` INTEGER PK AUTOINCREMENT, `claim_id` TEXT, `tactic_sequence` TEXT, `failure_reason` TEXT, `created_at` TEXT)
- **E2E Pass Criteria**:
  1. Calling `run_migrations(conn)` on a fresh database adds `(4, "v4_mde_schema", _v4_mde_schema)` to `_schema_migrations`.
  2. Querying `sqlite_master` confirms all 5 tables exist with exact foreign keys and indexes.
  3. Re-executing `run_migrations(conn)` is idempotent (no-op, 0 errors).
- **E2E Fail Criteria**: Any of the 5 tables is missing, or re-running migrations raises `OperationalError`.

---

### Feature 2: EGS Ontological Schema Models
- **Module Path**: `axiom/core/knowledge_graph/schema.py`
- **Pydantic Models**:
  - `MathematicalObjectNode`: `type="MATHEMATICAL_OBJECT"`, `symbol: str`, `domain: str`, `properties: List[str]`
  - `DefinitionNode`: `type="DEFINITION"`, `term: str`, `formal_def: str`, `domain: str`
  - `OpenProblemNode`: `type="OPEN_PROBLEM"`, `statement: str`, `domain: str`, `difficulty_rating: float`
  - `ConjectureNode`: `type="CONJECTURE"`, `statement: str`, `novelty_score: float`, `status: EpistemicStatus`
  - Edges: `EQUIVALENT_TO`, `DEPENDS_ON`, `PROVES`, `COUNTEREXAMPLE_FOR`
- **E2E Pass Criteria**:
  1. Serializing and deserializing nodes through `TypeAdapter(ScientificNode)` preserves type discriminator and attributes.
  2. Saving nodes to `EpistemicStore` and querying back via `get_node(id)` returns valid instance of respective model.
- **E2E Fail Criteria**: Field validation errors on valid model dicts or loss of node type during round-trip database serialization.

---

### Feature 3: Exact SymPy Symbolic Engine
- **Module Path**: `axiom/core/symbolic/sympy_engine.py`
- **Class**: `SymPyEngine`
- **Methods**:
  - `verify_identity(lhs: str, rhs: str) -> SymPyEngineResult`
  - `expand_dirichlet_series(terms: int) -> str`
  - `evaluate_zeta_zero(n: int, precision_digits: int = 50) -> str`
  - `sanitize_float(val: float) -> sympy.Rational`
- **E2E Pass Criteria**:
  1. `verify_identity("x**2 - y**2", "(x - y)*(x + y)")` returns `is_identical=True`.
  2. `sanitize_float(0.3333333333333333)` converts to exact rational `Rational(1, 3)` or exact float drift protection without IEEE 754 precision loss.
  3. `evaluate_zeta_zero(1)` returns high-precision complex zero ($\approx 0.5 + 14.134725...i$).
- **E2E Fail Criteria**: Returning `False` for valid algebraic identities, or unhandled SymPy exception on valid input strings.

---

### Feature 4: Formula Retrieval & Dependency DAG
- **Module Path**: `axiom/core/retrieval/engine.py`
- **Endpoint**: `GET /mde/retrieval?target_formula={formula}&domain={domain}`
- **Payload Schema**:
  ```json
  {
    "query_formula": "a * (b + c)",
    "canonical_form": "a*b + a*c",
    "matched_theorems": [
      { "id": "thm_distrib", "name": "Distributive Law", "score": 0.98 }
    ],
    "equivalent_formulations": ["(b + c) * a"],
    "dependency_dag": {
      "thm_distrib": ["lemma_add_comm", "lemma_mul_comm"]
    }
  }
  ```
- **E2E Pass Criteria**:
  1. Endpoint returns HTTP 200 OK with valid schema.
  2. Canonical form correctly normalizes variable names (e.g. `x + y` vs `a + b`).
  3. `dependency_dag` is a valid directed acyclic graph (no cycles).
- **E2E Fail Criteria**: HTTP 500 error, malformed JSON response, or cyclic graph in `dependency_dag`.

---

### Feature 5: Multi-Prover Script Generators
- **Module Path**: `axiom/core/verification/script_generators.py`
- **Supported Systems**: `"lean"`, `"coq"`, `"isabelle"`
- **E2E Pass Criteria**:
  1. `generate_script("lean", "distrib", "a*(b+c) = a*b + a*c", {"a": "Int", "b": "Int", "c": "Int"})` outputs valid Lean 4 syntax.
  2. `generate_script("coq", ...)` outputs valid Coq syntax (`Theorem ... Proof. ... Qed.`).
  3. `generate_script("isabelle", ...)` outputs valid Isabelle/HOL syntax (`theorem ... imports Main begin ... end`).
- **E2E Fail Criteria**: Invalid syntax in generated code or `ValueError` not raised when passing invalid system `"agda"`.

---

### Feature 6: Proof Compiler Checkers & Fallback
- **Module Path**: `axiom/core/verification/compiler_checkers.py`
- **Functions**: `check_lean()`, `check_coq()`, `check_isabelle()`
- **E2E Pass Criteria**:
  1. When Lean/Coq CLI is installed, runs subprocess and returns actual compiler stdout/stderr.
  2. When Lean/Coq CLI is NOT installed, gracefully falls back to AST simulation mode, sets `is_simulated=True`, and logs warning diagnostic without throwing `FileNotFoundError`.
  3. Process timeout (>10s) returns `status="TIMEOUT"`.
- **E2E Fail Criteria**: Process hanging, unhandled `FileNotFoundError`, or returning `is_valid=True` for invalid code statements.

---

### Feature 7: Mathlib Tactic Generator
- **Module Path**: `axiom/core/verification/lean_exporter.py`
- **Method**: `auto_generate_tactic(statement: str, variables: Dict[str, str]) -> str`
- **E2E Pass Criteria**:
  1. Algebraic identity (`a * (b + c) = a*b + a*c`) maps to `"ring"`.
  2. Inequality (`x + 1 > x`) maps to `"linarith"`.
  3. Numeric statement (`2 + 2 = 4`) maps to `"norm_num"`.
  4. Non-linear positivity (`x^2 >= 0`) maps to `"positivity"` or `"nlinarith"`.
- **E2E Fail Criteria**: Returning inappropriate tactic for known statement category.

---

### Feature 8: Formal Proof Compiler Endpoint
- **Module Path**: `axiom/services/api_gateway/routes/mde.py`
- **Endpoint**: `POST /mde/proof/compile`
- **Request Payload**:
  ```json
  {
    "system": "lean",
    "theorem_name": "binomial_expansion",
    "statement": "(a + b)^2 = a^2 + 2*a*b + b^2",
    "variables": { "a": "Int", "b": "Int" },
    "proof_body": "ring"
  }
  ```
- **Response Payload**:
  ```json
  {
    "system": "lean",
    "theorem_name": "binomial_expansion",
    "is_valid": true,
    "status": "compiled_successfully",
    "diagnostics": "",
    "is_simulated": false,
    "execution_time_ms": 120.5
  }
  ```
- **E2E Pass Criteria**: Endpoint returns HTTP 200 with schema matching `ProofCompileResponse`.
- **E2E Fail Criteria**: HTTP 500 error or unhandled compiler failure.

---

### Feature 9: Autonomous Conjecture Generator
- **Module Path**: `axiom/core/conjecture/generator.py`
- **Strategies**: `DUAL`, `BOUND`, `COMPLEX`, `GENERAL`, `COMPOSE`
- **E2E Pass Criteria**:
  1. Invoking generator produces `ConjectureCandidate` list with statements, variables, and assigned strategy metadata.
  2. Seed nodes are processed to derive non-trivial candidate conjectures.
- **E2E Fail Criteria**: Generating empty candidate list or invalid mathematical syntax (e.g. unclosed parentheses).

---

### Feature 10: Novelty Scorer & Weak Filter
- **Module Path**: `axiom/core/conjecture/novelty_scorer.py` & `filters.py`
- **E2E Pass Criteria**:
  1. Computes novelty score $N(C) \in [0.0, 1.0]$.
  2. Filters out tautologies (`x = x`, `0 = 0`) with `rejection_reason="TAUTOLOGY"`.
  3. Filters out near-duplicates (Jaccard / AST similarity > 0.90) with `rejection_reason="DUPLICATE_SIMILARITY"`.
- **E2E Fail Criteria**: High novelty score assigned to tautologies, or rejection of truly novel conjectures.

---

### Feature 11: Conjecture Generation Endpoint
- **Module Path**: `axiom/services/api_gateway/routes/mde.py`
- **Endpoint**: `POST /mde/conjectures/generate`
- **Request Payload**:
  ```json
  {
    "domain": "number_theory",
    "max_conjectures": 5,
    "min_novelty": 0.6,
    "strategies": ["DUAL", "BOUND", "COMPLEX"]
  }
  ```
- **Response Payload**:
  ```json
  {
    "status": "success",
    "count": 3,
    "conjectures": [
      {
        "id": "conj_8921",
        "statement": "sum(k=1..n, k^3) == (n*(n+1)/2)^2",
        "strategy": "GENERAL",
        "novelty_score": 0.82,
        "status": "CONJECTURED"
      }
    ]
  }
  ```
- **E2E Pass Criteria**: Returns HTTP 200 OK with requested number of conjectures filtered by `min_novelty`.
- **E2E Fail Criteria**: HTTP 500 error or failure to enforce `min_novelty` filter.

---

### Feature 12: 3-Tier Counterexample Gateway
- **Module Path**: `axiom/core/counterexample/gateway.py`
- **Tiers**: Tier 1 (Sweep) $\rightarrow$ Tier 2 (Z3 SMT) $\rightarrow$ Tier 3 (SymPy Exact)
- **E2E Pass Criteria**:
  1. Invalid claim (e.g. $x^2 + 1 = 0$ for $x \in \mathbb{R}$) returns `counterexample_found=True` with exact values.
  2. Valid claim returns `is_valid=True` and `counterexample_found=False`.
  3. Enforces total timeout guard < 60 seconds.
- **E2E Fail Criteria**: Execution exceeding 60 seconds or returning incorrect counterexamples.

---

### Feature 13: Counterexample Graph Updater
- **Module Path**: `axiom/core/counterexample/graph_updater.py`
- **E2E Pass Criteria**:
  1. When counterexample is found for `claim_id`, node status in SQLite transitions to `REFUTED`.
  2. Edge of type `COUNTEREXAMPLE_FOR` is created connecting experimental fact node to claim node.
- **E2E Fail Criteria**: Database status remains `CONJECTURED` or edge insertion fails.

---

### Feature 14: Counterexample Search Endpoint
- **Module Path**: `axiom/services/api_gateway/routes/mde.py`
- **Endpoint**: `POST /mde/counterexample/search`
- **Request Payload**:
  ```json
  {
    "claim_id": "claim_7712",
    "statement": "x^2 + y^2 == z^2 + 1",
    "variables": [
      { "name": "x", "min": 0, "max": 10 },
      { "name": "y", "min": 0, "max": 10 },
      { "name": "z", "min": 0, "max": 10 }
    ],
    "update_graph": true
  }
  ```
- **Response Payload**:
  ```json
  {
    "status": "success",
    "is_valid": false,
    "counterexample_found": true,
    "counterexample": { "x": 1, "y": 2, "z": 2 },
    "tier_used": "TIER_1_SWEEP",
    "execution_time_ms": 14.8,
    "graph_updated": true
  }
  ```
- **E2E Pass Criteria**: Returns HTTP 200 with search results and updates database when `update_graph=true`.
- **E2E Fail Criteria**: HTTP 500 error or failure to update graph state.

---

### Feature 15: Persistent Memory & Tactic Guard
- **Module Path**: `axiom/core/memory/persistent_store.py`
- **E2E Pass Criteria**:
  1. Session memory snapshots saved via `POST /mde/memory/snapshot` persist to SQLite table `memory_snapshots`.
  2. Failed proof attempts logged to `failed_proof_attempts` act as a failure guard, pruning MCTS expansion branches matching known failed tactic sequences.
- **E2E Fail Criteria**: Re-exploring known failed tactic sequences during proof search or losing session snapshots across restarts.

---

### Feature 16: Research Strategy Planner
- **Module Path**: `axiom/core/strategy/planner.py` & `riemann_tree.py`
- **Lemma Prioritization Index**:
  $$P(L) = \frac{\text{Novelty}(L) \times \text{Centrality}(L)}{1 + \text{Difficulty}(L)}$$
- **E2E Pass Criteria**:
  1. Requesting plan for `"riemann_hypothesis"` constructs hierarchical DAG decomposition of zero-free region lemmas.
  2. Prioritized queue ranks lemmas in descending order of $P(L)$.
- **E2E Fail Criteria**: Unranked queue, missing root lemma, or division by zero.

---

### Feature 17: Independent Verification Review Layer
- **Module Path**: `axiom/core/verification/review_controller.py`
- **E2E Pass Criteria**:
  1. When SMT, MCTS, and Compiler all agree, returns `consensus_status="VERIFIED"`, `confidence_score=1.0`, `conflict_detected=False`.
  2. When SMT returns `REFUTED` while MCTS returns `VERIFIED`, returns `consensus_status="UNDER_REVIEW"`, `confidence_score=0.0`, `conflict_detected=True`.
- **E2E Fail Criteria**: Blindly accepting proof when verifiers conflict.

---

### Feature 18: Strategy, Memory & Review Endpoints
- **Module Path**: `axiom/services/api_gateway/routes/mde.py`
- **Endpoints**:
  - `POST /mde/strategy/plan`
  - `GET /mde/strategy/decompose?problem_id=riemann_hypothesis`
  - `POST /mde/memory/snapshot`
  - `POST /mde/verification/review`
- **E2E Pass Criteria**: All 4 REST endpoints respond with HTTP 200 OK and valid JSON schemas under TestClient tests.
- **E2E Fail Criteria**: Any endpoint returns 404, 500, or schema validation error.

---

### Feature 19: FastAPI MDE Router Integration
- **Module Path**: `axiom/services/api_gateway/routes/mde.py` & `main.py`
- **E2E Pass Criteria**:
  1. Router mounted at `/mde/*` on main FastAPI application.
  2. Submitting requests to `/mde/*` with valid bearer token routes successfully.
  3. OpenAPI schema (`GET /openapi.json`) includes all `/mde/*` routes under `"mde"` tag.
- **E2E Fail Criteria**: 404 Not Found on `/mde/*` endpoints or unhandled router mounting exception.

---

### Feature 20: Exhaustive MDE Test Suite
- **Module Path**: `tests/`
- **E2E Pass Criteria**: Executing `pytest tests/` runs all unit and integration tests for ontology, retrieval, proof, conjecture, counterexample, strategy, review, and pipeline with 100% pass rate.
- **E2E Fail Criteria**: Any test assertion failure or unhandled exception.

---

### Feature 21: Millennium Prize Alignment Report
- **Module Path**: `docs/mde_prize_alignment.md`
- **E2E Pass Criteria**: Document exists at `docs/mde_prize_alignment.md`, exceeds 50 lines, and details Riemann Hypothesis analytic continuation, zero-free region tracking, capability gaps, and recommendations.
- **E2E Fail Criteria**: Document missing or lacking required RH breakdown sections.

---

## Edge Cases

| # | Feature | Input | Observed / Expected Behavior |
|---|---------|-------|-------------------|
| 1 | v4 Schema Migration | Re-running migration on existing v4 database | Idempotent check detects version 4 in `_schema_migrations` and skips DDL execution cleanly. |
| 2 | EGS Ontological Models | Deserializing node payload with unknown `type` discriminator | Pydantic raises `ValidationError` with clear error message detailing invalid type discriminator. |
| 3 | Exact SymPy Engine | Expression string containing floating point drift (e.g. `0.3333333333333333`) | Float drift guard converts input to exact `Rational(1, 3)` to preserve exact symbolic computation. |
| 4 | Formula Retrieval | Query formula with renamed variables (`a + b` vs `x + y`) | Canonical AST normalization reduces both formulas to identical representation for matching. |
| 5 | Multi-Prover Generators | Theorem name starting with number (e.g. `2_plus_2`) | `sanitize_name` prepends `thm_` to produce valid identifier `thm_2_plus_2`. |
| 6 | Proof Compiler Checkers | Missing local `lean` or `coqc` CLI binary | Gracefully switches to AST simulation mode (`is_simulated=True`) with warning diagnostics instead of throwing `FileNotFoundError`. |
| 7 | Mathlib Tactic Generator | Pure numerical expression without variables (`2 + 2 = 4`) | Recommends `norm_num` tactic instead of general `ring` or `linarith`. |
| 8 | Compiler Endpoint | Unsupported prover system parameter (`system="agda"`) | Endpoint returns HTTP 400 Bad Request with error detail `"Unsupported proof system"`. |
| 9 | Conjecture Generator | Empty seed nodes list passed to generator | Generator falls back to generating baseline domain identity candidates without throwing exception. |
| 10 | Novelty Scorer | Tautological claim candidate (`x = x` or `0 = 0`) | Scores candidate $N(C) = 0.0$ and sets `is_accepted = False` with `rejection_reason = "TAUTOLOGY"`. |
| 11 | Conjecture Endpoint | Request with `min_novelty = 1.0` (too strict) | Returns HTTP 200 OK with empty `conjectures` list (`count: 0`) rather than erroring out. |
| 12 | Counterexample Gateway | Non-linear equation Z3 solver cannot settle within time limit | Cascades solver evaluation to Tier 3 (SymPy exact solver). |
| 13 | Counterexample Graph Updater | `claim_id` passed does not exist in SQLite database | Raises `ValueError("Claim node not found")` and rolls back transaction. |
| 14 | Counterexample Endpoint | Parameter sweep exceeding total timeout (>60s) | Gateway aborts sweep, returns HTTP 504 Gateway Timeout or status `TIMEOUT`. |
| 15 | Persistent Memory | MCTS proof search encountering known failed tactic sequence | Tactic Expansion Guard prunes branch from MCTS search tree, avoiding repeated failures. |
| 16 | Research Strategy Planner | Lemma with zero difficulty rating (`Difficulty(L) = 0.0`) | Prioritization formula adds 1 to denominator ($1 + \text{Difficulty}$), preventing division by zero. |
| 17 | Verification Review Layer | Verifier results contradict (SMT: `REFUTED`, MCTS: `VERIFIED`) | Flags `conflict_detected = True`, sets status to `UNDER_REVIEW`, and sets confidence score to `0.0`. |
| 18 | MDE REST Endpoints | Request submitted without Bearer auth header | Gateway returns HTTP 401 Unauthorized across all MDE REST routes. |
| 19 | MDE Router Integration | Inspecting `/docs` Swagger UI endpoints | MDE route handlers correctly group under `"mde"` tag with full request/response schemas. |
| 20 | MDE Test Suite | Executing tests on machine without Lean 4 compiler | Tests execute fallback simulation checks and pass without failing environment dependencies. |
| 21 | Millennium Prize Report | Auditing document length and structure | Document contains >50 lines of structured analysis covering analytic number theory and RH zero-free regions. |

---

## Test Execution & Verification Methodology

To verify all 21 features in E2E testing:
1. **Unit Verification**: Execute `pytest tests/test_mde_*.py` to verify schema, symbolic, retrieval, multi-prover, conjecture, counterexample, strategy, and memory modules.
2. **API Verification**: Use FastAPI `TestClient(app)` to send HTTP requests to all `/mde/*` endpoints, asserting status codes (200 OK, 401 Unauthorized, 422 Unprocessable) and JSON response schemas.
3. **Database State Verification**: Inspect SQLite tables (`mathematical_objects`, `definitions`, `equivalent_statements`, `memory_snapshots`, `failed_proof_attempts`, `proof_lineage`) after running operations to ensure graph nodes and edges update correctly.
4. **Documentation Verification**: Confirm existence and non-empty content of `docs/mde_prize_alignment.md`.
