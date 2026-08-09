"""Computational counterexample workflow (SEC §25)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from axiom.experiment.sandbox import execute_sandboxed
from axiom.experiment.models import ResourceBudget


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def search_computational_counterexample(
    claim: str,
    test_code: str,
    *,
    modulus: int = 100,
    budget: ResourceBudget | None = None,
) -> dict[str, Any]:
    """Standardized counterexample search — triggers E&R on discovery."""
    budget = budget or ResourceBudget(timeout_seconds=10.0)
    result = execute_sandboxed(test_code, budget=budget)

    # Match positive hit only — do NOT treat NO_COUNTEREXAMPLE as a hit
    # (substring "COUNTEREXAMPLE" appears inside NO_COUNTEREXAMPLE).
    stdout_u = (result.stdout or "").upper()
    counterexample_found = result.success and (
        "COUNTEREXAMPLE_FOUND" in stdout_u
        or any(
            line.strip() == "COUNTEREXAMPLE"
            for line in stdout_u.splitlines()
        )
    )

    return {
        "workflow_id": f"cex_{uuid.uuid4().hex[:12]}",
        "claim": claim,
        "counterexample_found": counterexample_found,
        "sandbox_result": result.to_dict(),
        "created_at": _utc_now(),
        "evidence_class": "computational_evidence",
        "not_mathematical_proof": True,
        "er_trigger": counterexample_found,
        "verification_required": counterexample_found,
    }
