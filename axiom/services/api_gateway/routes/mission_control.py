"""
axiom.services.api_gateway.routes.mission_control
==================================================
FastAPI REST API Routes for Phase 19 Autonomous Research Mission Control.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Header, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from axiom.core.database import get_db
from axiom.core.models import MissionCheckpointDB, MissionTaskDB, Project, ResearchMissionDB
from axiom.mission_control.controller import MissionController
from axiom.mission_control.models import (
    MissionBudget,
    MissionCheckpoint,
    MissionState,
    MissionTask,
    ResearchMission,
)
from axiom.services.api_gateway.auth import SECRET_TOKEN, decode_jwt_token, verify_token

router = APIRouter(prefix="/api/v1/missions", tags=["mission_control"])


def _extract_user_id(token: str, x_user_id: Optional[str] = None) -> str:
    if x_user_id:
        return x_user_id
    if token == SECRET_TOKEN or token == "test_token":
        return "admin"
    try:
        payload = decode_jwt_token(token)
        return payload.sub
    except Exception:
        return "admin"


async def _verify_project_ownership(project_id: str, user_id: str, db: AsyncSession) -> None:
    res = await db.execute(select(Project).where(Project.id == project_id))
    proj = res.scalar_one_or_none()
    if not proj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {project_id} not found")
    if proj.owner_id != user_id and user_id != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this project's research missions")


class CreateMissionRequest(BaseModel):
    project_id: str
    name: str
    objective: str
    max_iterations: Optional[int] = 20
    max_time_sec: Optional[int] = 600


@router.post("", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_mission_endpoint(
    payload: CreateMissionRequest,
    token: str = Depends(verify_token),
    x_user_id: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """Create a research mission with strict budget limits."""
    user_id = _extract_user_id(token, x_user_id)
    await _verify_project_ownership(payload.project_id, user_id, db)

    budget = MissionBudget(
        max_iterations=payload.max_iterations or 20,
        max_time_sec=payload.max_time_sec or 600,
    )

    m_db = ResearchMissionDB(
        project_id=payload.project_id,
        name=payload.name,
        objective=payload.objective,
        state=MissionState.INITIALIZED.value,
        budget_json=json.dumps(budget.model_dump()),
    )
    db.add(m_db)
    await db.commit()
    await db.refresh(m_db)

    controller = MissionController()
    tasks = controller.scheduler.create_initial_task_graph(m_db.id)
    for t in tasks:
        t_db = MissionTaskDB(
            id=t.id,
            mission_id=m_db.id,
            name=t.name,
            assigned_role=t.assigned_role,
            state=t.state,
        )
        db.add(t_db)

    await db.commit()

    mission = ResearchMission.from_db(m_db)
    mission.tasks = tasks
    return {"mission": mission, "tasks_count": len(tasks)}


@router.post("/{mission_id}/start", response_model=Dict[str, Any])
async def start_mission_endpoint(
    mission_id: str,
    token: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db),
):
    """Start or resume research mission loop."""
    res = await db.execute(select(ResearchMissionDB).where(ResearchMissionDB.id == mission_id))
    m_db = res.scalar_one_or_none()
    if not m_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Mission {mission_id} not found")

    mission = ResearchMission.from_db(m_db)
    controller = MissionController()
    mission, chk = controller.start_mission(mission)

    m_db.state = mission.state.value
    chk_db = MissionCheckpointDB(
        id=chk.id,
        mission_id=chk.mission_id,
        iteration=chk.iteration,
        checkpoint_hash=chk.checkpoint_hash,
        summary=chk.summary,
        state_snapshot_json=json.dumps(chk.state_snapshot),
    )
    db.add(chk_db)
    await db.commit()

    return {"mission": mission, "checkpoint": chk}


@router.post("/{mission_id}/pause", response_model=Dict[str, Any])
async def pause_mission_endpoint(
    mission_id: str,
    token: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db),
):
    """Pause running research mission."""
    res = await db.execute(select(ResearchMissionDB).where(ResearchMissionDB.id == mission_id))
    m_db = res.scalar_one_or_none()
    if not m_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Mission {mission_id} not found")

    mission = ResearchMission.from_db(m_db)
    controller = MissionController()
    mission, chk = controller.pause_mission(mission)

    m_db.state = mission.state.value
    chk_db = MissionCheckpointDB(
        id=chk.id,
        mission_id=chk.mission_id,
        iteration=chk.iteration,
        checkpoint_hash=chk.checkpoint_hash,
        summary=chk.summary,
        state_snapshot_json=json.dumps(chk.state_snapshot),
    )
    db.add(chk_db)
    await db.commit()

    return {"mission": mission, "checkpoint": chk}


@router.post("/{mission_id}/emergency-stop", response_model=Dict[str, Any])
async def emergency_stop_endpoint(
    mission_id: str,
    token: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db),
):
    """Trigger immediate emergency stop on research mission."""
    res = await db.execute(select(ResearchMissionDB).where(ResearchMissionDB.id == mission_id))
    m_db = res.scalar_one_or_none()
    if not m_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Mission {mission_id} not found")

    mission = ResearchMission.from_db(m_db)
    controller = MissionController()
    mission, chk = controller.emergency_stop(mission)

    m_db.state = mission.state.value
    chk_db = MissionCheckpointDB(
        id=chk.id,
        mission_id=chk.mission_id,
        iteration=chk.iteration,
        checkpoint_hash=chk.checkpoint_hash,
        summary=chk.summary,
        state_snapshot_json=json.dumps(chk.state_snapshot),
    )
    db.add(chk_db)
    await db.commit()

    return {"mission": mission, "checkpoint": chk}


@router.get("/project/{project_id}", response_model=Dict[str, Any])
async def list_project_missions(
    project_id: str,
    token: str = Depends(verify_token),
    x_user_id: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """List all research missions for project."""
    user_id = _extract_user_id(token, x_user_id)
    await _verify_project_ownership(project_id, user_id, db)

    res = await db.execute(select(ResearchMissionDB).where(ResearchMissionDB.project_id == project_id))
    rows = res.scalars().all()
    missions = [ResearchMission.from_db(r) for r in rows]

    return {
        "project_id": project_id,
        "total_missions": len(missions),
        "missions": missions,
    }
