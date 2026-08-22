"""FastAPI Router for Phase 12 Mathematical Discovery Engine."""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from axiom.services.api_gateway.auth import get_current_user
from axiom.discovery.pipeline import DiscoveryPipeline

router = APIRouter(prefix="/discovery", tags=["discovery"])


@router.post("/run", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
async def run_discovery_session(current_user=Depends(get_current_user)):
    """Run an autonomous mathematical discovery cycle."""
    try:
        pipeline = DiscoveryPipeline()
        report = pipeline.run_discovery_cycle()
        return report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Discovery cycle failed: {str(e)}",
        )
