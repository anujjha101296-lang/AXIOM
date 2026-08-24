"""
axiom.challenge_harness.curator
===============================
Problem Curator Module.
Loads versioned golden benchmark problems (AXIOM-MATH-001) across Level 0 to Level 5.
"""
from __future__ import annotations

from typing import List

from axiom.challenge_harness.models import Challenge, ChallengeLevel


class ProblemCurator:
    """Manages versioned golden benchmark challenges."""

    def get_golden_challenges(self) -> List[Challenge]:
        """Return versioned golden benchmark problem suite (AXIOM-MATH-001)."""
        challenges = []

        # Level 0: Basic Mathematics
        challenges.append(
            Challenge(
                id="chal-lvl0-01",
                version="AXIOM-MATH-001",
                title="Level 0: Modular Addition Property",
                domain="Number Theory",
                difficulty_level=ChallengeLevel.LEVEL_0_BASIC,
                statement="For all natural numbers n, (n + 0) % 2 = n % 2.",
                allowed_resources=["Standard Arithmetic"],
            )
        )

        # Level 1: Elementary Proofs
        challenges.append(
            Challenge(
                id="chal-lvl1-01",
                version="AXIOM-MATH-001",
                title="Level 1: Sum of First N Positive Integers",
                domain="Induction",
                difficulty_level=ChallengeLevel.LEVEL_1_ELEMENTARY_PROOFS,
                statement="Prove by induction that sum(1..n) = n*(n+1)/2 for all n >= 1.",
                allowed_resources=["Mathematical Induction"],
            )
        )

        # Level 2: Intermediate Mathematics
        challenges.append(
            Challenge(
                id="chal-lvl2-01",
                version="AXIOM-MATH-001",
                title="Level 2: Prime Number Counterexample Search",
                domain="Number Theory",
                difficulty_level=ChallengeLevel.LEVEL_2_INTERMEDIATE,
                statement="Evaluate conjecture: All prime numbers are odd.",
                allowed_resources=["Counterexample Search"],
            )
        )

        # Level 3: Advanced Mathematics
        challenges.append(
            Challenge(
                id="chal-lvl3-01",
                version="AXIOM-MATH-001",
                title="Level 3: Matrix Trace Additivity",
                domain="Linear Algebra",
                difficulty_level=ChallengeLevel.LEVEL_3_ADVANCED,
                statement="Prove trace(A + B) = trace(A) + trace(B) for square matrices.",
                allowed_resources=["Linear Algebra"],
            )
        )

        return challenges
