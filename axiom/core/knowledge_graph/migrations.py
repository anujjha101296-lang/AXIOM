"""
Database Migrations — AXIOM EGS Schema Versioning
===================================================
Versioned, idempotent SQLite schema migrations.
Each migration is identified by a version integer and runs only once.

Usage:
    from axiom.core.knowledge_graph.migrations import run_migrations
    run_migrations(conn)
"""

from __future__ import annotations

import sqlite3
from typing import Callable, List, Tuple

from axiom.observability.logger import get_logger

logger = get_logger(__name__)


Migration = Tuple[int, str, Callable[[sqlite3.Connection], None]]


def _create_migration_table(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS _schema_migrations (
            version     INTEGER PRIMARY KEY,
            description TEXT    NOT NULL,
            applied_at  TEXT    NOT NULL DEFAULT (datetime('now'))
        );
    """)
    conn.commit()


def _applied_versions(conn: sqlite3.Connection) -> set[int]:
    cursor = conn.execute("SELECT version FROM _schema_migrations;")
    return {row[0] for row in cursor.fetchall()}


# ── Migration definitions ─────────────────────────────────────────────────────

def _v1_initial_schema(conn: sqlite3.Connection) -> None:
    """V1: Core nodes + edges tables (already created by EpistemicStore.__init__)."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS nodes (
            id   TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            name TEXT NOT NULL,
            data TEXT NOT NULL
        );
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS edges (
            source_id  TEXT NOT NULL,
            target_id  TEXT NOT NULL,
            type       TEXT NOT NULL,
            confidence REAL NOT NULL DEFAULT 1.0,
            provenance TEXT,
            PRIMARY KEY (source_id, target_id, type),
            FOREIGN KEY (source_id) REFERENCES nodes(id) ON DELETE CASCADE,
            FOREIGN KEY (target_id) REFERENCES nodes(id) ON DELETE CASCADE
        );
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_nodes_type   ON nodes(type);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source_id);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target_id);")
    conn.commit()


def _v2_proof_lineage(conn: sqlite3.Connection) -> None:
    """V2: Proof lineage tracker — records each verification attempt."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS proof_lineage (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            claim_id     TEXT    NOT NULL,
            verifier     TEXT    NOT NULL,   -- 'SMT' | 'LEAN' | 'MCTS'
            result       TEXT    NOT NULL,   -- 'VERIFIED' | 'REFUTED' | 'UNKNOWN'
            tactic_used  TEXT,
            duration_ms  REAL,
            created_at   TEXT    NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (claim_id) REFERENCES nodes(id) ON DELETE CASCADE
        );
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_lineage_claim_id
        ON proof_lineage(claim_id);
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_lineage_verifier
        ON proof_lineage(verifier);
    """)
    conn.commit()


def _v3_working_memory_snapshots(conn: sqlite3.Connection) -> None:
    """V3: Persist working memory snapshots for cross-session recall."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS memory_snapshots (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT    NOT NULL,
            snapshot   TEXT    NOT NULL,   -- JSON blob
            created_at TEXT    NOT NULL DEFAULT (datetime('now'))
        );
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_snapshots_session
        ON memory_snapshots(session_id);
    """)
    conn.commit()


# Ordered migration list: (version, description, function)
MIGRATIONS: List[Migration] = [
    (1, "Initial schema: nodes + edges",         _v1_initial_schema),
    (2, "Add proof_lineage table",               _v2_proof_lineage),
    (3, "Add memory_snapshots table",            _v3_working_memory_snapshots),
]


def run_migrations(conn: sqlite3.Connection) -> None:
    """
    Run all pending migrations in order.
    Idempotent — already-applied migrations are skipped.
    """
    conn.execute("PRAGMA foreign_keys = ON;")
    _create_migration_table(conn)
    applied = _applied_versions(conn)

    for version, description, migrate_fn in MIGRATIONS:
        if version in applied:
            continue
        logger.info(f"Applying migration v{version}: {description}")
        migrate_fn(conn)
        conn.execute(
            "INSERT INTO _schema_migrations (version, description) VALUES (?, ?);",
            (version, description),
        )
        conn.commit()
        logger.info(f"Migration v{version} applied successfully.")


def migration_status(conn: sqlite3.Connection) -> List[dict]:
    """Return the current migration status for all known migrations."""
    _create_migration_table(conn)
    applied = _applied_versions(conn)
    return [
        {
            "version": v,
            "description": desc,
            "status": "applied" if v in applied else "pending",
        }
        for v, desc, _ in MIGRATIONS
    ]
