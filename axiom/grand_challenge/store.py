"""SQLite persistence for Grand Challenge campaigns."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from axiom.grand_challenge.models import Campaign


class CampaignStore:
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
        CREATE TABLE IF NOT EXISTS gcp_campaigns (
            campaign_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            current_tier INTEGER NOT NULL,
            status TEXT NOT NULL,
            json_data TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_gcp_campaigns_status ON gcp_campaigns(status);
        CREATE INDEX IF NOT EXISTS idx_gcp_campaigns_tier ON gcp_campaigns(current_tier);
        """)
        conn.commit()

    def save(self, campaign: Campaign) -> None:
        conn = self._get_conn()
        conn.execute(
            """INSERT OR REPLACE INTO gcp_campaigns
               (campaign_id, name, current_tier, status, json_data, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                campaign.campaign_id,
                campaign.name,
                int(campaign.current_tier),
                campaign.status.value,
                json.dumps(campaign.model_dump(mode="json")),
                campaign.created_at.isoformat(),
                campaign.updated_at.isoformat(),
            ),
        )
        conn.commit()

    def get(self, campaign_id: str) -> Campaign | None:
        conn = self._get_conn()
        row = conn.execute(
            "SELECT json_data FROM gcp_campaigns WHERE campaign_id = ?", (campaign_id,)
        ).fetchone()
        if not row:
            return None
        return Campaign.model_validate(json.loads(row["json_data"]))

    def list_campaigns(self, limit: int = 50, status: str | None = None) -> list[Campaign]:
        conn = self._get_conn()
        if status:
            rows = conn.execute(
                "SELECT json_data FROM gcp_campaigns WHERE status = ? ORDER BY updated_at DESC LIMIT ?",
                (status, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT json_data FROM gcp_campaigns ORDER BY updated_at DESC LIMIT ?", (limit,)
            ).fetchall()
        return [Campaign.model_validate(json.loads(r["json_data"])) for r in rows]
