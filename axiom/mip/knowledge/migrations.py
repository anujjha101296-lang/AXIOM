"""
Department A — Mathematical Knowledge
SQLite v5 schema migration: mip_* tables for Mathematical Intelligence Platform.
"""
from __future__ import annotations

import sqlite3
import logging

logger = logging.getLogger(__name__)

MIP_V5_MIGRATIONS: list[str] = [
    # Mathematical objects — all 15 types
    """
    CREATE TABLE IF NOT EXISTS mip_objects (
        id             TEXT PRIMARY KEY,
        object_type    TEXT NOT NULL,
        name           TEXT NOT NULL,
        statement      TEXT NOT NULL,
        domain         TEXT NOT NULL DEFAULT 'unknown',
        epistemic_status TEXT NOT NULL DEFAULT 'unknown',
        axiom_system   TEXT,
        source_ref     TEXT,
        latex          TEXT,
        tags           TEXT,       -- JSON array
        metadata       TEXT,       -- JSON object
        created_at     TEXT NOT NULL,
        updated_at     TEXT NOT NULL
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_mip_objects_type ON mip_objects(object_type)",
    "CREATE INDEX IF NOT EXISTS idx_mip_objects_domain ON mip_objects(domain)",
    "CREATE INDEX IF NOT EXISTS idx_mip_objects_status ON mip_objects(epistemic_status)",
    "CREATE INDEX IF NOT EXISTS idx_mip_objects_name ON mip_objects(name)",

    # Directed edges between mathematical objects
    """
    CREATE TABLE IF NOT EXISTS mip_edges (
        id          TEXT PRIMARY KEY,
        source_id   TEXT NOT NULL REFERENCES mip_objects(id),
        target_id   TEXT NOT NULL REFERENCES mip_objects(id),
        edge_type   TEXT NOT NULL,
        confidence  REAL NOT NULL DEFAULT 1.0,
        metadata    TEXT,       -- JSON object
        created_at  TEXT NOT NULL
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_mip_edges_source ON mip_edges(source_id)",
    "CREATE INDEX IF NOT EXISTS idx_mip_edges_target ON mip_edges(target_id)",
    "CREATE INDEX IF NOT EXISTS idx_mip_edges_type ON mip_edges(edge_type)",

    # Mathematical domains registry
    """
    CREATE TABLE IF NOT EXISTS mip_domains (
        id          TEXT PRIMARY KEY,
        name        TEXT NOT NULL UNIQUE,
        description TEXT,
        parent_domain TEXT,
        keywords    TEXT        -- JSON array
    )
    """,

    # Axiom systems (ZFC, PA, etc.)
    """
    CREATE TABLE IF NOT EXISTS mip_axiom_systems (
        id          TEXT PRIMARY KEY,
        name        TEXT NOT NULL UNIQUE,
        description TEXT,
        axioms      TEXT        -- JSON array of axiom IDs
    )
    """,

    # Proof attempts (success and failures)
    """
    CREATE TABLE IF NOT EXISTS mip_proof_attempts (
        id              TEXT PRIMARY KEY,
        theorem_id      TEXT NOT NULL,
        formal_system   TEXT NOT NULL,  -- lean4, coq, isabelle, mcts, smt
        tactic_sequence TEXT,           -- JSON array
        status          TEXT NOT NULL,  -- SUCCESS, FAILED, TIMEOUT, ERROR
        proof_script    TEXT,
        error_message   TEXT,
        execution_time_ms REAL,
        created_at      TEXT NOT NULL
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_mip_proof_attempts_theorem ON mip_proof_attempts(theorem_id)",
    "CREATE INDEX IF NOT EXISTS idx_mip_proof_attempts_status ON mip_proof_attempts(status)",

    # Mathematical memory snapshots
    """
    CREATE TABLE IF NOT EXISTS mip_memory_snapshots (
        id              TEXT PRIMARY KEY,
        session_id      TEXT NOT NULL,
        problem_id      TEXT,
        active_hypotheses TEXT,      -- JSON array
        failed_tactics  TEXT,        -- JSON object {theorem_id: [tactic, ...]}
        open_questions  TEXT,        -- JSON array
        research_context TEXT,       -- JSON object
        snapshot_type   TEXT NOT NULL DEFAULT 'episodic',  -- episodic, semantic
        created_at      TEXT NOT NULL
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_mip_memory_session ON mip_memory_snapshots(session_id)",

    # Conjecture queue
    """
    CREATE TABLE IF NOT EXISTS mip_conjectures (
        id              TEXT PRIMARY KEY,
        statement       TEXT NOT NULL,
        domain          TEXT NOT NULL DEFAULT 'unknown',
        novelty_score   REAL NOT NULL DEFAULT 0.0,
        strategy_used   TEXT,
        source_nodes    TEXT,       -- JSON array of node IDs
        status          TEXT NOT NULL DEFAULT 'open',  -- open, verified, refuted, abandoned
        created_at      TEXT NOT NULL,
        updated_at      TEXT NOT NULL
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_mip_conjectures_status ON mip_conjectures(status)",
    "CREATE INDEX IF NOT EXISTS idx_mip_conjectures_novelty ON mip_conjectures(novelty_score DESC)",

    # Schema version tracking for MIP
    """
    CREATE TABLE IF NOT EXISTS mip_schema_version (
        version     INTEGER PRIMARY KEY,
        applied_at  TEXT NOT NULL,
        description TEXT
    )
    """,
]

SEED_DOMAINS = [
    ("algebra", "Algebraic structures: groups, rings, fields, modules"),
    ("number_theory", "Properties of integers and prime numbers"),
    ("analysis", "Limits, continuity, differentiation, integration"),
    ("topology", "Properties preserved under continuous deformations"),
    ("logic", "Formal reasoning, proof theory, model theory"),
    ("combinatorics", "Counting, graph theory, discrete structures"),
    ("category_theory", "Abstract structures and their relationships"),
    ("geometry", "Spatial properties and relationships"),
    ("probability", "Random phenomena and stochastic processes"),
    ("computational", "Complexity theory, algorithms, computability"),
    ("algebraic_geometry", "Geometric objects defined by polynomial equations"),
    ("differential_geometry", "Smooth manifolds and their geometric properties"),
    ("mathematical_physics", "Mathematical structures underlying physical theories"),
    ("unknown", "Unclassified mathematical content"),
]

SEED_AXIOM_SYSTEMS = [
    ("zfc", "Zermelo–Fraenkel set theory with Axiom of Choice"),
    ("pa", "Peano Arithmetic"),
    ("hol", "Higher-Order Logic"),
    ("lean4_core", "Lean 4 core type theory (CIC + quotient types)"),
    ("cic", "Calculus of Inductive Constructions (Coq foundation)"),
]


def run_v5_migration(db_path: str = "axiom.db") -> None:
    """Run the MIP v5 schema migration."""
    import json
    from datetime import datetime

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")

    try:
        with conn:
            for sql in MIP_V5_MIGRATIONS:
                conn.execute(sql)

            # Seed domains
            for domain_id, description in SEED_DOMAINS:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO mip_domains (id, name, description)
                    VALUES (?, ?, ?)
                    """,
                    (domain_id, domain_id, description),
                )

            # Seed axiom systems
            for sys_id, description in SEED_AXIOM_SYSTEMS:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO mip_axiom_systems (id, name, description)
                    VALUES (?, ?, ?)
                    """,
                    (sys_id, sys_id, description),
                )

            # Record migration
            conn.execute(
                """
                INSERT OR IGNORE INTO mip_schema_version (version, applied_at, description)
                VALUES (5, ?, 'MIP Mathematical Intelligence Platform — EPIC-001')
                """,
                (datetime.utcnow().isoformat(),),
            )

        logger.info("MIP v5 migration completed successfully.")
    except Exception as exc:
        logger.error("MIP v5 migration failed: %s", exc)
        raise
    finally:
        conn.close()


def check_v5_applied(db_path: str = "axiom.db") -> bool:
    """Return True if MIP v5 migration has already been applied."""
    try:
        conn = sqlite3.connect(db_path)
        result = conn.execute(
            "SELECT 1 FROM mip_schema_version WHERE version = 5"
        ).fetchone()
        conn.close()
        return result is not None
    except sqlite3.OperationalError:
        return False


if __name__ == "__main__":
    import sys
    db = sys.argv[1] if len(sys.argv) > 1 else "axiom.db"
    run_v5_migration(db)
    print(f"MIP v5 migration applied to {db}")
