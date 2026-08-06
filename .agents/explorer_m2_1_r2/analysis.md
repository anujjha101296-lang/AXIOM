# Milestone 2 Exploration Report: Symbolic Math Interface & Theorem Retrieval Engine

**Agent**: Explorer 1 for Milestone 2 (`explorer_m2_1_r2`)  
**Date**: 2026-08-06  
**Target Milestone**: Milestone 2 — Symbolic Math Interface & Theorem Retrieval Engine (Requirements R2 & R6)  
**Working Directory**: `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/explorer_m2_1_r2`

---

## 1. Executive Summary

This investigation analyzed the AXIOM repository state at `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom` for Milestone 2 (Symbolic Math Interface & Theorem Retrieval Engine). The objective was to audit the existing repository, verify dependency and Python environment conditions, locate where new core packages (`axiom/core/symbolic/` and `axiom/core/retrieval/`) and API routes belong, inspect the test runner setup (`pytest.py` & `tests/`), and define concrete implementation blueprints for subsequent worker agents.

### Core Discoveries:
1. **Core Directory Gaps**:
   - `axiom/core/symbolic/` does **not** exist yet and must be created (`axiom/core/symbolic/__init__.py` and `axiom/core/symbolic/sympy_engine.py`).
   - `axiom/core/retrieval/` does **not** exist yet and must be created (`axiom/core/retrieval/__init__.py` and `axiom/core/retrieval/engine.py`).
2. **FastAPI Route Architecture**:
   - Main application is in `axiom/services/api_gateway/main.py`.
   - Existing routers: `mip_router` (`axiom/services/api_gateway/routes/mip.py`) and `eval_router` (`axiom/services/api_gateway/routes/eval_api.py`).
   - New endpoint `GET /mde/retrieval` must be added either in `axiom/services/api_gateway/routes/mde.py` or directly mounted in `main.py`.
3. **Environment & Dependency Profile**:
   - Python Version: System Python 3.9.6 (`/usr/bin/python3`).
   - Network Mode: Offline / sandbox-restricted.
   - Dependencies: `pyproject.toml` specifies `pydantic ^2.5.0`, `sympy ^1.12`, `networkx ^3.0`, `fastapi ^0.100.0`, `z3-solver ^4.12.0`, `pytest ^8.0.0`.
   - Test Runner: A custom lightweight test runner `pytest.py` is present in the workspace root. Standalone tests support fallback shims registered in `sys.modules` for missing third-party packages (`sympy`, `networkx`, `pydantic`, `fastapi`) when needed.
4. **Target Verification Criteria**:
   - Exact identity verification via `sp.simplify(lhs - rhs) == 0` without IEEE 754 float precision loss (e.g. `(a+b)^2 == a^2 + 2ab + b^2`).
   - Exact rational arithmetic via `sp.Rational`.
   - Dirichlet series expansion ($\sum_{n=1}^k a_n / n^s$) and exact zeta zero evaluation (`sp.zeta(n)`).
   - Formula retrieval with syntactic AST tree matching (`SyntacticScore`), semantic SymPy difference matching (`SemanticScore`), alpha-conversion, canonicalization, and NetworkX dependency DAG extraction.
   - REST API `GET /mde/retrieval` returning structured Pydantic payload `RetrievalResponsePayload`.

---

## 2. Codebase Structure & Environment Inspection

### 2.1 Repository Directory Tree
```
/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/
├── .agents/                      # Agent metadata (plans, progress, handoffs)
├── axiom/                        # Core Python package
│   ├── config/                   # Settings and environment config (settings.py)
│   ├── core/                     # Core domain engines
│   │   ├── events/               # In-process event bus (bus.py)
│   │   ├── knowledge_graph/      # SQLite store (db.py), schema (schema.py), migrations (migrations.py)
│   │   ├── memory/               # Working memory (working_memory.py)
│   │   ├── parser/               # LaTeX parser (arxiv_parser.py), semantic tracker
│   │   ├── reasoning/            # Hypothesis engine, MCTS proof search, self-improvement
│   │   ├── verification/         # Lean exporter (lean_exporter.py), SMT gateway (smt_gateway.py)
│   │   ├── symbolic/             # [TO BE CREATED] SymPy exact math engine (sympy_engine.py)
│   │   └── retrieval/            # [TO BE CREATED] Formula retrieval & AST matching (engine.py)
│   ├── db/                       # Database migrations
│   ├── evaluation/               # SCEP framework, benchmarks, prize readiness, delta reports
│   ├── mip/                      # Mathematical Intelligence Platform modules
│   ├── observability/            # Logging and Prometheus metrics
│   └── services/
│       └── api_gateway/          # FastAPI application (main.py)
│           └── routes/           # REST routers (mip.py, eval_api.py, [TO BE ADDED: mde.py])
├── docs/                         # Specifications and framework documentation
├── pyproject.toml                # Dependencies & Poetry config
├── pytest.py                     # Custom test runner script
├── tests/                        # Unit and integration test suite
│   ├── test_epistemic_layer.py
│   ├── test_mde_ontology.py      # Added in Milestone 1
│   ├── test_verification_improvements.py
│   ├── test_mde_symbolic.py      # [TO BE CREATED] Unit tests for SymbolicMathEngine
│   ├── test_mde_retrieval.py     # [TO BE CREATED] Unit tests for FormulaRetrievalEngine
│   └── e2e/                      # E2E test suites (test_m1_m3_e2e.py, etc.)
```

### 2.2 Existing EGS Ontological Schema Inspection (`axiom/core/knowledge_graph/`)
The database schema (`schema.py` & `migrations.py` v4) includes mathematical ontology types required for theorem retrieval and symbolic representation:
- **Node Types (`NodeType`)**:
  - `MATHEMATICAL_OBJECT`: Fields: `domain`, `symbolic_representation`, `formal_type`, `properties`.
  - `DEFINITION`: Fields: `term`, `formal_definition`, `informal_description`, `domain`.
  - `OPEN_PROBLEM`: Fields: `statement`, `prize_bounty`, `importance_score`.
  - `CONJECTURE`: Fields: `statement`, `formal_specification`, `novelty_score`, `generation_strategy`.
  - `MATHEMATICAL_CLAIM`: Fields: `statement`, `formal_specification`, `status`, `tier`.
- **Edge Types (`EdgeType`)**:
  - `EQUIVALENT_TO`: Bidirectional equivalence relation.
  - `DEPENDS_ON`: Unidirectional dependency edge.
  - `PROVES`: Proof derivation edge.
- **EpistemicStore Methods (`db.py`)**:
  - `get_nodes_by_type(node_type)`
  - `get_edges_by_type(edge_type)`
  - `get_equivalent_statements(claim_id)`
  - `to_networkx() -> nx.DiGraph`

---

## 3. Module Specifications & Design Blueprints for Milestone 2

### 3.1 Symbolic Math Engine (`axiom/core/symbolic/sympy_engine.py`)

**Purpose**: Provide 100% exact mathematical operations using SymPy, eliminating float precision drift (IEEE 754 errors), and providing specialized routines for Riemann hypothesis (zeta zeros) and Dirichlet series expansions.

**Class Architecture**:
```python
from __future__ import annotations
import math
from typing import Dict, List, Optional, Any, Tuple, Union
import sympy as sp

class SymbolicMathEngine:
    """Exact symbolic computation engine wrapping SymPy."""

    def exact_rational(self, numerator: int, denominator: int) -> sp.Rational:
        """Create exact rational number without float conversion."""
        return sp.Rational(numerator, denominator)

    def verify_identity(self, lhs: str, rhs: str) -> bool:
        """Exact algebraic identity verification eliminating IEEE 754 float drift."""
        try:
            lhs_expr = sp.sympify(lhs)
            rhs_expr = sp.sympify(rhs)
            diff = sp.simplify(lhs_expr - rhs_expr)
            return diff == 0
        except Exception:
            return False

    def verify_algebraic_identity(self, lhs: str, rhs: str) -> Dict[str, Any]:
        """Verify identity returning detailed breakdown and exact difference."""
        try:
            lhs_expr = sp.sympify(lhs)
            rhs_expr = sp.sympify(rhs)
            simplified_lhs = sp.expand(lhs_expr)
            simplified_rhs = sp.expand(rhs_expr)
            diff = sp.simplify(simplified_lhs - simplified_rhs)
            is_valid = (diff == 0)
            return {
                "lhs": str(lhs_expr),
                "rhs": str(rhs_expr),
                "simplified_lhs": str(simplified_lhs),
                "simplified_rhs": str(simplified_rhs),
                "difference": str(diff),
                "is_identity": is_valid,
            }
        except Exception as e:
            return {
                "lhs": lhs,
                "rhs": rhs,
                "difference": "ERROR",
                "is_identity": False,
                "error": str(e),
            }

    def solve_integer_counterexample_grid(
        self, equation: str, var_bounds: Dict[str, Tuple[int, int]]
    ) -> Optional[Dict[str, int]]:
        """Exact integer counterexample solver over a bounded search grid."""
        try:
            expr = sp.sympify(equation)
            free_symbols = list(expr.free_symbols)
            symbol_names = [str(s) for s in free_symbols]
            
            ranges = [
                range(var_bounds.get(name, (0, 10))[0], var_bounds.get(name, (0, 10))[1] + 1)
                for name in symbol_names
            ]
            
            import itertools
            for val_tuple in itertools.product(*ranges):
                subs_map = dict(zip(free_symbols, val_tuple))
                res = expr.subs(subs_map)
                if res != 0:
                    return {str(s): val for s, val in zip(free_symbols, val_tuple)}
            return None
        except Exception:
            return None

    def evaluate_zeta_zero(self, n: int) -> Dict[str, Any]:
        """Evaluate exact/high-precision value of zeta function at integer or zero argument."""
        try:
            val = sp.zeta(n)
            return {
                "n": n,
                "exact_value": str(val),
                "numeric_float": float(val.evalf()) if hasattr(val, "evalf") else float(val),
                "is_zero": val == 0,
            }
        except Exception as e:
            return {"n": n, "error": str(e)}

    def expand_dirichlet_series(
        self, coefficients: List[Union[int, float, str]], s_var: str = "s", num_terms: int = 5
    ) -> str:
        """Expand Dirichlet series \\sum_{n=1}^k a_n / n^s into SymPy format string."""
        terms = []
        for n_idx, coeff in enumerate(coefficients[:num_terms], start=1):
            if coeff == 0:
                continue
            terms.append(f"({coeff}) / ({n_idx}**{s_var})")
        return " + ".join(terms) if terms else "0"
```

---

### 3.2 Theorem Retrieval & Dependency Discovery (`axiom/core/retrieval/engine.py`)

**Purpose**: Provide AST-based formula retrieval, syntactic tree distance matching, semantic SymPy difference matching, dummy variable canonicalization, and NetworkX dependency DAG extraction.

**Class Architecture**:
```python
from __future__ import annotations
import re
from typing import Dict, List, Optional, Any, Tuple, Union
import networkx as nx
import sympy as sp

from axiom.core.knowledge_graph.db import EpistemicStore
from axiom.core.symbolic.sympy_engine import SymbolicMathEngine

class FormulaRetrievalEngine:
    """Formula retrieval, AST matching, and dependency DAG discovery engine."""

    def __init__(self, store: Optional[EpistemicStore] = None):
        self.store = store
        self.symbolic_engine = SymbolicMathEngine()
        self.default_corpus = [
            {
                "id": "thm_add_comm",
                "name": "Commutativity of Addition",
                "formula": "a + b = b + a",
                "canonical": "x_0 + x_1 = x_1 + x_0",
                "domain": "algebra",
            },
            {
                "id": "thm_diff_sq",
                "name": "Difference of Squares",
                "formula": "x**2 - y**2 = (x - y)*(x + y)",
                "canonical": "x_0**2 - x_1**2 = (x_0 - x_1)*(x_0 + x_1)",
                "domain": "algebra",
            },
            {
                "id": "thm_rh_lemma1",
                "name": "Zeta Functional Equation",
                "formula": "zeta(s) = 2**s * pi**(s-1) * sin(pi*s/2) * gamma(1-s) * zeta(1-s)",
                "canonical": "zeta(s)",
                "domain": "analytic_number_theory",
            },
        ]

    def canonicalize_formula(self, formula_str: str) -> str:
        """Alpha-convert dummy variables into normalized index format (x_0, x_1, ...)."""
        try:
            expr = sp.sympify(formula_str.split("=")[0] if "=" in formula_str else formula_str)
            symbols = sorted(list(expr.free_symbols), key=lambda s: str(s))
            sub_map = {sym: sp.Symbol(f"x_{i}") for i, sym in enumerate(symbols)}
            canonical_expr = expr.subs(sub_map)
            return str(canonical_expr)
        except Exception:
            return re.sub(r"\s+", "", formula_str).lower()

    def compute_syntactic_score(self, query_norm: str, target_norm: str) -> float:
        """Syntactic AST / character edit similarity score [0, 1]."""
        if query_norm == target_norm:
            return 1.0
        common = set(query_norm).intersection(set(target_norm))
        denom = max(len(set(query_norm)), len(set(target_norm)))
        return round(len(common) / denom if denom > 0 else 0.0, 4)

    def compute_semantic_score(self, query_formula: str, target_formula: str) -> float:
        """Semantic SymPy difference score [0, 1]."""
        try:
            if self.symbolic_engine.verify_identity(query_formula, target_formula):
                return 1.0
            return 0.5 if any(tok in query_formula for tok in target_formula.split()) else 0.0
        except Exception:
            return 0.0

    def match_formula(self, formula_str: str, domain: Optional[str] = None) -> List[Dict[str, Any]]:
        """Match input formula against corpus and SQLite knowledge store."""
        results = []
        canonical_q = self.canonicalize_formula(formula_str)
        norm_query = re.sub(r"\s+", "", formula_str).lower()

        # Query database nodes if EpistemicStore is attached
        corpus = list(self.default_corpus)
        if self.store:
            db_claims = self.store.get_nodes_by_type("MATHEMATICAL_CLAIM")
            for claim in db_claims:
                corpus.append({
                    "id": claim.id,
                    "name": claim.name,
                    "formula": claim.statement,
                    "canonical": self.canonicalize_formula(claim.statement),
                    "domain": claim.metadata.get("domain", "general") if hasattr(claim, "metadata") else "general",
                })

        for item in corpus:
            if domain and item["domain"] != domain:
                continue
            norm_item = re.sub(r"\s+", "", item["formula"]).lower()

            syn_score = self.compute_syntactic_score(norm_query, norm_item)
            sem_score = self.compute_semantic_score(formula_str, item["formula"])
            confidence = round(0.4 * syn_score + 0.6 * sem_score, 4)

            if norm_query == norm_item or confidence > 0.3:
                results.append({
                    "theorem_id": item["id"],
                    "name": item["name"],
                    "formula": item["formula"],
                    "canonical": item["canonical"],
                    "confidence_score": max(confidence, 1.0 if norm_query == norm_item else confidence),
                    "syntactic_score": syn_score,
                    "semantic_score": sem_score,
                    "semantic_match": sem_score == 1.0,
                })

        results.sort(key=lambda x: x["confidence_score"], reverse=True)
        return results

    def extract_dependency_dag(self, store: EpistemicStore, root_id: Optional[str] = None) -> nx.DiGraph:
        """Extract NetworkX dependency DAG containing DEPENDS_ON, PROVES, and EQUIVALENT_TO edges."""
        G = store.to_networkx()
        dag = nx.DiGraph()

        if hasattr(G, "edges"):
            # If G.edges is a callable or iterable view
            edge_list = G.edges(data=True) if callable(getattr(G, "edges", None)) else G.edges
            for u, v, d in (edge_list if isinstance(edge_list, list) else G.edges(data=True)):
                edge_type = d.get("type") if isinstance(d, dict) else None
                if edge_type in ("DEPENDS_ON", "PROVES", "EQUIVALENT_TO"):
                    dag.add_edge(u, v, **(d if isinstance(d, dict) else {}))

        if hasattr(G, "nodes"):
            node_iter = G.nodes() if callable(getattr(G, "nodes", None)) else G.nodes
            for node in node_iter:
                if not dag.has_node(node):
                    dag.add_node(node)

        return dag
```

---

### 3.3 REST Router Blueprint (`axiom/services/api_gateway/routes/mde.py`)

**Endpoint**: `GET /mde/retrieval`

**Pydantic Models & Router**:
```python
from __future__ import annotations
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field

from axiom.core.knowledge_graph.db import EpistemicStore
from axiom.core.retrieval.engine import FormulaRetrievalEngine
from axiom.services.api_gateway.auth import verify_token

router = APIRouter(prefix="/mde", tags=["Mathematical Discovery Engine"])

class MatchedTheorem(BaseModel):
    theorem_id: str
    name: str
    formula: str
    confidence_score: float
    semantic_match: bool

class RetrievalResponsePayload(BaseModel):
    query_formula: str
    canonical_form: str
    matched_theorems: List[MatchedTheorem]
    equivalent_formulations: List[str]
    dependency_dag: Dict[str, Any]

@router.get("/retrieval", response_model=RetrievalResponsePayload)
def get_formula_retrieval(
    formula: str = Query(..., description="Target formula string e.g. 'a + b = b + a'"),
    domain: Optional[str] = Query(None, description="Optional domain filter"),
    token: str = Depends(verify_token),
):
    """Fetch relevant theorems, equivalent formulations, and dependency DAG for query formula."""
    try:
        store = EpistemicStore("axiom.db")
        retrieval_engine = FormulaRetrievalEngine(store)

        canonical = retrieval_engine.canonicalize_formula(formula)
        matches = retrieval_engine.match_formula(formula, domain=domain)
        dag = retrieval_engine.extract_dependency_dag(store)

        matched_list = [
            MatchedTheorem(
                theorem_id=m["theorem_id"],
                name=m["name"],
                formula=m["formula"],
                confidence_score=m.get("confidence_score", 1.0),
                semantic_match=m.get("semantic_match", True),
            )
            for m in matches
        ]

        dag_json = {
            "nodes": list(dag.nodes()),
            "edges": [{"source": u, "target": v, "type": d.get("type")} for u, v, d in dag.edges(data=True)],
        }

        return RetrievalResponsePayload(
            query_formula=formula,
            canonical_form=canonical,
            matched_theorems=matched_list,
            equivalent_formulations=[m["formula"] for m in matches if m["theorem_id"] != formula],
            dependency_dag=dag_json,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrieval engine error: {str(e)}")
```

---

## 4. Test Strategy & Test Runner Verification

### 4.1 Test Execution Command
In this repository environment, tests are executed using:
```bash
python3 pytest.py tests/test_mde_symbolic.py
python3 pytest.py tests/test_mde_retrieval.py
```

### 4.2 Unit Test Design for Milestone 2

1. **`tests/test_mde_symbolic.py`**:
   - `test_exact_rational_arithmetic()`: Verify `sp.Rational(1, 3) + sp.Rational(1, 6) == sp.Rational(1, 2)` without float drift.
   - `test_verify_algebraic_identity()`: Verify `(a+b)^2 == a^2 + 2ab + b^2` evaluates to 0 difference.
   - `test_integer_counterexample_solver()`: Verify finding counterexample for `x^2 + y^2 = 3` (no integer solution) vs `x^2 - y^2 = 5` (solvable).
   - `test_zeta_zero_evaluator()`: Verify `evaluate_zeta_zero(-2)` gives exact `0`.
   - `test_dirichlet_series_expansion()`: Verify expanding `[1, -1, 1, -1]` for variable `s`.

2. **`tests/test_mde_retrieval.py`**:
   - `test_canonicalize_formula()`: Verify variable renaming `a + b` to `x_0 + x_1`.
   - `test_syntactic_score()`: Verify exact match gets `1.0`.
   - `test_semantic_score()`: Verify `x**2 - y**2 = (x-y)*(x+y)` gets `1.0`.
   - `test_match_formula_ranking()`: Verify confidence score sorting.
   - `test_extract_dependency_dag()`: Verify DAG extraction from `EpistemicStore`.
   - `test_retrieval_api_endpoint()`: Verify `GET /mde/retrieval` payload structure and auth requirement.

---

## 5. Risk Analysis & Mitigation

| Risk Area | Threat | Mitigation Strategy |
|---|---|---|
| **Float Drift** | IEEE 754 rounding errors causing false inequality in algebraic identities | Mandatory usage of `sp.Rational` and `sp.simplify(lhs - rhs) == 0`. |
| **NetworkX API Differences** | Incompatibilities between full NetworkX and test environment shims (`G.edges(data=True)`) | Safely guard `G.edges` call with `isinstance` / `callable` checks in `extract_dependency_dag`. |
| **Pydantic Serialization** | Pydantic v2 `BaseModel.model_dump()` vs dict conversion in FastAPI responses | Explicitly define `RetrievalResponsePayload` using standard Pydantic v2 BaseModel. |
| **Malformed Formula Strings** | User input with bad syntax crashing SymPy parser (`sp.sympify`) | Wrap `sympify` in try/except blocks returning graceful fallback score/message. |

---

## 6. Recommendations & Next Steps

1. **Worker 1 (`worker_m2_1_r2`)**:
   - Implement `axiom/core/symbolic/__init__.py` and `axiom/core/symbolic/sympy_engine.py`.
   - Write unit tests in `tests/test_mde_symbolic.py`.
2. **Worker 2 (`worker_m2_2_r2`)**:
   - Implement `axiom/core/retrieval/__init__.py` and `axiom/core/retrieval/engine.py`.
   - Create router `axiom/services/api_gateway/routes/mde.py` and mount in `axiom/services/api_gateway/main.py`.
   - Write unit tests in `tests/test_mde_retrieval.py`.
3. **Verification**:
   - Run `python3 pytest.py tests/test_mde_symbolic.py` and `python3 pytest.py tests/test_mde_retrieval.py`.
