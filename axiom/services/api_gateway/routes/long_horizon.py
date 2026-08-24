"""
axiom.services.api_gateway.routes.long_horizon
===============================================
FastAPI REST API Routes for Phase 17 Long-Horizon Mathematical Research Engine.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Header, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from axiom.core.database import get_db
from axiom.core.models import (
    ApproachMemoryDB,
    Project,
    ResearchAttemptDB,
    ResearchDecisionDB,
    ResearchMilestoneDB,
    ResearchProblemDB,
    ResearchSubproblemDB,
    ResearchTaskDB,
)
from axiom.long_horizon.critic import ResearchCriticEngine
from axiom.long_horizon.decomposition import ProblemDecompositionEngine
from axiom.long_horizon.loop import LongHorizonResearchLoop
from axiom.long_horizon.memory import ApproachMemoryEngine
from axiom.long_horizon.models import (
    ApproachMemory,
    ApproachStatus,
    CriticRecommendation,
    ResearchAttempt,
    ResearchMilestone,
    ResearchProblem,
    ResearchSubproblem,
    ResearchTask,
    TaskState,
)
from axiom.services.api_gateway.auth import SECRET_TOKEN, decode_jwt_token, verify_token

router = APIRouter(prefix="/api/v1/long-horizon", tags=["long_horizon"])


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
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this project's research problems")


class CreateProblemRequest(BaseModel):
    project_id: str
    title: str
    description: str
    formal_statement: Optional[str] = ""


class ExecuteTaskStepRequest(BaseModel):
    problem_id: str
    subproblem_id: str
    task_id: str
    method: str = "Direct Proof"
    approach_description: str


@router.post("/problem", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_research_problem_endpoint(
    payload: CreateProblemRequest,
    token: str = Depends(verify_token),
    x_user_id: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """Create long-horizon research problem and generate subproblem decomposition."""
    user_id = _extract_user_id(token, x_user_id)
    await _verify_project_ownership(payload.project_id, user_id, db)

    prob_db = ResearchProblemDB(
        project_id=payload.project_id,
        title=payload.title,
        description=payload.description,
        formal_statement=payload.formal_statement or "",
        status=TaskState.PLANNED.value,
    )
    db.add(prob_db)
    await db.commit()
    await db.refresh(prob_db)

    decomposer = ProblemDecompositionEngine()
    subproblems = decomposer.decompose_problem(prob_db.id, payload.title, payload.description)

    sub_dbs = []
    for sp in subproblems:
        sp_db = ResearchSubproblemDB(
            id=sp.id,
            problem_id=prob_db.id,
            title=sp.title,
            statement=sp.statement,
            dependencies_json=json.dumps(sp.dependencies),
            status=sp.status.value,
        )
        db.add(sp_db)
        sub_dbs.append(sp_db)

        # Create default initial task for subproblem
        task_db = ResearchTaskDB(
            subproblem_id=sp.id,
            name=f"Task for {sp.title}",
            strategy="Decomposition",
            state=TaskState.PLANNED.value,
        )
        db.add(task_db)

    await db.commit()

    prob = ResearchProblem.from_db(prob_db)
    prob.subproblems = subproblems
    return {"problem": prob, "subproblems_count": len(subproblems)}


@router.post("/task/execute", response_model=Dict[str, Any])
async def execute_task_step_endpoint(
    payload: ExecuteTaskStepRequest,
    token: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db),
):
    """Execute research task step with approach memory duplicate detection."""
    res_p = await db.execute(select(ResearchProblemDB).where(ResearchProblemDB.id == payload.problem_id))
    prob_db = res_p.scalar_one_or_none()
    if not prob_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Problem {payload.problem_id} not found")

    res_t = await db.execute(select(ResearchTaskDB).where(ResearchTaskDB.id == payload.task_id))
    task_db = res_t.scalar_one_or_none()
    if not task_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task {payload.task_id} not found")

    res_m = await db.execute(select(ApproachMemoryDB).where(ApproachMemoryDB.problem_id == payload.problem_id))
    mem_rows = res_m.scalars().all()
    memories = [ApproachMemory.from_db(m) for m in mem_rows]

    prob = ResearchProblem.from_db(prob_db)
    subproblem = ResearchSubproblem(id=payload.subproblem_id, problem_id=payload.problem_id, title="Subproblem", statement="")
    task = ResearchTask.from_db(task_db)

    loop = LongHorizonResearchLoop()
    result = loop.execute_task_step(prob, subproblem, task, payload.method, payload.approach_description, memories)

    if result.get("executed"):
        task_db.current_step = task.current_step
        task_db.state = task.state.value

        att = result["attempt"]
        att_db = ResearchAttemptDB(
            id=att.id,
            task_id=att.task_id,
            approach_description=att.approach_description,
            method=att.method,
            result_summary=att.result_summary,
            status=att.status.value,
        )
        db.add(att_db)

        mem = result["memory"]
        mem_db = ApproachMemoryDB(
            id=mem.id,
            problem_id=mem.problem_id,
            approach_hash=mem.approach_hash,
            summary=mem.summary,
            status=mem.status.value,
        )
        db.add(mem_db)

        await db.commit()

    return result


@router.get("/project/{project_id}", response_model=Dict[str, Any])
async def list_project_problems(
    project_id: str,
    token: str = Depends(verify_token),
    x_user_id: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """List long-horizon research problems and approach memory for project."""
    user_id = _extract_user_id(token, x_user_id)
    await _verify_project_ownership(project_id, user_id, db)

    res_p = await db.execute(select(ResearchProblemDB).where(ResearchProblemDB.project_id == project_id))
    prob_rows = res_p.scalars().all()

    problems = [ResearchProblem.from_db(p) for p in prob_rows]
    return {
        "project_id": project_id,
        "total_problems": len(problems),
        "problems": problems,
    }
