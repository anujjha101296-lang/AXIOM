"""SQLite migrations for research workspace tables."""

from __future__ import annotations

import sqlite3

from axiom.observability.logger import get_logger

logger = get_logger(__name__)


def ensure_research_schema(conn: sqlite3.Connection) -> None:
    """Create research workspace tables and FTS index if missing."""
    conn.execute("PRAGMA foreign_keys = ON;")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS research_projects (
            id              TEXT PRIMARY KEY,
            name            TEXT NOT NULL,
            description     TEXT NOT NULL DEFAULT '',
            created_at      TEXT NOT NULL,
            updated_at      TEXT NOT NULL,
            last_session_at TEXT
        );
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS research_documents (
            id            TEXT PRIMARY KEY,
            project_id    TEXT NOT NULL,
            filename      TEXT NOT NULL,
            text_content  TEXT NOT NULL DEFAULT '',
            summary       TEXT NOT NULL DEFAULT '',
            page_count    INTEGER NOT NULL DEFAULT 0,
            char_count    INTEGER NOT NULL DEFAULT 0,
            file_path     TEXT,
            uploaded_at   TEXT NOT NULL,
            summarized_at TEXT,
            FOREIGN KEY (project_id) REFERENCES research_projects(id) ON DELETE CASCADE
        );
    """)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_research_docs_project "
        "ON research_documents(project_id);"
    )

    conn.execute("""
        CREATE TABLE IF NOT EXISTS research_notes (
            id          TEXT PRIMARY KEY,
            project_id  TEXT NOT NULL,
            document_id TEXT,
            title       TEXT NOT NULL,
            body        TEXT NOT NULL DEFAULT '',
            tags        TEXT NOT NULL DEFAULT '[]',
            created_at  TEXT NOT NULL,
            updated_at  TEXT NOT NULL,
            FOREIGN KEY (project_id) REFERENCES research_projects(id) ON DELETE CASCADE,
            FOREIGN KEY (document_id) REFERENCES research_documents(id) ON DELETE SET NULL
        );
    """)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_research_notes_project "
        "ON research_notes(project_id);"
    )

    conn.execute("""
        CREATE TABLE IF NOT EXISTS research_sessions (
            id                 TEXT PRIMARY KEY,
            project_id         TEXT NOT NULL UNIQUE,
            started_at         TEXT NOT NULL,
            last_active_at     TEXT NOT NULL,
            active_document_id TEXT,
            context_json       TEXT NOT NULL DEFAULT '{}',
            FOREIGN KEY (project_id) REFERENCES research_projects(id) ON DELETE CASCADE
        );
    """)

    conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS research_fts USING fts5(
            entity_type,
            entity_id,
            project_id,
            title,
            body,
            tokenize='porter'
        );
    """)

    conn.commit()
    logger.debug("Research workspace schema ensured")
