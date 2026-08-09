"""Frontier Research Campaign Engine — versioned campaign store."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from typing import Any

from axiom.campaign.models import FrontierCampaign, _utc_now


class CampaignEngineStore:
    """SQLite-backed store for frontier research campaigns."""

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
        CREATE TABLE IF NOT EXISTS frce_campaigns (
            campaign_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            phase TEXT NOT NULL,
            ladder_level INTEGER NOT NULL,
            version INTEGER NOT NULL DEFAULT 1,
            json_data TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS frce_campaign_versions (
            campaign_id TEXT NOT NULL,
            version INTEGER NOT NULL,
            json_data TEXT NOT NULL,
            archived_at TEXT NOT NULL,
            PRIMARY KEY (campaign_id, version)
        );
        CREATE TABLE IF NOT EXISTS frce_global_memory (
            entry_id TEXT PRIMARY KEY,
            source_campaign_id TEXT NOT NULL,
            json_data TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_frce_phase ON frce_campaigns(phase);
        CREATE INDEX IF NOT EXISTS idx_frce_ladder ON frce_campaigns(ladder_level);
        """)
        conn.commit()
        self._release_conn(conn)

    def save(self, campaign: FrontierCampaign, *, archive_previous: bool = True) -> FrontierCampaign:
        conn = self._conn()
        row = conn.execute(
            "SELECT version, json_data FROM frce_campaigns WHERE campaign_id = ?",
            (campaign.campaign_id,),
        ).fetchone()

        version = 1
        if row and archive_previous:
            version = int(row["version"]) + 1
            conn.execute(
                """INSERT OR REPLACE INTO frce_campaign_versions
                   (campaign_id, version, json_data, archived_at)
                   VALUES (?, ?, ?, ?)""",
                (campaign.campaign_id, int(row["version"]), row["json_data"], _utc_now()),
            )
        elif row:
            version = int(row["version"])

        campaign.updated_at = _utc_now()
        payload = json.dumps(campaign.to_dict())
        conn.execute(
            """INSERT OR REPLACE INTO frce_campaigns
               (campaign_id, name, phase, ladder_level, version, json_data, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                campaign.campaign_id,
                campaign.name,
                campaign.phase.value,
                int(campaign.ladder_level),
                version,
                payload,
                campaign.created_at,
                campaign.updated_at,
            ),
        )
        conn.commit()
        self._release_conn(conn)
        return campaign

    def get(self, campaign_id: str) -> FrontierCampaign | None:
        conn = self._conn()
        row = conn.execute(
            "SELECT json_data FROM frce_campaigns WHERE campaign_id = ?",
            (campaign_id,),
        ).fetchone()
        self._release_conn(conn)
        if not row:
            return None
        return FrontierCampaign.from_dict(json.loads(row["json_data"]))

    def list_campaigns(
        self,
        *,
        phase: str | None = None,
        limit: int = 50,
    ) -> list[FrontierCampaign]:
        conn = self._conn()
        if phase:
            rows = conn.execute(
                "SELECT json_data FROM frce_campaigns WHERE phase = ? ORDER BY updated_at DESC LIMIT ?",
                (phase, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT json_data FROM frce_campaigns ORDER BY updated_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        self._release_conn(conn)
        return [FrontierCampaign.from_dict(json.loads(r["json_data"])) for r in rows]

    def save_global_memory(
        self,
        source_campaign_id: str,
        entry: dict[str, Any],
    ) -> str:
        entry_id = entry.get("entry_id", f"gmem_{source_campaign_id[:8]}")
        conn = self._conn()
        conn.execute(
            """INSERT OR REPLACE INTO frce_global_memory
               (entry_id, source_campaign_id, json_data, created_at)
               VALUES (?, ?, ?, ?)""",
            (entry_id, source_campaign_id, json.dumps(entry), _utc_now()),
        )
        conn.commit()
        self._release_conn(conn)
        return entry_id

    def list_global_memory(self, limit: int = 100) -> list[dict[str, Any]]:
        conn = self._conn()
        rows = conn.execute(
            "SELECT json_data FROM frce_global_memory ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        self._release_conn(conn)
        return [json.loads(r["json_data"]) for r in rows]


_store_cache: dict[str, CampaignEngineStore] = {}


def get_campaign_store(db_path: str) -> CampaignEngineStore:
    if db_path not in _store_cache:
        _store_cache[db_path] = CampaignEngineStore(db_path)
    return _store_cache[db_path]
