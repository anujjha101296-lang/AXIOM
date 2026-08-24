"""
axiom.services.api_gateway.routes.challenge_harness
====================================================
FastAPI REST API Routes for Phase 18 Mathematical Research Challenge Harness.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Header, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from axiom.challenge_harness.curator import ProblemCurator
from axiom.challenge_harness.evaluator import IndependentEvaluator
from axiom.challenge_harness.models import Challenge, EvaluationOutcome, EvaluationRun, FailureClass
from axiom.core.database import get_db
from axiom.core.models import ChallengeDB, EvaluationRunDB
from axiom.services.api_gateway.auth import verify_token

router = APIRouter(prefix="/api/v1/benchmarks", tags=["challenge_harness"])


class EvaluateRequest(BaseModel):
    challenge_id: str
    agent_output: str
    proof_script: Optional[str] = ""
    counterexample_witness: Optional[str] = ""


@router.get("/challenges", response_model=Dict[str, Any])
async def list_challenges_endpoint(
    token: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db),
):
    """List versioned golden benchmark challenges (AXIOM-MATH-001)."""
    curator = ProblemCurator()
    challenges = curator.get_golden_challenges()

    # Persist challenges if not existing
    for ch in challenges:
        res = await db.execute(select(ChallengeDB).where(ChallengeDB.id == ch.id))
        if not res.scalar_one_or_none():
            ch_db = ChallengeDB(
                id=ch.id,
                version=ch.version,
                title=ch.title,
                domain=ch.domain,
                difficulty_level=ch.difficulty_level.value,
                statement=ch.statement,
                allowed_resources_json=json.dumps(ch.allowed_resources),
                time_budget_sec=ch.time_budget_sec,
                tool_budget_steps=ch.tool_budget_steps,
            )
            db.add(ch_db)

    await db.commit()
    return {"version": "AXIOM-MATH-001", "total_challenges": len(challenges), "challenges": challenges}


@router.post("/evaluate", response_model=EvaluationRun, status_code=status.HTTP_201_CREATED)
async def evaluate_challenge_endpoint(
    payload: EvaluateRequest,
    token: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db),
):
    """Execute blind challenge evaluation and persist multi-axis scores."""
    curator = ProblemCurator()
    challenges = curator.get_golden_challenges()
    ch = next((c for c in challenges if c.id == payload.challenge_id), None)
    if not ch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Challenge {payload.challenge_id} not found")

    evaluator = IndependentEvaluator()
    run = evaluator.evaluate_run(
        challenge=ch,
        agent_output=payload.agent_output,
        proof_script=payload.proof_script or "",
        counterexample_witness=payload.counterexample_witness or "",
    )

    run_db = EvaluationRunDB(
        id=run.id,
        challenge_id=run.challenge_id,
        outcome=run.outcome.value,
        score_json=json.dumps(run.score.model_dump()),
        failure_class=run.failure_class.value,
        runtime_sec=run.runtime_sec,
        steps_used=run.steps_used,
        proof_verified=run.proof_verified,
        counterexample_found=run.counterexample_found,
    )
    db.add(run_db)
    await db.commit()

    return run


@router.get("/results", response_model=Dict[str, Any])
async def list_evaluation_results_endpoint(
    token: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db),
):
    """List all benchmark evaluation runs and scores."""
    res = await db.execute(select(EvaluationRunDB))
    rows = res.scalars().all()
    runs = [EvaluationRun.from_db(r) for r in rows]

    return {
        "total_runs": len(runs),
        "runs": runs,
    }
