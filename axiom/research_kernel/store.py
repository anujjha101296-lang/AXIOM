"""SQLite persistence for Research Kernel runs."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from axiom.research_kernel.models import KernelRun


class KernelStore:
    """Persist kernel runs and learning records."""

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
        CREATE TABLE IF NOT EXISTS kernel_runs (
            run_id TEXT PRIMARY KEY,
            objective TEXT NOT NULL,
            domain TEXT NOT NULL,
            plugin_id TEXT NOT NULL,
            status TEXT NOT NULL,
            current_stage TEXT NOT NULL,
            json_data TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_kernel_runs_status ON kernel_runs(status);
        CREATE INDEX IF NOT EXISTS idx_kernel_runs_domain ON kernel_runs(domain);
        CREATE TABLE IF NOT EXISTS kernel_learning (
            record_id TEXT PRIMARY KEY,
            run_id TEXT NOT NULL,
            insight TEXT NOT NULL,
            json_data TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_kernel_learning_run ON kernel_learning(run_id);
        """)
        conn.commit()

    def save(self, run: KernelRun) -> None:
        conn = self._get_conn()
        payload = run.model_dump(mode="json")
        conn.execute(
            """INSERT OR REPLACE INTO kernel_runs
               (run_id, objective, domain, plugin_id, status, current_stage,
                json_data, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                run.run_id,
                run.objective,
                run.domain,
                run.plugin_id,
                run.status.value,
                run.current_stage.value,
                json.dumps(payload),
                run.created_at.isoformat(),
                run.updated_at.isoformat(),
            ),
        )
        conn.commit()

    def get(self, run_id: str) -> KernelRun | None:
        conn = self._get_conn()
        row = conn.execute(
            "SELECT json_data FROM kernel_runs WHERE run_id = ?", (run_id,)
        ).fetchone()
        if not row:
            return None
        return KernelRun.model_validate(json.loads(row["json_data"]))

    def list_runs(self, limit: int = 50, domain: str | None = None) -> list[KernelRun]:
        conn = self._get_conn()
        if domain:
            rows = conn.execute(
                "SELECT json_data FROM kernel_runs WHERE domain = ? ORDER BY updated_at DESC LIMIT ?",
                (domain, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT json_data FROM kernel_runs ORDER BY updated_at DESC LIMIT ?", (limit,)
            ).fetchall()
        return [KernelRun.model_validate(json.loads(r["json_data"])) for r in rows]
