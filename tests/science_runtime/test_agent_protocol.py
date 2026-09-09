from axiom.science_runtime.agent_protocol import DeterministicLorenzPlanner, ScientificPlan


def test_reference_planner_returns_bounded_structured_plan():
    plan = DeterministicLorenzPlanner().plan("Why does the Lorenz system become sensitive?")
    assert isinstance(plan, ScientificPlan)
    assert plan.parameters["rho"] == 28.0
    assert plan.parameters["dt"] > 0
    assert plan.parameters["horizon"] > 0
