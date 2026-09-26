"""Contract tests for the bounded scientific research API."""

from axiom.services.api_gateway.routes.science import router


def test_science_router_exposes_research_contract() -> None:
    paths = {route.path for route in router.routes}

    assert "/api/v1/science/research" in paths
    assert "/api/v1/science/research/async" in paths
    assert "/api/v1/science/research/{run_id}" in paths
    assert "/api/v1/science/research/{run_id}/events" in paths
    assert "/api/v1/science/research/{run_id}/events/stream" in paths
    assert "/api/v1/science/research/{run_id}/replay" in paths
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

    question = science.ResearchRequest(
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


def test_queued_run_records_persistence_provenance(monkeypatch, tmp_path) -> None:
    from axiom.services.api_gateway.routes import science
    from axiom.science_runtime.persistence import ResearchRunStore

    store = ResearchRunStore(tmp_path)
    monkeypatch.setattr(science, "_store", store)
    question = science.ResearchQuestion("Test whether nearby Lorenz trajectories separate.")

    science._initialize_queued_run(question, "research-provenance-test")
    snapshot = science._read_snapshot("research-provenance-test")

    assert snapshot["metadata"]["persistence"]["backend"] == "local_test"
    assert snapshot["metadata"]["persistence"]["event_schema"] == "axiom.research.event.v1"
    assert snapshot["metadata"]["persistence"]["durable"] is False


def test_replay_endpoint_is_fail_closed_on_tampered_snapshot(monkeypatch, tmp_path) -> None:
    from axiom.services.api_gateway.routes import science
    from axiom.science_runtime.persistence import ResearchRunStore
    import pytest

    store = ResearchRunStore(tmp_path)
    monkeypatch.setattr(science, "_store", store)
    run = science.ResearchRun(
        run_id="replay-api-test",
        question=science.ResearchQuestion("Test whether nearby Lorenz trajectories separate."),
    )
    science._persist_transition(run, science.Transition("PLANNED", "run_created", "created"))
    path = store.root / "replay-api-test.snapshot.json"
    data = __import__("json").loads(path.read_text())
    data["stage"] = "COMPLETED"
    path.write_text(__import__("json").dumps(data))

    events = science._read_events("replay-api-test")
    replay = science.replay_research_events(events)
    with pytest.raises(ValueError):
        science.verify_snapshot_against_replay(data, replay)


def test_async_research_supports_standard_idempotency_key_header():
    route = next(
        route
        for route in router.routes
        if route.path == "/api/v1/science/research/async" and "POST" in route.methods
    )
    header_names = {parameter.alias for parameter in route.dependant.header_params}
    assert "Idempotency-Key" in header_names


def test_research_run_can_resume_from_executed_checkpoint():
    from axiom.science_runtime.research_loop import (
        ExperimentPlan,
        Hypothesis,
        ResearchRun,
        ResearchStage,
        run_research,
    )
    from axiom.science_runtime.report import build_lorenz_evidence_bundle

    question = science.ResearchQuestion(
        question="Test resuming a bounded Lorenz investigation.",
        max_experiments=1,
        allowed_rho=[28.0],
    )
    bundle = build_lorenz_evidence_bundle(28.0)
    run = ResearchRun(
        run_id="resume-contract",
        question=question,
        hypothesis=Hypothesis("A bounded numerical observation is testable.", "checkpoint"),
        plans=[ExperimentPlan(rho=28.0)],
        evidence=[bundle],
        stage=ResearchStage.EXECUTED,
    )

    resumed = run_research(question, initial_run=run)

    assert resumed.run_id == "resume-contract"
    assert resumed.stage in {ResearchStage.COMPLETED, ResearchStage.FAILED}
    assert len(resumed.evidence) == 1
    assert len(resumed.critiques) == 1
