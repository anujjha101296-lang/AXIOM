from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from axiom.core.database import get_db
from axiom.core.repositories import ProjectRepository
from axiom.services.api_gateway.auth import get_current_user

router = APIRouter(prefix="/projects", tags=["projects"])

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    owner_id: str
    
    class Config:
        from_attributes = True

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    repo = ProjectRepository(db)
    project = await repo.create(
        owner_id=current_user.id,
        name=data.name,
        description=data.description
    )
    await db.commit()
    return project

@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    repo = ProjectRepository(db)
    return await repo.list_for_user(owner_id=current_user.id)

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    repo = ProjectRepository(db)
    project = await repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this project")
    return project

@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    repo = ProjectRepository(db)
    project = await repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this project")
    
    if data.name is not None:
        project.name = data.name
    if data.description is not None:
        project.description = data.description
        
    await db.commit()
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    repo = ProjectRepository(db)
    project = await repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this project")
    
    await repo.delete(project_id)
    await db.commit()
    return None
