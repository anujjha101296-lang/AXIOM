from axiom.science_runtime.persistence import ResearchRunStore
from axiom.science_runtime.research_loop import ResearchQuestion, ResearchRun


def test_research_run_store_appends_event_and_snapshot(tmp_path):
    run = ResearchRun(run_id="research-test", question=ResearchQuestion("Investigate Lorenz sensitivity", max_experiments=2))
    store = ResearchRunStore(tmp_path)

    event_path = store.append(run, "RUN_CREATED", {"source": "test"})
    snapshot_path = store.snapshot(run)

    assert event_path.exists()
    assert snapshot_path.exists()
    assert '"event_type": "RUN_CREATED"' in event_path.read_text()
    assert run.run_id in snapshot_path.read_text()
