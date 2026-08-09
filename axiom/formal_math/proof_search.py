"""Proof search engine (FMTP §5, §12)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

from axiom.mip.formal.lean4 import generate_theorem, suggest_tactics


@dataclass
class ProofStrategy:
    strategy_id: str
    name: str
    description: str
    tactics: list[str] = field(default_factory=list)
    estimated_depth: int = 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "strategy_id": self.strategy_id,
            "name": self.name,
            "description": self.description,
            "tactics": self.tactics,
            "estimated_depth": self.estimated_depth,
        }


STRATEGY_CATALOG = [
    ProofStrategy("direct", "Direct proof", "Apply tactics directly to goal"),
    ProofStrategy("contradiction", "Contradiction", "Assume negation and derive contradiction", ["contrapose", "push_neg"]),
    ProofStrategy("induction", "Induction", "Mathematical induction on natural number", ["induction"]),
    ProofStrategy("cases", "Case analysis", "Split into exhaustive cases", ["cases"]),
    ProofStrategy("rewrite", "Rewrite", "Apply known lemmas and simplification", ["simp", "ring", "ring_nf"]),
    ProofStrategy("construction", "Construction", "Explicitly construct witness", ["constructor", "use"]),
    ProofStrategy("library", "Library search", "Search Mathlib for applicable lemmas", []),
    ProofStrategy("automation", "Automation", "Prover automation tactics", ["aesop", "decide", "omega"]),
]


def generate_proof_strategies(statement: str) -> list[dict[str, Any]]:
    """Generate candidate proof strategies for a formal obligation."""
    suggested = suggest_tactics(statement)
    strategies = []

    for base in STRATEGY_CATALOG:
        s = base
        tactics = list(s.tactics) + [t for t in suggested if t not in s.tactics]
        strategies.append({
            **s.to_dict(),
            "strategy_id": f"pst_{uuid.uuid4().hex[:8]}",
            "tactics": tactics[:6],
            "confidence": _score_strategy(statement, s.name),
        })

    strategies.sort(key=lambda x: x["confidence"], reverse=True)
    return strategies


def attempt_proof_search(
    theorem_name: str,
    statement: str,
    *,
    strategy_name: str = "direct",
) -> dict[str, Any]:
    """Generate proof script for a strategy — does NOT claim verification."""
    strategies = generate_proof_strategies(statement)
    chosen = next((s for s in strategies if s["name"].lower() == strategy_name.lower()), strategies[0])

    result = generate_theorem(theorem_name, statement)
    return {
        "theorem_name": theorem_name,
        "statement": statement,
        "strategy": chosen,
        "script": result.script,
        "suggested_tactics": result.suggested_tactics,
        "compiler_available": result.compiler_available,
        "note": "Proof script generated — must be compiled by prover for verification",
    }


def _score_strategy(statement: str, name: str) -> float:
    lower = statement.lower()
    scores = {
        "Direct proof": 0.5,
        "Contradiction": 0.7 if "not" in lower or "¬" in lower else 0.3,
        "Induction": 0.8 if any(k in lower for k in ["natural", "induction", "n ≥", "forall n"]) else 0.2,
        "Case analysis": 0.6 if " or " in lower or "∨" in lower else 0.3,
        "Rewrite": 0.7 if "=" in lower else 0.4,
        "Automation": 0.5,
        "Library search": 0.4,
        "Construction": 0.6 if "exists" in lower or "∃" in lower else 0.3,
    }
    return scores.get(name, 0.4)
