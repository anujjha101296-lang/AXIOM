from axiom.science_runtime.research_loop import ResearchQuestion, run_research


def test_research_loop_emits_ordered_lifecycle_transitions():
    captured = []

    run = run_research(
        ResearchQuestion("Investigate Lorenz sensitivity", max_experiments=1),
        event_sink=lambda current, transition: captured.append((current.stage.value, transition.action)),
    )

    assert run.stage.value in {"COMPLETED", "FAILED"}
    assert captured[0][1] == "run_created"
    assert captured[1][1] == "hypothesis_proposed"
    assert captured[-1][1] in {"run_completed", "run_failed"}
    assert len(captured) == len(run.transitions)
    assert [action for _, action in captured] == [transition.action for transition in run.transitions]
