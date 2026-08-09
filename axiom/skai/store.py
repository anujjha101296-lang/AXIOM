"""SKAI knowledge store — sources, entities, relations, conflicts, gaps."""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from axiom.skai.models import (
    KnowledgeConflict,
    KnowledgeEntity,
    KnowledgeRelation,
    ResearchGap,
    SourceProvenance,
    _utc_now,
)


class SkaiStore:
    """SQLite-backed scientific knowledge acquisition store."""

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
        CREATE TABLE IF NOT EXISTS skai_sources (
            source_id TEXT PRIMARY KEY,
            source_type TEXT NOT NULL,
            quality_tier TEXT NOT NULL,
            scope TEXT NOT NULL,
            campaign_id TEXT,
            version INTEGER NOT NULL DEFAULT 1,
            json_data TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS skai_source_versions (
            source_id TEXT NOT NULL,
            version INTEGER NOT NULL,
            json_data TEXT NOT NULL,
            archived_at TEXT NOT NULL,
            PRIMARY KEY (source_id, version)
        );
        CREATE TABLE IF NOT EXISTS skai_entities (
            entity_id TEXT PRIMARY KEY,
            entity_type TEXT NOT NULL,
            source_id TEXT NOT NULL,
            scope TEXT NOT NULL,
            campaign_id TEXT,
            json_data TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS skai_relations (
            relation_id TEXT PRIMARY KEY,
            relation_type TEXT NOT NULL,
            source_entity_id TEXT NOT NULL,
            target_entity_id TEXT NOT NULL,
            json_data TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS skai_conflicts (
            conflict_id TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            json_data TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS skai_gaps (
            gap_id TEXT PRIMARY KEY,
            gap_type TEXT NOT NULL,
            campaign_id TEXT,
            json_data TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS skai_knowledge_versions (
            version_id TEXT PRIMARY KEY,
            entity_id TEXT NOT NULL,
            version_number INTEGER NOT NULL,
            json_data TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_skai_entities_source ON skai_entities(source_id);
        CREATE INDEX IF NOT EXISTS idx_skai_entities_type ON skai_entities(entity_type);
        CREATE INDEX IF NOT EXISTS idx_skai_relations_src ON skai_relations(source_entity_id);
        CREATE INDEX IF NOT EXISTS idx_skai_relations_tgt ON skai_relations(target_entity_id);
        CREATE INDEX IF NOT EXISTS idx_skai_sources_scope ON skai_sources(scope, campaign_id);
        """)
        conn.commit()
        self._release_conn(conn)

    def save_source(self, source: SourceProvenance, *, archive: bool = True) -> SourceProvenance:
        conn = self._conn()
        row = conn.execute(
            "SELECT version, json_data FROM skai_sources WHERE source_id = ?",
            (source.source_id,),
        ).fetchone()
        if row and archive:
            conn.execute(
                """INSERT OR REPLACE INTO skai_source_versions
                   (source_id, version, json_data, archived_at) VALUES (?, ?, ?, ?)""",
                (source.source_id, int(row["version"]), row["json_data"], _utc_now()),
            )
            source.version = int(row["version"]) + 1
        source.updated_at = _utc_now()
        conn.execute(
            """INSERT OR REPLACE INTO skai_sources
               (source_id, source_type, quality_tier, scope, campaign_id, version, json_data, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                source.source_id, source.source_type.value, source.quality_tier.value,
                source.scope.value, source.campaign_id, source.version,
                json.dumps(source.to_dict()), source.created_at, source.updated_at,
            ),
        )
        conn.commit()
        self._release_conn(conn)
        return source

    def get_source(self, source_id: str) -> SourceProvenance | None:
        conn = self._conn()
        row = conn.execute("SELECT json_data FROM skai_sources WHERE source_id = ?", (source_id,)).fetchone()
        self._release_conn(conn)
        return SourceProvenance.from_dict(json.loads(row["json_data"])) if row else None

    def find_source_by_content_hash(self, content_hash: str) -> SourceProvenance | None:
        if not content_hash:
            return None
        for source in self.list_sources(limit=500):
            if source.content_hash == content_hash:
                return source
        return None

    def find_source_by_location(self, location: str) -> SourceProvenance | None:
        if not location:
            return None
        normalized = location.strip().rstrip("/")
        for source in self.list_sources(limit=500):
            loc = (source.location or "").strip().rstrip("/")
            meta_url = str((source.metadata or {}).get("url", "")).strip().rstrip("/")
            if loc == normalized or meta_url == normalized:
                return source
        return None

    def list_sources(self, *, scope: str | None = None, campaign_id: str | None = None, limit: int = 100) -> list[SourceProvenance]:
        conn = self._conn()
        query = "SELECT json_data FROM skai_sources WHERE 1=1"
        params: list[Any] = []
        if scope:
            query += " AND scope = ?"
            params.append(scope)
        if campaign_id:
            query += " AND campaign_id = ?"
            params.append(campaign_id)
        query += " ORDER BY updated_at DESC LIMIT ?"
        params.append(limit)
        rows = conn.execute(query, params).fetchall()
        self._release_conn(conn)
        return [SourceProvenance.from_dict(json.loads(r["json_data"])) for r in rows]

    def save_entity(self, entity: KnowledgeEntity) -> KnowledgeEntity:
        conn = self._conn()
        conn.execute(
            """INSERT OR REPLACE INTO skai_entities
               (entity_id, entity_type, source_id, scope, campaign_id, json_data, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                entity.entity_id, entity.entity_type.value, entity.source_id,
                entity.scope.value, entity.campaign_id,
                json.dumps(entity.to_dict()), entity.created_at,
            ),
        )
        conn.commit()
        self._release_conn(conn)
        return entity

    def get_entity(self, entity_id: str) -> KnowledgeEntity | None:
        conn = self._conn()
        row = conn.execute("SELECT json_data FROM skai_entities WHERE entity_id = ?", (entity_id,)).fetchone()
        self._release_conn(conn)
        return KnowledgeEntity.from_dict(json.loads(row["json_data"])) if row else None

    def list_entities(self, *, entity_type: str | None = None, source_id: str | None = None, limit: int = 200) -> list[KnowledgeEntity]:
        conn = self._conn()
        query = "SELECT json_data FROM skai_entities WHERE 1=1"
        params: list[Any] = []
        if entity_type:
            query += " AND entity_type = ?"
            params.append(entity_type)
        if source_id:
            query += " AND source_id = ?"
            params.append(source_id)
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        rows = conn.execute(query, params).fetchall()
        self._release_conn(conn)
        return [KnowledgeEntity.from_dict(json.loads(r["json_data"])) for r in rows]

    def save_relation(self, relation: KnowledgeRelation) -> KnowledgeRelation:
        conn = self._conn()
        conn.execute(
            """INSERT OR REPLACE INTO skai_relations
               (relation_id, relation_type, source_entity_id, target_entity_id, json_data, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                relation.relation_id, relation.relation_type.value,
                relation.source_entity_id, relation.target_entity_id,
                json.dumps(relation.to_dict()), relation.created_at,
            ),
        )
        conn.commit()
        self._release_conn(conn)
        return relation

    def list_relations(self, entity_id: str | None = None, limit: int = 200) -> list[KnowledgeRelation]:
        conn = self._conn()
        if entity_id:
            rows = conn.execute(
                """SELECT json_data FROM skai_relations
                   WHERE source_entity_id = ? OR target_entity_id = ?
                   ORDER BY created_at DESC LIMIT ?""",
                (entity_id, entity_id, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT json_data FROM skai_relations ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        self._release_conn(conn)
        return [KnowledgeRelation.from_dict(json.loads(r["json_data"])) for r in rows]

    def save_conflict(self, conflict: KnowledgeConflict) -> KnowledgeConflict:
        conflict.updated_at = _utc_now()
        conn = self._conn()
        conn.execute(
            """INSERT OR REPLACE INTO skai_conflicts
               (conflict_id, status, json_data, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?)""",
            (conflict.conflict_id, conflict.status.value, json.dumps(conflict.to_dict()),
             conflict.created_at, conflict.updated_at),
        )
        conn.commit()
        self._release_conn(conn)
        return conflict

    def list_conflicts(self, status: str | None = None, limit: int = 50) -> list[KnowledgeConflict]:
        conn = self._conn()
        if status:
            rows = conn.execute(
                "SELECT json_data FROM skai_conflicts WHERE status = ? ORDER BY updated_at DESC LIMIT ?",
                (status, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT json_data FROM skai_conflicts ORDER BY updated_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        self._release_conn(conn)
        return [KnowledgeConflict.from_dict(json.loads(r["json_data"])) for r in rows]

    def save_gap(self, gap: ResearchGap) -> ResearchGap:
        conn = self._conn()
        conn.execute(
            """INSERT OR REPLACE INTO skai_gaps
               (gap_id, gap_type, campaign_id, json_data, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (gap.gap_id, gap.gap_type, gap.campaign_id, json.dumps(gap.to_dict()), gap.created_at),
        )
        conn.commit()
        self._release_conn(conn)
        return gap

    def list_gaps(self, campaign_id: str | None = None, limit: int = 50) -> list[ResearchGap]:
        conn = self._conn()
        if campaign_id:
            rows = conn.execute(
                "SELECT json_data FROM skai_gaps WHERE campaign_id = ? ORDER BY created_at DESC LIMIT ?",
                (campaign_id, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT json_data FROM skai_gaps ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        self._release_conn(conn)
        return [ResearchGap.from_dict(json.loads(r["json_data"])) for r in rows]

    def save_knowledge_version(self, version_id: str, entity_id: str, version_number: int, snapshot: dict, reason: str) -> None:
        conn = self._conn()
        conn.execute(
            """INSERT OR REPLACE INTO skai_knowledge_versions
               (version_id, entity_id, version_number, json_data, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (version_id, entity_id, version_number, json.dumps({
                "snapshot": snapshot, "change_reason": reason,
            }), _utc_now()),
        )
        conn.commit()
        self._release_conn(conn)

    def graph_summary(self) -> dict[str, Any]:
        conn = self._conn()
        sources = conn.execute("SELECT COUNT(*) as c FROM skai_sources").fetchone()["c"]
        entities = conn.execute("SELECT COUNT(*) as c FROM skai_entities").fetchone()["c"]
        relations = conn.execute("SELECT COUNT(*) as c FROM skai_relations").fetchone()["c"]
        conflicts = conn.execute("SELECT COUNT(*) as c FROM skai_conflicts WHERE status = 'unresolved'").fetchone()["c"]
        gaps = conn.execute("SELECT COUNT(*) as c FROM skai_gaps").fetchone()["c"]
        self._release_conn(conn)
        return {
            "sources": sources,
            "entities": entities,
            "relations": relations,
            "unresolved_conflicts": conflicts,
            "research_gaps": gaps,
        }


_store_cache: dict[str, SkaiStore] = {}


def get_skai_store(db_path: str) -> SkaiStore:
    if db_path not in _store_cache:
        _store_cache[db_path] = SkaiStore(db_path)
    return _store_cache[db_path]
