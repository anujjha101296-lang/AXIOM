"""Experiment comparison (SEC §16)."""

from __future__ import annotations

from typing import Any

from axiom.experiment.models import Experiment


def compare_experiments(a: Experiment, b: Experiment) -> dict[str, Any]:
    """Compare two experiments across parameters, results, and environment."""
    diffs: list[str] = []

    for key in set(a.spec.keys()) | set(b.spec.keys()):
        if a.spec.get(key) != b.spec.get(key):
            diffs.append(f"spec.{key}")

    for key in set(a.results.keys()) | set(b.results.keys()):
        if a.results.get(key) != b.results.get(key):
            diffs.append(f"results.{key}")

    return {
        "experiment_a": a.experiment_id,
        "experiment_b": b.experiment_id,
        "differences": diffs,
        "same_status": a.status == b.status,
        "cost_delta": None,
        "runtime_delta_ms": _runtime_delta(a, b),
    }


def _runtime_delta(a: Experiment, b: Experiment) -> float | None:
    ra = a.results.get("sandbox", {}).get("duration_ms")
    rb = b.results.get("sandbox", {}).get("duration_ms")
    if ra is not None and rb is not None:
        return round(float(rb) - float(ra), 2)
    return None
