import json
import math
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from axiom.core.models import Document, DocumentChunk
from axiom.research.embeddings import get_embedding_provider

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_v1 = math.sqrt(sum(a * a for a in v1))
    norm_v2 = math.sqrt(sum(b * b for b in v2))
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
    return dot_product / (norm_v1 * norm_v2)

async def search_chunks(query: str, project_id: str, db: AsyncSession, limit: int = 5) -> List[Dict[str, Any]]:
    provider = get_embedding_provider()
    query_embeddings = provider.embed_batch([query])
    if not query_embeddings:
        return []
    query_vector = query_embeddings[0]

    stmt = (
        select(DocumentChunk, Document)
        .join(Document, Document.id == DocumentChunk.document_id)
        .where(Document.project_id == project_id)
        .where(DocumentChunk.embedding.isnot(None))
    )
    result = await db.execute(stmt)
    
    scored_chunks = []
    for chunk, document in result.all():
        try:
            chunk_vector = json.loads(chunk.embedding)
            score = cosine_similarity(query_vector, chunk_vector)
            scored_chunks.append({
                "chunk_id": chunk.id,
                "document_id": document.id,
                "document_title": document.title,
                "content": chunk.content,
                "score": score
            })
        except (json.JSONDecodeError, TypeError, ValueError):
            continue

    scored_chunks.sort(key=lambda x: x["score"], reverse=True)
    return scored_chunks[:limit]
