import pytest

from axiom.science_runtime.agent_protocol import DeterministicLorenzPlanner, ScientificPlan
from axiom.science_runtime.llm_planners import validate_scientific_plan


def test_deterministic_planner_returns_bounded_plan():
    plan = DeterministicLorenzPlanner().plan("Investigate Lorenz sensitivity")
    assert isinstance(plan, ScientificPlan)
    validate_scientific_plan(plan)


@pytest.mark.parametrize(
    "parameters",
    [
        {"rho": 100.0, "dt": 0.01},
        {"rho": 28.0, "gamma": 1.0},
        {"rho": 28.0, "dt": 0.0},
        {"rho": True, "dt": 0.01},
    ],
)
def test_plan_guard_rejects_unsafe_parameters(parameters):
    plan = ScientificPlan(
        hypothesis="bounded hypothesis",
        rationale="test",
        experiment_name="contract-test",
        parameters=parameters,
        expected_observation="bounded observation",
    )
    with pytest.raises(ValueError):
        validate_scientific_plan(plan)


def test_plan_guard_rejects_empty_hypothesis():
    plan = ScientificPlan(
        hypothesis=" ",
        rationale="test",
        experiment_name="contract-test",
        parameters={"rho": 28.0},
        expected_observation="observation",
    )
    with pytest.raises(ValueError):
        validate_scientific_plan(plan)


def test_plan_guard_rejects_empty_parameters():
    plan = ScientificPlan(
        hypothesis="bounded hypothesis",
        rationale="test",
        experiment_name="contract-test",
        parameters={},
        expected_observation="observation",
    )
    with pytest.raises(ValueError):
        validate_scientific_plan(plan)
