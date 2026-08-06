"""Verification truthfulness — evidence modes and epistemic label assignment.

Ensures simulated, heuristic, and compiler-backed verification outcomes
are never conflated with formal proof status in API responses or graph nodes.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from axiom.core.knowledge_graph.schema import EpistemicStatus, VerificationTier


class EvidenceMode(str, Enum):
    """How a verification outcome was produced."""

    FORMAL_COMPILER = "formal_compiler"
    SMT_FINITE = "smt_finite"
    HEURISTIC = "heuristic"
    SIMULATED = "simulated"
    UNVERIFIED = "unverified"


@dataclass(frozen=True)
class EpistemicAssignment:
    """Epistemic labels assigned from verification evidence."""

    epistemic_status: EpistemicStatus
    verification_tier: VerificationTier
    evidence_mode: EvidenceMode
    formally_proven: bool

    def as_api_fields(self) -> dict[str, str | int | bool]:
        return {
            "epistemic_status": self.epistemic_status.value,
            "verification_tier": self.verification_tier.value,
            "evidence_mode": self.evidence_mode.value,
            "formally_proven": self.formally_proven,
        }


def is_simulated_compiler_output(output: str) -> bool:
    """Return True when compiler output indicates a simulated/fallback check."""
    if not output:
        return False
    lower = output.lower()
    return "simulation" in lower or lower.startswith("simulated")


def classify_compiler_status(compiler_status: str) -> EvidenceMode:
    """Classify a proof-route compiler status string."""
    if not compiler_status:
        return EvidenceMode.UNVERIFIED

    lower = compiler_status.lower()
    if "formally compiled successfully" in lower:
        return EvidenceMode.FORMAL_COMPILER
    if "simulated" in lower:
        return EvidenceMode.SIMULATED
    if "error" in lower or "unverified" in lower or "missing" in lower:
        return EvidenceMode.UNVERIFIED
    return EvidenceMode.UNVERIFIED


def classify_compiler_output(output: str, *, compiler_available: bool) -> EvidenceMode:
    """Classify MIP formal compile output."""
    if is_simulated_compiler_output(output) or not compiler_available:
        return EvidenceMode.SIMULATED
    return EvidenceMode.FORMAL_COMPILER


def evidence_mode_from_compile_result(success: bool, output: str) -> EvidenceMode:
    """Derive evidence mode from a compile attempt result."""
    if is_simulated_compiler_output(output):
        return EvidenceMode.SIMULATED
    if success:
        return EvidenceMode.FORMAL_COMPILER
    return EvidenceMode.UNVERIFIED


def assign_from_smt_modular(is_valid: bool) -> EpistemicAssignment:
    """Assign labels for exhaustive modular (finite-domain) SMT checks."""
    if is_valid:
        return EpistemicAssignment(
            epistemic_status=EpistemicStatus.VERIFIED,
            verification_tier=VerificationTier.TIER_1_SIMULATED,
            evidence_mode=EvidenceMode.SMT_FINITE,
            formally_proven=False,
        )
    return EpistemicAssignment(
        epistemic_status=EpistemicStatus.REFUTED,
        verification_tier=VerificationTier.TIER_0_CONJECTURE,
        evidence_mode=EvidenceMode.SMT_FINITE,
        formally_proven=False,
    )


def assign_from_proof_search(is_proven: bool, compiler_status: str) -> EpistemicAssignment:
    """Assign labels for MCTS proof search + Lean export outcomes."""
    evidence_mode = classify_compiler_status(compiler_status)
    formally_proven = is_proven and evidence_mode == EvidenceMode.FORMAL_COMPILER

    if formally_proven:
        return EpistemicAssignment(
            epistemic_status=EpistemicStatus.VERIFIED,
            verification_tier=VerificationTier.TIER_2_PROVEN,
            evidence_mode=evidence_mode,
            formally_proven=True,
        )

    if is_proven and evidence_mode == EvidenceMode.SIMULATED:
        return EpistemicAssignment(
            epistemic_status=EpistemicStatus.CONJECTURED,
            verification_tier=VerificationTier.TIER_1_SIMULATED,
            evidence_mode=evidence_mode,
            formally_proven=False,
        )

    if is_proven:
        return EpistemicAssignment(
            epistemic_status=EpistemicStatus.CONJECTURED,
            verification_tier=VerificationTier.TIER_0_CONJECTURE,
            evidence_mode=evidence_mode,
            formally_proven=False,
        )

    return EpistemicAssignment(
        epistemic_status=EpistemicStatus.CONJECTURED,
        verification_tier=VerificationTier.TIER_0_CONJECTURE,
        evidence_mode=EvidenceMode.UNVERIFIED,
        formally_proven=False,
    )


def assert_not_false_formal_proof(assignment: EpistemicAssignment) -> None:
    """Guard used in tests: simulated/heuristic paths must not claim formal proof."""
    if assignment.evidence_mode in {
        EvidenceMode.SIMULATED,
        EvidenceMode.HEURISTIC,
        EvidenceMode.SMT_FINITE,
        EvidenceMode.UNVERIFIED,
    }:
        assert not assignment.formally_proven
        assert assignment.verification_tier != VerificationTier.TIER_2_PROVEN
