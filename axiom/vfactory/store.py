"""Verification Factory store — registry, runs, evidence."""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from axiom.vfactory.models import (
    CapabilityRecord,
    JourneyResult,
    TestLevel,
    TestRunResult,
    VerificationRun,
    _utc_now,
)


class VFactoryStore:
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
        CREATE TABLE IF NOT EXISTS vf_capabilities (
            capability_id TEXT PRIMARY KEY,
            domain TEXT NOT NULL,
            status TEXT NOT NULL,
            json_data TEXT NOT NULL,
            last_verified TEXT,
            last_failed TEXT,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS vf_test_runs (
            run_id TEXT PRIMARY KEY,
            level INTEGER NOT NULL,
            test_name TEXT NOT NULL,
            passed INTEGER NOT NULL,
            json_data TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS vf_journey_runs (
            journey_id TEXT PRIMARY KEY,
            journey_name TEXT NOT NULL,
            passed INTEGER NOT NULL,
            json_data TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS vf_verification_runs (
            verification_run_id TEXT PRIMARY KEY,
            overall_passed INTEGER NOT NULL,
            json_data TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS vf_regressions (
            regression_id TEXT PRIMARY KEY,
            capability_id TEXT,
            description TEXT NOT NULL,
            root_cause TEXT,
            fix TEXT,
            regression_test TEXT,
            json_data TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_vf_cap_domain ON vf_capabilities(domain);
        CREATE INDEX IF NOT EXISTS idx_vf_cap_status ON vf_capabilities(status);
        """)
        conn.commit()
        self._release_conn(conn)

    def save_capability(self, cap: CapabilityRecord) -> CapabilityRecord:
        conn = self._conn()
        now = _utc_now()
        conn.execute(
            """INSERT OR REPLACE INTO vf_capabilities
               (capability_id, domain, status, json_data, last_verified, last_failed, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (cap.capability_id, cap.domain, cap.status.value, json.dumps(cap.to_dict()),
             cap.last_verified, cap.last_failed, now),
        )
        conn.commit()
        self._release_conn(conn)
        return cap

    def get_capability(self, capability_id: str) -> CapabilityRecord | None:
        conn = self._conn()
        row = conn.execute(
            "SELECT json_data FROM vf_capabilities WHERE capability_id = ?", (capability_id,)
        ).fetchone()
        self._release_conn(conn)
        return CapabilityRecord.from_dict(json.loads(row["json_data"])) if row else None

    def list_capabilities(self, domain: str | None = None, status: str | None = None) -> list[CapabilityRecord]:
        conn = self._conn()
        query = "SELECT json_data FROM vf_capabilities WHERE 1=1"
        params: list[Any] = []
        if domain:
            query += " AND domain = ?"
            params.append(domain)
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY capability_id"
        rows = conn.execute(query, params).fetchall()
        self._release_conn(conn)
        return [CapabilityRecord.from_dict(json.loads(r["json_data"])) for r in rows]

    def save_test_run(self, result: TestRunResult) -> None:
        conn = self._conn()
        conn.execute(
            """INSERT OR REPLACE INTO vf_test_runs
               (run_id, level, test_name, passed, json_data, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (result.run_id, int(result.level), result.test_name,
             1 if result.passed else 0, json.dumps(result.to_dict()), result.created_at),
        )
        conn.commit()
        self._release_conn(conn)

    def save_journey(self, result: JourneyResult) -> None:
        conn = self._conn()
        conn.execute(
            """INSERT OR REPLACE INTO vf_journey_runs
               (journey_id, journey_name, passed, json_data, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (result.journey_id, result.journey_name, 1 if result.passed else 0,
             json.dumps(result.to_dict()), result.created_at),
        )
        conn.commit()
        self._release_conn(conn)

    def save_verification_run(self, run: VerificationRun) -> None:
        conn = self._conn()
        conn.execute(
            """INSERT OR REPLACE INTO vf_verification_runs
               (verification_run_id, overall_passed, json_data, created_at)
               VALUES (?, ?, ?, ?)""",
            (run.verification_run_id, 1 if run.overall_passed else 0,
             json.dumps(run.to_dict()), run.created_at),
        )
        conn.commit()
        self._release_conn(conn)

    def get_latest_verification_run(self) -> VerificationRun | None:
        conn = self._conn()
        row = conn.execute(
            "SELECT json_data FROM vf_verification_runs ORDER BY created_at DESC LIMIT 1"
        ).fetchone()
        self._release_conn(conn)
        if not row:
            return None
        data = json.loads(row["json_data"])
        return VerificationRun(**{k: data[k] for k in VerificationRun.__dataclass_fields__ if k in data})

    def get_verification_run(self, verification_run_id: str) -> VerificationRun | None:
        conn = self._conn()
        row = conn.execute(
            "SELECT json_data FROM vf_verification_runs WHERE verification_run_id = ?",
            (verification_run_id,),
        ).fetchone()
        self._release_conn(conn)
        if not row:
            return None
        data = json.loads(row["json_data"])
        return VerificationRun(**{k: data[k] for k in VerificationRun.__dataclass_fields__ if k in data})

    def list_verification_runs(self, limit: int = 20) -> list[VerificationRun]:
        conn = self._conn()
        rows = conn.execute(
            "SELECT json_data FROM vf_verification_runs ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        self._release_conn(conn)
        runs: list[VerificationRun] = []
        for row in rows:
            data = json.loads(row["json_data"])
            runs.append(
                VerificationRun(**{k: data[k] for k in VerificationRun.__dataclass_fields__ if k in data})
            )
        return runs

    def list_test_runs(self, limit: int = 100) -> list[TestRunResult]:
        conn = self._conn()
        rows = conn.execute(
            "SELECT json_data FROM vf_test_runs ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
        self._release_conn(conn)
        results = []
        for r in rows:
            d = json.loads(r["json_data"])
            results.append(TestRunResult(
                run_id=d["run_id"],
                level=TestLevel(d["level"]),
                test_name=d["test_name"],
                passed=d["passed"],
                duration_seconds=d["duration_seconds"],
                output=d.get("output", ""),
                error=d.get("error", ""),
                commit=d.get("commit"),
                environment=d.get("environment", "local"),
                created_at=d.get("created_at", _utc_now()),
            ))
        return results

    def record_regression(
        self,
        regression_id: str,
        capability_id: str | None,
        description: str,
        *,
        root_cause: str = "",
        fix: str = "",
        regression_test: str = "",
    ) -> None:
        conn = self._conn()
        conn.execute(
            """INSERT OR REPLACE INTO vf_regressions
               (regression_id, capability_id, description, root_cause, fix, regression_test, json_data, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (regression_id, capability_id, description, root_cause, fix, regression_test,
             json.dumps({"description": description}), _utc_now()),
        )
        conn.commit()
        self._release_conn(conn)


_store_cache: dict[str, VFactoryStore] = {}


def get_vfactory_store(db_path: str) -> VFactoryStore:
    if db_path not in _store_cache:
        _store_cache[db_path] = VFactoryStore(db_path)
    return _store_cache[db_path]
