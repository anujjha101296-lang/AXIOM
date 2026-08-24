"""
axiom.hypothesis.planner
========================
Verification Planning Engine.
Formulates structured verification plans for hypothesis testing.
"""
from __future__ import annotations

from typing import List

from axiom.hypothesis.models import Hypothesis, VerificationPlan


class VerificationPlanner:
    """Formulates structured verification plans for hypotheses."""

    def create_verification_plan(
        self,
        hypothesis: Hypothesis,
        question: str = "",
    ) -> VerificationPlan:
        """Build structured verification plan."""
        q_text = question or f"Verification of claim: {hypothesis.claim[:80]}"
        preds = [p.prediction_text for p in hypothesis.predictions] if hypothesis.predictions else ["Direct quantitative measurement"]

        return VerificationPlan(
            hypothesis_id=hypothesis.id,
            project_id=hypothesis.project_id,
            question=q_text,
            hypothesis_summary=hypothesis.claim,
            required_evidence=["Literature citation", "Benchmark measurement log", "Falsification test"],
            predictions=preds,
            method="literature_research_and_benchmark",
            data_sources=["Internal document store", "External research papers"],
            success_criteria="At least 2 supporting evidence items with zero direct counter-evidence items",
            failure_criteria="At least 1 verified counter-evidence item disproving claim",
            limitations=["Bounded search scope", "Language model extraction precision limits"],
        )
