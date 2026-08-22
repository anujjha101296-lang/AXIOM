"""FastAPI Router for Phase 13 Research Pipeline."""
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from axiom.services.api_gateway.auth import get_current_user
from axiom.research_pipeline.pipeline import ResearchPipeline

router = APIRouter(prefix="/api/v1/research-pipeline", tags=["research-pipeline"])


class RunPipelineRequest(BaseModel):
    question: str
    simulated_sources: Optional[List[Dict[str, str]]] = None


@router.post("/run", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
async def run_research_pipeline(
    req: RunPipelineRequest,
    current_user=Depends(get_current_user),
):
    """Execute all 13 stages of the research pipeline for a given question."""
    try:
        pipeline = ResearchPipeline()
        artifact = pipeline.run_pipeline(
            question_text=req.question,
            simulated_sources=req.simulated_sources,
        )
        return artifact.model_dump()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Research pipeline execution failed: {str(e)}",
        )
