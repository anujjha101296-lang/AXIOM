"""Contract tests for the bounded scientific research API."""

from axiom.services.api_gateway.routes.science import router


def test_science_router_exposes_research_contract() -> None:
    paths = {route.path for route in router.routes}

    assert "/api/v1/science/research" in paths
    assert "/api/v1/science/research/{run_id}" in paths
    assert "/api/v1/science/research/{run_id}/events" in paths
    assert "/api/v1/science/benchmark/lorenz" in paths


def test_science_router_uses_bounded_post_request() -> None:
    route = next(
        route
        for route in router.routes
        if route.path == "/api/v1/science/research" and "POST" in route.methods
    )

    assert route.response_model is not None
    assert route.dependant.dependencies
