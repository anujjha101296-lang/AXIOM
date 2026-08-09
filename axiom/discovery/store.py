"""Persistent store for Discovery objects."""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from axiom.discovery.models import Discovery, _utc_now


class DiscoveryStore:
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

    def _release(self, conn: sqlite3.Connection) -> None:
        if conn is not self._persistent_conn:
            conn.close()

    def _ensure_schema(self) -> None:
        conn = self._conn()
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS discovery_records (
                discovery_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                owner_id TEXT,
                campaign_id TEXT,
                json_data TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_discovery_status ON discovery_records(status);
            CREATE INDEX IF NOT EXISTS idx_discovery_owner ON discovery_records(owner_id);
            CREATE TABLE IF NOT EXISTS discovery_memory (
                entry_id TEXT PRIMARY KEY,
                kind TEXT NOT NULL,
                content TEXT NOT NULL,
                discovery_id TEXT,
                created_at TEXT NOT NULL
            );
            """
        )
        conn.commit()
        self._release(conn)

    def save(self, discovery: Discovery) -> Discovery:
        discovery.updated_at = _utc_now()
        conn = self._conn()
        conn.execute(
            """INSERT OR REPLACE INTO discovery_records
               (discovery_id, status, owner_id, campaign_id, json_data, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                discovery.discovery_id,
                discovery.status.value,
                discovery.owner_id,
                discovery.campaign_id,
                json.dumps(discovery.to_dict()),
                discovery.created_at,
                discovery.updated_at,
            ),
        )
        conn.commit()
        self._release(conn)
        return discovery

    def get(self, discovery_id: str) -> Discovery | None:
        conn = self._conn()
        row = conn.execute(
            "SELECT json_data FROM discovery_records WHERE discovery_id = ?",
            (discovery_id,),
        ).fetchone()
        self._release(conn)
        if not row:
            return None
        return Discovery.from_dict(json.loads(row["json_data"]))

    def list(
        self,
        *,
        status: str | None = None,
        owner_id: str | None = None,
        limit: int = 50,
    ) -> list[Discovery]:
        conn = self._conn()
        fetch = max(limit * 3, 100) if owner_id not in (None, "dev") else limit
        if status:
            rows = conn.execute(
                "SELECT json_data FROM discovery_records WHERE status = ? ORDER BY updated_at DESC LIMIT ?",
                (status, fetch),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT json_data FROM discovery_records ORDER BY updated_at DESC LIMIT ?",
                (fetch,),
            ).fetchall()
        self._release(conn)
        items = [Discovery.from_dict(json.loads(r["json_data"])) for r in rows]
        if owner_id is None or owner_id == "dev":
            return items[:limit]
        return [d for d in items if d.owner_id == owner_id][:limit]

    def save_memory(self, kind: str, content: str, *, discovery_id: str | None = None) -> str:
        import uuid

        entry_id = f"dmem_{uuid.uuid4().hex[:12]}"
        conn = self._conn()
        conn.execute(
            """INSERT INTO discovery_memory (entry_id, kind, content, discovery_id, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (entry_id, kind, content, discovery_id, _utc_now()),
        )
        conn.commit()
        self._release(conn)
        return entry_id

    def list_memory(
        self,
        *,
        kind: str | None = None,
        discovery_id: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        conn = self._conn()
        if kind and discovery_id:
            rows = conn.execute(
                """SELECT * FROM discovery_memory
                   WHERE kind = ? AND discovery_id = ?
                   ORDER BY created_at DESC LIMIT ?""",
                (kind, discovery_id, limit),
            ).fetchall()
        elif discovery_id:
            rows = conn.execute(
                """SELECT * FROM discovery_memory
                   WHERE discovery_id = ?
                   ORDER BY created_at DESC LIMIT ?""",
                (discovery_id, limit),
            ).fetchall()
        elif kind:
            rows = conn.execute(
                "SELECT * FROM discovery_memory WHERE kind = ? ORDER BY created_at DESC LIMIT ?",
                (kind, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM discovery_memory ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        self._release(conn)
        return [dict(r) for r in rows]


_cache: dict[str, DiscoveryStore] = {}


def get_discovery_store(db_path: str) -> DiscoveryStore:
    if db_path not in _cache:
        _cache[db_path] = DiscoveryStore(db_path)
    return _cache[db_path]
