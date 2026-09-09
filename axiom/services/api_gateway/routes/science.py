"""HTTP API for the bounded, deterministic scientific research runtime."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from axiom.services.api_gateway.auth import verify_token
from axiom.science_runtime import ResearchQuestion, run_lorenz_reference_benchmark, run_research

router = APIRouter(prefix="/api/v1/science", tags=["science-runtime"])


class ResearchRequest(BaseModel):
    question: str = Field(min_length=5, max_length=2000)
    model: str = Field(default="lorenz", min_length=1, max_length=64)
    max_experiments: int = Field(default=3, ge=1, le=10)
    allowed_rho: list[float] = Field(default_factory=lambda: [20.0, 24.0, 28.0, 32.0, 40.0], min_length=1, max_length=10)


@router.post("/research", response_model=dict[str, Any])
async def start_bounded_research(
    payload: ResearchRequest,
    token: str = Depends(verify_token),
) -> dict[str, Any]:
    """Execute a bounded research run; scientific execution stays deterministic."""
    if payload.model.lower() != "lorenz":
        raise HTTPException(status_code=422, detail="Only the Lorenz runtime is currently enabled")
    try:
        question = ResearchQuestion(
            text=payload.question.strip(),
            model=payload.model,
            max_experiments=payload.max_experiments,
            allowed_rho=tuple(payload.allowed_rho),
        )
        run = await run_in_threadpool(run_research, question)
        return run.to_dict()
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Scientific research run failed") from exc


@router.get("/benchmark/lorenz", response_model=dict[str, Any])
async def lorenz_benchmark(token: str = Depends(verify_token)) -> dict[str, Any]:
    """Run the fixed Lorenz evidence benchmark."""
    try:
        result = await run_in_threadpool(run_lorenz_reference_benchmark, 28.0)
        return result.to_dict()
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Lorenz benchmark failed") from exc
