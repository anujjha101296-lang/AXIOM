"""Executable scientific-intelligence benchmark v0.2.

The harness evaluates response contracts rather than prose quality. Three arms are
supported: an LLM-only responder, a deterministic/tool-assisted responder, and
AXIOM's bounded research runtime. An unavailable provider is recorded as NOT_RUN;
no synthetic score is substituted.
"""
from __future__ import annotations

import json
import re
import time
from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Callable

from .agent_protocol import DeterministicLorenzPlanner
from .intelligence_benchmark import (
    BenchmarkLevel,
    BenchmarkScore,
    BenchmarkTask,
    Outcome,
    build_v0_1_tasks,
    dataset_sha256,
    score_contract,
)
from .llm_planners import validate_scientific_plan
from .research_loop import ResearchQuestion, run_research


BENCHMARK_VERSION = "scientific-intelligence-v0.2"
ARMS = ("llm_only", "tool_assisted", "axiom")
Responder = Callable[[BenchmarkTask], str]


class ArmStatus(StrEnum):
    COMPLETED = "COMPLETED"
    NOT_RUN = "NOT_RUN"
    FAILED = "FAILED"


@dataclass(frozen=True)
class ArmResult:
    arm: str
    status: ArmStatus
    scores: tuple[BenchmarkScore, ...]
    runtime_seconds: float
    error: str | None = None

    @property
    def mean_correctness(self) -> float:
        return sum(item.correctness for item in self.scores) / len(self.scores) if self.scores else 0.0

    @property
    def mean_evidence_correctness(self) -> float:
        return (
            sum(item.evidence_correctness for item in self.scores) / len(self.scores)
            if self.scores else 0.0
        )

    @property
    def false_proof_rate(self) -> float:
        return sum(item.false_proof for item in self.scores) / len(self.scores) if self.scores else 0.0

    @property
    def reproducibility_rate(self) -> float:
        return sum(item.reproducible for item in self.scores) / len(self.scores) if self.scores else 0.0

    def to_dict(self) -> dict[str, object]:
        return {
            "arm": self.arm,
            "status": self.status.value,
            "runtime_seconds": self.runtime_seconds,
            "task_count": len(self.scores),
            "mean_correctness": self.mean_correctness,
            "mean_evidence_correctness": self.mean_evidence_correctness,
            "false_proof_rate": self.false_proof_rate,
            "reproducibility_rate": self.reproducibility_rate,
            "scores": [item.to_dict() for item in self.scores],
            "error": self.error,
        }


@dataclass(frozen=True)
class Delta:
    arm: str
    metric: str
    baseline_value: float | None
    comparison_value: float | None
    classification: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _classify_delta(baseline: float | None, comparison: float | None, *, higher_is_better: bool) -> str:
    if baseline is None or comparison is None:
        return "INCONCLUSIVE"
    if abs(comparison - baseline) < 1e-12:
        return "UNCHANGED"
    improved = comparison > baseline if higher_is_better else comparison < baseline
    return "IMPROVED" if improved else "REGRESSED"


def evaluate_text(task: BenchmarkTask, response: str) -> BenchmarkScore:
    """Conservative deterministic evaluator for the v0.2 contract.

    It rewards explicit coverage of the expected concept and penalizes claims of
    mathematical proof. This is intentionally a transparent baseline evaluator,
    not an LLM judge.
    """
    text = response.lower()
    concept_terms = {
        BenchmarkLevel.NUMERICAL_REASONING: ("numerical observation", "not a proof"),
        BenchmarkLevel.EQUATION_INTERPRETATION: ("sigma", "coupling"),
        BenchmarkLevel.HYPOTHESIS: ("falsifiable", "measure"),
        BenchmarkLevel.EXPERIMENT_DESIGN: ("timestep", "dt"),
        BenchmarkLevel.FALSIFICATION: ("reject", "resolution"),
        BenchmarkLevel.RESULT_INTERPRETATION: ("numerically", "not", "proof"),
        BenchmarkLevel.COMPETING_HYPOTHESES: ("alternative", "uncertain"),
        BenchmarkLevel.AUTONOMOUS_INVESTIGATION: ("hypothesis", "experiment", "evidence", "critic"),
    }[task.level]
    hits = sum(term in text for term in concept_terms)
    correctness = min(1.0, hits / len(concept_terms))
    proof_claim = re.search(r"(?<!not )(?:is|constitutes|establishes|proves) (?:a |the )?(?:formal|mathematical) proof", text)
    false_proof = proof_claim is not None
    evidence_correctness = 0.0 if false_proof else correctness
    reproducible = all(term in text for term in ("rho", "dt")) if task.level in {
        BenchmarkLevel.EXPERIMENT_DESIGN,
        BenchmarkLevel.AUTONOMOUS_INVESTIGATION,
    } else True
    return score_contract(
        task,
        correctness=correctness,
        evidence_correctness=evidence_correctness,
        false_proof=false_proof,
        reproducible=reproducible,
    )


def run_responder_arm(
    arm: str,
    responder: Responder | None,
    *,
    tasks: tuple[BenchmarkTask, ...] | None = None,
) -> ArmResult:
    if arm not in ARMS:
        raise ValueError(f"Unsupported arm: {arm}")
    if responder is None:
        return ArmResult(arm, ArmStatus.NOT_RUN, (), 0.0, "No responder configured.")
    selected = tasks or build_v0_1_tasks()
    started = time.perf_counter()
    scores: list[BenchmarkScore] = []
    try:
        for task in selected:
            scores.append(evaluate_text(task, responder(task)))
    except Exception as exc:
        return ArmResult(arm, ArmStatus.FAILED, tuple(scores), time.perf_counter() - started, str(exc))
    return ArmResult(arm, ArmStatus.COMPLETED, tuple(scores), time.perf_counter() - started)


def _tool_assisted_response(task: BenchmarkTask) -> str:
    return (
        f"For {task.task_id}, use a bounded Lorenz experiment at the stated rho. "
        "Record numerical observation, keep dt fixed or compare a timestep ladder, "
        "retain uncertainty, and do not call the result a mathematical proof."
    )


def _axiom_response(task: BenchmarkTask) -> str:
    plan = DeterministicLorenzPlanner().plan(task.prompt)
    validate_scientific_plan(plan)
    run = run_research(
        ResearchQuestion(
            text=task.prompt,
            max_experiments=1,
            allowed_rho=(28.0,),
        ),
        run_id=f"benchmark-{task.task_id}",
    )
    evidence = run.evidence[-1] if run.evidence else None
    if evidence is None:
        return "No evidence was produced; the bounded investigation failed closed."
    return (
        f"Hypothesis: {plan.hypothesis} Experiment: {plan.experiment_name}. "
        f"Evidence: {evidence.evidence_tier}, reproducible={run.stage.value == 'COMPLETED'}. "
        "The result is numerical evidence, not a formal proof."
    )


def run_v0_2_benchmark(
    *,
    llm_responder: Responder | None = None,
    tasks: tuple[BenchmarkTask, ...] | None = None,
) -> dict[str, object]:
    selected = tasks or build_v0_1_tasks()
    arms = (
        run_responder_arm("llm_only", llm_responder, tasks=selected),
        run_responder_arm("tool_assisted", _tool_assisted_response, tasks=selected),
        run_responder_arm("axiom", _axiom_response, tasks=selected),
    )
    by_name = {item.arm: item for item in arms}
    baseline = by_name["llm_only"]
    deltas: list[Delta] = []
    for arm_name in ("tool_assisted", "axiom"):
        result = by_name[arm_name]
        for metric, higher in (
            ("mean_correctness", True),
            ("mean_evidence_correctness", True),
            ("false_proof_rate", False),
            ("reproducibility_rate", True),
        ):
            deltas.append(
                Delta(
                    arm=arm_name,
                    metric=metric,
                    baseline_value=getattr(baseline, metric) if baseline.status == ArmStatus.COMPLETED else None,
                    comparison_value=getattr(result, metric) if result.status == ArmStatus.COMPLETED else None,
                    classification=_classify_delta(
                        getattr(baseline, metric) if baseline.status == ArmStatus.COMPLETED else None,
                        getattr(result, metric) if result.status == ArmStatus.COMPLETED else None,
                        higher_is_better=higher,
                    ),
                )
            )
    return {
        "benchmark": BENCHMARK_VERSION,
        "dataset": {
            "version": "scientific-intelligence-v0.1",
            "task_count": len(selected),
            "sha256": dataset_sha256() if tasks is None else None,
            "immutable": tasks is None,
        },
        "epistemic_boundary": "Scores measure benchmark behavior only; they do not establish general scientific intelligence.",
        "arms": [item.to_dict() for item in arms],
        "delta_report": [item.to_dict() for item in deltas],
    }


def render_report(result: dict[str, object]) -> str:
    return json.dumps(result, indent=2, sort_keys=True)


__all__ = [
    "ARMS",
    "ArmResult",
    "ArmStatus",
    "BENCHMARK_VERSION",
    "Delta",
    "evaluate_text",
    "render_report",
    "run_responder_arm",
    "run_v0_2_benchmark",
]
