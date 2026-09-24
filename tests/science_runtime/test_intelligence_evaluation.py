from axiom.science_runtime.intelligence_benchmark import BenchmarkLevel, build_v0_1_tasks, dataset_sha256
from axiom.science_runtime.intelligence_evaluation import (
    ArmStatus,
    evaluate_text,
    run_responder_arm,
    run_v0_2_benchmark,
)


def test_executable_benchmark_has_40_tasks():
    tasks = build_v0_1_tasks()
    assert len(tasks) == 40
    assert {level: sum(task.level is level for task in tasks) for level in BenchmarkLevel} == {
        level: 5 for level in BenchmarkLevel
    }
    assert len({task.task_id for task in tasks}) == 40


def test_immutable_dataset_hash_is_pinned():
    assert dataset_sha256() == "b5299290fc320c36fb2006efcf6c9cdac8a92b14577223731133b058f1c47686"


def test_text_evaluator_rejects_proof_claims():
    task = build_v0_1_tasks()[0]
    score = evaluate_text(task, "This numerical result is a formal proof.")
    assert score.false_proof is True
    assert score.outcome.value == "UNSUPPORTED_CLAIM"


def test_responder_arm_is_machine_checkable():
    tasks = build_v0_1_tasks()[:3]
    result = run_responder_arm(
        "tool_assisted",
        lambda task: "numerical observation, not a proof; rho and dt are recorded",
        tasks=tasks,
    )
    assert result.status is ArmStatus.COMPLETED
    assert len(result.scores) == 3
    assert 0.0 <= result.mean_correctness <= 1.0


def test_missing_llm_provider_is_not_faked_as_a_score():
    result = run_v0_2_benchmark(tasks=build_v0_1_tasks()[:2])
    llm = result["arms"][0]
    assert llm["status"] == "NOT_RUN"
    assert llm["task_count"] == 0
    assert all(item["classification"] == "INCONCLUSIVE" for item in result["delta_report"])


def test_axiom_arm_executes_bounded_runtime():
    result = run_v0_2_benchmark(tasks=build_v0_1_tasks()[:1])
    axiom = next(item for item in result["arms"] if item["arm"] == "axiom")
    assert axiom["status"] == "COMPLETED"
    assert axiom["task_count"] == 1
    assert axiom["scores"][0]["false_proof"] is False


def test_benchmark_report_contains_dataset_provenance():
    result = run_v0_2_benchmark(tasks=None)
    dataset = result["dataset"]
    assert dataset["immutable"] is True
    assert dataset["task_count"] == 40
    assert dataset["sha256"] == "b5299290fc320c36fb2006efcf6c9cdac8a92b14577223731133b058f1c47686"
