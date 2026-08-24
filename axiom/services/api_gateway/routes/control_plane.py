"""
axiom.services.api_gateway.routes.control_plane
================================================
FastAPI REST API Routes for Phase 20 Production Control Plane.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Header, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from axiom.control_plane.models import AgentProfile, DomainEvent, WorkerNode, WorkerStatus
from axiom.control_plane.registry import AgentRegistry
from axiom.core.database import get_db
from axiom.core.models import AgentProfileDB, DomainEventDB, WorkerNodeDB
from axiom.services.api_gateway.auth import verify_token

router = APIRouter(prefix="/api/v1/control-plane", tags=["control_plane"])


class EmitEventRequest(BaseModel):
    project_id: str
    mission_id: Optional[str] = None
    task_id: Optional[str] = None
    event_type: str
    actor: Optional[str] = "system"
    payload: Optional[Dict[str, Any]] = None


@router.get("/agents", response_model=Dict[str, Any])
async def list_agent_profiles_endpoint(
    token: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db),
):
    """List registered canonical specialist agent profiles."""
    registry = AgentRegistry()
    profiles = registry.list_profiles()

    # Persist profiles if missing
    for p in profiles:
        res = await db.execute(select(AgentProfileDB).where(AgentProfileDB.role == p.role))
        if not res.scalar_one_or_none():
            p_db = AgentProfileDB(
                id=p.id,
                name=p.name,
                role=p.role,
                allowed_tools_json=json.dumps(p.allowed_tools),
                allowed_models_json=json.dumps(p.allowed_models),
                max_steps=p.max_steps,
                max_tokens=p.max_tokens,
                timeout_sec=p.timeout_sec,
            )
            db.add(p_db)

    await db.commit()
    return {"total_agents": len(profiles), "agents": profiles}


@router.post("/events", response_model=DomainEvent, status_code=status.HTTP_201_CREATED)
async def emit_domain_event_endpoint(
    payload: EmitEventRequest,
    token: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db),
):
    """Emit an append-only domain event for auditability."""
    evt = DomainEvent(
        project_id=payload.project_id,
        mission_id=payload.mission_id,
        task_id=payload.task_id,
        event_type=payload.event_type,
        actor=payload.actor or "system",
        payload=payload.payload or {},
    )

    evt_db = DomainEventDB(
        id=evt.id,
        project_id=evt.project_id,
        mission_id=evt.mission_id,
        task_id=evt.task_id,
        event_type=evt.event_type,
        actor=evt.actor,
        payload_json=json.dumps(evt.payload),
    )
    db.add(evt_db)
    await db.commit()

    return evt


@router.get("/events", response_model=Dict[str, Any])
async def list_domain_events_endpoint(
    token: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db),
):
    """List append-only domain events."""
    res = await db.execute(select(DomainEventDB))
    rows = res.scalars().all()
    events = [DomainEvent.from_db(r) for r in rows]

    return {"total_events": len(events), "events": events}


@router.get("/workers", response_model=Dict[str, Any])
async def list_worker_nodes_endpoint(
    token: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db),
):
    """List active background worker nodes."""
    res = await db.execute(select(WorkerNodeDB))
    rows = res.scalars().all()
    workers = [WorkerNode.from_db(r) for r in rows]

    return {"total_workers": len(workers), "workers": workers}
