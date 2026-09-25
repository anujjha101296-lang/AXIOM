import pytest
from sqlalchemy import create_engine, select

from axiom.science_runtime.postgres_persistence import (
    PostgresResearchRunStore,
    ResearchEventRow,
    ResearchRunRow,
    _Base,
)
from axiom.science_runtime.research_loop import ResearchQuestion, ResearchRun, ResearchStage, Transition
from axiom.science_runtime.replay import replay_research_events, verify_snapshot_against_replay


@pytest.fixture
def store(tmp_path):
    db = f"sqlite:///{tmp_path / 'research.db'}"
    value = PostgresResearchRunStore(db, create_schema=True)
    yield value
    value.close()


def _run(run_id="run-test"):
    return ResearchRun(run_id=run_id, question=ResearchQuestion("Test bounded Lorenz evidence"))


def test_persists_event_and_snapshot_transactionally(store):
    run = _run()
    transition = Transition(ResearchStage.PLANNED.value, "run_created", "created")

    event = store.persist_transition(run, transition)

    assert event.sequence == 1
    assert store.read_events(run.run_id)[0]["event_id"] == "run-test:1"
    assert store.read_snapshot(run.run_id)["stage"] == ResearchStage.PLANNED.value


def test_sequences_are_monotonic_and_replayable(store):
    run = _run()
    for i in range(3):
        run.stage = ResearchStage.PLANNED
        store.persist_transition(run, Transition("PLANNED", f"step_{i}", str(i)))

    events = store.read_events(run.run_id)
    assert [event["sequence"] for event in events] == [1, 2, 3]
    assert [event["event_id"] for event in events] == ["run-test:1", "run-test:2", "run-test:3"]
    assert [event["sequence"] for event in store.read_events(run.run_id, after_sequence=1)] == [2, 3]


def test_database_contains_durable_system_of_record_tables(store):
    with store.engine.connect() as connection:
        tables = set(connection.dialect.get_table_names(connection))
    assert {"research_runs", "research_events"}.issubset(tables)


def test_event_row_is_linked_to_run(store):
    run = _run()
    store.persist_transition(run, Transition("PLANNED", "run_created", "created"))
    with store.engine.connect() as connection:
        event = connection.execute(select(ResearchEventRow)).mappings().one()
        saved = connection.execute(select(ResearchRunRow)).mappings().one()
    assert event["run_id"] == saved["run_id"] == run.run_id


def test_database_readiness_check_is_explicit(store):
    store.check_ready()


def test_event_log_replays_to_the_materialized_terminal_stage(store):
    run = _run("replay-test")
    run.stage = ResearchStage.PLANNED
    store.persist_transition(run, Transition("PLANNED", "run_created", "created"))
    run.stage = ResearchStage.COMPLETED
    store.persist_transition(run, Transition("COMPLETED", "run_completed", "done"))

    events = store.read_events(run.run_id)
    snapshot = store.read_snapshot(run.run_id)
    replay = replay_research_events(events)
    verify_snapshot_against_replay(snapshot, replay)

    assert replay.run_id == run.run_id
    assert replay.last_sequence == 2
    assert replay.stage == "COMPLETED"
    assert replay.terminal


def test_replay_rejects_sequence_gaps(store):
    run = _run("gap-test")
    store.persist_transition(run, Transition("PLANNED", "run_created", "created"))
    events = store.read_events(run.run_id)
    events[0]["sequence"] = 2

    with pytest.raises(ValueError, match="sequence gap"):
        replay_research_events(events)
