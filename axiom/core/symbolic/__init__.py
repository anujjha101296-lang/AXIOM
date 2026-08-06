"""
AXIOM Symbolic Mathematics Package
Exact symbolic computations using SymPy and exact rational arithmetic.
"""
from axiom.core.symbolic.sympy_engine import (
    SymbolicMathEngine,
    IdentityVerificationResult,
    CounterexampleResult,
    ZetaEvaluationResult,
    DirichletSeriesResult,
)

__all__ = [
    "SymbolicMathEngine",
    "IdentityVerificationResult",
    "CounterexampleResult",
    "ZetaEvaluationResult",
    "DirichletSeriesResult",
]
