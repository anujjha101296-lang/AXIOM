"""Provider-neutral protocol for scientific planning agents.

The scientific runtime never depends on a specific LLM vendor. Providers must
return bounded structured plans; execution and evidence evaluation stay local.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ScientificPlan:
    hypothesis: str
    rationale: str
    experiment_name: str
    parameters: dict[str, float]
    expected_observation: str


class ScientificPlanner(Protocol):
    def plan(self, question: str) -> ScientificPlan:
        """Return one bounded, executable scientific plan."""


class DeterministicLorenzPlanner:
    """Reference planner used for local tests, demos, and offline operation."""

    def plan(self, question: str) -> ScientificPlan:
        return ScientificPlan(
            hypothesis="For rho=28, nearby initial conditions diverge over a bounded horizon.",
            rationale="Use a paired-trajectory sensitivity experiment before making any stronger claim.",
            experiment_name="lorenz-paired-sensitivity",
            parameters={"rho": 28.0, "sigma": 10.0, "beta": 8.0 / 3.0, "dt": 0.01, "horizon": 2.0},
            expected_observation="Nearby trajectories exhibit measurable separation while remaining numerically finite.",
        )
