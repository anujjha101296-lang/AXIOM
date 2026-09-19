from axiom.science_runtime.intelligence_benchmark import (
    BenchmarkLevel,
    Outcome,
    build_v0_1_tasks,
    score_contract,
)


def test_benchmark_v0_1_has_five_tasks_per_level():
    tasks = build_v0_1_tasks()
    assert len(tasks) == 40
    assert {task.level for task in tasks} == set(BenchmarkLevel)
    for level in BenchmarkLevel:
        assert sum(task.level == level for task in tasks) == 5


def test_benchmark_scores_false_proof_as_unsupported_claim():
    task = build_v0_1_tasks()[0]
    score = score_contract(
        task,
        correctness=1.0,
        evidence_correctness=1.0,
        false_proof=True,
        reproducible=True,
    )
    assert score.outcome == Outcome.UNSUPPORTED_CLAIM
    assert score.false_proof is True


def test_benchmark_score_contract_is_bounded():
    task = build_v0_1_tasks()[0]
    score = score_contract(
        task,
        correctness=4.0,
        evidence_correctness=-2.0,
        false_proof=False,
        reproducible=False,
    )
    assert score.correctness == 1.0
    assert score.evidence_correctness == 0.0
    assert score.outcome == Outcome.INVALID_EXPERIMENT
