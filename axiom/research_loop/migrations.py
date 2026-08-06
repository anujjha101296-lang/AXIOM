"""SQLite schema for autonomous research loop persistence."""

from __future__ import annotations

import sqlite3

from axiom.observability.logger import get_logger

logger = get_logger(__name__)


def ensure_research_loop_schema(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA foreign_keys = ON;")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS research_loop_runs (
            id              TEXT PRIMARY KEY,
            workflow_id     TEXT NOT NULL,
            research_question TEXT NOT NULL,
            status          TEXT NOT NULL DEFAULT 'pending',
            config_json     TEXT NOT NULL DEFAULT '{}',
            state_json      TEXT NOT NULL DEFAULT '{}',
            benchmark_id    TEXT,
            project_id      TEXT,
            error           TEXT,
            created_at      TEXT NOT NULL,
            started_at      TEXT,
            completed_at    TEXT
        );
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS research_loop_failures (
            id                  TEXT PRIMARY KEY,
            run_id              TEXT,
            approach            TEXT NOT NULL,
            reason_attempted    TEXT NOT NULL DEFAULT '',
            evidence_json       TEXT NOT NULL DEFAULT '[]',
            failure_reason      TEXT NOT NULL,
            critic_feedback     TEXT NOT NULL DEFAULT '',
            learned             TEXT NOT NULL DEFAULT '',
            reuse_conditions    TEXT NOT NULL DEFAULT '',
            fingerprint         TEXT NOT NULL,
            iteration           INTEGER NOT NULL DEFAULT 0,
            created_at          TEXT NOT NULL
        );
    """)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_rl_failures_fingerprint "
        "ON research_loop_failures(fingerprint);"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_rl_failures_run "
        "ON research_loop_failures(run_id);"
    )

    conn.execute("""
        CREATE TABLE IF NOT EXISTS research_loop_benchmark_scores (
            id                  TEXT PRIMARY KEY,
            benchmark_id        TEXT NOT NULL,
            run_id              TEXT NOT NULL,
            score_json          TEXT NOT NULL,
            created_at          TEXT NOT NULL
        );
    """)

    conn.commit()
    logger.debug("Research loop schema ensured")
