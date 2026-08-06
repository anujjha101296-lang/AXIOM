"""SQLite persistence for research projects, documents, notes, and search."""

from __future__ import annotations

import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from axiom.observability.logger import get_logger
from axiom.research.migrations import ensure_research_schema
from axiom.research.schema import (
    ConversationDetail,
    ProjectDetail,
    ResearchConversation,
    ResearchDocument,
    ResearchMessage,
    ResearchNote,
    ResearchProject,
    ResearchSession,
    SearchResult,
)

logger = get_logger(__name__)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id() -> str:
    return str(uuid.uuid4())


class ResearchStore:
    """Research workspace store backed by SQLite."""

    def __init__(self, db_path: str, upload_dir: str):
        self.db_path = db_path
        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        ensure_research_schema(self.conn)

    def close(self) -> None:
        if self.conn:
            self.conn.close()

    # ── Projects ──────────────────────────────────────────────────────────────

    def create_project(self, name: str, description: str = "") -> ResearchProject:
        now = _utc_now()
        project_id = _new_id()
        self.conn.execute(
            """
            INSERT INTO research_projects (id, name, description, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (project_id, name.strip(), description.strip(), now, now),
        )
        self.conn.execute(
            """
            INSERT INTO research_sessions
            (id, project_id, started_at, last_active_at, active_document_id, context_json)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (_new_id(), project_id, now, now, None, "{}"),
        )
        self.conn.commit()
        logger.info(
            "Research project created",
            extra={"project_id": project_id, "project_name": name},
        )
        return self.get_project(project_id)

    def list_projects(self) -> List[ResearchProject]:
        rows = self.conn.execute(
            """
            SELECT p.*,
                   (SELECT COUNT(*) FROM research_documents d WHERE d.project_id = p.id) AS document_count,
                   (SELECT COUNT(*) FROM research_notes n WHERE n.project_id = p.id) AS note_count
            FROM research_projects p
            ORDER BY COALESCE(p.last_session_at, p.updated_at) DESC
            """
        ).fetchall()
        return [self._row_to_project(row) for row in rows]

    def get_project(self, project_id: str) -> ResearchProject:
        row = self.conn.execute(
            """
            SELECT p.*,
                   (SELECT COUNT(*) FROM research_documents d WHERE d.project_id = p.id) AS document_count,
                   (SELECT COUNT(*) FROM research_notes n WHERE n.project_id = p.id) AS note_count
            FROM research_projects p WHERE p.id = ?
            """,
            (project_id,),
        ).fetchone()
        if not row:
            raise KeyError(f"Project not found: {project_id}")
        return self._row_to_project(row)

    def get_project_detail(self, project_id: str) -> ProjectDetail:
        project = self.get_project(project_id)
        documents = self.list_documents(project_id)
        notes = self.list_notes(project_id)
        session = self.get_session(project_id)
        conversations = self.list_conversations(project_id)
        active_conversation = None
        if session and session.active_conversation_id:
            try:
                active_conversation = self.get_conversation_detail(session.active_conversation_id)
            except KeyError:
                pass
        return ProjectDetail(
            project=project,
            documents=documents,
            notes=notes,
            session=session,
            conversations=conversations,
            active_conversation=active_conversation,
        )

    def update_project(
        self,
        project_id: str,
        name: str | None = None,
        description: str | None = None,
    ) -> ResearchProject:
        project = self.get_project(project_id)
        new_name = name.strip() if name is not None else project.name
        new_desc = description.strip() if description is not None else project.description
        now = _utc_now()
        self.conn.execute(
            """
            UPDATE research_projects
            SET name = ?, description = ?, updated_at = ?
            WHERE id = ?
            """,
            (new_name, new_desc, now, project_id),
        )
        self.conn.commit()
        logger.info("Research project updated", extra={"project_id": project_id})
        return self.get_project(project_id)

    def touch_project(self, project_id: str) -> None:
        self._touch_project_unlocked(project_id)
        self.conn.commit()

    def _touch_project_unlocked(self, project_id: str) -> None:
        now = _utc_now()
        self.conn.execute(
            "UPDATE research_projects SET updated_at = ?, last_session_at = ? WHERE id = ?",
            (now, now, project_id),
        )

    # ── Documents ─────────────────────────────────────────────────────────────

    def add_document(
        self,
        project_id: str,
        filename: str,
        text_content: str,
        page_count: int,
        file_bytes: bytes | None = None,
    ) -> ResearchDocument:
        self.get_project(project_id)  # validate exists
        doc_id = _new_id()
        now = _utc_now()
        file_path: str | None = None

        if file_bytes:
            safe_name = f"{doc_id}_{os.path.basename(filename)}"
            file_path = os.path.join(self.upload_dir, safe_name)
            with open(file_path, "wb") as fh:
                fh.write(file_bytes)

        char_count = len(text_content)
        self.conn.execute(
            """
            INSERT INTO research_documents
            (id, project_id, filename, text_content, page_count, char_count,
             file_path, uploaded_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                doc_id,
                project_id,
                filename,
                text_content,
                page_count,
                char_count,
                file_path,
                now,
            ),
        )
        self._index_fts("document", doc_id, project_id, filename, text_content)
        self._touch_project_unlocked(project_id)
        self.conn.commit()

        logger.info(
            "Document added",
            extra={"project_id": project_id, "document_id": doc_id, "document_filename": filename},
        )
        return self.get_document(doc_id)

    def get_document(self, document_id: str) -> ResearchDocument:
        row = self.conn.execute(
            "SELECT * FROM research_documents WHERE id = ?", (document_id,)
        ).fetchone()
        if not row:
            raise KeyError(f"Document not found: {document_id}")
        return self._row_to_document(row)

    def list_documents(self, project_id: str) -> List[ResearchDocument]:
        rows = self.conn.execute(
            "SELECT * FROM research_documents WHERE project_id = ? ORDER BY uploaded_at DESC",
            (project_id,),
        ).fetchall()
        return [self._row_to_document(row) for row in rows]

    def update_document_summary(self, document_id: str, summary: str) -> ResearchDocument:
        now = _utc_now()
        doc = self.get_document(document_id)
        self.conn.execute(
            """
            UPDATE research_documents
            SET summary = ?, summarized_at = ?
            WHERE id = ?
            """,
            (summary, now, document_id),
        )
        self._index_fts(
            "document",
            document_id,
            doc.project_id,
            doc.filename,
            f"{doc.text_content}\n\n{summary}",
        )
        self._touch_project_unlocked(doc.project_id)
        self.conn.commit()
        return self.get_document(document_id)

    # ── Notes ─────────────────────────────────────────────────────────────────

    def create_note(
        self,
        project_id: str,
        title: str,
        body: str,
        document_id: str | None = None,
        tags: List[str] | None = None,
    ) -> ResearchNote:
        self.get_project(project_id)
        if document_id:
            self.get_document(document_id)

        note_id = _new_id()
        now = _utc_now()
        tag_list = tags or []
        self.conn.execute(
            """
            INSERT INTO research_notes
            (id, project_id, document_id, title, body, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                note_id,
                project_id,
                document_id,
                title.strip(),
                body,
                json.dumps(tag_list),
                now,
                now,
            ),
        )
        self._index_fts("note", note_id, project_id, title, body)
        self._touch_project_unlocked(project_id)
        self.conn.commit()

        logger.info("Note created", extra={"project_id": project_id, "note_id": note_id})
        return self.get_note(note_id)

    def get_note(self, note_id: str) -> ResearchNote:
        row = self.conn.execute(
            "SELECT * FROM research_notes WHERE id = ?", (note_id,)
        ).fetchone()
        if not row:
            raise KeyError(f"Note not found: {note_id}")
        return self._row_to_note(row)

    def list_notes(
        self, project_id: str, tag: str | None = None
    ) -> List[ResearchNote]:
        if tag:
            rows = self.conn.execute(
                """
                SELECT * FROM research_notes
                WHERE project_id = ? AND tags LIKE ?
                ORDER BY updated_at DESC
                """,
                (project_id, f'%"{tag}"%'),
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT * FROM research_notes WHERE project_id = ? ORDER BY updated_at DESC",
                (project_id,),
            ).fetchall()
        return [self._row_to_note(row) for row in rows]

    def delete_note(self, note_id: str) -> None:
        note = self.get_note(note_id)
        self.conn.execute("DELETE FROM research_notes WHERE id = ?", (note_id,))
        self.conn.execute(
            "DELETE FROM research_fts WHERE entity_type = ? AND entity_id = ?",
            ("note", note_id),
        )
        self._touch_project_unlocked(note.project_id)
        self.conn.commit()
        logger.info("Note deleted", extra={"note_id": note_id, "project_id": note.project_id})

    def update_note(
        self,
        note_id: str,
        title: str | None = None,
        body: str | None = None,
        tags: List[str] | None = None,
    ) -> ResearchNote:
        note = self.get_note(note_id)
        new_title = title.strip() if title is not None else note.title
        new_body = body if body is not None else note.body
        new_tags = tags if tags is not None else note.tags
        now = _utc_now()

        self.conn.execute(
            """
            UPDATE research_notes
            SET title = ?, body = ?, tags = ?, updated_at = ?
            WHERE id = ?
            """,
            (new_title, new_body, json.dumps(new_tags), now, note_id),
        )
        self._index_fts("note", note_id, note.project_id, new_title, new_body)
        self._touch_project_unlocked(note.project_id)
        self.conn.commit()

        return self.get_note(note_id)

    # ── Conversations & Q&A ───────────────────────────────────────────────────

    def create_conversation(
        self,
        project_id: str,
        title: str,
        document_id: str | None = None,
    ) -> ResearchConversation:
        self.get_project(project_id)
        if document_id:
            self.get_document(document_id)
        conv_id = _new_id()
        now = _utc_now()
        self.conn.execute(
            """
            INSERT INTO research_conversations
            (id, project_id, title, document_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (conv_id, project_id, title.strip(), document_id, now, now),
        )
        self._touch_project_unlocked(project_id)
        self.conn.commit()
        return self.get_conversation(conv_id)

    def get_conversation(self, conversation_id: str) -> ResearchConversation:
        row = self.conn.execute(
            """
            SELECT c.*,
                   (SELECT COUNT(*) FROM research_messages m WHERE m.conversation_id = c.id) AS message_count
            FROM research_conversations c WHERE c.id = ?
            """,
            (conversation_id,),
        ).fetchone()
        if not row:
            raise KeyError(f"Conversation not found: {conversation_id}")
        return self._row_to_conversation(row)

    def list_conversations(self, project_id: str) -> List[ResearchConversation]:
        rows = self.conn.execute(
            """
            SELECT c.*,
                   (SELECT COUNT(*) FROM research_messages m WHERE m.conversation_id = c.id) AS message_count
            FROM research_conversations c
            WHERE c.project_id = ?
            ORDER BY c.updated_at DESC
            """,
            (project_id,),
        ).fetchall()
        return [self._row_to_conversation(row) for row in rows]

    def get_conversation_detail(self, conversation_id: str) -> ConversationDetail:
        conversation = self.get_conversation(conversation_id)
        messages = self.list_messages(conversation_id)
        return ConversationDetail(conversation=conversation, messages=messages)

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        sources: List[str] | None = None,
    ) -> ResearchMessage:
        conv = self.get_conversation(conversation_id)
        msg_id = _new_id()
        now = _utc_now()
        source_list = sources or []
        self.conn.execute(
            """
            INSERT INTO research_messages
            (id, conversation_id, role, content, sources_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (msg_id, conversation_id, role, content, json.dumps(source_list), now),
        )
        self.conn.execute(
            "UPDATE research_conversations SET updated_at = ? WHERE id = ?",
            (now, conversation_id),
        )
        self._index_fts("conversation", msg_id, conv.project_id, f"{role}: {content[:80]}", content)
        self._touch_project_unlocked(conv.project_id)
        self.conn.commit()
        return self.get_message(msg_id)

    def get_message(self, message_id: str) -> ResearchMessage:
        row = self.conn.execute(
            "SELECT * FROM research_messages WHERE id = ?", (message_id,)
        ).fetchone()
        if not row:
            raise KeyError(f"Message not found: {message_id}")
        return self._row_to_message(row)

    def list_messages(self, conversation_id: str) -> List[ResearchMessage]:
        rows = self.conn.execute(
            """
            SELECT * FROM research_messages
            WHERE conversation_id = ?
            ORDER BY created_at ASC
            """,
            (conversation_id,),
        ).fetchall()
        return [self._row_to_message(row) for row in rows]

    def set_active_conversation(self, project_id: str, conversation_id: str) -> ResearchSession:
        self.get_conversation(conversation_id)
        session = self.get_session(project_id)
        ctx = session.context if session else {}
        ctx["active_conversation_id"] = conversation_id
        return self.resume_session(project_id, context=ctx)

    # ── Sessions ──────────────────────────────────────────────────────────────

    def resume_session(
        self,
        project_id: str,
        active_document_id: str | None = None,
        context: dict | None = None,
    ) -> ResearchSession:
        self.get_project(project_id)
        if active_document_id:
            self.get_document(active_document_id)

        now = _utc_now()
        existing = self.get_session(project_id)
        ctx = context if context is not None else (existing.context if existing else {})

        self.conn.execute(
            """
            INSERT INTO research_sessions
            (id, project_id, started_at, last_active_at, active_document_id, context_json)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(project_id) DO UPDATE SET
                last_active_at = excluded.last_active_at,
                active_document_id = excluded.active_document_id,
                context_json = excluded.context_json
            """,
            (
                existing.id if existing else _new_id(),
                project_id,
                existing.started_at if existing else now,
                now,
                active_document_id,
                json.dumps(ctx),
            ),
        )
        self.conn.execute(
            "UPDATE research_projects SET updated_at = ?, last_session_at = ? WHERE id = ?",
            (now, now, project_id),
        )
        self.conn.commit()

        logger.info("Session resumed", extra={"project_id": project_id})
        return self.get_session(project_id)

    def get_session(self, project_id: str) -> ResearchSession | None:
        row = self.conn.execute(
            "SELECT * FROM research_sessions WHERE project_id = ?", (project_id,)
        ).fetchone()
        if not row:
            return None
        return self._row_to_session(row)
    # ── Search ────────────────────────────────────────────────────────────────

    def search(
        self,
        query: str,
        project_id: str | None = None,
        limit: int = 20,
    ) -> List[SearchResult]:
        if not query or not query.strip():
            return []

        terms = query.strip()
        sql = """
            SELECT entity_type, entity_id, project_id, title, body,
                   bm25(research_fts) AS score
            FROM research_fts
            WHERE research_fts MATCH ?
        """
        params: list = [terms]

        if project_id:
            sql += " AND project_id = ?"
            params.append(project_id)

        sql += " ORDER BY score LIMIT ?"
        params.append(limit)

        try:
            rows = self.conn.execute(sql, params).fetchall()
        except sqlite3.OperationalError as exc:
            logger.warning("FTS search failed", extra={"query": terms, "error": str(exc)})
            return self._fallback_search(terms, project_id, limit)

        results: List[SearchResult] = []
        for row in rows:
            snippet = self._make_snippet(row["body"], terms)
            results.append(
                SearchResult(
                    result_type=row["entity_type"],
                    id=row["entity_id"],
                    project_id=row["project_id"],
                    title=row["title"],
                    snippet=snippet,
                    score=float(row["score"]) if row["score"] is not None else 0.0,
                )
            )
        return results

    def _fallback_search(
        self, query: str, project_id: str | None, limit: int
    ) -> List[SearchResult]:
        """LIKE-based fallback when FTS query syntax fails."""
        q = f"%{query.lower()}%"
        results: List[SearchResult] = []

        doc_sql = """
            SELECT id, project_id, filename, text_content
            FROM research_documents
            WHERE (LOWER(filename) LIKE ? OR LOWER(text_content) LIKE ?)
        """
        doc_params: list = [q, q]
        if project_id:
            doc_sql += " AND project_id = ?"
            doc_params.append(project_id)
        doc_sql += f" LIMIT {limit}"

        for row in self.conn.execute(doc_sql, doc_params).fetchall():
            results.append(
                SearchResult(
                    result_type="document",
                    id=row["id"],
                    project_id=row["project_id"],
                    title=row["filename"],
                    snippet=self._make_snippet(row["text_content"], query),
                    score=0.5,
                )
            )

        note_sql = """
            SELECT id, project_id, title, body
            FROM research_notes
            WHERE (LOWER(title) LIKE ? OR LOWER(body) LIKE ?)
        """
        note_params: list = [q, q]
        if project_id:
            note_sql += " AND project_id = ?"
            note_params.append(project_id)
        note_sql += f" LIMIT {limit}"

        for row in self.conn.execute(note_sql, note_params).fetchall():
            results.append(
                SearchResult(
                    result_type="note",
                    id=row["id"],
                    project_id=row["project_id"],
                    title=row["title"],
                    snippet=self._make_snippet(row["body"], query),
                    score=0.5,
                )
            )

        return results[:limit]

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _index_fts(
        self,
        entity_type: str,
        entity_id: str,
        project_id: str,
        title: str,
        body: str,
    ) -> None:
        self.conn.execute(
            "DELETE FROM research_fts WHERE entity_type = ? AND entity_id = ?",
            (entity_type, entity_id),
        )
        self.conn.execute(
            """
            INSERT INTO research_fts (entity_type, entity_id, project_id, title, body)
            VALUES (?, ?, ?, ?, ?)
            """,
            (entity_type, entity_id, project_id, title, body or ""),
        )

    @staticmethod
    def _make_snippet(text: str, query: str, radius: int = 120) -> str:
        if not text:
            return ""
        lower = text.lower()
        idx = lower.find(query.lower().split()[0] if query.split() else query.lower())
        if idx < 0:
            return text[:radius] + ("..." if len(text) > radius else "")
        start = max(0, idx - radius // 2)
        end = min(len(text), idx + radius)
        snippet = text[start:end]
        if start > 0:
            snippet = "..." + snippet
        if end < len(text):
            snippet += "..."
        return snippet

    @staticmethod
    def _row_to_project(row: sqlite3.Row) -> ResearchProject:
        return ResearchProject(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            last_session_at=row["last_session_at"],
            document_count=row["document_count"] if "document_count" in row.keys() else 0,
            note_count=row["note_count"] if "note_count" in row.keys() else 0,
        )

    @staticmethod
    def _row_to_document(row: sqlite3.Row) -> ResearchDocument:
        return ResearchDocument(
            id=row["id"],
            project_id=row["project_id"],
            filename=row["filename"],
            text_content=row["text_content"],
            summary=row["summary"] or "",
            page_count=row["page_count"],
            char_count=row["char_count"],
            uploaded_at=row["uploaded_at"],
            summarized_at=row["summarized_at"],
        )

    @staticmethod
    def _row_to_note(row: sqlite3.Row) -> ResearchNote:
        tags_raw = row["tags"] or "[]"
        try:
            tags = json.loads(tags_raw)
        except json.JSONDecodeError:
            tags = []
        return ResearchNote(
            id=row["id"],
            project_id=row["project_id"],
            document_id=row["document_id"],
            title=row["title"],
            body=row["body"],
            tags=tags,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    @staticmethod
    def _row_to_session(row: sqlite3.Row) -> ResearchSession:
        try:
            context = json.loads(row["context_json"] or "{}")
        except json.JSONDecodeError:
            context = {}
        return ResearchSession(
            id=row["id"],
            project_id=row["project_id"],
            started_at=row["started_at"],
            last_active_at=row["last_active_at"],
            active_document_id=row["active_document_id"],
            active_conversation_id=context.get("active_conversation_id"),
            context=context,
        )

    @staticmethod
    def _row_to_conversation(row: sqlite3.Row) -> ResearchConversation:
        return ResearchConversation(
            id=row["id"],
            project_id=row["project_id"],
            title=row["title"],
            document_id=row["document_id"],
            message_count=row["message_count"] if "message_count" in row.keys() else 0,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    @staticmethod
    def _row_to_message(row: sqlite3.Row) -> ResearchMessage:
        try:
            sources = json.loads(row["sources_json"] or "[]")
        except json.JSONDecodeError:
            sources = []
        return ResearchMessage(
            id=row["id"],
            conversation_id=row["conversation_id"],
            role=row["role"],
            content=row["content"],
            sources=sources,
            created_at=row["created_at"],
        )
