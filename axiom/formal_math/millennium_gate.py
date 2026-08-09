"""Millennium readiness gate (FMTP §26)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ReadinessResult:
    ready: bool
    score: float
    requirements: dict[str, bool]
    blockers: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "ready": self.ready,
            "score": self.score,
            "requirements": self.requirements,
            "blockers": self.blockers,
        }


def evaluate_millennium_readiness(
    *,
    formal_benchmark_level: int = 0,
    proof_reproduction_rate: float = 0.0,
    counterexample_rate: float = 0.0,
    formal_verification_reliability: float = 0.0,
    human_expert_review: bool = False,
) -> ReadinessResult:
    """Evaluate readiness for major prize campaigns — do NOT skip levels."""
    requirements = {
        "formal_benchmark_level_4_plus": formal_benchmark_level >= 4,
        "proof_reproduction_50pct": proof_reproduction_rate >= 0.5,
        "counterexample_capability": counterexample_rate > 0,
        "formal_verification_reliable": formal_verification_reliability >= 0.7,
        "human_expert_review": human_expert_review,
        "literature_coverage": False,
        "failure_recovery": False,
        "long_horizon_research": True,
    }

    passed = sum(requirements.values())
    total = len(requirements)
    score = round(passed / total, 2)
    blockers = [k for k, v in requirements.items() if not v]

    return ReadinessResult(
        ready=score >= 0.75 and formal_benchmark_level >= 4,
        score=score,
        requirements=requirements,
        blockers=blockers,
    )
