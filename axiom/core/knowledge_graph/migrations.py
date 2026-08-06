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
import time
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


def _v4_mathematical_ontology(conn: sqlite3.Connection) -> None:
    """V4: EGS Mathematical Ontology tables & memory structures (R1, R8)."""
    # 1. mathematical_objects table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS mathematical_objects (
            id              TEXT PRIMARY KEY,
            node_id         TEXT NOT NULL,
            object_type     TEXT NOT NULL,
            formal_symbol   TEXT,
            domain          TEXT NOT NULL,
            properties_json TEXT,
            created_at      TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (node_id) REFERENCES nodes(id) ON DELETE CASCADE
        );
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_math_obj_node_id ON mathematical_objects(node_id);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_math_obj_type ON mathematical_objects(object_type);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_math_obj_domain ON mathematical_objects(domain);")

    # 2. definitions table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS definitions (
            id                  TEXT PRIMARY KEY,
            node_id             TEXT NOT NULL,
            term                TEXT NOT NULL,
            formal_definition   TEXT,
            informal_definition TEXT,
            domain              TEXT,
            created_at          TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (node_id) REFERENCES nodes(id) ON DELETE CASCADE
        );
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_def_node_id ON definitions(node_id);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_def_term ON definitions(term);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_def_domain ON definitions(domain);")

    # 3. equivalent_statements table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS equivalent_statements (
            id               TEXT PRIMARY KEY,
            statement_a_id   TEXT NOT NULL,
            statement_b_id   TEXT NOT NULL,
            equivalence_type TEXT NOT NULL DEFAULT 'LOGICAL',
            proof_reference  TEXT,
            confidence       REAL NOT NULL DEFAULT 1.0,
            created_at       TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (statement_a_id) REFERENCES nodes(id) ON DELETE CASCADE,
            FOREIGN KEY (statement_b_id) REFERENCES nodes(id) ON DELETE CASCADE
        );
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_eq_stmt_a ON equivalent_statements(statement_a_id);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_eq_stmt_b ON equivalent_statements(statement_b_id);")
    conn.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_eq_pair 
        ON equivalent_statements(statement_a_id, statement_b_id, equivalence_type);
    """)

    # 4. memory_snapshots table (ensure table and optional domain column exist)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS memory_snapshots (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT    NOT NULL,
            snapshot   TEXT    NOT NULL,
            domain     TEXT,
            created_at TEXT    NOT NULL DEFAULT (datetime('now'))
        );
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_session ON memory_snapshots(session_id);")

    # Check if domain column exists in memory_snapshots (in case v3 created it without domain)
    cursor = conn.execute("PRAGMA table_info(memory_snapshots);")
    columns = {row[1] for row in cursor.fetchall()}
    if "domain" not in columns:
        try:
            conn.execute("ALTER TABLE memory_snapshots ADD COLUMN domain TEXT;")
        except sqlite3.OperationalError as e:
            if "duplicate column" not in str(e).lower():
                raise

    # 5. failed_proof_attempts table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS failed_proof_attempts (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            claim_id        TEXT    NOT NULL,
            tactic_sequence TEXT    NOT NULL,
            verifier        TEXT    NOT NULL,
            error_message   TEXT,
            created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (claim_id) REFERENCES nodes(id) ON DELETE CASCADE
        );
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_failed_proofs_claim ON failed_proof_attempts(claim_id);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_failed_proofs_verifier ON failed_proof_attempts(verifier);")
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_failed_proofs_claim_verifier 
        ON failed_proof_attempts(claim_id, verifier);
    """)

    conn.commit()


# Ordered migration list: (version, description, function)
MIGRATIONS: List[Migration] = [
    (1, "Initial schema: nodes + edges",         _v1_initial_schema),
    (2, "Add proof_lineage table",               _v2_proof_lineage),
    (3, "Add memory_snapshots table",            _v3_working_memory_snapshots),
    (4, "Mathematical ontology & memory schema", _v4_mathematical_ontology),
]


def _ensure_migration_table(conn: sqlite3.Connection) -> None:
    max_retries = 10
    for attempt in range(max_retries):
        try:
            _create_migration_table(conn)
            return
        except (sqlite3.OperationalError, sqlite3.IntegrityError) as e:
            err_msg = str(e).lower()
            if "locked" in err_msg or "busy" in err_msg:
                time.sleep(0.05 * (attempt + 1))
                continue
            if "already exists" in err_msg:
                return
            if attempt == max_retries - 1:
                raise
            time.sleep(0.05 * (attempt + 1))


def _apply_migration_safely(
    conn: sqlite3.Connection,
    version: int,
    description: str,
    migrate_fn: Callable[[sqlite3.Connection], None],
) -> None:
    max_retries = 10
    for attempt in range(max_retries):
        # Initial check
        try:
            if version in _applied_versions(conn):
                return
        except (sqlite3.OperationalError, sqlite3.IntegrityError):
            pass

        transaction_started = False
        try:
            if not conn.in_transaction:
                conn.execute("BEGIN IMMEDIATE")
                transaction_started = True
        except (sqlite3.OperationalError, sqlite3.IntegrityError) as e:
            err_msg = str(e).lower()
            if "locked" in err_msg or "busy" in err_msg:
                time.sleep(0.05 * (attempt + 1))
                continue

        try:
            # Re-check under lock
            if version in _applied_versions(conn):
                if transaction_started and conn.in_transaction:
                    conn.rollback()
                return

            logger.info(f"Applying migration v{version}: {description}")
            migrate_fn(conn)
            conn.execute(
                "INSERT INTO _schema_migrations (version, description) VALUES (?, ?);",
                (version, description),
            )
            conn.commit()
            logger.info(f"Migration v{version} applied successfully.")
            return
        except (sqlite3.IntegrityError, sqlite3.OperationalError) as e:
            if conn.in_transaction:
                try:
                    conn.rollback()
                except Exception:
                    pass
            err_msg = str(e).lower()

            try:
                if version in _applied_versions(conn):
                    return
            except Exception:
                pass

            if "locked" in err_msg or "busy" in err_msg:
                time.sleep(0.05 * (attempt + 1))
                continue

            if "unique" in err_msg or "already exists" in err_msg:
                try:
                    if version in _applied_versions(conn):
                        return
                except Exception:
                    pass

            if attempt == max_retries - 1:
                try:
                    if version in _applied_versions(conn):
                        return
                except Exception:
                    pass
                raise
            time.sleep(0.05 * (attempt + 1))


def run_migrations(conn: sqlite3.Connection) -> None:
    """
    Run all pending migrations in order.
    Idempotent — already-applied migrations are skipped.
    Handles concurrent execution cleanly across multiple threads/connections.
    """
    conn.execute("PRAGMA foreign_keys = ON;")
    _ensure_migration_table(conn)

    for version, description, migrate_fn in MIGRATIONS:
        _apply_migration_safely(conn, version, description, migrate_fn)


def migration_status(conn: sqlite3.Connection) -> List[dict]:
    """Return the current migration status for all known migrations."""
    _ensure_migration_table(conn)
    applied = _applied_versions(conn)
    return [
        {
            "version": v,
            "description": desc,
            "status": "applied" if v in applied else "pending",
        }
        for v, desc, _ in MIGRATIONS
    ]

