"""
H1-OBS — Unified run provenance records for SCEP (EPIC-002).

Every scientific evaluation run records inputs, runtime, configuration, environment,
and evidence tier in a queryable `run_provenance` table. Provenance is additive and
does not duplicate score payloads in `eval_runs`.
"""

from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal

from axiom.config import settings
from axiom.evaluation.frameworks.capability import CapabilitySnapshot, EvidenceState

RunType = Literal["scep", "rvp"]


@dataclass
class RunProvenance:
    """Auditable envelope for a single SCEP or RVP run."""

    run_id: str
    run_type: RunType
    started_at: str
    finished_at: str
    duration_ms: float
    config_hash: str | None
    inputs: dict[str, Any]
    environment: dict[str, Any]
    evidence_tier: dict[str, Any]
    runtime: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def capture_environment() -> dict[str, Any]:
    """Capture runtime environment fingerprint for reproducibility audits."""
    env: dict[str, Any] = {
        "python_version": sys.version.split()[0],
        "platform": sys.platform,
        "app_version": settings.app_version,
        "deployment_environment": settings.environment,
    }
    try:
        repo_root = Path(__file__).resolve().parents[2]
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=2,
            cwd=repo_root,
        )
        if result.returncode == 0:
            env["git_sha"] = result.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return env


def build_scep_provenance(
    *,
    snapshot: CapabilitySnapshot,
    db_path: str,
    started_at: str,
    finished_at: str,
    duration_ms: float,
    benchmark_case_count: int,
    total_benchmark_ms: float | None = None,
    trigger: str = "api",
) -> RunProvenance:
    """Build provenance envelope for an EPIC-002 SCEP benchmark run."""
    evidence_tier = snapshot.evidence_tier or {
        "aggregate": EvidenceState.BASELINE.value,
        "dimensions": {},
    }
    return RunProvenance(
        run_id=snapshot.run_id,
        run_type="scep",
        started_at=started_at,
        finished_at=finished_at,
        duration_ms=round(duration_ms, 3),
        config_hash=None,
        inputs={
            "db_path": db_path,
            "benchmark_suite": "EPIC-002",
            "trigger": trigger,
            "benchmark_case_count": benchmark_case_count,
            "composite_score": snapshot.composite_score,
        },
        environment=capture_environment(),
        evidence_tier=evidence_tier,
        runtime={
            "total_benchmark_ms": round(total_benchmark_ms, 3) if total_benchmark_ms is not None else None,
            "timestamp": snapshot.timestamp,
        },
    )


def build_rvp_provenance(
    *,
    run_id: str,
    config_hash: str,
    config: dict[str, Any],
    started_at: str,
    finished_at: str,
    duration_ms: float,
    stage: int,
    problem_id: str,
    answer_score: float,
    passed: bool,
    verification_invoked: bool = False,
) -> RunProvenance:
    """Build provenance envelope for a single RVP validation run."""
    return RunProvenance(
        run_id=run_id,
        run_type="rvp",
        started_at=started_at,
        finished_at=finished_at,
        duration_ms=round(duration_ms, 3),
        config_hash=config_hash,
        inputs={
            "stage": stage,
            "problem_id": problem_id,
            "config": config,
            "answer_score": answer_score,
            "passed": passed,
        },
        environment=capture_environment(),
        evidence_tier={
            "aggregate": EvidenceState.MEASURED.value,
            "verification_invoked": verification_invoked,
            "method": "heuristic_scoring",
        },
        runtime={"latency_ms": round(duration_ms, 3)},
    )


class ProvenanceStore:
    """SQLite persistence for cross-system run provenance."""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
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
        CREATE TABLE IF NOT EXISTS run_provenance (
            run_type TEXT NOT NULL,
            run_id TEXT NOT NULL,
            config_hash TEXT,
            started_at TEXT NOT NULL,
            finished_at TEXT NOT NULL,
            duration_ms REAL NOT NULL,
            json_data TEXT NOT NULL,
            PRIMARY KEY (run_type, run_id)
        );
        CREATE INDEX IF NOT EXISTS idx_run_provenance_type ON run_provenance(run_type);
        CREATE INDEX IF NOT EXISTS idx_run_provenance_started ON run_provenance(started_at);
        CREATE INDEX IF NOT EXISTS idx_run_provenance_config_hash ON run_provenance(config_hash);
        """)
        conn.commit()

    def save(self, record: RunProvenance) -> None:
        payload = record.to_dict()
        conn = self._get_conn()
        conn.execute(
            """INSERT OR REPLACE INTO run_provenance
               (run_type, run_id, config_hash, started_at, finished_at, duration_ms, json_data)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                record.run_type,
                record.run_id,
                record.config_hash,
                record.started_at,
                record.finished_at,
                record.duration_ms,
                json.dumps(payload),
            ),
        )
        conn.commit()

    def get(self, run_type: RunType, run_id: str) -> dict[str, Any] | None:
        conn = self._get_conn()
        row = conn.execute(
            "SELECT json_data FROM run_provenance WHERE run_type = ? AND run_id = ?",
            (run_type, run_id),
        ).fetchone()
        return json.loads(row["json_data"]) if row else None

    def list_runs(
        self,
        run_type: RunType | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        conn = self._get_conn()
        if run_type:
            rows = conn.execute(
                """SELECT json_data FROM run_provenance
                   WHERE run_type = ? ORDER BY started_at DESC LIMIT ?""",
                (run_type, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT json_data FROM run_provenance ORDER BY started_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [json.loads(r["json_data"]) for r in rows]


_store_cache: dict[str, ProvenanceStore] = {}


def get_provenance_store(db_path: str) -> ProvenanceStore:
    """Return a cached store per database path (required for :memory: in tests)."""
    if db_path not in _store_cache:
        _store_cache[db_path] = ProvenanceStore(db_path)
    return _store_cache[db_path]


def record_scep_run(
    db_path: str,
    snapshot: CapabilitySnapshot,
    benchmark_results: list[Any],
    *,
    started_at: str | None = None,
    duration_ms: float | None = None,
    trigger: str = "api",
) -> RunProvenance:
    """Persist SCEP provenance after a benchmark run completes."""
    finished_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    if started_at is None:
        started_at = finished_at

    total_benchmark_ms = sum(getattr(r, "time_ms", 0.0) for r in benchmark_results)

    record = build_scep_provenance(
        snapshot=snapshot,
        db_path=db_path,
        started_at=started_at,
        finished_at=finished_at,
        duration_ms=duration_ms if duration_ms is not None else total_benchmark_ms,
        benchmark_case_count=len(benchmark_results),
        total_benchmark_ms=total_benchmark_ms,
        trigger=trigger,
    )
    get_provenance_store(db_path).save(record)
    return record


def record_rvp_run(
    db_path: str,
    *,
    run_id: str,
    config_hash: str,
    config: dict[str, Any],
    started_at: str,
    finished_at: str,
    duration_ms: float,
    stage: int,
    problem_id: str,
    answer_score: float,
    passed: bool,
    verification_invoked: bool = False,
) -> RunProvenance:
    """Persist RVP provenance for a single validation run."""
    record = build_rvp_provenance(
        run_id=run_id,
        config_hash=config_hash,
        config=config,
        started_at=started_at,
        finished_at=finished_at,
        duration_ms=duration_ms,
        stage=stage,
        problem_id=problem_id,
        answer_score=answer_score,
        passed=passed,
        verification_invoked=verification_invoked,
    )
    get_provenance_store(db_path).save(record)
    return record
