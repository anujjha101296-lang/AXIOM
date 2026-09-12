import json

from axiom.science_runtime.persistence import ResearchRunStore
from axiom.science_runtime.research_loop import ResearchQuestion, ResearchRun, Transition


def test_research_run_store_appends_event_and_snapshot(tmp_path):
    run = ResearchRun(run_id="research-test", question=ResearchQuestion("Investigate Lorenz sensitivity", max_experiments=2))
    store = ResearchRunStore(tmp_path)

    event_path = store.append(run, "RUN_CREATED", {"source": "test"})
    snapshot_path = store.snapshot(run)

    assert event_path.exists()
    assert snapshot_path.exists()
    assert '"event_type": "RUN_CREATED"' in event_path.read_text()
    assert run.run_id in snapshot_path.read_text()


def test_research_run_store_sequences_events_and_replays_after_cursor(tmp_path):
    run = ResearchRun(run_id="research-order", question=ResearchQuestion("Investigate Lorenz sensitivity"))
    store = ResearchRunStore(tmp_path)
    run.stage = "HYPOTHESIS"  # type: ignore[assignment]

    first = store.append(run, "RUN_CREATED")
    second = store.append(run, "HYPOTHESIS_PROPOSED")
    events = [json.loads(line) for line in first.read_text().splitlines() if line.strip()]

    assert [event["sequence"] for event in events] == [1, 2]
    assert [event["event_id"] for event in events] == ["research-order:1", "research-order:2"]
    assert [event["sequence"] for event in store.read_events(run.run_id, after_sequence=1)] == [2]
    assert second == first


def test_record_transition_persists_structured_lifecycle_event(tmp_path):
    run = ResearchRun(run_id="research-transition", question=ResearchQuestion("Investigate Lorenz sensitivity"))
    store = ResearchRunStore(tmp_path)
    transition = Transition("EXECUTED", "experiment_executed", "experiment-123")

    path = store.record_transition(run, transition)
    event = json.loads(path.read_text().strip())

    assert event["event_type"] == "EXPERIMENT_EXECUTED"
    assert event["payload"]["detail"] == "experiment-123"
    assert event["payload"]["transition_stage"] == "EXECUTED"
