"""Theorem library search (FMTP §6)."""

from __future__ import annotations

import re
from typing import Any


_BUILTIN_LIBRARY: list[dict[str, Any]] = [
    {
        "name": "add_comm",
        "statement": "∀ a b : ℕ, a + b = b + a",
        "domain": "algebra",
        "strength": "lemma",
        "dependencies": ["Nat.add_comm"],
    },
    {
        "name": "mul_comm",
        "statement": "∀ a b : ℕ, a * b = b * a",
        "domain": "algebra",
        "strength": "lemma",
        "dependencies": ["Nat.mul_comm"],
    },
    {
        "name": "lagrange_theorem",
        "statement": "∀ G finite group, ∀ H subgroup, |H| divides |G|",
        "domain": "group_theory",
        "strength": "theorem",
        "dependencies": ["Subgroup", "Fintype"],
    },
    {
        "name": "prime_divisor",
        "statement": "∀ n > 1, ∃ p prime, p divides n",
        "domain": "number_theory",
        "strength": "theorem",
        "dependencies": ["Nat.Prime"],
    },
]


def search_library(
    query: str,
    *,
    domain: str | None = None,
    goal_shape: str | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Semantic + structural search across formal library entries."""
    query_lower = query.lower()
    query_tokens = set(re.findall(r"\w+", query_lower))

    results = []
    for entry in _BUILTIN_LIBRARY:
        if domain and entry["domain"] != domain:
            continue
        stmt_tokens = set(re.findall(r"\w+", entry["statement"].lower()))
        overlap = len(query_tokens & stmt_tokens) / max(len(query_tokens | stmt_tokens), 1)
        name_match = 1.0 if query_lower in entry["name"].lower() else 0.0
        name_token_overlap = len(query_tokens & set(entry["name"].lower().split("_"))) / max(len(query_tokens), 1)
        score = overlap * 0.5 + name_match * 0.3 + name_token_overlap * 0.2

        if goal_shape and goal_shape.lower() in entry["statement"].lower():
            score += 0.2

        if score > 0.1:
            results.append({**entry, "relevance_score": round(score, 3)})

    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    return results[:limit]
