from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from axiom.core.database import get_db
from axiom.core.repositories import ProjectRepository
from axiom.services.api_gateway.auth import get_current_user
from axiom.research.retrieval import search_chunks

router = APIRouter(prefix="/projects/{project_id}/search", tags=["search"])

class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 5

class SearchResult(BaseModel):
    chunk_id: str
    document_id: str
    document_title: str
    content: str
    score: float

@router.post("", response_model=List[SearchResult])
async def search_project(
    project_id: str,
    request: SearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    project_repo = ProjectRepository(db)
    project = await project_repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this project")

    results = await search_chunks(
        query=request.query,
        project_id=project_id,
        db=db,
        limit=request.limit
    )
    
    return results
