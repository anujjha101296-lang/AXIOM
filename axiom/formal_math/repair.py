"""Proof repair (FMTP §8)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from axiom.formal_math.models import ProofFailureRecord
from axiom.mip.formal.lean4 import suggest_tactics


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def analyze_failure(
    prover_output: str,
    *,
    attempted_tactic: str = "",
    goal_state: str = "",
) -> dict[str, str]:
    """Extract failure diagnosis from prover output."""
    diagnosis = "unknown_error"
    if "sorry" in prover_output.lower():
        diagnosis = "incomplete_proof_sorry"
    elif "timeout" in prover_output.lower():
        diagnosis = "timeout"
    elif "unknown identifier" in prover_output.lower():
        diagnosis = "missing_definition"
    elif "type mismatch" in prover_output.lower():
        diagnosis = "type_error"
    elif "tactic failed" in prover_output.lower():
        diagnosis = "tactic_failure"

    return {
        "diagnosis": diagnosis,
        "attempted_tactic": attempted_tactic,
        "goal_state": goal_state,
        "suggestion": _suggest_repair(diagnosis, goal_state),
    }


def suggest_repair_tactics(
    statement: str,
    failed_tactic: str,
    previous_attempts: list[str] | None = None,
) -> list[str]:
    """Suggest alternative tactics — avoid repeating failed attempts."""
    previous = set(previous_attempts or [])
    candidates = suggest_tactics(statement)
    return [t for t in candidates if t != failed_tactic and t not in previous][:5]


def create_failure_record(
    theorem_id: str,
    approach: str,
    prover_output: str,
    *,
    goal_state: str = "",
    attempted_tactic: str = "",
) -> ProofFailureRecord:
    analysis = analyze_failure(prover_output, attempted_tactic=attempted_tactic, goal_state=goal_state)
    return ProofFailureRecord(
        failure_id=f"pfl_{uuid.uuid4().hex[:12]}",
        theorem_id=theorem_id,
        approach=approach,
        prover_output=prover_output,
        goal_state=goal_state,
        attempted_tactic=attempted_tactic,
        created_at=_utc_now(),
        learned=analysis["suggestion"],
    )


def _suggest_repair(diagnosis: str, goal_state: str) -> str:
    suggestions = {
        "incomplete_proof_sorry": "Replace sorry with explicit proof or automation",
        "timeout": "Decompose goal or use stronger automation",
        "missing_definition": "Add missing import or definition",
        "type_error": "Check variable types and coercions",
        "tactic_failure": "Try alternative tactic from suggest_tactics()",
    }
    return suggestions.get(diagnosis, "Review goal state and try decomposition")
