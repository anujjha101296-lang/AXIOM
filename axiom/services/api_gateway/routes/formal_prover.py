"""FastAPI Router for Phase 14 Formal Verification Engine."""
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from axiom.services.api_gateway.auth import get_current_user
from axiom.formal_prover.models import FormalTheorem, ProverType
from axiom.formal_prover.engine import FormalVerificationEngine

router = APIRouter(prefix="/api/v1/formal-prover", tags=["formal-prover"])


class VerifyTheoremRequest(BaseModel):
    name: str
    statement: str
    prover: ProverType
    tactic_script: str
    imports: Optional[List[str]] = None


@router.post("/verify", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
async def verify_formal_theorem(
    req: VerifyTheoremRequest,
    current_user=Depends(get_current_user),
):
    """Verify a formal theorem script in Lean 4, Coq, or Isabelle."""
    try:
        engine = FormalVerificationEngine()
        theorem = FormalTheorem(
            name=req.name,
            statement=req.statement,
            prover=req.prover,
            imports=req.imports or [],
        )
        res = engine.verify_theorem(theorem, req.tactic_script)
        return res.model_dump()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Formal verification failed: {str(e)}",
        )
