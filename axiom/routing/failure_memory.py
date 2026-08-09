"""Model failure memory — learn from failures (SIMR §9)."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone

from axiom.routing.models import ModelFailureRecord, ModelSpec


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class FailureMemory:
    """Track model-specific failure profiles for adaptive routing."""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._persistent_conn: sqlite3.Connection | None = None
        if db_path == ":memory:":
            self._persistent_conn = sqlite3.connect(":memory:", check_same_thread=False)
            self._persistent_conn.row_factory = sqlite3.Row
        self._ensure_schema()

    def _conn(self) -> sqlite3.Connection:
        if self._persistent_conn is not None:
            return self._persistent_conn
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _release_conn(self, conn: sqlite3.Connection) -> None:
        if conn is not self._persistent_conn:
            conn.close()

    def _ensure_schema(self) -> None:
        conn = self._conn()
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS simr_failures (
            failure_id TEXT PRIMARY KEY,
            model_id TEXT NOT NULL,
            failure_type TEXT NOT NULL,
            json_data TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_simr_failures_model ON simr_failures(model_id);
        CREATE TABLE IF NOT EXISTS simr_conflicts (
            conflict_id TEXT PRIMARY KEY,
            json_data TEXT NOT NULL,
            created_at TEXT NOT NULL,
            resolution_status TEXT NOT NULL
        );
        """)
        conn.commit()
        self._release_conn(conn)

    def record_failure(
        self,
        model_id: str,
        failure_type: str,
        description: str,
        *,
        problem_domain: str = "unknown",
        capability: str | None = None,
        severity: str = "medium",
    ) -> ModelFailureRecord:
        record = ModelFailureRecord(
            failure_id=f"fail_{uuid.uuid4().hex[:12]}",
            model_id=model_id,
            failure_type=failure_type,
            description=description,
            created_at=_utc_now(),
            problem_domain=problem_domain,
            capability=capability,
            severity=severity,
        )
        conn = self._conn()
        conn.execute(
            "INSERT INTO simr_failures (failure_id, model_id, failure_type, json_data, created_at) VALUES (?, ?, ?, ?, ?)",
            (record.failure_id, model_id, failure_type, json.dumps(record.to_dict()), record.created_at),
        )
        conn.commit()
        self._release_conn(conn)
        return record

    def list_failures(self, model_id: str | None = None, limit: int = 50) -> list[ModelFailureRecord]:
        conn = self._conn()
        if model_id:
            rows = conn.execute(
                "SELECT json_data FROM simr_failures WHERE model_id = ? ORDER BY created_at DESC LIMIT ?",
                (model_id, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT json_data FROM simr_failures ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        self._release_conn(conn)
        return [_failure_from_dict(json.loads(r["json_data"])) for r in rows]

    def has_recent_failures(self, model_id: str, capability: str, threshold: int = 2) -> bool:
        conn = self._conn()
        count = conn.execute(
            """SELECT COUNT(*) FROM simr_failures
               WHERE model_id = ? AND json_data LIKE ?""",
            (model_id, f'%"capability": "{capability}"%'),
        ).fetchone()[0]
        self._release_conn(conn)
        return count >= threshold

    def filter_models(
        self,
        models: list[ModelSpec],
        capability: str,
    ) -> list[ModelSpec]:
        """Deprioritize models with repeated failures — do not remove entirely."""
        good = [m for m in models if not self.has_recent_failures(m.model_id, capability)]
        bad = [m for m in models if self.has_recent_failures(m.model_id, capability)]
        return good + bad

    def record_conflict(
        self,
        source_a: str,
        source_b: str,
        claim_a: str,
        claim_b: str,
        **kwargs,
    ) -> dict:
        from axiom.routing.models import KnowledgeConflict

        conflict = KnowledgeConflict(
            conflict_id=f"cnf_{uuid.uuid4().hex[:12]}",
            source_a=source_a,
            source_b=source_b,
            claim_a=claim_a,
            claim_b=claim_b,
            created_at=_utc_now(),
            resolution_status="open",
            confidence_a=kwargs.get("confidence_a", 0.5),
            confidence_b=kwargs.get("confidence_b", 0.5),
            metadata=kwargs.get("metadata", {}),
        )
        conn = self._conn()
        conn.execute(
            "INSERT INTO simr_conflicts (conflict_id, json_data, created_at, resolution_status) VALUES (?, ?, ?, ?)",
            (conflict.conflict_id, json.dumps(conflict.to_dict()), conflict.created_at, "open"),
        )
        conn.commit()
        self._release_conn(conn)
        return conflict.to_dict()


def _failure_from_dict(data: dict) -> ModelFailureRecord:
    return ModelFailureRecord(
        failure_id=data["failure_id"],
        model_id=data["model_id"],
        failure_type=data["failure_type"],
        description=data["description"],
        created_at=data["created_at"],
        problem_domain=data.get("problem_domain", "unknown"),
        capability=data.get("capability"),
        severity=data.get("severity", "medium"),
    )


_memory_cache: dict[str, FailureMemory] = {}


def get_failure_memory(db_path: str) -> FailureMemory:
    if db_path not in _memory_cache:
        _memory_cache[db_path] = FailureMemory(db_path)
    return _memory_cache[db_path]
