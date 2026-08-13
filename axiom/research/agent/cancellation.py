"""Session Cancellation System for Controlled Research Agent."""

import json
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from axiom.core.models import ResearchSession, Project, ResearchArtifact
from axiom.research.agent.state import ResearchAgentState, validate_state_transition


class SessionCancelledError(Exception):
    """Raised when an operation is aborted due to session cancellation."""

    pass


async def is_cancellation_requested(session_id: str, db: AsyncSession) -> bool:
    """Check if cancellation has been requested for a research session.

    Args:
        session_id: ID of the ResearchSession.
        db: AsyncSession database connection.

    Returns:
        bool: True if cancellation_requested is set on the session, False otherwise.
    """
    stmt = select(ResearchSession.cancellation_requested).where(ResearchSession.id == session_id)
    res = await db.execute(stmt)
    requested = res.scalar_one_or_none()
    return bool(requested)


async def request_session_cancellation(
    session_id: str,
    db: AsyncSession,
    user_id: str,
) -> bool:
    """Request session cancellation: verify ownership, flag session, log artifact, transition state.

    Args:
        session_id: ID of the ResearchSession to cancel.
        db: AsyncSession database connection.
        user_id: ID of the requesting user.

    Returns:
        bool: True if cancellation was successfully requested/processed, False if session not found.

    Raises:
        PermissionError: If requesting user does not own the session's project.
    """
    stmt = select(ResearchSession).where(ResearchSession.id == session_id)
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    if not session:
        return False

    # Verify project ownership for session
    stmt_proj = select(Project).where(Project.id == session.project_id)
    res_proj = await db.execute(stmt_proj)
    project = res_proj.scalar_one_or_none()

    if project and project.owner_id != user_id:
        raise PermissionError(
            f"User '{user_id}' is not authorized to cancel research session '{session_id}' in project '{project.id}'"
        )

    # Set cancellation_requested flag in DB ResearchSession
    session.cancellation_requested = True

    # Persist ResearchArtifact(type="cancellation", content=...) detailing cancellation request
    cancellation_payload = {
        "event": "cancellation_requested",
        "session_id": session_id,
        "project_id": session.project_id,
        "requested_by": user_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "reason": "User requested research session cancellation",
    }
    artifact = ResearchArtifact(
        session_id=session_id,
        type="cancellation",
        content=json.dumps(cancellation_payload),
    )
    db.add(artifact)

    # Immediately transition session status to CANCELLED if session is idle or awaiting next step (non-terminal)
    terminal_states = {
        ResearchAgentState.COMPLETED.value,
        ResearchAgentState.FAILED.value,
        ResearchAgentState.CANCELLED.value,
        "COMPLETED",
        "FAILED",
        "CANCELLED",
    }
    if session.status not in terminal_states:
        session.status = validate_state_transition(
            session.status, ResearchAgentState.CANCELLED
        )
        session.completed_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(session)
    return True

