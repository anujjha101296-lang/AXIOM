"""Conjecture Generator for Phase 12 Discovery Engine.

Generates candidate mathematical conjectures (sums, inequalities, recurrence relations).
"""
import uuid
from datetime import datetime, timezone
from typing import List
import sympy as sp
from axiom.discovery.models import CandidateConjecture, FormulaType


class ConjectureGenerator:
    """Generates structured candidate conjectures across algebraic domains."""

    def generate_summation_candidates(self) -> List[CandidateConjecture]:
        """Generate summation series candidates for closed-form analysis."""
        k = sp.Symbol('k', integer=True, positive=True)
        candidates = []

        patterns = [
            (k * 2**k, "k * 2^k"),
            (k**2 * 2**k, "k^2 * 2^k"),
            (k**3 * 2**k, "k^3 * 2^k"),
            (k * 3**k, "k * 3^k"),
            (k**2 + 3*k + 1, "k^2 + 3k + 1"),
        ]

        for expr, name in patterns:
            candidates.append(
                CandidateConjecture(
                    id=str(uuid.uuid4()),
                    formula_type=FormulaType.SUMMATION,
                    expression_str=str(expr),
                    variables=["k", "n"],
                    domain_constraints={"k": "1..n", "n": "positive integer"},
                    generated_at=datetime.now(timezone.utc).isoformat(),
                )
            )
        return candidates

    def generate_inequality_candidates(self) -> List[CandidateConjecture]:
        """Generate algebraic inequality candidates for SMT verification."""
        candidates = [
            CandidateConjecture(
                id=str(uuid.uuid4()),
                formula_type=FormulaType.INEQUALITY,
                expression_str="x^3 + y^3 < (x + y)^3",
                variables=["x", "y"],
                domain_constraints={"x": ">0", "y": ">0"},
                generated_at=datetime.now(timezone.utc).isoformat(),
            ),
            CandidateConjecture(
                id=str(uuid.uuid4()),
                formula_type=FormulaType.INEQUALITY,
                expression_str="2*(x^2 + y^2) >= (x + y)^2",
                variables=["x", "y"],
                domain_constraints={"x": "real", "y": "real"},
                generated_at=datetime.now(timezone.utc).isoformat(),
            ),
        ]
        return candidates
