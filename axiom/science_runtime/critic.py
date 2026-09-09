from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Critique:
    verdict: str
    severity: str
    checks: dict[str, bool]
    concerns: tuple[str, ...]
    next_actions: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "verdict": self.verdict,
            "severity": self.severity,
            "checks": self.checks,
            "concerns": list(self.concerns),
            "next_actions": list(self.next_actions),
        }


def critique_evidence(
    *,
    evidence_tier: str,
    reproducible: bool,
    convergence_errors: list[float],
    independent_relative_error: float,
    finite: bool,
    has_provenance: bool,
) -> Critique:
    """Apply deterministic scientific-quality gates to an evidence bundle.

    This critic evaluates evidence quality; it does not infer a mathematical
    theorem from numerical data.
    """
    checks = {
        "finite": finite,
        "reproducible": reproducible,
        "provenance": has_provenance,
        "convergence": bool(convergence_errors) and all(e >= 0 and e < 1.0 for e in convergence_errors),
        "independent_check": independent_relative_error < 0.1,
        "evidence_tier_declared": evidence_tier == "NUMERICAL_OBSERVATION",
    }
    concerns: list[str] = []
    next_actions: list[str] = []
    if not finite:
        concerns.append("Non-finite numerical state detected.")
        next_actions.append("Reject run and inspect integration stability.")
    if not reproducible:
        concerns.append("Experiment is not marked reproducible.")
        next_actions.append("Record deterministic inputs, environment, and execution metadata.")
    if not has_provenance:
        concerns.append("Provenance metadata is incomplete.")
        next_actions.append("Persist source, parameters, method, and content hash.")
    if not checks["convergence"]:
        concerns.append("Convergence evidence did not satisfy the current numerical gate.")
        next_actions.append("Repeat with a finer timestep ladder or shorter horizon.")
    if not checks["independent_check"]:
        concerns.append("Independent solver disagreement exceeds the current tolerance.")
        next_actions.append("Investigate solver error and repeat the cross-check.")
    if not checks["evidence_tier_declared"]:
        concerns.append("Evidence tier is missing or incorrectly upgraded.")
        next_actions.append("Downgrade the claim to the strongest explicitly supported evidence tier.")

    passed = all(checks.values())
    if passed:
        return Critique(
            verdict="ACCEPT_NUMERICAL_EVIDENCE",
            severity="LOW",
            checks=checks,
            concerns=(),
            next_actions=("Proceed to scientific interpretation; do not label this a formal proof.",),
        )
    return Critique(
        verdict="REJECT_OR_REPEAT",
        severity="HIGH" if not finite or not checks["evidence_tier_declared"] else "MEDIUM",
        checks=checks,
        concerns=tuple(concerns),
        next_actions=tuple(next_actions),
    )
