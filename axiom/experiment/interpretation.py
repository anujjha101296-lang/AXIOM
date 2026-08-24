"""
axiom.experiment.interpretation
==============================
Scientific Interpretation Engine.
Compares expected prediction vs actual observation. Updates hypothesis status while preserving epistemic limits.
"""
from __future__ import annotations

from typing import Tuple

from axiom.experiment.models import (
    ExperimentObservation,
    ExperimentRun,
    ExperimentStatus,
    InterpretationStatus,
    ObservationLevel,
    ReproducibilityStatus,
)
from axiom.hypothesis.models import Hypothesis, HypothesisStatus


class ScientificInterpreter:
    """Interprets experiment observations and updates hypothesis epistemic status."""

    def interpret_experiment(
        self,
        experiment_id: str,
        run: ExperimentRun,
        hypothesis: Hypothesis,
        expected_prediction: str = "",
    ) -> Tuple[ExperimentObservation, Hypothesis]:
        """
        Evaluate experiment run against hypothesis prediction.
        Returns (observation, updated_hypothesis).
        """
        if run.status != ExperimentStatus.COMPLETED:
            obs = ExperimentObservation(
                experiment_id=experiment_id,
                run_id=run.id,
                observation_level=ObservationLevel.COMPUTATIONAL_OBSERVATION,
                summary=f"Experiment execution failed with status: {run.status.value}",
                metrics={"status": run.status.value},
                reproducibility_status=ReproducibilityStatus.FAILED_REPRODUCTION,
                interpretation_status=InterpretationStatus.EXPERIMENT_FAILED,
                is_mathematical_proof=False,
                limitations=["Execution failure or resource limit exceeded"],
            )
            return obs, hypothesis

        # Evaluation of successful run
        res = run.result_data or {}
        summary = f"Computational observation completed in {run.runtime_ms}ms with output: {res}"
        
        # Check identity error or contradictory metrics
        err = res.get("identity_error", 0.0)
        if err > 0.1 or res.get("failed", False):
            interp = InterpretationStatus.NOT_SUPPORTED
            hypothesis.status = HypothesisStatus.CONTRADICTED
            hypothesis.confidence_score = 0.2
            hypothesis.rationale = "Contradicted by computational experiment observation."
        else:
            interp = InterpretationStatus.SUPPORTED
            hypothesis.status = HypothesisStatus.SUPPORTED
            hypothesis.confidence_score = 0.85
            hypothesis.rationale = "Supported by verified computational experiment observation."

        obs = ExperimentObservation(
            experiment_id=experiment_id,
            run_id=run.id,
            observation_level=ObservationLevel.COMPUTATIONAL_OBSERVATION,
            summary=summary,
            metrics=res,
            reproducibility_status=ReproducibilityStatus.REPRODUCIBLE,
            interpretation_status=interp,
            is_mathematical_proof=False, # CRITICAL: Computational observation != mathematical proof
            limitations=[
                "Observation is bounded to tested domain size",
                "Finite computational simulation does NOT constitute a formal mathematical proof",
            ],
        )

        return obs, hypothesis
