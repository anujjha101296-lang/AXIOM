"""SQLite persistence for OpenProblem objects."""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from axiom.open_problems.models import OpenProblem, _utc_now


class OpenProblemStore:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._init()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init(self) -> None:
        with self._conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS open_problems (
                    problem_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    domain TEXT,
                    research_status TEXT,
                    stage_level INTEGER,
                    owner_id TEXT,
                    updated_at TEXT,
                    json_data TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def save(self, problem: OpenProblem) -> OpenProblem:
        problem.last_updated = _utc_now()
        with self._conn() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO open_problems
                (problem_id, title, domain, research_status, stage_level, owner_id, updated_at, json_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    problem.problem_id,
                    problem.title,
                    problem.domain,
                    problem.research_status.value,
                    problem.stage_level,
                    problem.owner_id,
                    problem.last_updated,
                    json.dumps(problem.to_dict()),
                ),
            )
            conn.commit()
        return problem

    def get(self, problem_id: str) -> OpenProblem | None:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT json_data FROM open_problems WHERE problem_id = ?",
                (problem_id,),
            ).fetchone()
        return OpenProblem.from_dict(json.loads(row["json_data"])) if row else None

    def list(
        self,
        *,
        owner_id: str | None = None,
        status: str | None = None,
        limit: int = 50,
    ) -> list[OpenProblem]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT json_data FROM open_problems ORDER BY updated_at DESC LIMIT ?",
                (max(limit * 3, 50),),
            ).fetchall()
        items = [OpenProblem.from_dict(json.loads(r["json_data"])) for r in rows]
        if owner_id and owner_id != "dev":
            items = [p for p in items if p.owner_id == owner_id]
        if status:
            items = [p for p in items if p.research_status.value == status]
        return items[:limit]


_cache: dict[str, OpenProblemStore] = {}


def get_open_problem_store(db_path: str) -> OpenProblemStore:
    if db_path not in _cache:
        _cache[db_path] = OpenProblemStore(db_path)
    return _cache[db_path]
