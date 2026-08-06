"""
AXIOM Mathematical Discovery Engine (MDE) REST API Router
Provides endpoints for formula retrieval, theorem matching, and dependency discovery.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from axiom.core.retrieval.engine import (
    TheoremRetrievalEngine,
    RetrievalResponsePayload,
)
from axiom.services.api_gateway.auth import verify_token

router = APIRouter(prefix="/mde", tags=["mde"])

# Global singleton retrieval engine
_retrieval_engine = TheoremRetrievalEngine()


@router.get(
    "/retrieval",
    response_model=RetrievalResponsePayload,
    summary="Theorem Retrieval & Dependency Search",
    description="Discovers relevant mathematical theorems, proof dependencies, and equivalent formulations based on syntactic and semantic matches.",
)
def get_theorem_retrieval(
    query_formula: str = Query(..., description="Target formula expression string"),
    top_k: int = Query(default=5, ge=1, le=50, description="Maximum number of matches to return"),
    token: str = Depends(verify_token),
) -> RetrievalResponsePayload:
    """
    Fetch relevant theorems and equivalent formulations for a target formula with confidence scores and dependency DAG.
    """
    if not query_formula or not query_formula.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="query_formula parameter cannot be empty.",
        )

    try:
        payload = _retrieval_engine.retrieve_theorems(query_formula=query_formula, top_k=top_k)
        return payload
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Theorem retrieval failed: {str(e)}",
        )
