from __future__ import annotations

import pytest

from axiom.science_runtime.agent_protocol import ScientificPlan
from axiom.science_runtime.planner_bridge import scientific_plan_to_research_planner
from axiom.science_runtime.research_loop import ResearchQuestion, run_research


def _plan(**parameters: float) -> ScientificPlan:
    values = {"rho": 28.0, "sigma": 10.0, "beta": 8.0 / 3.0, "dt": 0.01, "horizon": 1.0}
    values.update(parameters)
    return ScientificPlan(
        hypothesis="Nearby trajectories separate measurably.",
        rationale="Run bounded numerical sensitivity evidence.",
        experiment_name="lorenz-paired-sensitivity",
        parameters=values,
        expected_observation="Finite trajectories with measurable separation.",
    )


def test_ai_plan_enters_deterministic_research_loop():
    plan = _plan()
    planner = scientific_plan_to_research_planner(plan)
    run = run_research(
        ResearchQuestion(text="Investigate Lorenz sensitivity", allowed_rho=(28.0,)),
        planner=planner,
        run_id="planner-bridge-test",
    )

    assert run.hypothesis is not None
    assert run.hypothesis.statement == plan.hypothesis
    assert run.plans[0].rho == 28.0
    assert run.plans[0].horizon == 1.0
    assert run.plans[0].dts == (0.02, 0.01, 0.005)
    assert run.evidence
    assert run.critiques
    assert run.stage.value in {"COMPLETED", "FAILED"}


def test_ai_plan_cannot_escape_question_rho_allowlist():
    planner = scientific_plan_to_research_planner(_plan(rho=32.0))
    with pytest.raises(ValueError, match="allowlist"):
        run_research(ResearchQuestion(text="test", allowed_rho=(28.0,)), planner=planner)


def test_ai_plan_rejects_parameters_not_faithfully_executed():
    with pytest.raises(ValueError, match="sigma=10"):
        scientific_plan_to_research_planner(_plan(sigma=11.0))


def test_ai_plan_keeps_timestep_inside_execution_bounds():
    with pytest.raises(ValueError, match="safe convergence ladder"):
        scientific_plan_to_research_planner(_plan(dt=0.1))
