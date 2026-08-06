"""
AXIOM Workflow Engine — Versioned Artifact Store
=================================================
Every worker produces typed, versioned artifacts.
Stored in SQLite; queryable by workflow, task, and type.
"""
from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from .models import Artifact, ArtifactType

logger = logging.getLogger(__name__)

_DEFAULT_DB = Path(__file__).parent.parent.parent / "axiom.db"


class ArtifactStore:
    """
    Versioned artifact store backed by SQLite.

    Every update to an existing artifact creates a new version.
    Queries always return the latest version unless version= is specified.
    """

    def __init__(self, db_path: str | Path = _DEFAULT_DB) -> None:
        self.db_path = Path(db_path)
        self._ensure_schema()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _ensure_schema(self) -> None:
        with self._conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS artifacts (
                    id           TEXT NOT NULL,
                    task_id      TEXT NOT NULL,
                    workflow_id  TEXT NOT NULL,
                    artifact_type TEXT NOT NULL,
                    version      INTEGER NOT NULL DEFAULT 1,
                    title        TEXT NOT NULL DEFAULT '',
                    content_json TEXT NOT NULL DEFAULT '{}',
                    text_content TEXT NOT NULL DEFAULT '',
                    metadata_json TEXT NOT NULL DEFAULT '{}',
                    created_at   TEXT NOT NULL,
                    updated_at   TEXT NOT NULL,
                    PRIMARY KEY (id, version)
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_artifacts_workflow
                ON artifacts (workflow_id, artifact_type)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_artifacts_task
                ON artifacts (task_id)
            """)

    def save(self, artifact: Artifact) -> Artifact:
        """
        Save an artifact. If an artifact with this ID already exists,
        creates a new version (immutable history).
        """
        with self._conn() as conn:
            existing = conn.execute(
                "SELECT MAX(version) as max_v FROM artifacts WHERE id = ?",
                (artifact.id,),
            ).fetchone()
            max_v = existing["max_v"] if existing and existing["max_v"] else 0
            artifact.version = max_v + 1
            artifact.updated_at = datetime.utcnow()

            conn.execute("""
                INSERT INTO artifacts
                    (id, task_id, workflow_id, artifact_type, version,
                     title, content_json, text_content, metadata_json,
                     created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                artifact.id,
                artifact.task_id,
                artifact.workflow_id,
                artifact.artifact_type.value,
                artifact.version,
                artifact.title,
                json.dumps(artifact.content),
                artifact.text_content,
                json.dumps(artifact.metadata),
                artifact.created_at.isoformat(),
                artifact.updated_at.isoformat(),
            ))
        logger.debug(f"ArtifactStore: saved {artifact.id} v{artifact.version} ({artifact.artifact_type})")
        return artifact

    def get(self, artifact_id: str, version: int | None = None) -> Artifact | None:
        """Get an artifact by ID. Returns latest version unless version is specified."""
        with self._conn() as conn:
            if version is not None:
                row = conn.execute(
                    "SELECT * FROM artifacts WHERE id = ? AND version = ?",
                    (artifact_id, version),
                ).fetchone()
            else:
                row = conn.execute(
                    "SELECT * FROM artifacts WHERE id = ? ORDER BY version DESC LIMIT 1",
                    (artifact_id,),
                ).fetchone()
        return self._row_to_artifact(row) if row else None

    def get_by_task(self, task_id: str) -> list[Artifact]:
        """Get all latest-version artifacts produced by a task."""
        with self._conn() as conn:
            rows = conn.execute("""
                SELECT a.*
                FROM artifacts a
                INNER JOIN (
                    SELECT id, MAX(version) as max_v
                    FROM artifacts WHERE task_id = ?
                    GROUP BY id
                ) latest ON a.id = latest.id AND a.version = latest.max_v
            """, (task_id,)).fetchall()
        return [self._row_to_artifact(r) for r in rows]

    def get_by_workflow(
        self,
        workflow_id: str,
        artifact_type: ArtifactType | None = None,
    ) -> list[Artifact]:
        """Get all latest-version artifacts for a workflow, optionally filtered by type."""
        with self._conn() as conn:
            if artifact_type:
                rows = conn.execute("""
                    SELECT a.*
                    FROM artifacts a
                    INNER JOIN (
                        SELECT id, MAX(version) as max_v
                        FROM artifacts WHERE workflow_id = ? AND artifact_type = ?
                        GROUP BY id
                    ) latest ON a.id = latest.id AND a.version = latest.max_v
                """, (workflow_id, artifact_type.value)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT a.*
                    FROM artifacts a
                    INNER JOIN (
                        SELECT id, MAX(version) as max_v
                        FROM artifacts WHERE workflow_id = ?
                        GROUP BY id
                    ) latest ON a.id = latest.id AND a.version = latest.max_v
                """, (workflow_id,)).fetchall()
        return [self._row_to_artifact(r) for r in rows]

    def get_versions(self, artifact_id: str) -> list[Artifact]:
        """Get all versions of an artifact (history)."""
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM artifacts WHERE id = ? ORDER BY version ASC",
                (artifact_id,),
            ).fetchall()
        return [self._row_to_artifact(r) for r in rows]

    def count(self, workflow_id: str) -> int:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT COUNT(DISTINCT id) as cnt FROM artifacts WHERE workflow_id = ?",
                (workflow_id,),
            ).fetchone()
        return row["cnt"] if row else 0

    def _row_to_artifact(self, row: sqlite3.Row) -> Artifact:
        return Artifact(
            id=row["id"],
            task_id=row["task_id"],
            workflow_id=row["workflow_id"],
            artifact_type=ArtifactType(row["artifact_type"]),
            version=row["version"],
            title=row["title"],
            content=json.loads(row["content_json"]),
            text_content=row["text_content"],
            metadata=json.loads(row["metadata_json"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )


# Global singleton
_artifact_store: ArtifactStore | None = None


def get_artifact_store(db_path: str | Path | None = None) -> ArtifactStore:
    global _artifact_store
    if _artifact_store is None:
        _artifact_store = ArtifactStore(db_path or _DEFAULT_DB)
    return _artifact_store
