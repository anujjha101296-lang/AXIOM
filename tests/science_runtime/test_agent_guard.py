import pytest

from axiom.science_runtime.agent_guard import validate_plan
from axiom.science_runtime.agent_protocol import ScientificPlan


def plan(**parameters):
    return ScientificPlan(
        hypothesis="bounded hypothesis",
        rationale="bounded rationale",
        experiment_name="lorenz-test",
        parameters=parameters,
        expected_observation="finite numerical observation",
    )


def test_valid_plan_is_accepted():
    result = validate_plan(
        plan(rho=28.0, sigma=10.0, beta=8.0 / 3.0, dt=0.01, horizon=2.0)
    )
    assert result.parameters["rho"] == 28.0


@pytest.mark.parametrize(
    "parameters",
    [
        dict(rho=21.0, sigma=10.0, beta=8.0 / 3.0, dt=0.01, horizon=2.0),
        dict(rho=28.0, sigma=11.0, beta=8.0 / 3.0, dt=0.01, horizon=2.0),
        dict(rho=28.0, sigma=10.0, beta=3.0, dt=0.01, horizon=2.0),
        dict(rho=28.0, sigma=10.0, beta=8.0 / 3.0, dt=0.1, horizon=2.0),
        dict(rho=28.0, sigma=10.0, beta=8.0 / 3.0, dt=0.01, horizon=20.0),
    ],
)
def test_invalid_plan_fails_closed(parameters):
    with pytest.raises(ValueError):
        validate_plan(plan(**parameters))
