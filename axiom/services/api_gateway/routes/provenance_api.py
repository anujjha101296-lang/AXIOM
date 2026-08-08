"""H1-OBS — Unified provenance API for SCEP and RVP runs."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from axiom.config import settings
from axiom.observability.run_provenance import RunType, get_provenance_store

router = APIRouter(prefix="/provenance", tags=["provenance"])


@router.get("/runs")
def list_provenance_runs(
    run_type: RunType | None = Query(None, description="Filter by scep or rvp"),
    limit: int = Query(50, ge=1, le=500),
) -> dict[str, Any]:
    """List provenance records across SCEP and RVP evaluation runs."""
    records = get_provenance_store(settings.db_path).list_runs(run_type=run_type, limit=limit)
    return {"count": len(records), "runs": records}


@router.get("/runs/{run_type}/{run_id}")
def get_provenance_run(run_type: RunType, run_id: str) -> dict[str, Any]:
    """Retrieve full provenance envelope for a specific run."""
    record = get_provenance_store(settings.db_path).get(run_type, run_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Provenance not found: {run_type}/{run_id}")
    return record
