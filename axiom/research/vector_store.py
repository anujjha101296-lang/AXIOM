"""Lightweight cosine-similarity vector store backed by SQLite.

This module reads chunk embeddings stored as JSON float arrays in the
`document_chunks` table and performs exact nearest-neighbour search in
Python. This is suitable for development and small corpora.

For production with large corpora, replace with pgvector or an ANN index.
Every query MUST enforce project isolation — no cross-project leakage.
"""

from __future__ import annotations

import json
import math
from typing import Any, List, Optional, Tuple

from axiom.observability.logger import get_logger

logger = get_logger(__name__)


def _dot(a: List[float], b: List[float]) -> float:
    """Dot product of two equal-length float lists."""
    return sum(x * y for x, y in zip(a, b))


def _norm(v: List[float]) -> float:
    """L2 norm of a float list."""
    return math.sqrt(sum(x * x for x in v))


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Cosine similarity in [-1, 1].  Returns 0.0 on zero-length vectors."""
    na = _norm(a)
    nb = _norm(b)
    if na == 0.0 or nb == 0.0:
        return 0.0
    return _dot(a, b) / (na * nb)


class VectorSearchResult:
    """A single ranked retrieval result."""

    __slots__ = ("chunk_id", "document_id", "project_id", "content", "score",
                 "chunk_index", "char_start", "char_end")

    def __init__(
        self,
        chunk_id: str,
        document_id: str,
        project_id: str,
        content: str,
        score: float,
        chunk_index: int = 0,
        char_start: Optional[int] = None,
        char_end: Optional[int] = None,
    ) -> None:
        self.chunk_id = chunk_id
        self.document_id = document_id
        self.project_id = project_id
        self.content = content
        self.score = score
        self.chunk_index = chunk_index
        self.char_start = char_start
        self.char_end = char_end

    def to_dict(self) -> dict:
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "project_id": self.project_id,
            "content": self.content,
            "score": self.score,
            "chunk_index": self.chunk_index,
            "char_start": self.char_start,
            "char_end": self.char_end,
        }


class VectorStore:
    """Project-isolated exact cosine-similarity search over SQLAlchemy Session."""

    async def search(
        self,
        db: Any,
        query_vector: List[float],
        project_id: str,
        top_k: int = 5,
        document_id: Optional[str] = None,
    ) -> List[VectorSearchResult]:
        """Search for the *top_k* most similar chunks within *project_id*.

        Parameters
        ----------
        db:
            SQLAlchemy AsyncSession.
        query_vector:
            Embedding of the search query (must match stored dimension).
        project_id:
            All results are restricted to this project — enforced at query level.
        top_k:
            Maximum number of results to return.
        document_id:
            Optional: restrict search to a single document.
        """
        from sqlalchemy import select
        from axiom.core.models import DocumentChunk, Document

        # Load all chunks belonging to this project (with optional doc filter)
        stmt = (
            select(DocumentChunk, Document)
            .join(Document, DocumentChunk.document_id == Document.id)
            .where(Document.project_id == project_id)  # PROJECT ISOLATION
        )
        if document_id is not None:
            stmt = stmt.where(DocumentChunk.document_id == document_id)

        result = await db.execute(stmt)
        rows = result.all()

        if not rows:
            logger.info("VectorStore: no chunks found", extra={"project_id": project_id})
            return []

        scored: List[Tuple[float, DocumentChunk, Document]] = []
        skipped = 0

        for chunk, doc in rows:
            if not chunk.embedding:
                skipped += 1
                continue
            try:
                stored_vec = json.loads(chunk.embedding)
            except (json.JSONDecodeError, TypeError):
                skipped += 1
                continue

            score = cosine_similarity(query_vector, stored_vec)
            scored.append((score, chunk, doc))

        if skipped:
            logger.warning(
                "VectorStore: skipped chunks without embeddings",
                extra={"count": skipped, "project_id": project_id},
            )

        # Sort descending by cosine similarity
        scored.sort(key=lambda t: t[0], reverse=True)

        return [
            VectorSearchResult(
                chunk_id=chunk.id,
                document_id=chunk.document_id,
                project_id=doc.project_id,
                content=chunk.content,
                score=round(score, 6),
                chunk_index=getattr(chunk, "chunk_index", 0),
                char_start=getattr(chunk, "char_start", None),
                char_end=getattr(chunk, "char_end", None),
            )
            for score, chunk, doc in scored[:top_k]
        ]
