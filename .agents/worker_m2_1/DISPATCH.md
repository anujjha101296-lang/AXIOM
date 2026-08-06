## 2026-08-06T16:22:52Z
<USER_REQUEST>
You are the Worker for Milestone 2 (Symbolic Math Interface & Theorem Retrieval Engine).
Your working directory: /Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/worker_m2_1
Project root: /Users/itachiuchiha/.gemini/antigravity/scratch/axiom

Read:
- /Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/ORIGINAL_REQUEST.md
- /Users/itachiuchiha/.gemini/antigravity/scratch/axiom/PROJECT.md
- /Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/sub_orch_mde_m2/SCOPE.md
- /Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/explorer_m2_1_r2/handoff.md
- /Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/explorer_m2_2_r2/handoff.md
- /Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/explorer_m2_3_r2/handoff.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Tasks to implement:
1. `axiom/core/symbolic/sympy_engine.py`:
   - Exact SymPy engine eliminating IEEE 754 float drift using `sp.Rational`.
   - `SymbolicMathEngine` class:
     * `verify_identity(lhs: str, rhs: str)` checking `sp.simplify(lhs - rhs) == 0`.
     * `find_integer_counterexample(lhs: str, rhs: str, variables: list[str], search_range: tuple[int, int])` exact integer grid solver.
     * `evaluate_zeta(n_or_s: Union[int, str])` exact zeta zero / value evaluator (`sp.zeta(n)`).
     * `expand_dirichlet_series(coefficients: list[Union[int, str]], k: int, s_var: str = 's')` ($\sum_{n=1}^k a_n / n^s$).
   - Proper Pydantic v2 data models for returns (`IdentityVerificationResult`, `CounterexampleResult`, `ZetaEvaluationResult`, `DirichletSeriesResult`).
2. `axiom/core/retrieval/engine.py`:
   - Formula retrieval & formula AST matching engine `TheoremRetrievalEngine`.
   - Syntactic AST tree distance matching (`SyntacticScore`).
   - Semantic SymPy difference matching (`SemanticScore`).
   - Dummy variable alpha-conversion and formula canonicalization (`canonicalize_formula`).
   - NetworkX dependency DAG topological extraction (`extract_dependency_dag`).
   - Models: `TheoremMatch`, `RetrievalResponsePayload`.
3. `axiom/services/api_gateway/routes/mde.py`:
   - Expose `GET /mde/retrieval` API endpoint returning `RetrievalResponsePayload(query_formula, canonical_form, matched_theorems, equivalent_formulations, dependency_dag)`.
   - Register route in `axiom/services/api_gateway/main.py`.
4. Write unit tests:
   - `tests/test_mde_symbolic.py` testing all `SymbolicMathEngine` functionality.
   - `tests/test_mde_retrieval.py` testing theorem retrieval engine and API endpoint (`GET /mde/retrieval` via FastAPI TestClient).
5. Run pytest and verify 100% pass: `python3 -m pytest tests/test_mde_symbolic.py tests/test_mde_retrieval.py` (or using pytest runner).

Write your handoff report at `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/worker_m2_1/handoff.md` detailing code changes, test execution commands, and test outputs. Send a completion message to sub-orchestrator when finished.
</USER_REQUEST>
