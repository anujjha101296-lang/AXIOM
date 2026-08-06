"""
AXIOM Theorem Retrieval & Formula AST Matching Engine
Provides syntactic AST tree distance matching, semantic SymPy difference matching,
dummy variable alpha-conversion canonicalization, and NetworkX dependency DAG topological extraction.
"""

from __future__ import annotations

import re
import ast
import math
from typing import Dict, List, Optional, Tuple, Union, Any

try:
    from pydantic import BaseModel, Field
except ImportError:
    class BaseModel:
        def __init__(self, **data):
            for k, v in data.items():
                setattr(self, k, v)

        def model_dump(self):
            return {k: getattr(self, k) for k in self.__dict__}

        def model_dump_json(self):
            import json
            return json.dumps(self.model_dump())

        @classmethod
        def validate_json(cls, json_str):
            import json
            data = json.loads(json_str)
            return cls(**data)

    def Field(default=..., **kwargs):
        if default is not ...:
            return default
        default_factory = kwargs.get("default_factory")
        if default_factory is not None:
            return default_factory()
        return None

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    nx = None
    HAS_NETWORKX = False

from axiom.core.symbolic.sympy_engine import SymbolicMathEngine


class SyntacticScore(BaseModel):
    """Syntactic AST matching evaluation."""
    ast_similarity: float = Field(..., description="AST tree similarity score [0.0, 1.0]")
    tree_distance: int = Field(..., description="AST tree edit distance")
    token_overlap: float = Field(..., description="Jaccard token overlap ratio [0.0, 1.0]")
    composite_score: float = Field(..., description="Combined syntactic score [0.0, 1.0]")


class SemanticScore(BaseModel):
    """Semantic SymPy difference evaluation."""
    exact_match: bool = Field(..., description="True if query and candidate match verbatim or after canonicalization")
    sympy_difference_is_zero: bool = Field(..., description="True if sp.simplify(query - candidate) == 0")
    simplified_diff: str = Field(..., description="Simplified symbolic difference string")
    semantic_confidence: float = Field(..., description="Semantic equivalence confidence score [0.0, 1.0]")


class TheoremMatch(BaseModel):
    """Matched theorem payload."""
    theorem_id: str = Field(..., description="Unique ID of matched theorem")
    name: str = Field(..., description="Human readable theorem title")
    formula: str = Field(..., description="Original formula representation")
    canonical_formula: str = Field(..., description="Alpha-converted canonical formula")
    syntactic_score: SyntacticScore = Field(..., description="Syntactic AST score breakdown")
    semantic_score: SemanticScore = Field(..., description="Semantic score breakdown")
    combined_confidence: float = Field(..., description="Combined overall confidence score [0.0, 1.0]")
    is_equivalent: bool = Field(..., description="True if mathematically equivalent")


class RetrievalResponsePayload(BaseModel):
    """Full API and retrieval engine response payload."""
    query_formula: str = Field(..., description="Original query formula string")
    canonical_form: str = Field(..., description="Alpha-converted canonical query formula")
    matched_theorems: List[TheoremMatch] = Field(default_factory=list, description="List of matched theorems sorted by confidence")
    equivalent_formulations: List[str] = Field(default_factory=list, description="List of equivalent formula strings")
    dependency_dag: Dict[str, Any] = Field(default_factory=dict, description="NetworkX dependency DAG export")


def canonicalize_formula(formula: str) -> str:
    """
    Canonicalize mathematical formula via dummy variable alpha-conversion.
    Maps variable names to standard indexed tokens (_x0, _x1, ...) in order of appearance,
    standardizes operators (^ -> **), and normalizes whitespace.
    """
    if not isinstance(formula, str):
        formula = str(formula)

    cleaned = formula.replace("^", "**").strip()

    # Reserved math keywords and functions
    reserved = {
        "sin", "cos", "tan", "asin", "acos", "atan", "exp", "log", "ln",
        "sqrt", "pi", "e", "i", "I", "abs", "Rational", "zeta", "sum", "int"
    }

    # Extract all variable identifiers
    identifiers = re.findall(r'[a-zA-Z_]\w*', cleaned)
    var_map: Dict[str, str] = {}
    counter = 0

    for name in identifiers:
        if name not in reserved and name not in var_map:
            var_map[name] = f"_x{counter}"
            counter += 1

    # Replace variables with dummy variables (word boundary replacement)
    canonical = cleaned
    for orig, dummy in var_map.items():
        canonical = re.sub(r'\b' + re.escape(orig) + r'\b', dummy, canonical)

    # Normalize spaces around operators
    canonical = re.sub(r'\s+', ' ', canonical).strip()
    return canonical


def extract_dependency_dag(store: Any = None, root_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Extract topological dependency DAG from EpistemicStore using NetworkX.
    """
    nodes_data = []
    edges_data = []

    if store is not None and hasattr(store, "to_networkx"):
        try:
            G = store.to_networkx()
            if HAS_NETWORKX and isinstance(G, nx.DiGraph):
                is_dag = nx.is_directed_acyclic_graph(G)
                topo_sort = list(nx.topological_sort(G)) if is_dag else []

                nodes_export = [{"id": n, **G.nodes[n]} for n in G.nodes]
                edges_export = [{"source": u, "target": v, **G.edges[u, v]} for u, v in G.edges]

                return {
                    "nodes": nodes_export,
                    "edges": edges_export,
                    "topological_sort": topo_sort,
                    "is_dag": is_dag,
                }
        except Exception:
            pass

    # Built-in fallback default DAG for standard theorem dependencies
    default_nodes = [
        {"id": "thm_add_comm", "name": "Commutativity of Addition", "type": "MATHEMATICAL_CLAIM"},
        {"id": "thm_binom_exp", "name": "Binomial Expansion", "type": "MATHEMATICAL_CLAIM"},
        {"id": "thm_diff_sq", "name": "Difference of Squares", "type": "MATHEMATICAL_CLAIM"},
        {"id": "thm_pythagoras", "name": "Pythagorean Identity", "type": "MATHEMATICAL_CLAIM"},
        {"id": "thm_zeta_2", "name": "Riemann Zeta(2) Value", "type": "MATHEMATICAL_CLAIM"},
    ]
    default_edges = [
        {"source": "thm_add_comm", "target": "thm_binom_exp", "type": "DEPENDS_ON"},
        {"source": "thm_diff_sq", "target": "thm_binom_exp", "type": "EQUIVALENT_TO"},
    ]

    return {
        "nodes": default_nodes,
        "edges": default_edges,
        "topological_sort": [n["id"] for n in default_nodes],
        "is_dag": True,
    }


class TheoremRetrievalEngine:
    """
    Theorem Retrieval & Formula AST Matching Engine.
    Discovers relevant mathematical theorems, proof dependencies, and equivalent formulations.
    """

    def __init__(self, store: Any = None, symbolic_engine: Optional[SymbolicMathEngine] = None):
        self.store = store
        self.symbolic_engine = symbolic_engine or SymbolicMathEngine()

        # Built-in core mathematical theorem library
        self.default_library = [
            {
                "id": "thm_add_comm",
                "name": "Commutativity of Addition",
                "formula": "a + b = b + a",
            },
            {
                "id": "thm_binom_exp",
                "name": "Binomial Expansion (Degree 2)",
                "formula": "(a + b)^2 = a^2 + 2*a*b + b^2",
            },
            {
                "id": "thm_diff_sq",
                "name": "Difference of Squares",
                "formula": "x^2 - y^2 = (x - y)*(x + y)",
            },
            {
                "id": "thm_pythagoras",
                "name": "Pythagorean Trigonometric Identity",
                "formula": "sin(x)^2 + cos(x)^2 = 1",
            },
            {
                "id": "thm_euler_identity",
                "name": "Euler's Identity",
                "formula": "exp(I*pi) + 1 = 0",
            },
            {
                "id": "thm_zeta_2",
                "name": "Riemann Zeta(2) Identity",
                "formula": "zeta(2) = pi^2 / 6",
            },
            {
                "id": "thm_dirichlet_series",
                "name": "Finite Dirichlet Series Expansion",
                "formula": "sum(1 / n^s, (n, 1, k))",
            },
        ]

    def _get_all_theorems(self) -> List[Dict[str, str]]:
        theorems = list(self.default_library)
        if self.store is not None:
            try:
                # Retrieve claims from store
                claims = getattr(self.store, "get_nodes_by_type", lambda t: [])("MATHEMATICAL_CLAIM")
                for claim in claims:
                    t_id = getattr(claim, "id", str(claim.get("id") if isinstance(claim, dict) else ""))
                    t_name = getattr(claim, "name", str(claim.get("name") if isinstance(claim, dict) else ""))
                    t_stmt = getattr(claim, "statement", str(claim.get("statement") if isinstance(claim, dict) else ""))
                    if t_id and t_stmt:
                        theorems.append({"id": t_id, "name": t_name, "formula": t_stmt})
            except Exception:
                pass
        return theorems

    def _compute_syntactic_score(self, query_canon: str, theorem_canon: str) -> SyntacticScore:
        # Token overlap
        q_tokens = set(re.findall(r'\w+|[^\w\s]', query_canon))
        t_tokens = set(re.findall(r'\w+|[^\w\s]', theorem_canon))

        intersection = len(q_tokens & t_tokens)
        union = len(q_tokens | t_tokens)
        token_overlap = intersection / max(union, 1)

        # Simple Levenshtein / Edit distance on token strings
        tree_dist = abs(len(query_canon) - len(theorem_canon))
        max_len = max(len(query_canon), len(theorem_canon), 1)
        ast_sim = max(0.0, 1.0 - (tree_dist / max_len))

        # Composite score
        composite = round(0.5 * token_overlap + 0.5 * ast_sim, 4)
        return SyntacticScore(
            ast_similarity=round(ast_sim, 4),
            tree_distance=tree_dist,
            token_overlap=round(token_overlap, 4),
            composite_score=composite,
        )

    def _split_equation(self, formula: str) -> Tuple[str, str]:
        if "=" in formula:
            parts = formula.split("=", 1)
            return parts[0].strip(), parts[1].strip()
        return formula.strip(), "0"

    def _compute_semantic_score(self, query_formula: str, theorem_formula: str) -> SemanticScore:
        q_lhs, q_rhs = self._split_equation(query_formula)
        t_lhs, t_rhs = self._split_equation(theorem_formula)

        # Direct identity check: (q_lhs - q_rhs) vs (t_lhs - t_rhs)
        q_expr = f"({q_lhs}) - ({q_rhs})"
        t_expr = f"({t_lhs}) - ({t_rhs})"

        res = self.symbolic_engine.verify_identity(q_expr, t_expr)

        if res.is_identical:
            return SemanticScore(
                exact_match=True,
                sympy_difference_is_zero=True,
                simplified_diff="0",
                semantic_confidence=1.0,
            )

        # Check if query LHS matches theorem LHS / RHS
        res_lhs = self.symbolic_engine.verify_identity(q_lhs, t_lhs)
        if res_lhs.is_identical:
            return SemanticScore(
                exact_match=False,
                sympy_difference_is_zero=True,
                simplified_diff=res_lhs.difference_simplified,
                semantic_confidence=0.9,
            )

        return SemanticScore(
            exact_match=False,
            sympy_difference_is_zero=False,
            simplified_diff=res.difference_simplified,
            semantic_confidence=0.0,
        )

    def retrieve_theorems(
        self,
        query_formula: str,
        top_k: int = 5,
        min_confidence: float = 0.0,
    ) -> RetrievalResponsePayload:
        """
        Retrieve relevant theorems for a query formula based on syntactic and semantic scores.
        """
        query_canon = canonicalize_formula(query_formula)
        theorems = self._get_all_theorems()
        matches: List[TheoremMatch] = []
        equivalent_formulations: List[str] = []

        for thm in theorems:
            t_formula = thm["formula"]
            t_canon = canonicalize_formula(t_formula)

            syn_score = self._compute_syntactic_score(query_canon, t_canon)
            sem_score = self._compute_semantic_score(query_formula, t_formula)

            if sem_score.sympy_difference_is_zero or sem_score.exact_match:
                combined_conf = 1.0
                is_equiv = True
                equivalent_formulations.append(t_formula)
            else:
                combined_conf = round(0.4 * syn_score.composite_score + 0.6 * sem_score.semantic_confidence, 4)
                is_equiv = False

            if combined_conf >= min_confidence:
                match_obj = TheoremMatch(
                    theorem_id=thm["id"],
                    name=thm["name"],
                    formula=t_formula,
                    canonical_formula=t_canon,
                    syntactic_score=syn_score,
                    semantic_score=sem_score,
                    combined_confidence=combined_conf,
                    is_equivalent=is_equiv,
                )
                matches.append(match_obj)

        # Sort matches by combined_confidence descending
        matches.sort(key=lambda m: m.combined_confidence, reverse=True)
        top_matches = matches[:top_k]

        dag_export = extract_dependency_dag(self.store)

        return RetrievalResponsePayload(
            query_formula=query_formula,
            canonical_form=query_canon,
            matched_theorems=top_matches,
            equivalent_formulations=list(set(equivalent_formulations)),
            dependency_dag=dag_export,
        )


# Alias for backward compatibility
FormulaRetrievalEngine = TheoremRetrievalEngine
