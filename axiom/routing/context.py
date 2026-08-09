"""Context management — structured research context bundles (SIMR §21–23)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ContextBundle:
    """Separate context sections — do not stuff entire histories into every call."""

    problem_statement: str
    definitions: list[str] = field(default_factory=list)
    known_facts: list[dict[str, Any]] = field(default_factory=list)
    evidence: list[dict[str, Any]] = field(default_factory=list)
    research_history: list[dict[str, Any]] = field(default_factory=list)
    working_hypotheses: list[dict[str, Any]] = field(default_factory=list)
    tool_outputs: list[dict[str, Any]] = field(default_factory=list)
    failed_attempts: list[dict[str, Any]] = field(default_factory=list)
    current_plan: dict[str, Any] = field(default_factory=dict)
    verification_requirements: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "problem_statement": self.problem_statement,
            "definitions": self.definitions,
            "known_facts": self.known_facts,
            "evidence": self.evidence,
            "research_history": self.research_history,
            "working_hypotheses": self.working_hypotheses,
            "tool_outputs": self.tool_outputs,
            "failed_attempts": self.failed_attempts,
            "current_plan": self.current_plan,
            "verification_requirements": self.verification_requirements,
        }

    def build_prompt_context(self, *, max_items: int = 5) -> str:
        """Build a bounded context string for model calls."""
        sections = [f"Problem: {self.problem_statement}"]
        if self.definitions:
            sections.append("Definitions:\n" + "\n".join(f"- {d}" for d in self.definitions[:max_items]))
        verified_facts = [
            f for f in self.known_facts
            if f.get("verification_status") in ("verified", "formally_verified", "measured")
        ]
        speculative = [f for f in self.known_facts if f not in verified_facts]
        if verified_facts:
            sections.append(
                "Verified facts:\n"
                + "\n".join(f"- {f.get('statement', f)}" for f in verified_facts[:max_items])
            )
        if speculative:
            sections.append(
                "Speculative (unverified):\n"
                + "\n".join(f"- {f.get('statement', f)}" for f in speculative[:3])
            )
        if self.verification_requirements:
            sections.append(
                "Verification required: " + ", ".join(self.verification_requirements)
            )
        return "\n\n".join(sections)


def rank_memories(
    memories: list[dict[str, Any]],
    *,
    query: str = "",
) -> list[dict[str, Any]]:
    """Rank memories by relevance, recency, and verification status (SIMR §22)."""
    status_rank = {
        "formally_verified": 5,
        "verified": 4,
        "measured": 4,
        "supported": 3,
        "plausible": 2,
        "speculative": 1,
        "unknown": 0,
    }

    def score(mem: dict[str, Any]) -> float:
        s = status_rank.get(mem.get("verification_status", "unknown"), 0) * 2.0
        s += mem.get("reliability", 0.5)
        if query and query.lower() in str(mem.get("content", "")).lower():
            s += 1.0
        s += mem.get("recency_score", 0.0)
        return s

    return sorted(memories, key=score, reverse=True)
