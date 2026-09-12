"""Contract tests for the bounded scientific research API."""

from axiom.services.api_gateway.routes.science import router


def test_science_router_exposes_research_contract() -> None:
    paths = {route.path for route in router.routes}

    assert "/api/v1/science/research" in paths
    assert "/api/v1/science/research/async" in paths
    assert "/api/v1/science/research/{run_id}" in paths
    assert "/api/v1/science/research/{run_id}/events" in paths
    assert "/api/v1/science/research/{run_id}/events/stream" in paths
    assert "/api/v1/science/benchmark/lorenz" in paths


def test_science_router_uses_bounded_post_request() -> None:
    route = next(
        route
        for route in router.routes
        if route.path == "/api/v1/science/research" and "POST" in route.methods
    )

    assert route.response_model is not None
    assert route.dependant.dependencies


def test_async_research_endpoint_returns_accepted_job_contract() -> None:
    route = next(
        route
        for route in router.routes
        if route.path == "/api/v1/science/research/async" and "POST" in route.methods
    )

    assert route.status_code == 202
    assert route.response_model is not None
    assert route.dependant.dependencies


def test_event_stream_is_server_sent_events() -> None:
    route = next(route for route in router.routes if route.path.endswith("/events/stream"))
    assert route.response_class is not None
