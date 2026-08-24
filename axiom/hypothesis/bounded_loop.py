"""
axiom.hypothesis.bounded_loop
=============================
Bounded Scientific Reasoning Loop.
Executes scientific workflow loop with strict step limits and budget controls.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from axiom.hypothesis.critic import ScientificCritic
from axiom.hypothesis.falsification import FalsificationEngine
from axiom.hypothesis.generator import HypothesisGenerator
from axiom.hypothesis.models import Hypothesis, HypothesisStatus, VerificationPlan
from axiom.hypothesis.planner import VerificationPlanner
from axiom.hypothesis.prediction import PredictionGenerator
from axiom.hypothesis.ranking import HypothesisRanker


class BoundedScientificLoop:
    """Bounded loop orchestrator for scientific hypothesis management."""

    def __init__(self, max_iterations: int = 5):
        self.max_iterations = max_iterations
        self.generator = HypothesisGenerator()
        self.critic = ScientificCritic()
        self.predictor = PredictionGenerator()
        self.falsifier = FalsificationEngine()
        self.ranker = HypothesisRanker()
        self.planner = VerificationPlanner()

    def run_scientific_loop(
        self,
        project_id: str,
        question: str,
        gaps: List[Dict[str, Any]] = None,
        evidence_pool: List[Dict[str, str]] = None,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute bounded scientific reasoning workflow."""
        gaps = gaps or []
        evidence_pool = evidence_pool or []

        # Step 1: Candidate Generation
        hypotheses = self.generator.generate_hypotheses(
            project_id=project_id,
            question=question,
            gaps=gaps,
            session_id=session_id,
        )

        processed = []
        plans = []

        # Bound iterations to max_iterations
        for idx, h in enumerate(hypotheses[: self.max_iterations]):
            # Step 2: Critique
            critique = self.critic.critique_hypothesis(h)
            h.critiques.append(critique)

            # Step 3: Prediction Generation
            preds = self.predictor.generate_predictions(h)
            h.predictions.extend(preds)

            # Step 4: Falsification Search
            h, counter_ev = self.falsifier.search_counterevidence(h, evidence_pool)
            h.evidences.extend(counter_ev)

            # Step 5: Verification Planning if not falsified
            if h.status not in (HypothesisStatus.FALSIFIED, HypothesisStatus.CONTRADICTED):
                plan = self.planner.create_verification_plan(h, question)
                h.verification_plan = plan
                plans.append(plan)

            processed.append(h)

        # Step 6: Ranking
        ranked = self.ranker.rank_hypotheses(processed)

        return {
            "project_id": project_id,
            "question": question,
            "iterations_executed": len(ranked),
            "hypotheses": ranked,
            "plans": plans,
        }
