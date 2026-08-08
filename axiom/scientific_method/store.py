"""SQLite persistence for Scientific Method Engine sessions."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from axiom.scientific_method.models import SMESession


class SMEStore:
    """Persist SME sessions and research memory."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = str(db_path)
        self._conn: sqlite3.Connection | None = None
        self._ensure_schema()

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def _ensure_schema(self) -> None:
        conn = self._get_conn()
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS sme_sessions (
            session_id TEXT PRIMARY KEY,
            objective TEXT NOT NULL,
            domain TEXT NOT NULL,
            status TEXT NOT NULL,
            current_phase TEXT NOT NULL,
            workflow_id TEXT,
            json_data TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_sme_sessions_status ON sme_sessions(status);
        CREATE INDEX IF NOT EXISTS idx_sme_sessions_workflow ON sme_sessions(workflow_id);
        CREATE TABLE IF NOT EXISTS sme_memory (
            record_id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            category TEXT NOT NULL,
            content TEXT NOT NULL,
            phase TEXT,
            json_data TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_sme_memory_session ON sme_memory(session_id);
        """)
        conn.commit()

    def save_session(self, session: SMESession) -> None:
        conn = self._get_conn()
        payload = session.model_dump(mode="json")
        conn.execute(
            """INSERT OR REPLACE INTO sme_sessions
               (session_id, objective, domain, status, current_phase, workflow_id,
                json_data, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                session.session_id,
                session.objective,
                session.domain,
                session.status.value,
                session.current_phase.value,
                session.workflow_id,
                json.dumps(payload),
                session.created_at.isoformat(),
                session.updated_at.isoformat(),
            ),
        )
        conn.commit()

    def get_session(self, session_id: str) -> SMESession | None:
        conn = self._get_conn()
        row = conn.execute(
            "SELECT json_data FROM sme_sessions WHERE session_id = ?", (session_id,)
        ).fetchone()
        if not row:
            return None
        return SMESession.model_validate(json.loads(row["json_data"]))

    def list_sessions(self, limit: int = 50, status: str | None = None) -> list[SMESession]:
        conn = self._get_conn()
        if status:
            rows = conn.execute(
                "SELECT json_data FROM sme_sessions WHERE status = ? ORDER BY updated_at DESC LIMIT ?",
                (status, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT json_data FROM sme_sessions ORDER BY updated_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [SMESession.model_validate(json.loads(r["json_data"])) for r in rows]

    def get_by_workflow(self, workflow_id: str) -> SMESession | None:
        conn = self._get_conn()
        row = conn.execute(
            "SELECT json_data FROM sme_sessions WHERE workflow_id = ? ORDER BY updated_at DESC LIMIT 1",
            (workflow_id,),
        ).fetchone()
        if not row:
            return None
        return SMESession.model_validate(json.loads(row["json_data"]))

    def save_memory_record(self, session_id: str, record: dict[str, Any]) -> None:
        conn = self._get_conn()
        conn.execute(
            """INSERT OR REPLACE INTO sme_memory
               (record_id, session_id, category, content, phase, json_data, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                record["record_id"],
                session_id,
                record["category"],
                record["content"],
                record.get("phase"),
                json.dumps(record),
                record.get("created_at", ""),
            ),
        )
        conn.commit()
