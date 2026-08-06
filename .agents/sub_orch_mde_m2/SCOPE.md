# Scope: Milestone 2 — Symbolic Math Interface & Theorem Retrieval Engine (R2 & R6)

## Architecture
- `axiom/core/symbolic/sympy_engine.py`: Exact SymPy engine eliminating IEEE 754 float drift. Implement `SymbolicMathEngine` with exact rational arithmetic (`sp.Rational`), identity verification (`sp.simplify(lhs - rhs) == 0`), exact integer counterexample grid solver, exact zeta zero evaluator (`sp.zeta(n)`), and Dirichlet series expansion (`\sum_{n=1}^k a_n / n^s`).
- `axiom/core/retrieval/engine.py`: Formula retrieval & AST matching engine. Syntactic AST tree distance matching (`SyntacticScore`), semantic SymPy difference matching (`SemanticScore`), dummy variable alpha-conversion, canonicalization, and NetworkX dependency DAG topological extraction.
- REST Endpoint: `GET /mde/retrieval` returning `RetrievalResponsePayload(query_formula, canonical_form, matched_theorems, equivalent_formulations, dependency_dag)`.
- Unit tests in `tests/test_mde_retrieval.py` and `tests/test_mde_symbolic.py`.

## Scope Items
1. Implement `axiom/core/symbolic/sympy_engine.py` with 100% exact math arithmetic, precision float drift guard, and Dirichlet series/zeta zero support.
2. Implement `axiom/core/retrieval/engine.py` with formula AST parsing, syntactic/semantic scoring, NetworkX DAG extraction, and canonicalization.
3. Expose `GET /mde/retrieval` API contract with Pydantic payload models.
4. Write unit tests in `tests/test_mde_symbolic.py` and `tests/test_mde_retrieval.py` and run verification.

## Verification Criteria
- `verify_algebraic_identity` evaluates `(a+b)^2 == a^2+2ab+b^2` to exact 0 difference without float precision loss.
- `GET /mde/retrieval` returns matched theorems, confidence scores, and valid NetworkX dependency DAG.
- All tests in `tests/test_mde_symbolic.py` and `tests/test_mde_retrieval.py` pass.
