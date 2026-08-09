"""Conjecture pipeline (FMTP §10)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from axiom.formal_math.models import ConjectureStatus


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def generate_conjecture(
    source_statement: str,
    *,
    name: str = "source_theorem",
    domain: str = "unknown",
    motivation: str = "",
) -> dict[str, Any]:
    """Controlled conjecture workflow — always begins UNVERIFIED."""
    try:
        from axiom.mip.conjecture.generator import STRATEGIES, ConjectureCandidate

        candidates: list[ConjectureCandidate] = []
        for strategy_name, strategy_fn in STRATEGIES.items():
            result = strategy_fn(source_statement, name)
            if result:
                candidates.append(
                    ConjectureCandidate(
                        statement=result,
                        strategy=strategy_name,
                        source_node_ids=[],
                        domain=domain,
                    )
                )
        if candidates:
            best = candidates[0]
            return {
                "conjecture_id": f"cnj_{uuid.uuid4().hex[:12]}",
                "statement": best.statement,
                "status": ConjectureStatus.UNVERIFIED.value,
                "strategy": best.strategy,
                "novelty_score": best.novelty_score,
                "motivation": motivation or f"Derived via {best.strategy} strategy",
                "formalization_status": "unverified",
                "verification_plan": [
                    "counterexample_search",
                    "literature_search",
                    "formalization",
                    "independent_proof",
                ],
                "created_at": _utc_now(),
            }
    except ImportError:
        pass

    return {
        "conjecture_id": f"cnj_{uuid.uuid4().hex[:12]}",
        "statement": f"Generalization of: {source_statement}",
        "status": ConjectureStatus.UNVERIFIED.value,
        "strategy": "GENERAL",
        "novelty_score": 0.3,
        "motivation": motivation or "Fallback generalization",
        "formalization_status": "unverified",
        "verification_plan": ["counterexample_search", "formalization"],
        "created_at": _utc_now(),
    }
