"""Versioned scientific-intelligence benchmark contracts.

The benchmark measures whether a system can reason about a bounded scientific
question, design valid experiments, interpret evidence, and avoid unsupported
claims. It does not score eloquence or generic language ability.

v0.1 tasks are loaded from an immutable, hashed JSON corpus committed under
benchmarks/scientific_intelligence/v0.1. Runtime generation is deliberately
not used so benchmark inputs cannot drift with code changes.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


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


_DATASET_PATH = (
    Path(__file__).resolve().parents[2]
    / "benchmarks"
    / "scientific_intelligence"
    / "v0.1"
    / "tasks.json"
)
_MANIFEST_PATH = _DATASET_PATH.with_name("manifest.json")


def _load_v0_1_tasks() -> tuple[BenchmarkTask, ...]:
    if not _DATASET_PATH.is_file() or not _MANIFEST_PATH.is_file():
        raise RuntimeError("Scientific Intelligence v0.1 corpus or manifest is missing.")

    raw = _DATASET_PATH.read_bytes()
    manifest = json.loads(_MANIFEST_PATH.read_text(encoding="utf-8"))
    digest = hashlib.sha256(raw).hexdigest()
    expected_digest = manifest.get("sha256")
    if digest != expected_digest:
        raise RuntimeError(
            "Scientific Intelligence v0.1 corpus hash mismatch: "
            f"expected {expected_digest}, got {digest}."
        )

    payload = json.loads(raw.decode("utf-8"))
    if payload.get("benchmark_version") != "scientific-intelligence-v0.1":
        raise RuntimeError("Unexpected Scientific Intelligence v0.1 corpus version.")

    raw_tasks = payload.get("tasks")
    if not isinstance(raw_tasks, list) or len(raw_tasks) != 40:
        raise RuntimeError("Scientific Intelligence v0.1 must contain exactly 40 tasks.")

    tasks: list[BenchmarkTask] = []
    seen: set[str] = set()
    for item in raw_tasks:
        if not isinstance(item, dict):
            raise RuntimeError("Scientific Intelligence task entries must be objects.")
        required = {"task_id", "level", "prompt", "expected_concept", "forbidden_shortcut"}
        if set(item) != required:
            raise RuntimeError(f"Unexpected task schema for {item.get('task_id', '<unknown>')}.")
        task_id = str(item["task_id"])
        if task_id in seen:
            raise RuntimeError(f"Duplicate benchmark task id: {task_id}.")
        seen.add(task_id)
        tasks.append(
            BenchmarkTask(
                task_id=task_id,
                level=BenchmarkLevel(str(item["level"])),
                prompt=str(item["prompt"]),
                expected_concept=str(item["expected_concept"]),
                forbidden_shortcut=str(item["forbidden_shortcut"]),
            )
        )

    counts = {level: 0 for level in BenchmarkLevel}
    for task in tasks:
        counts[task.level] += 1
    if any(count != 5 for count in counts.values()):
        raise RuntimeError(f"Each benchmark level must contain exactly 5 tasks: {counts}.")
    return tuple(tasks)


def build_v0_1_tasks() -> tuple[BenchmarkTask, ...]:
    """Load the immutable 40-task Scientific Intelligence v0.1 corpus."""
    return _load_v0_1_tasks()


def dataset_sha256() -> str:
    """Return the verified SHA-256 of the immutable v0.1 task corpus."""
    _load_v0_1_tasks()
    return hashlib.sha256(_DATASET_PATH.read_bytes()).hexdigest()


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


__all__ = [
    "BenchmarkLevel",
    "BenchmarkScore",
    "BenchmarkTask",
    "Outcome",
    "build_v0_1_tasks",
    "dataset_sha256",
    "score_contract",
]
