from axiom.science_runtime.intelligence_benchmark import build_v0_1_tasks
from axiom.science_runtime.intelligence_evaluation import (
    ArmStatus,
    evaluate_text,
    run_responder_arm,
    run_v0_2_benchmark,
)


def test_executable_benchmark_has_40_tasks():
    assert len(build_v0_1_tasks()) == 40


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
