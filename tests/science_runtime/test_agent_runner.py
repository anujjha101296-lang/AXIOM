from axiom.science_runtime.agent_protocol import ScientificPlan
from axiom.science_runtime.agent_runner import as_research_planner
from axiom.science_runtime.research_loop import ResearchQuestion


class FakePlanner:
    def plan(self, question: str) -> ScientificPlan:
        return ScientificPlan(
            hypothesis="test hypothesis",
            rationale="test rationale",
            experiment_name="lorenz-test",
            parameters={
                "rho": 28.0,
                "sigma": 10.0,
                "beta": 8.0 / 3.0,
                "dt": 0.01,
                "horizon": 2.0,
            },
            expected_observation="finite numerical observation",
        )


def test_agent_plan_maps_into_research_contract():
    planner = as_research_planner(FakePlanner())
    hypothesis, experiment = planner(ResearchQuestion("investigate sensitivity"))
    assert hypothesis.statement == "test hypothesis"
    assert experiment.rho == 28.0
    assert experiment.horizon == 2.0
