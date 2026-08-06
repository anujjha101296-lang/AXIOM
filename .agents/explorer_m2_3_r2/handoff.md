# Handoff Report: Milestone 2 — Theorem Retrieval Engine & /mde/retrieval API (R2 & R3)

**Agent:** Explorer 3 (Milestone 2)  
**Target:** Sub-Orchestrator (`c614aeb9-e901-4e61-b5f5-ea8838c096cb`)  
**Date:** 2026-08-06  
**Working Directory:** `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/explorer_m2_3_r2`

---

## 1. Observation

1. **File Locations & Existing Structure**:
   - `axiom/services/api_gateway/main.py` lines 66-70: App mounts `mip_router` and `eval_router`.
   - `tests/e2e/test_m1_m3_e2e.py` lines 1066-1168: Feature 4 tests exist, referencing a fixture class `FormulaRetrievalEngine` matching `a + b = b + a`, `x**2 - y**2 = (x - y)*(x + y)`, and NetworkX DAG extraction.
   - `tests/e2e/test_tier3_tier4_e2e.py` lines 620-687: Prototype `FormulaRetrievalEngine` implemented in test code.

2. **Requirements from `SCOPE.md`**:
   - Create production module `axiom/core/retrieval/engine.py`.
   - Syntactic AST tree distance matching (`SyntacticScore`).
   - Semantic SymPy difference matching (`SemanticScore`).
   - Dummy variable alpha-conversion.
   - Canonicalization.
   - NetworkX dependency DAG topological extraction.
   - REST Endpoint: `GET /mde/retrieval` returning `RetrievalResponsePayload(query_formula, canonical_form, matched_theorems, equivalent_formulations, dependency_dag)`.
   - Unit test suite: `tests/test_mde_retrieval.py`.

---

## 2. Logic Chain

1. **Observation 1 & 2** show that while E2E test suites contain inline fixture stubs for `FormulaRetrievalEngine`, production code in `axiom/core/retrieval/engine.py` and `axiom/services/api_gateway/routes/mde.py` does not yet exist.
2. **Canonicalization & Alpha-Conversion**: Expressions must be converted to SymPy AST, bound/dummy variables mapped to `_x0, _x1...`, and terms ordered canonically to ensure robust formula matching.
3. **AST & Semantic Matching**: Syntactic matching compares AST structure (tree edit distance or subtree overlap ratio), while semantic matching uses `SymbolicMathEngine` / `sp.simplify(expr1 - expr2) == 0`.
4. **DAG Extraction**: `NetworkX` graph is built from `EpistemicStore` nodes/edges (`DEPENDS_ON`, `EQUIVALENT_TO`), checking acyclicity via `nx.is_directed_acyclic_graph()` and running topological sort.
5. **API Endpoint & Routing**: Exposing `GET /mde/retrieval` via a dedicated router `axiom/services/api_gateway/routes/mde.py` mounted on `main.py` cleanly separates MDE domain endpoints and fulfills all Pydantic response contract requirements (`RetrievalResponsePayload`).

---

## 3. Caveats

- **Assumption**: Implementers will create `axiom/core/symbolic/sympy_engine.py` (Requirement 1 of M2) alongside `axiom/core/retrieval/engine.py` (Requirement 2 & 3), or `FormulaRetrievalEngine` can import `SymbolicMathEngine` with a fallback to `sympy.simplify`.
- **Scope Limit**: Read-only exploration. No production source files under `axiom/` were created or modified during this investigation.

---

## 4. Conclusion

The specification, architecture, Pydantic schemas, and test strategies for Requirement 2 & 3 of Milestone 2 are fully investigated and ready for implementation. 

Implementation tasks for Implementer:
1. Implement `axiom/core/retrieval/engine.py` with `FormulaCanonicalizer`, `SyntacticScore`, `SemanticScore`, `NetworkX` DAG extractor, and `TheoremRetrievalEngine`.
2. Implement `axiom/services/api_gateway/routes/mde.py` with `GET /mde/retrieval` returning `RetrievalResponsePayload`. Register `mde_router` in `axiom/services/api_gateway/main.py`.
3. Implement `tests/test_mde_retrieval.py` with unit tests for canonicalization, AST matching, semantic scoring, DAG extraction, and API endpoints.

---

## 5. Verification Method

To verify the upcoming implementation:
1. Run unit test suite:
   ```bash
   pytest tests/test_mde_retrieval.py -v
   ```
2. Run E2E test suites to ensure zero regression:
   ```bash
   pytest tests/e2e/test_m1_m3_e2e.py -v -k "retrieval"
   pytest tests/e2e/test_tier3_tier4_e2e.py -v -k "FormulaRetrievalEngine"
   ```
3. Test API endpoint via FastAPI `TestClient`:
   ```python
   client = TestClient(app)
   res = client.get("/mde/retrieval?query_formula=a%2Bb%3Db%2Ba", headers={"Authorization": "Bearer test_token"})
   assert res.status_code == 200
   assert "canonical_form" in res.json()
   ```
