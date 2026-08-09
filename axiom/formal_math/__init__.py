"""Formal Mathematics & Theorem-Proving Loop package."""

from axiom.formal_math.benchmarks import estimate_difficulty, list_benchmarks
from axiom.formal_math.compilation import compile_proof
from axiom.formal_math.conjecture import generate_conjecture
from axiom.formal_math.counterexample import search_counterexample
from axiom.formal_math.decomposition import decompose_goal
from axiom.formal_math.dependency_graph import build_dependency_graph
from axiom.formal_math.explanation import explain_formal_artifact
from axiom.formal_math.formalization import formalize_informal
from axiom.formal_math.library_search import search_library
from axiom.formal_math.millennium_gate import evaluate_millennium_readiness
from axiom.formal_math.proof_search import attempt_proof_search, generate_proof_strategies
from axiom.formal_math.prover_registry import get_prover, list_provers
from axiom.formal_math.repair import create_failure_record, suggest_repair_tactics
from axiom.formal_math.store import FormalMathStore, get_formal_math_store

__all__ = [
    "FormalMathStore",
    "attempt_proof_search",
    "build_dependency_graph",
    "compile_proof",
    "create_failure_record",
    "estimate_difficulty",
    "evaluate_millennium_readiness",
    "explain_formal_artifact",
    "formalize_informal",
    "generate_conjecture",
    "generate_proof_strategies",
    "get_formal_math_store",
    "get_prover",
    "list_benchmarks",
    "list_provers",
    "search_counterexample",
    "search_library",
    "suggest_repair_tactics",
    "decompose_goal",
]
