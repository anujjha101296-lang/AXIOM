# Analysis Report: Milestone 2 — Theorem Retrieval Engine & /mde/retrieval API (R2 & R3)

**Author:** Explorer 3 (Milestone 2)  
**Date:** 2026-08-06  
**Working Directory:** `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/explorer_m2_3_r2`  
**Target Modules:** `axiom/core/retrieval/engine.py`, `axiom/services/api_gateway/routes/mde.py`, `tests/test_mde_retrieval.py`

---

## Executive Summary

This report provides the architectural design, evidence chain, and actionable implementation recommendations for **Requirements 2 & 3** of Milestone 2 (Mathematical Discovery Engine). The target components are:
1. `axiom/core/retrieval/engine.py`: Formula retrieval, syntactic AST matching, semantic SymPy difference matching, dummy variable alpha-conversion, canonicalization, and NetworkX dependency DAG topological extraction.
2. `GET /mde/retrieval` API Endpoint: FastAPI route returning `RetrievalResponsePayload(query_formula, canonical_form, matched_theorems, equivalent_formulations, dependency_dag)`.
3. `tests/test_mde_retrieval.py`: Exhaustive unit and integration test suite verifying retrieval accuracy, scoring algorithms, DAG extraction, edge cases, and API compliance.

---

## 1. System Context & Requirements Mapping

### 1.1 Scope & Alignment
- **Milestone Goal**: Implement formula retrieval and theorem matching system capable of syntactic and semantic search across the epistemic knowledge graph (`EpistemicStore`).
- **Dependencies**:
  - `axiom/core/knowledge_graph/db.py`: `EpistemicStore` and SQLite graph storage (`nodes`, `edges`, `equivalent_statements`).
  - `axiom/core/knowledge_graph/schema.py`: `MathematicalClaimNode`, `DefinitionNode`, `EdgeType.DEPENDS_ON`, `EdgeType.EQUIVALENT_TO`.
  - `axiom/core/symbolic/sympy_engine.py`: `SymbolicMathEngine` for exact SymPy identity verification (`lhs - rhs == 0`).
  - `networkx`: Directed graph manipulations and topological sorting.
  - `fastapi` & `pydantic`: REST API schemas and router mounting.

---

## 2. Core Architectural Design: `axiom/core/retrieval/engine.py`

The retrieval engine contains five core modular sub-components:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       TheoremRetrievalEngine                            │
├───────────────────┬─────────────────────┬───────────────────────────────┤
│  Canonicalizer    │   Syntactic Matcher │       Semantic Matcher        │
│  & Alpha-Convert  │   (AST Distance)    │   (SymPy Difference Solver)   │
└─────────┬─────────┴──────────┬──────────┴──────────────┬────────────────┘
          │                    │                         │
          ▼                    ▼                         ▼
  Canonical Form        Syntactic Score           Semantic Score
          │                    │                         │
          └────────────────────┼─────────────────────────┘
                               ▼
                    Combined Confidence Score
                               │
                               ▼
                   NetworkX Dependency DAG
```

### 2.1 Formula Canonicalization & Alpha-Conversion (`FormulaCanonicalizer`)
- **Canonicalization**:
  - Parses string expressions into SymPy AST using `sympy.sympify()`.
  - Normalizes term order, expands or simplifies polynomials (e.g. `(a + b)**2` -> `a**2 + 2*a*b + b**2`), and formats variables consistently.
- **Dummy Variable Alpha-Conversion**:
  - Identifies bound indices (e.g., in `Sum`, `Integral`, `Product`) and free variables.
  - Renames dummy variables sequentially (`_x0, _x1, _x2...`) in pre-order traversal order.
  - Ensures formulas like `\sum_{i=1}^n i^2` and `\sum_{j=1}^n j^2` yield identical canonical strings.

### 2.2 Syntactic AST Tree Distance Matching (`SyntacticScore`)
- Converts expressions into AST tree structures (node types: `Add`, `Mul`, `Pow`, `Symbol`, `Integer`, `Function`).
- Calculates structural similarity between query AST $T_1$ and database claim AST $T_2$:
  $$\text{SyntacticScore}(T_1, T_2) = \frac{2 \cdot |\text{Subtrees}(T_1) \cap \text{Subtrees}(T_2)|}{|\text{Subtrees}(T_1)| + |\text{Subtrees}(T_2)|}$$
  or tree edit distance $d$:
  $$\text{SyntacticScore} = \frac{1}{1 + d}$$
- Score range: $[0.0, 1.0]$. Exact tree matches return $1.0$, structurally similar algebraic identities return $>0.8$, and unrelated formulas return $<0.3$.

### 2.3 Semantic SymPy Difference Matching (`SemanticScore`)
- Uses `SymbolicMathEngine` or `sp.simplify(query_expr - target_expr)`.
- For equations ($LHS = RHS$), converts to $LHS - RHS = 0$.
- If `sp.simplify(diff) == 0`, `SemanticScore = 1.0`.
- If symbolic simplification is inconclusive (e.g., transcendental functions), performs randomized high-precision numerical evaluation across sample points:
  - If $|f(x_k) - g(x_k)| < 10^{-12}$ for $k=1..5$, `SemanticScore = 0.95`.
- Range: $[0.0, 1.0]$.

### 2.4 Confidence Score Weighting
- Composite confidence score formula:
  $$\text{ConfidenceScore} = 0.6 \cdot \text{SemanticScore} + 0.4 \cdot \text{SyntacticScore}$$
- If `SemanticScore == 1.0`, confidence score is boosted to $1.0$.

### 2.5 NetworkX Dependency DAG Extraction
- Queries `EpistemicStore` for nodes and edges connected via `DEPENDS_ON`, `PROVES`, and `EQUIVALENT_TO`.
- Constructs `networkx.DiGraph`.
- Validates acyclicity using `nx.is_directed_acyclic_graph(G)`.
- Performs topological extraction (`list(nx.topological_sort(G))`).
- If cycles exist, sets `is_dag = False` and returns cycle details without crashing.

---

## 3. REST API Endpoint: `GET /mde/retrieval`

### 3.1 Route Registration Location
- File: `axiom/services/api_gateway/routes/mde.py`
- Prefix: `/mde`
- Mounted in `axiom/services/api_gateway/main.py`: `app.include_router(mde_router)`

### 3.2 Request Contract
```http
GET /mde/retrieval?query_formula=(a%2Bb)%5E2&domain=algebra&top_k=10
Authorization: Bearer <token>
```

### 3.3 Response Payload Schemas (`RetrievalResponsePayload`)
```python
class MatchedTheoremPayload(BaseModel):
    id: str
    name: str
    statement: str
    domain: str
    syntactic_score: float
    semantic_score: float
    confidence_score: float

class EquivalentFormulationPayload(BaseModel):
    id: str
    name: str
    statement: str
    proof_reference: Optional[str] = None
    match_score: float

class DependencyDagPayload(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    topological_order: List[str]
    is_dag: bool

class RetrievalResponsePayload(BaseModel):
    query_formula: str
    canonical_form: str
    matched_theorems: List[MatchedTheoremPayload]
    equivalent_formulations: List[EquivalentFormulationPayload]
    dependency_dag: DependencyDagPayload
```

---

## 4. Recommendations for `tests/test_mde_retrieval.py`

`tests/test_mde_retrieval.py` should be organized into 5 test groups:

1. **Canonicalization & Alpha Conversion**:
   - Test expansion and normalization of polynomial expressions.
   - Test alpha-conversion of sum/integral dummy variables.
   - Test malformed LaTeX/math string fallback handling.

2. **Syntactic AST Matching**:
   - Test identical AST tree score == 1.0.
   - Test sub-expression similarity scoring.
   - Test ranking ordering for multiple candidate theorems.

3. **Semantic Equivalence Matching**:
   - Test algebraic identity equivalence (`(a+b)^2` vs `a^2+2ab+b^2`).
   - Test trigonometric identity equivalence (`sin^2(x) + cos^2(x)` vs `1`).
   - Test non-equivalent expression rejection (score == 0.0).

4. **NetworkX DAG Extraction**:
   - Test valid dependency DAG extraction and topological order.
   - Test cyclic dependency graph detection (`is_dag == False`).
   - Test isolated disconnected node handling.

5. **FastAPI `GET /mde/retrieval` Endpoint Tests**:
   - Test successful HTTP 200 response with populated `RetrievalResponsePayload`.
   - Test domain filtering (`domain="analytic_number_theory"`).
   - Test empty database response structure.
   - Test large query string safety.

---

## 5. Evidence Chain

| Component | Target File | Source Reference | Verification Method |
|-----------|-------------|------------------|---------------------|
| SymPy Engine | `axiom/core/symbolic/sympy_engine.py` | `SCOPE.md`, `test_tier3_tier4_e2e.py:547` | Unit tests for exact arithmetic |
| Retrieval Engine | `axiom/core/retrieval/engine.py` | `SCOPE.md`, `test_m1_m3_e2e.py:1066` | Unit tests for match & DAG extraction |
| MDE Route | `axiom/services/api_gateway/routes/mde.py` | `main.py`, `SCOPE.md` | `TestClient(app).get("/mde/retrieval")` |
| Retrieval Test Suite | `tests/test_mde_retrieval.py` | `SCOPE.md` | `pytest tests/test_mde_retrieval.py` |
