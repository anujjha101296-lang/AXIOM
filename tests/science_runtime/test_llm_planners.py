from __future__ import annotations

import pytest

from axiom.science_runtime.agent_protocol import ScientificPlan
from axiom.science_runtime.llm_planners import (
    PlannerConfigurationError,
    validate_scientific_plan,
)


def _valid_plan() -> ScientificPlan:
    return ScientificPlan(
        hypothesis="Nearby Lorenz trajectories separate over a bounded horizon.",
        rationale="Test sensitivity numerically before making a stronger claim.",
        experiment_name="lorenz-paired-sensitivity",
        parameters={"rho": 28.0, "sigma": 10.0, "beta": 8.0 / 3.0, "dt": 0.01, "horizon": 2.0},
        expected_observation="Finite trajectories with measurable separation.",
    )


def test_provider_plan_validation_accepts_bounded_plan():
    plan = validate_scientific_plan(_valid_plan())
    assert plan.experiment_name == "lorenz-paired-sensitivity"


@pytest.mark.parametrize(
    "parameters",
    [
        {"rho": 100.0},
        {"dt": 0.0},
        {"unknown": 1.0},
    ],
)
def test_provider_plan_validation_rejects_unsafe_parameters(parameters):
    plan = _valid_plan()
    object.__setattr__(plan, "parameters", parameters)
    with pytest.raises(ValueError):
        validate_scientific_plan(plan)


def test_provider_modules_are_importable_without_configuring_a_provider():
    from axiom.science_runtime.llm_planners import OllamaAgentsScientificPlanner, OpenAIAgentsScientificPlanner

    assert OpenAIAgentsScientificPlanner().model
    assert OllamaAgentsScientificPlanner().base_url.startswith("http")
    assert PlannerConfigurationError.__name__ == "PlannerConfigurationError"
