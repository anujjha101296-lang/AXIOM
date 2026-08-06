"""Failure memory — prevents repeated equivalent failed strategies."""

from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from axiom.research_loop.migrations import ensure_research_loop_schema
from axiom.research_loop.schema import FailedAttemptRecord


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def fingerprint_approach(approach: str) -> str:
    normalized = " ".join(approach.lower().split())
    return hashlib.sha256(normalized.encode()).hexdigest()[:16]


class FailureMemoryStore:
    """Persistent store of failed research approaches."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        ensure_research_loop_schema(self.conn)

    def close(self) -> None:
        if self.conn:
            self.conn.close()

    def record_failure(
        self,
        run_id: str,
        attempt: FailedAttemptRecord,
    ) -> FailedAttemptRecord:
        fp = attempt.fingerprint or fingerprint_approach(attempt.approach)
        attempt.fingerprint = fp
        self.conn.execute(
            """
            INSERT INTO research_loop_failures
            (id, run_id, approach, reason_attempted, evidence_json, failure_reason,
             critic_feedback, learned, reuse_conditions, fingerprint, iteration, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                attempt.id,
                run_id,
                attempt.approach,
                attempt.reason_attempted,
                json.dumps(attempt.evidence_considered),
                attempt.failure_reason,
                attempt.critic_feedback,
                attempt.learned,
                attempt.reuse_conditions,
                fp,
                attempt.iteration,
                _utc_now(),
            ),
        )
        self.conn.commit()
        return attempt

    def is_blocked(self, approach: str, run_id: Optional[str] = None) -> bool:
        fp = fingerprint_approach(approach)
        if run_id:
            row = self.conn.execute(
                "SELECT id FROM research_loop_failures WHERE fingerprint = ? AND run_id = ?",
                (fp, run_id),
            ).fetchone()
        else:
            row = self.conn.execute(
                "SELECT id FROM research_loop_failures WHERE fingerprint = ?",
                (fp,),
            ).fetchone()
        return row is not None

    def find_similar(
        self, approach: str, run_id: Optional[str] = None, limit: int = 5
    ) -> List[FailedAttemptRecord]:
        fp = fingerprint_approach(approach)
        if run_id:
            rows = self.conn.execute(
                """
                SELECT * FROM research_loop_failures
                WHERE run_id = ? AND (fingerprint = ? OR approach LIKE ?)
                ORDER BY created_at DESC LIMIT ?
                """,
                (run_id, fp, f"%{approach[:40]}%", limit),
            ).fetchall()
        else:
            rows = self.conn.execute(
                """
                SELECT * FROM research_loop_failures
                WHERE fingerprint = ? OR approach LIKE ?
                ORDER BY created_at DESC LIMIT ?
                """,
                (fp, f"%{approach[:40]}%", limit),
            ).fetchall()
        return [self._row_to_record(r) for r in rows]

    def list_for_run(self, run_id: str) -> List[FailedAttemptRecord]:
        rows = self.conn.execute(
            "SELECT * FROM research_loop_failures WHERE run_id = ? ORDER BY created_at",
            (run_id,),
        ).fetchall()
        return [self._row_to_record(r) for r in rows]

    def _row_to_record(self, row: sqlite3.Row) -> FailedAttemptRecord:
        return FailedAttemptRecord(
            id=row["id"],
            approach=row["approach"],
            reason_attempted=row["reason_attempted"],
            evidence_considered=json.loads(row["evidence_json"]),
            failure_reason=row["failure_reason"],
            critic_feedback=row["critic_feedback"],
            learned=row["learned"],
            reuse_conditions=row["reuse_conditions"],
            fingerprint=row["fingerprint"],
            iteration=row["iteration"],
        )
