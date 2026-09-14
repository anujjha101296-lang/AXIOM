"""Versioned scientific-intelligence benchmark contracts.

The benchmark measures whether a system can reason about a bounded scientific
question, design valid experiments, interpret evidence, and avoid unsupported
claims. It does not score eloquence or generic language ability.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Callable


class BenchmarkLevel(StrEnum):
    NUMERICAL_REASONING = "L1"
    EQUATION_INTERPRETATION = "L2"
    HYPOTHESIS = "L3"
    EXPERIMENT_DESIGN = "L4"
    FALSIFICATION = "L5"
    RESULT_INTERPRETATION = "L6"
    COMPETING_HYPOTHESES = "L7"
    AUTONOMOUS_INVESTIGATION = "L8"


class Outcome(StrEnum):
    CORRECT = "CORRECT"
    INCORRECT = "INCORRECT"
    INVALID_EXPERIMENT = "INVALID_EXPERIMENT"
    UNSUPPORTED_CLAIM = "UNSUPPORTED_CLAIM"
    INCONCLUSIVE = "INCONCLUSIVE"


@dataclass(frozen=True)
class BenchmarkTask:
    task_id: str
    level: BenchmarkLevel
    prompt: str
    expected_concept: str
    forbidden_shortcut: str


@dataclass(frozen=True)
class BenchmarkScore:
    task_id: str
    outcome: Outcome
    correctness: float
    evidence_correctness: float
    false_proof: bool
    reproducible: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "task_id": self.task_id,
            "outcome": self.outcome.value,
            "correctness": self.correctness,
            "evidence_correctness": self.evidence_correctness,
            "false_proof": self.false_proof,
            "reproducible": self.reproducible,
        }


_LEVEL_PROMPTS: dict[BenchmarkLevel, tuple[str, str]] = {
    BenchmarkLevel.NUMERICAL_REASONING: (
        "For the Lorenz system at rho={rho}, explain what a finite paired-trajectory separation value establishes.",
        "distinguish numerical observation from proof",
    ),
    BenchmarkLevel.EQUATION_INTERPRETATION: (
        "Given dx/dt=sigma(y-x), dy/dt=x(rho-z)-y, dz/dt=xy-beta z, identify which parameter changes the linear coupling in dx/dt.",
        "sigma controls the x-y coupling rate",
    ),
    BenchmarkLevel.HYPOTHESIS: (
        "Formulate one falsifiable hypothesis about sensitivity of nearby Lorenz trajectories near rho={rho}.",
        "state a measurable observation and bounded conditions",
    ),
    BenchmarkLevel.EXPERIMENT_DESIGN: (
        "Design a bounded test of whether the Lorenz sensitivity observation is robust to timestep resolution.",
        "use a declared timestep ladder and fixed other inputs",
    ),
    BenchmarkLevel.FALSIFICATION: (
        "A sensitivity result changes substantially when dt is halved. What should a scientific critic do next?",
        "reject the robustness claim and request resolution checks",
    ),
    BenchmarkLevel.RESULT_INTERPRETATION: (
        "A paired trajectory separates at rho={rho}, all states remain finite, and an independent solver agrees within tolerance. Interpret the evidence.",
        "numerically robust evidence, not formal proof",
    ),
    BenchmarkLevel.COMPETING_HYPOTHESES: (
        "Compare hypotheses H1='chaotic sensitivity' and H2='numerical artifact' after timestep and independent-solver checks disagree.",
        "retain uncertainty and identify the check that discriminates",
    ),
    BenchmarkLevel.AUTONOMOUS_INVESTIGATION: (
        "Investigate whether Lorenz sensitivity near rho={rho} is robust to numerical resolution and solver choice. Return the minimum bounded experiment sequence needed.",
        "question -> hypothesis -> experiment -> evidence -> critique -> independent check -> conclusion",
    ),
}


def build_v0_1_tasks() -> tuple[BenchmarkTask, ...]:
    """Build 40 deterministic benchmark tasks: 5 tasks per capability level."""
    tasks: list[BenchmarkTask] = []
    rhos = (20.0, 24.0, 28.0, 32.0, 40.0)
    for level in BenchmarkLevel:
        template, concept = _LEVEL_PROMPTS[level]
        for index, rho in enumerate(rhos, start=1):
            task_id = f"sci-v0.1-{level.value.lower()}-{index:02d}"
            tasks.append(
                BenchmarkTask(
                    task_id=task_id,
                    level=level,
                    prompt=template.format(rho=rho),
                    expected_concept=concept,
                    forbidden_shortcut="Do not call finite numerical evidence a mathematical proof.",
                )
            )
    return tuple(tasks)


def score_contract(
    task: BenchmarkTask,
    *,
    correctness: float,
    evidence_correctness: float,
    false_proof: bool,
    reproducible: bool,
) -> BenchmarkScore:
    """Normalize a machine-evaluated result into the benchmark score contract."""
    correctness = max(0.0, min(1.0, float(correctness)))
    evidence_correctness = max(0.0, min(1.0, float(evidence_correctness)))
    if false_proof:
        outcome = Outcome.UNSUPPORTED_CLAIM
    elif correctness < 0.5:
        outcome = Outcome.INCORRECT
    elif evidence_correctness < 0.5:
        outcome = Outcome.INVALID_EXPERIMENT
    elif correctness < 1.0 or evidence_correctness < 1.0:
        outcome = Outcome.INCONCLUSIVE
    else:
        outcome = Outcome.CORRECT
    return BenchmarkScore(
        task_id=task.task_id,
        outcome=outcome,
        correctness=correctness,
        evidence_correctness=evidence_correctness,
        false_proof=false_proof,
        reproducible=reproducible,
    )


__all__ = ["BenchmarkLevel", "BenchmarkScore", "BenchmarkTask", "Outcome", "build_v0_1_tasks", "score_contract"]
