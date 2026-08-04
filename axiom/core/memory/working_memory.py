"""
Working Memory System (MEM)
===========================
Maintains an in-process session store of the active research context:
  - current research problem
  - active hypotheses
  - failed proof attempts
  - open questions

Separate from the persistent SQLite EGS store; designed to be fast,
mutable, and session-scoped.
"""

from __future__ import annotations
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class FailedAttempt:
    expression: str
    target: str
    strategy: str          # e.g. "MCTS", "SMT", "LEAN"
    reason: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class ActiveHypothesis:
    node_id: str
    statement: str
    confidence: float      # 0.0 – 1.0
    origin_strategy: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class ResearchContext:
    problem: str = ""
    active_hypotheses: List[ActiveHypothesis] = field(default_factory=list)
    failed_attempts: List[FailedAttempt] = field(default_factory=list)
    open_questions: List[str] = field(default_factory=list)
    session_start: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


class WorkingMemory:
    """
    Session-scoped working memory for AXIOM's active research context.
    Thread-safe through Python's GIL for single-process deployments.
    """

    def __init__(self):
        self._ctx = ResearchContext()

    # ── Problem ─────────────────────────────────────────────────────────────

    def set_problem(self, problem: str) -> None:
        self._ctx.problem = problem
        self._touch()

    def get_problem(self) -> str:
        return self._ctx.problem

    # ── Hypotheses ───────────────────────────────────────────────────────────

    def add_hypothesis(
        self,
        node_id: str,
        statement: str,
        confidence: float = 0.5,
        origin_strategy: str = "HYP",
    ) -> None:
        # Avoid duplicates by node_id
        existing_ids = {h.node_id for h in self._ctx.active_hypotheses}
        if node_id not in existing_ids:
            self._ctx.active_hypotheses.append(
                ActiveHypothesis(node_id, statement, confidence, origin_strategy)
            )
            self._touch()

    def get_hypotheses(self) -> List[ActiveHypothesis]:
        return list(self._ctx.active_hypotheses)

    def remove_hypothesis(self, node_id: str) -> bool:
        before = len(self._ctx.active_hypotheses)
        self._ctx.active_hypotheses = [
            h for h in self._ctx.active_hypotheses if h.node_id != node_id
        ]
        self._touch()
        return len(self._ctx.active_hypotheses) < before

    # ── Failed Attempts ──────────────────────────────────────────────────────

    def record_failure(
        self,
        expression: str,
        target: str,
        strategy: str,
        reason: str,
    ) -> None:
        self._ctx.failed_attempts.append(
            FailedAttempt(expression, target, strategy, reason)
        )
        self._touch()

    def get_failures(self) -> List[FailedAttempt]:
        return list(self._ctx.failed_attempts)

    # ── Open Questions ───────────────────────────────────────────────────────

    def add_question(self, question: str) -> None:
        if question not in self._ctx.open_questions:
            self._ctx.open_questions.append(question)
            self._touch()

    def get_questions(self) -> List[str]:
        return list(self._ctx.open_questions)

    # ── Full Context ─────────────────────────────────────────────────────────

    def snapshot(self) -> Dict[str, Any]:
        """Return a JSON-serialisable snapshot of the current context."""
        return {
            "problem": self._ctx.problem,
            "session_start": self._ctx.session_start,
            "last_updated": self._ctx.last_updated,
            "active_hypotheses": [
                {
                    "node_id": h.node_id,
                    "statement": h.statement,
                    "confidence": h.confidence,
                    "origin_strategy": h.origin_strategy,
                    "timestamp": h.timestamp,
                }
                for h in self._ctx.active_hypotheses
            ],
            "failed_attempts": [
                {
                    "expression": f.expression,
                    "target": f.target,
                    "strategy": f.strategy,
                    "reason": f.reason,
                    "timestamp": f.timestamp,
                }
                for f in self._ctx.failed_attempts
            ],
            "open_questions": self._ctx.open_questions,
            "metadata": self._ctx.metadata,
        }

    def reset(self) -> None:
        """Clear the working memory (start a new research session)."""
        self._ctx = ResearchContext()

    # ── Internal ─────────────────────────────────────────────────────────────

    def _touch(self) -> None:
        self._ctx.last_updated = time.time()
