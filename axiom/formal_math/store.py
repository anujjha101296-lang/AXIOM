"""Formal mathematics store — versioned proofs and entities (FMTP §14)."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any

from axiom.formal_math.models import (
    CounterexampleRecord,
    FormalizationResult,
    MathEntity,
    ProofArtifact,
    ProofCompilationStatus,
    ProofFailureRecord,
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class FormalMathStore:
    """SQLite-backed store for formal math entities, proofs, and failures."""

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
        CREATE TABLE IF NOT EXISTS fmtp_entities (
            entity_id TEXT PRIMARY KEY,
            entity_type TEXT NOT NULL,
            json_data TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS fmtp_proofs (
            proof_id TEXT PRIMARY KEY,
            theorem_id TEXT NOT NULL,
            version INTEGER NOT NULL,
            json_data TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS fmtp_proof_versions (
            proof_id TEXT NOT NULL,
            version INTEGER NOT NULL,
            json_data TEXT NOT NULL,
            archived_at TEXT NOT NULL,
            PRIMARY KEY (proof_id, version)
        );
        CREATE TABLE IF NOT EXISTS fmtp_formalizations (
            result_id TEXT PRIMARY KEY,
            json_data TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS fmtp_counterexamples (
            counterexample_id TEXT PRIMARY KEY,
            json_data TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS fmtp_failures (
            failure_id TEXT PRIMARY KEY,
            theorem_id TEXT NOT NULL,
            json_data TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_fmtp_proofs_theorem ON fmtp_proofs(theorem_id);
        CREATE INDEX IF NOT EXISTS idx_fmtp_failures_theorem ON fmtp_failures(theorem_id);
        """)
        conn.commit()
        self._release_conn(conn)

    def register_entity(
        self,
        entity_type: str,
        name: str,
        statement: str,
        **kwargs: Any,
    ) -> MathEntity:
        now = _utc_now()
        entity = MathEntity(
            entity_id=_new_id("ent"),
            entity_type=entity_type,
            name=name,
            statement=statement,
            created_at=now,
            formal_spec=kwargs.get("formal_spec"),
            prover=kwargs.get("prover"),
            library_version=kwargs.get("library_version"),
            dependencies=kwargs.get("dependencies", []),
            assumptions=kwargs.get("assumptions", []),
            domain=kwargs.get("domain", "unknown"),
            notation=kwargs.get("notation", {}),
            metadata=kwargs.get("metadata", {}),
        )
        conn = self._conn()
        conn.execute(
            "INSERT INTO fmtp_entities (entity_id, entity_type, json_data, created_at) VALUES (?, ?, ?, ?)",
            (entity.entity_id, entity_type, json.dumps(entity.to_dict()), now),
        )
        conn.commit()
        self._release_conn(conn)
        return entity

    def get_entity(self, entity_id: str) -> MathEntity | None:
        conn = self._conn()
        row = conn.execute(
            "SELECT json_data FROM fmtp_entities WHERE entity_id = ?", (entity_id,)
        ).fetchone()
        self._release_conn(conn)
        if not row:
            return None
        return _entity_from_dict(json.loads(row["json_data"]))

    def save_proof(self, artifact: ProofArtifact) -> str:
        conn = self._conn()
        existing = conn.execute(
            "SELECT version, json_data FROM fmtp_proofs WHERE proof_id = ?",
            (artifact.proof_id,),
        ).fetchone()
        if existing:
            conn.execute(
                "INSERT OR REPLACE INTO fmtp_proof_versions (proof_id, version, json_data, archived_at) VALUES (?, ?, ?, ?)",
                (artifact.proof_id, existing["version"], existing["json_data"], _utc_now()),
            )
        conn.execute(
            """INSERT OR REPLACE INTO fmtp_proofs
               (proof_id, theorem_id, version, json_data, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (
                artifact.proof_id,
                artifact.theorem_id,
                artifact.version,
                json.dumps(artifact.to_dict()),
                artifact.created_at,
            ),
        )
        conn.commit()
        self._release_conn(conn)
        return artifact.proof_id

    def get_proof(self, proof_id: str) -> ProofArtifact | None:
        conn = self._conn()
        row = conn.execute(
            "SELECT json_data FROM fmtp_proofs WHERE proof_id = ?", (proof_id,)
        ).fetchone()
        self._release_conn(conn)
        if not row:
            return None
        return _proof_from_dict(json.loads(row["json_data"]))

    def list_proofs(self, theorem_id: str | None = None, limit: int = 50) -> list[ProofArtifact]:
        conn = self._conn()
        if theorem_id:
            rows = conn.execute(
                "SELECT json_data FROM fmtp_proofs WHERE theorem_id = ? ORDER BY created_at DESC LIMIT ?",
                (theorem_id, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT json_data FROM fmtp_proofs ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        self._release_conn(conn)
        return [_proof_from_dict(json.loads(r["json_data"])) for r in rows]

    def save_formalization(self, result: FormalizationResult) -> str:
        conn = self._conn()
        conn.execute(
            "INSERT INTO fmtp_formalizations (result_id, json_data, created_at) VALUES (?, ?, ?)",
            (result.result_id, json.dumps(result.to_dict()), result.created_at or _utc_now()),
        )
        conn.commit()
        self._release_conn(conn)
        return result.result_id

    def save_counterexample(self, record: CounterexampleRecord) -> str:
        conn = self._conn()
        conn.execute(
            "INSERT INTO fmtp_counterexamples (counterexample_id, json_data, created_at) VALUES (?, ?, ?)",
            (record.counterexample_id, json.dumps(record.to_dict()), record.created_at),
        )
        conn.commit()
        self._release_conn(conn)
        return record.counterexample_id

    def save_failure(self, record: ProofFailureRecord) -> str:
        conn = self._conn()
        conn.execute(
            "INSERT INTO fmtp_failures (failure_id, theorem_id, json_data, created_at) VALUES (?, ?, ?, ?)",
            (record.failure_id, record.theorem_id, json.dumps(record.to_dict()), record.created_at),
        )
        conn.commit()
        self._release_conn(conn)
        return record.failure_id

    def list_failures(self, theorem_id: str | None = None, limit: int = 50) -> list[ProofFailureRecord]:
        conn = self._conn()
        if theorem_id:
            rows = conn.execute(
                "SELECT json_data FROM fmtp_failures WHERE theorem_id = ? ORDER BY created_at DESC LIMIT ?",
                (theorem_id, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT json_data FROM fmtp_failures ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        self._release_conn(conn)
        return [_failure_from_dict(json.loads(r["json_data"])) for r in rows]

    def dashboard_stats(self) -> dict[str, Any]:
        conn = self._conn()
        entities = conn.execute("SELECT COUNT(*) FROM fmtp_entities").fetchone()[0]
        proofs = conn.execute("SELECT COUNT(*) FROM fmtp_proofs").fetchone()[0]
        verified = conn.execute(
            """SELECT COUNT(*) FROM fmtp_proofs
               WHERE json_data LIKE '%"compilation_status": "FORMALLY_VERIFIED"%'"""
        ).fetchone()[0]
        counterexamples = conn.execute("SELECT COUNT(*) FROM fmtp_counterexamples").fetchone()[0]
        failures = conn.execute("SELECT COUNT(*) FROM fmtp_failures").fetchone()[0]
        self._release_conn(conn)
        return {
            "entities": entities,
            "proofs": proofs,
            "formally_verified": verified,
            "counterexamples": counterexamples,
            "failures": failures,
        }


def _entity_from_dict(data: dict[str, Any]) -> MathEntity:
    return MathEntity(**{k: data[k] for k in MathEntity.__dataclass_fields__ if k in data})


def _proof_from_dict(data: dict[str, Any]) -> ProofArtifact:
    data = dict(data)
    data["compilation_status"] = ProofCompilationStatus(data["compilation_status"])
    return ProofArtifact(**{k: data[k] for k in ProofArtifact.__dataclass_fields__ if k in data})


def _failure_from_dict(data: dict[str, Any]) -> ProofFailureRecord:
    return ProofFailureRecord(**{k: data[k] for k in ProofFailureRecord.__dataclass_fields__ if k in data})


_store_cache: dict[str, FormalMathStore] = {}


def get_formal_math_store(db_path: str) -> FormalMathStore:
    if db_path not in _store_cache:
        _store_cache[db_path] = FormalMathStore(db_path)
    return _store_cache[db_path]
