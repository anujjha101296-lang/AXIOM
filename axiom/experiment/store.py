"""Experiment store — lifecycle and artifacts (SEC §1–2, §12)."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any

from axiom.experiment.models import (
    DatasetRecord,
    Experiment,
    ExperimentFailure,
    ExperimentSpec,
    ExperimentStatus,
    can_transition,
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class ExperimentStore:
    """SQLite-backed experiment kernel store."""

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
        CREATE TABLE IF NOT EXISTS sec_experiments (
            experiment_id TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            version INTEGER NOT NULL,
            json_data TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS sec_experiment_versions (
            experiment_id TEXT NOT NULL,
            version INTEGER NOT NULL,
            json_data TEXT NOT NULL,
            archived_at TEXT NOT NULL,
            PRIMARY KEY (experiment_id, version)
        );
        CREATE TABLE IF NOT EXISTS sec_datasets (
            dataset_id TEXT PRIMARY KEY,
            version TEXT NOT NULL,
            json_data TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS sec_failures (
            failure_id TEXT PRIMARY KEY,
            experiment_id TEXT NOT NULL,
            json_data TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS sec_parameter_runs (
            run_id TEXT PRIMARY KEY,
            experiment_id TEXT NOT NULL,
            json_data TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_sec_exp_status ON sec_experiments(status);
        CREATE INDEX IF NOT EXISTS idx_sec_failures_exp ON sec_failures(experiment_id);
        """)
        conn.commit()
        self._release_conn(conn)

    def create_experiment(
        self,
        spec: ExperimentSpec,
        *,
        campaign_id: str | None = None,
        claim_id: str | None = None,
        hypothesis_id: str | None = None,
        owner_id: str | None = None,
    ) -> Experiment:
        now = _utc_now()
        experiment = Experiment(
            experiment_id=_new_id("exp"),
            status=ExperimentStatus.DRAFT,
            version=1,
            created_at=now,
            updated_at=now,
            spec=spec.to_dict(),
            campaign_id=campaign_id,
            claim_id=claim_id,
            hypothesis_id=hypothesis_id,
            owner_id=owner_id,
        )
        self._save(experiment)
        return experiment

    def _save(self, experiment: Experiment) -> None:
        conn = self._conn()
        conn.execute(
            """INSERT OR REPLACE INTO sec_experiments
               (experiment_id, status, version, json_data, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                experiment.experiment_id,
                experiment.status.value,
                experiment.version,
                json.dumps(experiment.to_dict()),
                experiment.created_at,
                experiment.updated_at,
            ),
        )
        conn.commit()
        self._release_conn(conn)

    def _archive(self, experiment: Experiment) -> None:
        conn = self._conn()
        conn.execute(
            """INSERT OR REPLACE INTO sec_experiment_versions
               (experiment_id, version, json_data, archived_at) VALUES (?, ?, ?, ?)""",
            (experiment.experiment_id, experiment.version, json.dumps(experiment.to_dict()), _utc_now()),
        )
        conn.commit()
        self._release_conn(conn)

    def get(self, experiment_id: str) -> Experiment | None:
        conn = self._conn()
        row = conn.execute(
            "SELECT json_data FROM sec_experiments WHERE experiment_id = ?", (experiment_id,)
        ).fetchone()
        self._release_conn(conn)
        if not row:
            return None
        return _experiment_from_dict(json.loads(row["json_data"]))

    def list_experiments(
        self,
        status: ExperimentStatus | None = None,
        limit: int = 50,
        *,
        owner_id: str | None = None,
    ) -> list[Experiment]:
        conn = self._conn()
        fetch_limit = limit if owner_id in (None, "dev") else max(limit * 3, 100)
        if status:
            rows = conn.execute(
                "SELECT json_data FROM sec_experiments WHERE status = ? ORDER BY updated_at DESC LIMIT ?",
                (status.value, fetch_limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT json_data FROM sec_experiments ORDER BY updated_at DESC LIMIT ?",
                (fetch_limit,),
            ).fetchall()
        self._release_conn(conn)
        experiments = [_experiment_from_dict(json.loads(r["json_data"])) for r in rows]
        if owner_id is None or owner_id == "dev":
            return experiments[:limit]
        return [e for e in experiments if e.owner_id == owner_id][:limit]

    def transition(self, experiment_id: str, new_status: ExperimentStatus) -> Experiment:
        experiment = self.get(experiment_id)
        if not experiment:
            raise KeyError(f"Experiment not found: {experiment_id}")
        old = ExperimentStatus(experiment.status)
        if not can_transition(old, new_status):
            raise ValueError(f"Invalid transition: {old.value} → {new_status.value}")

        self._archive(experiment)
        experiment.status = new_status
        experiment.version += 1
        experiment.updated_at = _utc_now()
        self._save(experiment)
        return experiment

    def update_results(
        self,
        experiment_id: str,
        results: dict[str, Any],
        *,
        artifacts: list[str] | None = None,
        environment: dict[str, Any] | None = None,
    ) -> Experiment:
        experiment = self.get(experiment_id)
        if not experiment:
            raise KeyError(f"Experiment not found: {experiment_id}")
        self._archive(experiment)
        experiment.results = results
        if artifacts:
            experiment.artifacts.extend(artifacts)
        if environment:
            experiment.environment = environment
        experiment.version += 1
        experiment.updated_at = _utc_now()
        self._save(experiment)
        return experiment

    def save_failure(self, failure: ExperimentFailure) -> str:
        conn = self._conn()
        conn.execute(
            "INSERT INTO sec_failures (failure_id, experiment_id, json_data, created_at) VALUES (?, ?, ?, ?)",
            (failure.failure_id, failure.experiment_id, json.dumps(failure.to_dict()), failure.created_at),
        )
        conn.commit()
        self._release_conn(conn)
        return failure.failure_id

    def register_dataset(self, record: DatasetRecord) -> str:
        conn = self._conn()
        conn.execute(
            "INSERT OR REPLACE INTO sec_datasets (dataset_id, version, json_data, created_at) VALUES (?, ?, ?, ?)",
            (record.dataset_id, record.version, json.dumps(record.to_dict()), record.created_at),
        )
        conn.commit()
        self._release_conn(conn)
        return record.dataset_id

    def get_dataset(self, dataset_id: str, version: str | None = None) -> DatasetRecord | None:
        conn = self._conn()
        if version:
            row = conn.execute(
                "SELECT json_data FROM sec_datasets WHERE dataset_id = ? AND version = ?",
                (dataset_id, version),
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT json_data FROM sec_datasets WHERE dataset_id = ? ORDER BY created_at DESC LIMIT 1",
                (dataset_id,),
            ).fetchone()
        self._release_conn(conn)
        if not row:
            return None
        return _dataset_from_dict(json.loads(row["json_data"]))

    def record_parameter_run(self, experiment_id: str, config: dict[str, Any], result: dict[str, Any]) -> str:
        run_id = _new_id("prm")
        now = _utc_now()
        conn = self._conn()
        conn.execute(
            "INSERT INTO sec_parameter_runs (run_id, experiment_id, json_data, created_at) VALUES (?, ?, ?, ?)",
            (run_id, experiment_id, json.dumps({"config": config, "result": result}), now),
        )
        conn.commit()
        self._release_conn(conn)
        return run_id

    def dashboard_stats(self) -> dict[str, Any]:
        conn = self._conn()
        total = conn.execute("SELECT COUNT(*) FROM sec_experiments").fetchone()[0]
        by_status = {
            row[0]: row[1]
            for row in conn.execute(
                "SELECT status, COUNT(*) FROM sec_experiments GROUP BY status"
            ).fetchall()
        }
        failures = conn.execute("SELECT COUNT(*) FROM sec_failures").fetchone()[0]
        datasets = conn.execute("SELECT COUNT(*) FROM sec_datasets").fetchone()[0]
        self._release_conn(conn)
        return {
            "total_experiments": total,
            "by_status": by_status,
            "failures": failures,
            "datasets": datasets,
            "active": by_status.get(ExperimentStatus.RUNNING.value, 0),
            "queued": by_status.get(ExperimentStatus.QUEUED.value, 0),
        }


def _experiment_from_dict(data: dict[str, Any]) -> Experiment:
    data = dict(data)
    data["status"] = ExperimentStatus(data["status"])
    return Experiment(**{k: data[k] for k in Experiment.__dataclass_fields__ if k in data})


def _dataset_from_dict(data: dict[str, Any]) -> DatasetRecord:
    return DatasetRecord(**{k: data[k] for k in DatasetRecord.__dataclass_fields__ if k in data})


_store_cache: dict[str, ExperimentStore] = {}


def get_experiment_store(db_path: str) -> ExperimentStore:
    if db_path not in _store_cache:
        _store_cache[db_path] = ExperimentStore(db_path)
    return _store_cache[db_path]
