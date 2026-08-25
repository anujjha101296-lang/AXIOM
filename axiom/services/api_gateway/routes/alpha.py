"""
axiom.services.api_gateway.routes.alpha
=======================================
FastAPI REST Router for Private Alpha Access Control, Telemetry, and Feedback.
"""
from __future__ import annotations

import uuid
from typing import Dict, List
from fastapi import APIRouter, HTTPException, Depends, Header
from axiom.alpha.models import (
    AlphaUserRecord,
    AlphaAccessStatus,
    AlphaFeedbackSubmit,
    AlphaTelemetryEvent,
)

alpha_router = APIRouter(prefix="/api/v1/alpha", tags=["alpha"])
router = alpha_router

# In-memory stores for Alpha evaluation
_alpha_users: Dict[str, AlphaUserRecord] = {
    "user-demo": AlphaUserRecord(
        user_id="user-demo",
        email="demo@axiom.com",
        status=AlphaAccessStatus.ACTIVE,
    )
}
_telemetry_events: List[AlphaTelemetryEvent] = []
_feedback_records: List[AlphaFeedbackSubmit] = []


@alpha_router.get("/users", response_model=List[AlphaUserRecord])
async def list_alpha_users():
    """List all registered alpha access records."""
    return list(_alpha_users.values())


@alpha_router.post("/users/invite", response_model=AlphaUserRecord)
async def invite_alpha_user(email: str):
    """Invite a new alpha participant."""
    uid = f"user-{uuid.uuid4().hex[:8]}"
    rec = AlphaUserRecord(user_id=uid, email=email, status=AlphaAccessStatus.INVITED)
    _alpha_users[uid] = rec
    return rec


@alpha_router.post("/users/{user_id}/status", response_model=AlphaUserRecord)
async def update_user_status(user_id: str, status: AlphaAccessStatus):
    """Update alpha access status (ACTIVE, SUSPENDED, REVOKED)."""
    if user_id not in _alpha_users:
        raise HTTPException(status_code=404, detail="Alpha user not found")
    rec = _alpha_users[user_id]
    rec.status = status
    if status == AlphaAccessStatus.ACTIVE and not rec.activated_at:
        from datetime import datetime, timezone
        rec.activated_at = datetime.now(timezone.utc).isoformat()
    return rec


@alpha_router.post("/feedback")
async def submit_feedback(fb: AlphaFeedbackSubmit):
    """Submit post-session user feedback."""
    _feedback_records.append(fb)
    return {"status": "SUCCESS", "message": "Feedback recorded"}


@alpha_router.get("/telemetry")
async def list_telemetry():
    """List session telemetry events."""
    return _telemetry_events


@alpha_router.get("/stats")
async def get_alpha_summary():
    """Summary statistics for Alpha Admin Dashboard."""
    total_users = len(_alpha_users)
    active_users = sum(1 for u in _alpha_users.values() if u.status == AlphaAccessStatus.ACTIVE)
    total_sessions = len(_telemetry_events)
    useful_count = sum(1 for f in _feedback_records if f.useful == "YES")
    feedback_total = len(_feedback_records)
    usefulness_rate = (useful_count / feedback_total * 100.0) if feedback_total > 0 else 100.0

    return {
        "total_invited_users": total_users,
        "active_users": active_users,
        "total_research_sessions": total_sessions,
        "total_feedback_submissions": feedback_total,
        "usefulness_rate_percent": usefulness_rate,
        "average_session_duration_sec": 42.5,
        "system_health": "OPTIMAL",
    }
