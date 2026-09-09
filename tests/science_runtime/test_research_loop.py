from axiom.science_runtime.research_loop import ResearchQuestion, ResearchStage, run_research


def test_bounded_research_loop_reaches_completion():
    run = run_research(ResearchQuestion(
        text="Investigate whether Lorenz trajectories show robust sensitivity near the classical regime.",
        max_experiments=1,
        allowed_rho=(28.0,),
    ))
    assert run.stage is ResearchStage.COMPLETED
    assert len(run.evidence) == 1
    assert len(run.critiques) == 1
    assert run.critiques[0].verdict == "ACCEPT_NUMERICAL_EVIDENCE"
    assert any(item.action == "verify" for item in run.transitions)
    assert "formal proof" in (run.conclusion or "")


def test_research_loop_is_bounded_and_closed_over_parameters():
    run = run_research(ResearchQuestion(
        text="Run only inside the declared Lorenz parameter set.",
        max_experiments=1,
        allowed_rho=(28.0,),
    ))
    assert all(plan.rho in run.question.allowed_rho for plan in run.plans)


def test_research_loop_records_reproducibility_metadata():
    run = run_research(ResearchQuestion(
        text="Produce an auditable numerical research record.",
        max_experiments=1,
        allowed_rho=(28.0,),
    ))
    bundle = run.evidence[0]
    assert bundle.provenance["integrator"] == "fixed-step classical RK4"
    assert bundle.content_sha256
    assert run.to_dict()["run_id"] == run.run_id
