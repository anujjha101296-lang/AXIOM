"""SQLite persistence for research validation runs."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


class RVPStore:
    """Persist RVP runs for dashboard, replay, and trend analysis."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = str(db_path)
        self._ensure_schema()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self) -> None:
        conn = self._conn()
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS rvp_runs (
            run_id TEXT PRIMARY KEY,
            config_hash TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            stage INTEGER NOT NULL,
            problem_id TEXT NOT NULL,
            answer_score REAL NOT NULL,
            composite_score REAL NOT NULL,
            passed INTEGER NOT NULL,
            cost_ms REAL NOT NULL,
            latency_ms REAL NOT NULL,
            json_data TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_rvp_runs_stage ON rvp_runs(stage);
        CREATE INDEX IF NOT EXISTS idx_rvp_runs_timestamp ON rvp_runs(timestamp);
        CREATE INDEX IF NOT EXISTS idx_rvp_runs_config_hash ON rvp_runs(config_hash);
        """)
        conn.commit()
        conn.close()

    def save_run(self, result: dict[str, Any]) -> None:
        conn = self._conn()
        conn.execute(
            """INSERT OR REPLACE INTO rvp_runs
               (run_id, config_hash, timestamp, stage, problem_id, answer_score,
                composite_score, passed, cost_ms, latency_ms, json_data)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                result["run_id"],
                result["config_hash"],
                result["timestamp"],
                result["stage"],
                result["problem_id"],
                result["answer_score"],
                result["capability_score"]["composite"],
                1 if result["passed"] else 0,
                result["cost_ms"],
                result["latency_ms"],
                json.dumps(result),
            ),
        )
        conn.commit()
        conn.close()

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        conn = self._conn()
        row = conn.execute("SELECT json_data FROM rvp_runs WHERE run_id = ?", (run_id,)).fetchone()
        conn.close()
        return json.loads(row["json_data"]) if row else None

    def list_runs(self, limit: int = 50, stage: int | None = None) -> list[dict[str, Any]]:
        conn = self._conn()
        if stage is not None:
            rows = conn.execute(
                "SELECT json_data FROM rvp_runs WHERE stage = ? ORDER BY timestamp DESC LIMIT ?",
                (stage, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT json_data FROM rvp_runs ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            ).fetchall()
        conn.close()
        return [json.loads(r["json_data"]) for r in rows]

    def find_by_config_hash(self, config_hash: str) -> list[dict[str, Any]]:
        conn = self._conn()
        rows = conn.execute(
            "SELECT json_data FROM rvp_runs WHERE config_hash = ? ORDER BY timestamp",
            (config_hash,),
        ).fetchall()
        conn.close()
        return [json.loads(r["json_data"]) for r in rows]
