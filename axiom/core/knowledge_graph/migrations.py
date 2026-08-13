"""axiom.core.knowledge_graph.migrations - schema migration utilities."""
from __future__ import annotations
import sqlite3
from typing import List, Dict, Any


def run_migrations(conn: sqlite3.Connection) -> None:
    """Apply all schema migrations idempotently (delegates to EpistemicStore schema logic)."""
    from axiom.core.knowledge_graph.db import EpistemicStore
    store = EpistemicStore.__new__(EpistemicStore)
    store.conn = conn
    store._apply_schema()


def migration_status(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    """Return migration status as list of dicts with 'version', 'name', 'status', 'applied_at'."""
    try:
        rows = conn.execute(
            "SELECT version, name, applied_at FROM _schema_migrations ORDER BY version"
        ).fetchall()
    except sqlite3.OperationalError:
        return []
    return [
        {"version": row[0], "name": row[1], "status": "applied", "applied_at": row[2]}
        for row in rows
    ]
