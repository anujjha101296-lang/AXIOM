"""
axiom.experiment.reproducibility
================================
Reproducibility Engine.
Executes experiment runs twice and compares input/spec hashes and result outputs.
"""
from __future__ import annotations

from typing import Tuple

from axiom.experiment.executor import ExperimentExecutor
from axiom.experiment.models import (
    Experiment,
    ExperimentRun,
    ReproducibilityStatus,
)


class ReproducibilityEngine:
    """Evaluates reproducibility across multiple experiment runs."""

    def __init__(self):
        self.executor = ExperimentExecutor()

    def test_reproducibility(
        self,
        experiment: Experiment,
        seed: int = 42,
    ) -> Tuple[ReproducibilityStatus, ExperimentRun, ExperimentRun]:
        """Run experiment twice and check for result identity."""
        run1 = self.executor.run_experiment(experiment, run_number=1, seed=seed)
        run2 = self.executor.run_experiment(experiment, run_number=2, seed=seed)

        if run1.status != run2.status:
            return ReproducibilityStatus.FAILED_REPRODUCTION, run1, run2

        if run1.result_data == run2.result_data and run1.input_hash == run2.input_hash:
            return ReproducibilityStatus.REPRODUCIBLE, run1, run2

        return ReproducibilityStatus.NONDETERMINISTIC, run1, run2
