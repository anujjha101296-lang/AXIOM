"""Formal mathematics bridge for Discovery Engine.

Hypothesis → formal statement attempt → (optional) compile. Never labels prose as verified.
"""

from __future__ import annotations

from typing import Any

from axiom.discovery.hypotheses import active_hypotheses
from axiom.discovery.models import AttackRecord, Discovery, _new_id


_MATH_MARKERS = (
    "theorem",
    "lemma",
    "prove",
    "formal",
    "integer",
    "prime",
    "zeta",
    "n+0",
    "∀",
    "∃",
    "=",
)


def looks_mathematical(text: str) -> bool:
    lower = text.lower()
    return any(m in lower for m in _MATH_MARKERS)


def attempt_formal_bridge(d: Discovery) -> dict[str, Any]:
    """Attempt FMTP formalization for mathematical questions. Never claims VERIFIED."""
    primary = next((h for h in active_hypotheses(d.hypotheses) if not h.rejected), None)
    statement = (primary.statement if primary else d.research_question)[:1500]

    if not looks_mathematical(statement) and not looks_mathematical(d.research_question):
        return {
            "attempted": False,
            "reason": "Question does not appear mathematical; formal bridge skipped",
            "compiled_verified": False,
            "prose_is_not_proof": True,
        }

    try:
        from axiom.formal_math.formalization import formalize_informal

        result = formalize_informal(
            statement,
            theorem_name=f"disc_{d.discovery_id[-8:]}",
        )
        payload = result.to_dict() if hasattr(result, "to_dict") else {
            "status": getattr(getattr(result, "status", None), "value", str(getattr(result, "status", ""))),
            "structured_statement": getattr(result, "structured_statement", None),
            "formal_spec": getattr(result, "formal_spec", None),
            "ambiguities": getattr(result, "ambiguities", []),
            "prover": getattr(result, "prover", None),
            "result_id": getattr(result, "result_id", None),
        }
        status = str(payload.get("status", "")).lower()
        compiled_verified = False  # never auto-compile to VERIFIED from this bridge
        return {
            "attempted": True,
            "formalization": payload,
            "status": status,
            "compiled_verified": compiled_verified,
            "prose_is_not_proof": True,
            "notes": (
                "Formalization attempt recorded. Independent prover compilation is required "
                "before any FORMALLY_VERIFIED label. Prose is not proof."
            ),
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "attempted": True,
            "error": str(exc)[:300],
            "compiled_verified": False,
            "prose_is_not_proof": True,
        }


def formal_attack_record(bridge: dict[str, Any]) -> AttackRecord:
    outcome = "inconclusive"
    if bridge.get("compiled_verified"):
        outcome = "supporting"
    elif bridge.get("attempted") and bridge.get("error"):
        outcome = "challenging"
    elif bridge.get("attempted"):
        outcome = "inconclusive"
    return AttackRecord(
        attack_id=_new_id("atk"),
        attack_type="formal",
        summary=bridge.get("notes")
        or bridge.get("reason")
        or bridge.get("error")
        or "Formal bridge attempt",
        outcome=outcome,
        artifact_ids=[str(bridge.get("formalization", {}).get("result_id") or "")],
    )
