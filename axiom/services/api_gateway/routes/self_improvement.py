"""FastAPI Router for Phase 15 Self-Improvement Loop."""
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from axiom.services.api_gateway.auth import get_current_user
from axiom.self_improvement.loop import SelfImprovementLoop

router = APIRouter(prefix="/api/v1/self-improvement", tags=["self-improvement"])


class RunSelfImprovementRequest(BaseModel):
    baseline_pass_rate: Optional[float] = 1.0


@router.post("/run", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
async def run_self_improvement_cycle(
    req: RunSelfImprovementRequest,
    current_user=Depends(get_current_user),
):
    """Run an automated self-improvement & regression evaluation cycle."""
    try:
        loop = SelfImprovementLoop()
        report = loop.run_cycle(baseline_pass_rate=req.baseline_pass_rate or 1.0)
        return report.model_dump()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Self-improvement cycle failed: {str(e)}",
        )
