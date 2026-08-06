## 2026-08-06T05:56:51Z

You are the Milestone 2 Sub-Orchestrator for MDE (Mathematical Discovery Engine) in AXIOM.
Working directory: /Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/sub_orch_mde_m2
Project root: /Users/itachiuchiha/.gemini/antigravity/scratch/axiom

Task:
Read:
- /Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/ORIGINAL_REQUEST.md
- /Users/itachiuchiha/.gemini/antigravity/scratch/axiom/PROJECT.md
- /Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/sub_orch_mde_m2/SCOPE.md

Your scope is Milestone 2: Symbolic Math Interface & Theorem Retrieval Engine (R2 & R6).
Scope items:
1. Implement `axiom/core/symbolic/sympy_engine.py`: Exact SymPy engine eliminating IEEE 754 float drift. Implement `SymbolicMathEngine` with exact rational arithmetic (`sp.Rational`), identity verification (`sp.simplify(lhs - rhs) == 0`), exact integer counterexample grid solver, exact zeta zero evaluator (`sp.zeta(n)`), and Dirichlet series expansion (`\sum_{n=1}^k a_n / n^s`).
2. Implement `axiom/core/retrieval/engine.py`: Formula retrieval & formula AST matching engine. Syntactic AST tree distance matching (`SyntacticScore`), semantic SymPy difference matching (`SemanticScore`), dummy variable alpha-conversion, canonicalization, and NetworkX dependency DAG topological extraction.
3. Expose `GET /mde/retrieval` API endpoint returning `RetrievalResponsePayload(query_formula, canonical_form, matched_theorems, equivalent_formulations, dependency_dag)`.
4. Write unit tests in `tests/test_mde_symbolic.py` and `tests/test_mde_retrieval.py` and run verification.

Follow the iteration loop: Explorer -> Worker -> Reviewer -> Challenger -> Auditor -> Gate check.
Once verified and complete, update your status and send a completion message to parent.
