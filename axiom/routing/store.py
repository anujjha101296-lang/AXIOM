"""Routing decision store and cost tracking (SIMR §15, §18)."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any

from axiom.routing.models import RoutingDecision


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class RoutingStore:
    """Persist routing decisions for audit and adaptive learning."""

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
        CREATE TABLE IF NOT EXISTS simr_decisions (
            decision_id TEXT PRIMARY KEY,
            problem_id TEXT NOT NULL,
            selected_model TEXT NOT NULL,
            json_data TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS simr_costs (
            cost_id TEXT PRIMARY KEY,
            decision_id TEXT,
            campaign_id TEXT,
            json_data TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_simr_decisions_model ON simr_decisions(selected_model);
        """)
        conn.commit()
        self._release_conn(conn)

    def save_decision(self, decision: RoutingDecision) -> str:
        conn = self._conn()
        conn.execute(
            """INSERT OR REPLACE INTO simr_decisions
               (decision_id, problem_id, selected_model, json_data, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (
                decision.decision_id,
                decision.problem_id,
                decision.selected_model,
                json.dumps(decision.to_dict()),
                decision.created_at,
            ),
        )
        conn.commit()
        self._release_conn(conn)
        return decision.decision_id

    def get_decision(self, decision_id: str) -> RoutingDecision | None:
        conn = self._conn()
        row = conn.execute(
            "SELECT json_data FROM simr_decisions WHERE decision_id = ?", (decision_id,)
        ).fetchone()
        self._release_conn(conn)
        if not row:
            return None
        return _decision_from_dict(json.loads(row["json_data"]))

    def list_decisions(self, limit: int = 50) -> list[RoutingDecision]:
        conn = self._conn()
        rows = conn.execute(
            "SELECT json_data FROM simr_decisions ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
        self._release_conn(conn)
        return [_decision_from_dict(json.loads(r["json_data"])) for r in rows]

    def record_cost(
        self,
        *,
        decision_id: str | None = None,
        campaign_id: str | None = None,
        tokens: int = 0,
        model_calls: int = 0,
        tool_calls: int = 0,
        compute_seconds: float = 0.0,
        estimated_usd: float = 0.0,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        record = {
            "cost_id": f"cst_{uuid.uuid4().hex[:12]}",
            "decision_id": decision_id,
            "campaign_id": campaign_id,
            "tokens": tokens,
            "model_calls": model_calls,
            "tool_calls": tool_calls,
            "compute_seconds": compute_seconds,
            "estimated_usd": estimated_usd,
            "metadata": metadata or {},
            "created_at": _utc_now(),
        }
        conn = self._conn()
        conn.execute(
            "INSERT INTO simr_costs (cost_id, decision_id, campaign_id, json_data, created_at) VALUES (?, ?, ?, ?, ?)",
            (record["cost_id"], decision_id, campaign_id, json.dumps(record), record["created_at"]),
        )
        conn.commit()
        self._release_conn(conn)
        return record

    def dashboard_stats(self) -> dict[str, Any]:
        conn = self._conn()
        total = conn.execute("SELECT COUNT(*) FROM simr_decisions").fetchone()[0]
        by_model = {
            row[0]: row[1]
            for row in conn.execute(
                "SELECT selected_model, COUNT(*) FROM simr_decisions GROUP BY selected_model"
            ).fetchall()
        }
        total_cost = conn.execute(
            "SELECT COALESCE(SUM(json_extract(json_data, '$.estimated_usd')), 0) FROM simr_costs"
        ).fetchone()[0]
        human_review = conn.execute(
            """SELECT COUNT(*) FROM simr_decisions
               WHERE json_data LIKE '%"requires_human_review": true%'"""
        ).fetchone()[0]
        self._release_conn(conn)
        return {
            "total_decisions": total,
            "by_model": by_model,
            "total_estimated_cost_usd": round(float(total_cost or 0), 4),
            "human_review_triggered": human_review,
        }


def _decision_from_dict(data: dict[str, Any]) -> RoutingDecision:
    return RoutingDecision(
        decision_id=data["decision_id"],
        problem_id=data["problem_id"],
        created_at=data["created_at"],
        profile=data["profile"],
        selected_model=data["selected_model"],
        selected_tools=data["selected_tools"],
        selected_strategy=data["selected_strategy"],
        rationale=data["rationale"],
        verification_plan=data.get("verification_plan", []),
        fallback_model=data.get("fallback_model"),
        cost_estimate=data.get("cost_estimate", 0.0),
        requires_human_review=data.get("requires_human_review", False),
        model_version=data.get("model_version", ""),
        metadata=data.get("metadata", {}),
    )


_store_cache: dict[str, RoutingStore] = {}


def get_routing_store(db_path: str) -> RoutingStore:
    if db_path not in _store_cache:
        _store_cache[db_path] = RoutingStore(db_path)
    return _store_cache[db_path]
