"""Persistence for autonomous research loop runs."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any, List, Optional

from axiom.research_loop.migrations import ensure_research_loop_schema
from axiom.research_loop.schema import (
    BenchmarkScore,
    ResearchRunConfig,
    ResearchRunStatus,
    ResearchState,
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ResearchLoopStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        ensure_research_loop_schema(self.conn)

    def close(self) -> None:
        if self.conn:
            self.conn.close()

    def create_run(
        self,
        research_question: str,
        workflow_id: str,
        config: ResearchRunConfig,
        state: ResearchState,
    ) -> ResearchState:
        now = _utc_now()
        self.conn.execute(
            """
            INSERT INTO research_loop_runs
            (id, workflow_id, research_question, status, config_json, state_json,
             benchmark_id, project_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                state.run_id,
                workflow_id,
                research_question,
                ResearchRunStatus.PENDING.value,
                config.model_dump_json(),
                state.model_dump_json(),
                config.benchmark_id,
                config.project_id,
                now,
            ),
        )
        self.conn.commit()
        return state

    def update_state(
        self,
        run_id: str,
        state: ResearchState,
        status: Optional[ResearchRunStatus] = None,
    ) -> None:
        fields = ["state_json = ?"]
        values: list[Any] = [state.model_dump_json()]
        if status:
            fields.append("status = ?")
            values.append(status.value)
        values.append(run_id)
        self.conn.execute(
            f"UPDATE research_loop_runs SET {', '.join(fields)} WHERE id = ?",
            values,
        )
        self.conn.commit()

    def set_status(self, run_id: str, status: ResearchRunStatus, error: str = "") -> None:
        now = _utc_now()
        if status in (ResearchRunStatus.COMPLETED, ResearchRunStatus.FAILED, ResearchRunStatus.CANCELLED):
            self.conn.execute(
                "UPDATE research_loop_runs SET status = ?, error = ?, completed_at = ? WHERE id = ?",
                (status.value, error or None, now, run_id),
            )
        elif status == ResearchRunStatus.RUNNING:
            self.conn.execute(
                "UPDATE research_loop_runs SET status = ?, started_at = COALESCE(started_at, ?) WHERE id = ?",
                (status.value, now, run_id),
            )
        else:
            self.conn.execute(
                "UPDATE research_loop_runs SET status = ?, error = ? WHERE id = ?",
                (status.value, error or None, run_id),
            )
        self.conn.commit()

    def get_state(self, run_id: str) -> Optional[ResearchState]:
        row = self.conn.execute(
            "SELECT state_json FROM research_loop_runs WHERE id = ?", (run_id,)
        ).fetchone()
        if not row:
            return None
        return ResearchState.model_validate_json(row["state_json"])

    def get_run_row(self, run_id: str) -> Optional[sqlite3.Row]:
        return self.conn.execute(
            "SELECT * FROM research_loop_runs WHERE id = ?", (run_id,)
        ).fetchone()

    def list_runs(self, limit: int = 50) -> List[dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT id, workflow_id, research_question, status, benchmark_id, created_at, completed_at "
            "FROM research_loop_runs ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]

    def save_benchmark_score(self, score: BenchmarkScore) -> str:
        score_id = str(uuid.uuid4())
        self.conn.execute(
            """
            INSERT INTO research_loop_benchmark_scores (id, benchmark_id, run_id, score_json, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (score_id, score.benchmark_id, score.run_id, score.model_dump_json(), _utc_now()),
        )
        self.conn.commit()
        return score_id

    def get_config(self, run_id: str) -> ResearchRunConfig:
        row = self.conn.execute(
            "SELECT config_json FROM research_loop_runs WHERE id = ?", (run_id,)
        ).fetchone()
        if not row:
            return ResearchRunConfig()
        return ResearchRunConfig.model_validate_json(row["config_json"])
