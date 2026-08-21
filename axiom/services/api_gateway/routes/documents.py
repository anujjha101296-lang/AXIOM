from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import datetime

from axiom.core.database import get_db
from axiom.core.repositories import ProjectRepository, DocumentRepository
from axiom.services.api_gateway.auth import get_current_user
from axiom.research.pdf_extractor import PdfExtractor
from axiom.research.chunking import TextChunker
from axiom.core.models import DocumentChunk
from axiom.research.embeddings import get_embedding_provider, EmbeddingConfigurationError
from axiom.observability.logger import get_logger
import json

logger = get_logger(__name__)
router = APIRouter(prefix="/projects/{project_id}/documents", tags=["documents"])

class DocumentResponse(BaseModel):
    id: str
    project_id: str
    title: str
    status: str
    indexing_status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    project_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    project_repo = ProjectRepository(db)
    project = await project_repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this project")

    doc_repo = DocumentRepository(db)
    document = await doc_repo.create(project_id=project_id, title=file.filename)
    await db.commit()
    
    try:
        # 1. Extract text from PDF
        extractor = PdfExtractor()
        content = await file.read()
        extraction_result = extractor.extract_bytes(content)
        
        if not extraction_result.text.strip():
            raise ValueError("No text could be extracted from this document")

        # 2. Chunk the text
        chunker = TextChunker(chunk_size=500, chunk_overlap=50)
        text_chunks = chunker.chunk(
            extraction_result.text,
            document_id=document.id,
            project_id=project_id,
        )

        if not text_chunks:
            raise ValueError("Document produced no usable chunks after extraction")

        # 3. Generate embeddings for all chunks in a batch
        try:
            provider = get_embedding_provider()
            chunk_texts = [c.content for c in text_chunks]
            embeddings = provider.embed_batch(chunk_texts)
            dim = provider.dimension
        except EmbeddingConfigurationError as e:
            logger.warning("Embedding provider not configured, storing chunks without vectors",
                           extra={"error": str(e)})
            embeddings = [None] * len(text_chunks)
            dim = None

        # 4. Persist chunks with their embeddings
        for i, (tc, emb) in enumerate(zip(text_chunks, embeddings)):
            chunk = DocumentChunk(
                document_id=document.id,
                content=tc.content,
                chunk_index=tc.chunk_index,
                char_start=tc.char_start,
                char_end=tc.char_end,
                embedding=json.dumps(emb) if emb is not None else None,
                embedding_dim=dim,
            )
            db.add(chunk)

        # 5. Mark document as indexed
        await doc_repo.update_status(document.id, "completed")
        document.indexing_status = "INDEXED"
        db.add(document)
        await db.commit()
        
        logger.info(
            "Document indexed",
            extra={
                "document_id": document.id,
                "project_id": project_id,
                "chunks": len(text_chunks),
                "pages": extraction_result.page_count,
            },
        )
    except Exception as e:
        logger.error("Document ingestion failed", extra={"error": str(e), "document_id": document.id})
        await doc_repo.update_status(document.id, "failed")
        document.indexing_status = "INDEX_FAILED"
        db.add(document)
        await db.commit()
        raise HTTPException(status_code=400, detail=f"Failed to process document: {str(e)}")
        
    return document

@router.get("", response_model=List[DocumentResponse])
async def list_documents(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    project_repo = ProjectRepository(db)
    project = await project_repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this project")

    doc_repo = DocumentRepository(db)
    documents = await doc_repo.list_for_project(project_id)
    return documents

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    project_id: str,
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    project_repo = ProjectRepository(db)
    project = await project_repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this project")

    doc_repo = DocumentRepository(db)
    document = await doc_repo.get(document_id)
    if not document or document.project_id != project_id:
        raise HTTPException(status_code=404, detail="Document not found")
        
    return document

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    project_id: str,
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    project_repo = ProjectRepository(db)
    project = await project_repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this project")

    doc_repo = DocumentRepository(db)
    document = await doc_repo.get(document_id)
    if not document or document.project_id != project_id:
        raise HTTPException(status_code=404, detail="Document not found")
        
    await doc_repo.delete(document_id)
    await db.commit()
    return None
