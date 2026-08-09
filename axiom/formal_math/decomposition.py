"""Proof decomposition (FMTP §7)."""

from __future__ import annotations

import uuid
from typing import Any


def decompose_goal(
    theorem_name: str,
    statement: str,
) -> dict[str, Any]:
    """Decompose a difficult goal into subgoals and lemma candidates."""
    subgoals: list[dict[str, Any]] = []
    lemmas: list[dict[str, Any]] = []

    if "→" in statement or "->" in statement or "implies" in statement.lower():
        parts = statement.replace("->", "→").split("→")
        if len(parts) == 2:
            subgoals.append({
                "subgoal_id": f"sg_{uuid.uuid4().hex[:8]}",
                "description": "Prove antecedent or assume hypothesis",
                "statement": parts[0].strip(),
                "status": "open",
            })
            subgoals.append({
                "subgoal_id": f"sg_{uuid.uuid4().hex[:8]}",
                "description": "Prove consequent under hypothesis",
                "statement": parts[1].strip(),
                "status": "open",
            })

    if "∧" in statement or " and " in statement.lower():
        parts = statement.replace(" and ", " ∧ ").split("∧")
        for i, part in enumerate(parts):
            subgoals.append({
                "subgoal_id": f"sg_{uuid.uuid4().hex[:8]}",
                "description": f"Conjunct {i + 1}",
                "statement": part.strip(),
                "status": "open",
            })

    if not subgoals:
        subgoals.append({
            "subgoal_id": f"sg_{uuid.uuid4().hex[:8]}",
            "description": "Main goal",
            "statement": statement,
            "status": "open",
        })

    if any(op in statement for op in ["+", "*", "="]):
        lemmas.append({
            "lemma_id": f"lm_{uuid.uuid4().hex[:8]}",
            "name": f"{theorem_name}_helper_algebra",
            "description": "Algebraic manipulation helper lemma",
            "suggested_tactics": ["ring", "simp"],
        })

    blocking = subgoals[0]["subgoal_id"] if subgoals else None

    return {
        "theorem_name": theorem_name,
        "statement": statement,
        "subgoals": subgoals,
        "lemma_candidates": lemmas,
        "blocking_subgoal": blocking,
    }
