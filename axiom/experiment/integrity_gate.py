"""Scientific integrity gate (SEC §34)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from axiom.experiment.models import Experiment, EvidenceClass


@dataclass
class IntegrityResult:
    allowed: bool
    reason: str
    checks: dict[str, bool]

    def to_dict(self) -> dict[str, Any]:
        return {"allowed": self.allowed, "reason": self.reason, "checks": self.checks}


def check_experiment_integrity(experiment: Experiment) -> IntegrityResult:
    """Gate before experiment results can support important claims."""
    checks = {
        "has_provenance": bool(experiment.provenance or experiment.environment),
        "has_results": bool(experiment.results),
        "completed": experiment.status.value in ("COMPLETED", "ANALYZED", "VERIFIED"),
        "not_claimed_as_proof": experiment.evidence_class != "mathematical_proof",
        "computational_evidence_labeled": experiment.evidence_class in (
            EvidenceClass.COMPUTATIONAL_EVIDENCE.value,
            EvidenceClass.NUMERICAL_EVIDENCE.value,
            EvidenceClass.STATISTICAL_EVIDENCE.value,
            EvidenceClass.SYMBOLIC_EVIDENCE.value,
        ),
        "has_research_question": bool(experiment.spec.get("research_question")),
        "has_hypothesis": bool(experiment.spec.get("hypothesis")),
    }

    if not checks["completed"]:
        return IntegrityResult(False, "Experiment not completed", checks)
    if not checks["has_results"]:
        return IntegrityResult(False, "No results recorded", checks)
    if not checks["has_provenance"]:
        return IntegrityResult(False, "Missing provenance/environment", checks)

    return IntegrityResult(
        True,
        "Computational evidence — not mathematical proof or established scientific fact",
        checks,
    )
