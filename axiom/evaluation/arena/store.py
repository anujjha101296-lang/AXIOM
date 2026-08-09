"""Arena run persistence + regression comparison."""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from axiom.evaluation.arena.models import ArenaRun, CaseResult, DimensionScores, _utc_now


class ArenaStore:
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
                CREATE TABLE IF NOT EXISTS arena_runs (
                    run_id TEXT PRIMARY KEY,
                    dataset_version TEXT NOT NULL,
                    git_commit TEXT,
                    is_baseline INTEGER DEFAULT 0,
                    started_at TEXT,
                    ended_at TEXT,
                    mean_score REAL,
                    json_data TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS arena_results (
                    run_id TEXT NOT NULL,
                    benchmark_id TEXT NOT NULL,
                    score REAL NOT NULL,
                    passed INTEGER NOT NULL,
                    time_ms REAL NOT NULL,
                    notes TEXT,
                    PRIMARY KEY (run_id, benchmark_id)
                )
                """
            )
            conn.commit()

    def save_run(self, run: ArenaRun) -> ArenaRun:
        summary = run.to_dict()["summary"]
        with self._conn() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO arena_runs
                (run_id, dataset_version, git_commit, is_baseline, started_at, ended_at, mean_score, json_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run.run_id,
                    run.dataset_version,
                    run.git_commit,
                    1 if run.is_baseline else 0,
                    run.started_at,
                    run.ended_at or _utc_now(),
                    summary["mean_score"],
                    json.dumps(run.to_dict()),
                ),
            )
            for r in run.results:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO arena_results
                    (run_id, benchmark_id, score, passed, time_ms, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (run.run_id, r.benchmark_id, r.score, 1 if r.passed else 0, r.time_ms, r.notes),
                )
            conn.commit()
        return run

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT json_data FROM arena_runs WHERE run_id = ?", (run_id,)
            ).fetchone()
        return json.loads(row["json_data"]) if row else None

    def list_runs(self, limit: int = 20) -> list[dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute(
                """
                SELECT run_id, dataset_version, git_commit, is_baseline, started_at, ended_at, mean_score
                FROM arena_runs ORDER BY started_at DESC LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(r) for r in rows]

    def latest_run(self) -> dict[str, Any] | None:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT json_data FROM arena_runs ORDER BY started_at DESC LIMIT 1"
            ).fetchone()
        return json.loads(row["json_data"]) if row else None

    def baseline_run(self) -> dict[str, Any] | None:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT json_data FROM arena_runs WHERE is_baseline=1 ORDER BY started_at ASC LIMIT 1"
            ).fetchone()
        return json.loads(row["json_data"]) if row else None


def compare_runs(previous: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    """Detect regressions across dimension scores and per-case pass flips."""
    prev_dims = previous.get("dimension_scores", {})
    curr_dims = current.get("dimension_scores", {})
    regressions: list[dict[str, Any]] = []
    improvements: list[dict[str, Any]] = []

    rate_keys = {
        "false_discovery_rate",
        "false_confidence_rate",
        "hallucination_rate",
        "unsupported_claim_rate",
    }
    for key in sorted(set(prev_dims) | set(curr_dims)):
        pv = float(prev_dims.get(key, 0.0))
        cv = float(curr_dims.get(key, 0.0))
        delta = cv - pv
        if key in rate_keys:
            if delta > 0.05:
                regressions.append({"metric": key, "previous": pv, "current": cv, "delta": round(delta, 4)})
            elif delta < -0.05:
                improvements.append({"metric": key, "previous": pv, "current": cv, "delta": round(delta, 4)})
        else:
            if delta < -0.05:
                regressions.append({"metric": key, "previous": pv, "current": cv, "delta": round(delta, 4)})
            elif delta > 0.05:
                improvements.append({"metric": key, "previous": pv, "current": cv, "delta": round(delta, 4)})

    prev_pass = {r["benchmark_id"]: r["passed"] for r in previous.get("results", [])}
    flips = []
    for r in current.get("results", []):
        bid = r["benchmark_id"]
        if bid in prev_pass and prev_pass[bid] and not r["passed"]:
            flips.append(bid)

    return {
        "regressions": regressions,
        "improvements": improvements,
        "case_regressions": flips,
        "significant_regression": bool(regressions) or bool(flips),
        "previous_run_id": previous.get("run_id"),
        "current_run_id": current.get("run_id"),
        "mean_score_delta": round(
            float(current.get("summary", {}).get("mean_score", 0))
            - float(previous.get("summary", {}).get("mean_score", 0)),
            4,
        ),
    }
