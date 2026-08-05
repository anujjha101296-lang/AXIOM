"""
Department G — Mathematical Memory
Episodic (session-scoped) memory cache and failure guard.
"""
from __future__ import annotations

import json
import sqlite3
import uuid
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class EpisodicMemory:
    """Session-scoped in-memory context cache. Resets per session."""

    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    problem_id: str | None = None
    active_hypotheses: list[str] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)
    research_context: dict[str, Any] = field(default_factory=dict)
    _failed_tactics: dict[str, list[str]] = field(default_factory=dict)
    _event_log: list[dict[str, Any]] = field(default_factory=list)

    def record_failed_tactic(self, theorem_id: str, tactic: str) -> None:
        """Record a failed tactic so it is not retried."""
        if theorem_id not in self._failed_tactics:
            self._failed_tactics[theorem_id] = []
        if tactic not in self._failed_tactics[theorem_id]:
            self._failed_tactics[theorem_id].append(tactic)
        self._log_event("tactic_failed", {"theorem_id": theorem_id, "tactic": tactic})

    def get_failed_tactics(self, theorem_id: str) -> list[str]:
        """Return list of tactics that failed for this theorem."""
        return self._failed_tactics.get(theorem_id, [])

    def add_hypothesis(self, hypothesis: str) -> None:
        if hypothesis not in self.active_hypotheses:
            self.active_hypotheses.append(hypothesis)

    def add_open_question(self, question: str) -> None:
        if question not in self.open_questions:
            self.open_questions.append(question)

    def clear(self) -> None:
        """Reset episodic memory (new session)."""
        self.session_id = str(uuid.uuid4())
        self.problem_id = None
        self.active_hypotheses.clear()
        self.open_questions.clear()
        self.research_context.clear()
        self._failed_tactics.clear()
        self._event_log.clear()
        logger.info("Episodic memory cleared (new session: %s)", self.session_id)

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "problem_id": self.problem_id,
            "active_hypotheses": self.active_hypotheses,
            "open_questions": self.open_questions,
            "research_context": self.research_context,
            "failed_tactics_summary": {
                tid: len(tactics)
                for tid, tactics in self._failed_tactics.items()
            },
        }

    def _log_event(self, event_type: str, data: dict[str, Any]) -> None:
        self._event_log.append({
            "type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        })


class SemanticMemory:
    """Long-term SQLite memory store persisting across sessions."""

    def __init__(self, db_path: str = "axiom.db") -> None:
        self.db_path = db_path

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def save_snapshot(self, episodic: EpisodicMemory) -> str:
        """Persist episodic memory to long-term store. Returns snapshot_id."""
        snapshot_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        conn = self._conn()
        try:
            with conn:
                conn.execute(
                    """
                    INSERT INTO mip_memory_snapshots
                    (id, session_id, problem_id, active_hypotheses,
                     failed_tactics, open_questions, research_context,
                     snapshot_type, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'semantic', ?)
                    """,
                    (
                        snapshot_id,
                        episodic.session_id,
                        episodic.problem_id,
                        json.dumps(episodic.active_hypotheses),
                        json.dumps(episodic._failed_tactics),
                        json.dumps(episodic.open_questions),
                        json.dumps(episodic.research_context),
                        now,
                    ),
                )
            logger.info("Saved semantic memory snapshot: %s", snapshot_id)
            return snapshot_id
        finally:
            conn.close()

    def get_all_failed_tactics(self, theorem_id: str) -> list[str]:
        """Retrieve all historically failed tactics for a theorem across all sessions."""
        conn = self._conn()
        try:
            rows = conn.execute(
                "SELECT failed_tactics FROM mip_memory_snapshots WHERE failed_tactics IS NOT NULL"
            ).fetchall()
            all_failed: set[str] = set()
            for row in rows:
                try:
                    data = json.loads(row["failed_tactics"])
                    if theorem_id in data:
                        all_failed.update(data[theorem_id])
                except (json.JSONDecodeError, KeyError):
                    pass
            return list(all_failed)
        finally:
            conn.close()

    def get_recent_snapshots(self, limit: int = 10) -> list[dict[str, Any]]:
        """Retrieve the most recent memory snapshots."""
        conn = self._conn()
        try:
            rows = conn.execute(
                "SELECT * FROM mip_memory_snapshots ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()


class FailureGuard:
    """
    Tactic failure suppression system.
    Integrates episodic + semantic memory to prevent MCTS from re-trying failed tactics.
    """

    def __init__(
        self,
        episodic: EpisodicMemory,
        semantic: SemanticMemory | None = None,
    ) -> None:
        self.episodic = episodic
        self.semantic = semantic

    def get_excluded_tactics(self, theorem_id: str) -> list[str]:
        """Get all tactics that should be excluded for this theorem."""
        excluded = set(self.episodic.get_failed_tactics(theorem_id))
        if self.semantic:
            try:
                excluded.update(self.semantic.get_all_failed_tactics(theorem_id))
            except Exception as exc:
                logger.warning("SemanticMemory unavailable: %s", exc)
        return list(excluded)

    def filter_tactics(self, theorem_id: str, tactics: list[str]) -> list[str]:
        """Remove known-failed tactics from a candidate list."""
        excluded = set(self.get_excluded_tactics(theorem_id))
        filtered = [t for t in tactics if t not in excluded]
        if len(filtered) < len(tactics):
            skipped = len(tactics) - len(filtered)
            logger.debug("FailureGuard: excluded %d known-failed tactics", skipped)
        return filtered

    def record_failure(self, theorem_id: str, tactic: str) -> None:
        """Record a new tactic failure."""
        self.episodic.record_failed_tactic(theorem_id, tactic)
