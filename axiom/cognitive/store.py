"""SQLite persistence for cognitive cycles."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from axiom.cognitive.models import CognitiveCycle


class CognitiveStore:
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
        CREATE TABLE IF NOT EXISTS aca_cycles (
            cycle_id TEXT PRIMARY KEY,
            objective TEXT NOT NULL,
            domain TEXT NOT NULL,
            status TEXT NOT NULL,
            model_provider TEXT NOT NULL,
            json_data TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_aca_cycles_status ON aca_cycles(status);
        """)
        conn.commit()

    def save(self, cycle: CognitiveCycle) -> None:
        conn = self._get_conn()
        conn.execute(
            """INSERT OR REPLACE INTO aca_cycles
               (cycle_id, objective, domain, status, model_provider, json_data, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                cycle.cycle_id,
                cycle.objective,
                cycle.domain,
                cycle.status.value,
                cycle.model_provider,
                json.dumps(cycle.model_dump(mode="json")),
                cycle.created_at.isoformat(),
                cycle.updated_at.isoformat(),
            ),
        )
        conn.commit()

    def get(self, cycle_id: str) -> CognitiveCycle | None:
        conn = self._get_conn()
        row = conn.execute("SELECT json_data FROM aca_cycles WHERE cycle_id = ?", (cycle_id,)).fetchone()
        if not row:
            return None
        return CognitiveCycle.model_validate(json.loads(row["json_data"]))

    def list_cycles(self, limit: int = 50) -> list[CognitiveCycle]:
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT json_data FROM aca_cycles ORDER BY updated_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [CognitiveCycle.model_validate(json.loads(r["json_data"])) for r in rows]
