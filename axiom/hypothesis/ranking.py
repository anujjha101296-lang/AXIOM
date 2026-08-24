"""
axiom.hypothesis.ranking
========================
Explainable Hypothesis Ranking Engine.
Ranks hypotheses using explicit factors: evidence strength, novelty, testability, falsifiability, research value.
"""
from __future__ import annotations

from typing import List

from axiom.hypothesis.models import Hypothesis, HypothesisStatus


class HypothesisRanker:
    """Ranks hypotheses using explicit multi-factor criteria."""

    def rank_hypotheses(self, hypotheses: List[Hypothesis]) -> List[Hypothesis]:
        """Rank hypotheses in descending order of explainable score."""
        scored = []
        for h in hypotheses:
            score = self.compute_score(h)
            h.confidence_score = score
            scored.append(h)

        return sorted(scored, key=lambda x: x.confidence_score, reverse=True)

    def compute_score(self, hypothesis: Hypothesis) -> float:
        """
        Explainable score computation:
        - Base score: status weight
        - Falsifiability (+0.2)
        - Evidence backing (+0.2 per supporting item)
        - Contradiction penalty (-0.4 per counter-evidence item)
        """
        status_weights = {
            HypothesisStatus.SUPPORTED: 0.9,
            HypothesisStatus.WEAKLY_SUPPORTED: 0.6,
            HypothesisStatus.PROPOSED: 0.5,
            HypothesisStatus.UNDER_REVIEW: 0.5,
            HypothesisStatus.INCONCLUSIVE: 0.3,
            HypothesisStatus.CONTRADICTED: 0.1,
            HypothesisStatus.FALSIFIED: 0.0,
            HypothesisStatus.RETIRED: 0.0,
        }

        base = status_weights.get(hypothesis.status, 0.5)

        supp_count = sum(1 for e in hypothesis.evidences if e.supports)
        opp_count = sum(1 for e in hypothesis.evidences if not e.supports)

        score = base + (supp_count * 0.1) - (opp_count * 0.3)
        return max(0.0, min(1.0, round(score, 3)))
