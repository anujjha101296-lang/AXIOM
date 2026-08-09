"""Informal → formal pipeline (FMTP §3)."""

from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone

from axiom.core.verification.lean_exporter import LeanExporter
from axiom.formal_math.models import FormalizationResult, FormalizationStatus
from axiom.formal_math.prover_registry import recommended_prover


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def structure_statement(informal: str) -> tuple[str, list[str]]:
    """Parse informal math into structured statement; surface ambiguities."""
    ambiguities: list[str] = []
    text = informal.strip()

    if re.search(r"\b(some|many|often|usually|probably)\b", text, re.I):
        ambiguities.append("Vague quantifier or hedging language detected")

    if "?" in text and not text.endswith("?"):
        ambiguities.append("Mixed declarative and interrogative phrasing")

    if not re.search(r"\b(for all|there exists|∀|∃|every|all)\b", text, re.I):
        if re.search(r"\b(theorem|lemma|prove|show)\b", text, re.I):
            ambiguities.append("Universal/existential quantifiers not explicit")

    structured = text
    if "prove that" in text.lower():
        structured = re.sub(r"(?i)prove that\s*", "∀ relevant x, ", text)

    return structured, ambiguities


def formalize_informal(
    informal_statement: str,
    *,
    theorem_name: str = "informal_theorem",
    prover: str | None = None,
    variables: dict[str, str] | None = None,
) -> FormalizationResult:
    """Transform natural-language math toward formal specification."""
    structured, ambiguities = structure_statement(informal_statement)
    selected_prover = prover or recommended_prover("algebra")

    if ambiguities and len(ambiguities) >= 2:
        return FormalizationResult(
            result_id=f"frm_{uuid.uuid4().hex[:12]}",
            informal_statement=informal_statement,
            structured_statement=structured,
            formal_spec=None,
            status=FormalizationStatus.AMBIGUOUS,
            prover=selected_prover,
            ambiguities=ambiguities,
            created_at=_utc_now(),
        )

    exporter = LeanExporter()
    vars_dict = variables or {"n": "Nat"}
    try:
        lean_code = exporter.export_theorem(
            theorem_name,
            structured,
            vars_dict,
            proof_body="sorry",
        )
    except Exception as exc:
        return FormalizationResult(
            result_id=f"frm_{uuid.uuid4().hex[:12]}",
            informal_statement=informal_statement,
            structured_statement=structured,
            formal_spec=None,
            status=FormalizationStatus.FAILED,
            prover=selected_prover,
            ambiguities=ambiguities + [str(exc)],
            created_at=_utc_now(),
        )

    status = FormalizationStatus.PARTIAL if ambiguities else FormalizationStatus.SUCCESS
    if "sorry" in lean_code:
        status = FormalizationStatus.PARTIAL

    return FormalizationResult(
        result_id=f"frm_{uuid.uuid4().hex[:12]}",
        informal_statement=informal_statement,
        structured_statement=structured,
        formal_spec=lean_code,
        status=status,
        prover=selected_prover,
        ambiguities=ambiguities,
        created_at=_utc_now(),
    )
