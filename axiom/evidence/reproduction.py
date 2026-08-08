"""Reproduction engine — compare runs against prior provenance (E&R §7)."""

from __future__ import annotations

from typing import Any

from axiom.evidence.models import ReproductionStatus


def compare_provenance_runs(
    original: dict[str, Any],
    reproduction: dict[str, Any],
    *,
    score_tolerance: float = 0.01,
) -> tuple[ReproductionStatus, list[str]]:
    """Compare two provenance envelopes and classify reproduction outcome."""
    differences: list[str] = []

    if not original or not reproduction:
        return ReproductionStatus.UNABLE_TO_REPRODUCE, ["missing provenance record"]

    orig_inputs = original.get("inputs", {})
    repro_inputs = reproduction.get("inputs", {})
    if orig_inputs.get("benchmark_suite") != repro_inputs.get("benchmark_suite"):
        differences.append("benchmark_suite mismatch")

    orig_score = orig_inputs.get("composite_score")
    repro_score = repro_inputs.get("composite_score")
    if orig_score is not None and repro_score is not None:
        if abs(float(orig_score) - float(repro_score)) > score_tolerance:
            differences.append(
                f"composite_score delta {abs(float(orig_score) - float(repro_score)):.4f}"
            )

    orig_env = original.get("environment", {})
    repro_env = reproduction.get("environment", {})
    if orig_env.get("python_version") != repro_env.get("python_version"):
        differences.append("python_version mismatch")

    if not differences:
        return ReproductionStatus.REPRODUCED, differences

    if len(differences) <= 2 and repro_score is not None:
        return ReproductionStatus.PARTIALLY_REPRODUCED, differences

    return ReproductionStatus.NOT_REPRODUCED, differences
