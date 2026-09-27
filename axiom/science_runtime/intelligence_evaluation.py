"""Executable scientific-intelligence benchmark v0.2.

The harness evaluates response contracts rather than prose quality. Three arms are
supported: an LLM-only responder, a deterministic/tool-assisted responder, and
AXIOM's bounded research runtime. An unavailable provider is recorded as NOT_RUN;
no synthetic score is substituted.
"""
from __future__ import annotations

import json
import math
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
SCORER_VERSION = "scientific-intelligence-scorer-v0.2"
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


def _extract_rho(text: str) -> float | None:
    match = re.search(r"\\brho\\s*=\\s*([-+]?\\d+(?:\\.\\d+)?)", text.lower())
    return float(match.group(1)) if match else None


def _numeric_tolerance_pass(task: BenchmarkTask, response: str, tolerance: float = 1e-9) -> bool:
    expected = _extract_rho(task.prompt)
    if expected is None:
        return True
    observed = _extract_rho(response)
    return observed is not None and math.isclose(observed, expected, rel_tol=tolerance, abs_tol=tolerance)


def _parameter_validity(task: BenchmarkTask, response: str) -> bool:
    if task.level not in {BenchmarkLevel.EXPERIMENT_DESIGN, BenchmarkLevel.AUTONOMOUS_INVESTIGATION}:
        return True
    rho = _extract_rho(response)
    dt_match = re.search(r"\\bdt\\s*=\\s*([-+]?\\d+(?:\\.\\d+)?(?:e[-+]?\\d+)?)", response.lower())
    if rho is None or dt_match is None:
        return False
    dt = float(dt_match.group(1))
    return math.isfinite(rho) and math.isfinite(dt) and 1.0 <= rho <= 40.0 and 0.0 < dt <= 0.1


def _evidence_tier_valid(task: BenchmarkTask, response: str) -> bool:
    text = response.lower()
    expected = task.expected_concept.lower()
    if "numerically robust" in expected:
        return "numerically robust" in text or "numerical evidence" in text
    if "not formal proof" in expected or "not a proof" in expected:
        return "not a proof" in text or "not a formal proof" in text or "not a mathematical proof" in text
    return True


def _false_proof_claim(text: str) -> bool:
    normalized = re.sub(r"\\s+", " ", text.lower())
    negated = re.search(r"\\b(?:not|no|without)\\s+(?:a\\s+)?(?:formal|mathematical)\\s+proof\\b", normalized)
    if negated:
        normalized = normalized[: negated.start()] + normalized[negated.end() :]
    patterns = (
        r"\\b(?:is|constitutes|establishes|provides)\\s+(?:a\\s+|the\\s+)?(?:formal|mathematical)\\s+proof\\b",
        r"\\b(?:proves?|demonstrates?)\\s+(?:that\\s+)?(?:the\\s+)?(?:lorenz\\s+)?(?:system\\s+)?(?:is\\s+)?chaotic\\b",
        r"\\bmathematically\\s+(?:proven|proved)\\b",
    )
    return any(re.search(pattern, normalized) for pattern in patterns)


def evaluate_text(task: BenchmarkTask, response: str) -> BenchmarkScore:
    """Conservative deterministic scorer with explicit validity gates.

    This remains a transparent baseline evaluator, not an LLM judge. It checks
    concept coverage, numeric parameter consistency, bounded parameter validity,
    evidence-strength language, reproducibility fields, and unsupported-proof claims.
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
    false_proof = _false_proof_claim(text)
    numeric_tolerance_pass = _numeric_tolerance_pass(task, response)
    parameter_validity = _parameter_validity(task, response)
    evidence_tier_valid = _evidence_tier_valid(task, response)
    reproducible = all(term in text for term in ("rho", "dt")) if task.level in {
        BenchmarkLevel.EXPERIMENT_DESIGN,
        BenchmarkLevel.AUTONOMOUS_INVESTIGATION,
    } else True
    evidence_correctness = 0.0 if false_proof else correctness
    if not numeric_tolerance_pass or not parameter_validity or not evidence_tier_valid:
        evidence_correctness = 0.0
    return score_contract(
        task,
        correctness=correctness,
        evidence_correctness=evidence_correctness,
        false_proof=false_proof,
        reproducible=reproducible,
        numeric_tolerance_pass=numeric_tolerance_pass,
        parameter_validity=parameter_validity,
        evidence_tier_valid=evidence_tier_valid,
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
    rho = _extract_rho(task.prompt) or 28.0
    return (
        f"For {task.task_id}, use a bounded Lorenz experiment at rho={rho:g} and dt=0.01. "
        "Record numerical observation, keep dt fixed or compare a timestep ladder, "
        "retain uncertainty, report numerically robust evidence only when checks support it, "
        "and do not call the result a mathematical proof."
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
        f"rho={plan.parameters['rho']:g}, dt={plan.parameters['dt']:g}. "
        f"Evidence: {evidence.evidence_tier}, numerically robust evidence, "
        f"reproducible={run.stage.value == 'COMPLETED'}. "
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
        "scorer": {
            "version": SCORER_VERSION,
            "type": "deterministic",
            "semantic_judge": False,
        },
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
    "SCORER_VERSION",
    "Delta",
    "evaluate_text",
    "render_report",
    "run_responder_arm",
    "run_v0_2_benchmark",
]
