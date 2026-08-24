"""
axiom.long_horizon.critic
========================
Research Critic Engine.
Periodically audits research direction, checks assumption stability, and recommends strategic pivots.
"""
from __future__ import annotations

from typing import List, Tuple

from axiom.long_horizon.models import CriticRecommendation, ResearchAttempt, ResearchProblem, ApproachStatus


class ResearchCriticEngine:
    """Audits research progress and recommends strategic direction."""

    def audit_research_progress(
        self,
        problem: ResearchProblem,
        attempts: List[ResearchAttempt],
    ) -> Tuple[CriticRecommendation, str]:
        """
        Audit research attempts and generate recommendation.
        Returns (CriticRecommendation, rationale_string).
        """
        failed_count = sum(1 for a in attempts if a.status in (ApproachStatus.FAILED, ApproachStatus.FALSIFIED))
        completed_count = sum(1 for a in attempts if a.status == ApproachStatus.COMPLETED)

        if failed_count >= 5 and completed_count == 0:
            return (
                CriticRecommendation.PIVOT,
                f"Research Critic Audit: 5 consecutive failed attempts detected on '{problem.title}'. Recommending strategy PIVOT to alternative mathematical domains.",
            )

        if any("falsified" in (a.failure_reason or "").lower() for a in attempts):
            return (
                CriticRecommendation.REVISE,
                "Research Critic Audit: Counterexample found falsifying core premise. Recommending REVISE of problem assumptions.",
            )

        return (
            CriticRecommendation.CONTINUE,
            f"Research Critic Audit: Research progress on '{problem.title}' is consistent. Recommending CONTINUE with current subproblem tasks.",
        )
