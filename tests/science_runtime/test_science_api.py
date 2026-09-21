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


def test_production_requires_durable_database(monkeypatch) -> None:
    import pytest
    from axiom.services.api_gateway.routes import science

    monkeypatch.delenv("AXIOM_DATABASE_URL", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("AXIOM_ENVIRONMENT", "production")

    with pytest.raises(RuntimeError, match="Durable scientific persistence"):
        science._build_store()

def test_queued_run_is_persisted_before_background_execution(monkeypatch, tmp_path) -> None:
    from axiom.services.api_gateway.routes import science
    from axiom.science_runtime.persistence import ResearchRunStore

    store = ResearchRunStore(tmp_path)
    monkeypatch.setattr(science, "_store", store)

    question = science.ResearchQuestion(
        question="Test whether nearby Lorenz trajectories separate.",
    )
    run_id = "research-queued-test"

    science._initialize_queued_run(
        science._question(question),
        run_id,
    )

    snapshot = science._read_snapshot(run_id)
    events = science._read_events(run_id)

    assert snapshot is not None
    assert snapshot["run_id"] == run_id
    assert snapshot["stage"] == "PLANNED"
    assert events[0]["event_type"] == "RUN_QUEUED"
    assert events[0]["payload"]["transition_stage"] == "PLANNED"
