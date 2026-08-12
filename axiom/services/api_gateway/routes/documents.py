from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import datetime

from axiom.core.database import get_db
from axiom.core.repositories import ProjectRepository, DocumentRepository
from axiom.services.api_gateway.auth import get_current_user
from axiom.research.pdf_extractor import PdfExtractor
from axiom.core.models import DocumentChunk
from axiom.research.embeddings import get_embedding_provider
import json

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
    await db.commit() # Commit to make sure document exists if something fails below
    
    try:
        extractor = PdfExtractor()
        content = await file.read()
        extraction_result = extractor.extract_bytes(content)
        
        # update document status
        await doc_repo.update_status(document.id, "completed")
        
        # chunking (storing as one chunk for now as per instructions)
        chunk = DocumentChunk(document_id=document.id, content=extraction_result.text)
        
        # embed chunk
        provider = get_embedding_provider()
        embeddings = provider.embed_batch([chunk.content])
        if embeddings:
            chunk.embedding = json.dumps(embeddings[0])
            
        document.indexing_status = "INDEXED"
        db.add(chunk)
        await db.commit()
    except Exception as e:
        await doc_repo.update_status(document.id, "failed")
        document.indexing_status = "INDEX_FAILED"
        db.add(document)
        await db.commit()
        raise HTTPException(status_code=400, detail=f"Failed to process document: {str(e)}")
        
    # We may need to refresh the document after commits or return dict/model directly
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
