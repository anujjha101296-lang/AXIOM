"""Experiment reproduction engine (SEC §15)."""

from __future__ import annotations

from typing import Any

from axiom.experiment.models import Experiment, ExperimentReproductionStatus


def compare_experiment_results(
    original: Experiment,
    reproduction: Experiment,
    *,
    tolerance: float = 1e-6,
) -> tuple[ExperimentReproductionStatus, list[str]]:
    """Compare two experiment runs and classify reproduction outcome."""
    differences: list[str] = []

    orig_env = original.environment
    repro_env = reproduction.environment
    if orig_env.get("python_version") != repro_env.get("python_version"):
        differences.append("python_version mismatch")

    orig_sandbox = original.results.get("sandbox", {})
    repro_sandbox = reproduction.results.get("sandbox", {})
    if orig_sandbox.get("stdout") != repro_sandbox.get("stdout"):
        differences.append("stdout mismatch")
    if orig_sandbox.get("exit_code") != repro_sandbox.get("exit_code"):
        differences.append("exit_code mismatch")

    orig_seed = original.spec.get("random_seed")
    repro_seed = reproduction.spec.get("random_seed")
    if orig_seed is not None and repro_seed is not None and orig_seed != repro_seed:
        differences.append("random_seed mismatch")

    if not differences:
        return ExperimentReproductionStatus.EXACT_REPRODUCTION, differences

    if len(differences) <= 2 and orig_sandbox.get("exit_code") == repro_sandbox.get("exit_code"):
        return ExperimentReproductionStatus.APPROXIMATE_REPRODUCTION, differences

    if orig_sandbox and repro_sandbox:
        return ExperimentReproductionStatus.PARTIAL_REPRODUCTION, differences

    return ExperimentReproductionStatus.FAILED_REPRODUCTION, differences
