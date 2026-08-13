"""State-Machine Execution Engine for Controlled Research Agent."""

import asyncio
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from axiom.core.models import ResearchSession, ResearchArtifact, Project
from axiom.research.agent.state import (
    ResearchAgentState,
    validate_state_transition,
    InvalidStateTransitionError,
)
from axiom.research.agent.plan import (
    ResearchPlan,
    generate_initial_plan,
)
from axiom.research.agent.tools import (
    ToolRegistry,
    ToolExecutionContext,
    ToolObservation,
    execute_tool,
)
from axiom.research.agent.budgets import check_budget_exceeded, BudgetLimits, BudgetTracker
from axiom.research.agent.cancellation import is_cancellation_requested

TERMINAL_STATES = {
    ResearchAgentState.COMPLETED.value,
    ResearchAgentState.FAILED.value,
    ResearchAgentState.CANCELLED.value,
    "COMPLETED",
    "FAILED",
    "CANCELLED",
}


class ControlledExecutionEngine:
    """State-machine based controlled execution engine enforcing cancellation and budget controls."""

    def __init__(
        self,
        session_id: Optional[str] = None,
        db: Optional[AsyncSession] = None,
        user_id: Optional[str] = None,
        registry: Optional[ToolRegistry] = None,
        tool_registry: Optional[ToolRegistry] = None,
    ):
        self.session_id = session_id
        self.db = db
        self.user_id = user_id
        self.registry = registry or tool_registry or ToolRegistry()
        self.session: Optional[ResearchSession] = None
        self.plan: Optional[ResearchPlan] = None
        self.budget_tracker: Optional[BudgetTracker] = None

    async def load_session(
        self,
        session_id: Optional[str] = None,
        db: Optional[AsyncSession] = None,
        user_id: Optional[str] = None,
    ) -> ResearchSession:
        """Fetch ResearchSession from DB and verify project ownership authorization."""
        if session_id:
            self.session_id = session_id
        if db:
            self.db = db
        if user_id:
            self.user_id = user_id

        if not self.session_id or self.db is None or not self.user_id:
            raise ValueError("session_id, db, and user_id must be provided to load_session.")

        stmt = select(ResearchSession).where(ResearchSession.id == self.session_id)
        res = await self.db.execute(stmt)
        session = res.scalar_one_or_none()
        if session is None:
            raise ValueError(f"ResearchSession '{self.session_id}' not found.")

        # Verify project authorization
        proj_stmt = select(Project).where(Project.id == session.project_id)
        proj_res = await self.db.execute(proj_stmt)
        project = proj_res.scalar_one_or_none()
        if project and project.owner_id != self.user_id:
            raise PermissionError(
                f"User '{self.user_id}' is not authorized to access project '{session.project_id}'"
            )

        self.session = session
        self.budget_tracker = BudgetTracker.from_session(session)
        return session

    async def check_cancellation(
        self,
        session: Optional[ResearchSession] = None,
        db: Optional[AsyncSession] = None,
        cancellation_token: Optional[asyncio.Event] = None,
    ) -> bool:
        """Check if cancellation was requested for session in DB or via cancellation_token."""
        target_session = session or self.session
        target_db = db or self.db

        if not target_session:
            return False

        if cancellation_token and cancellation_token.is_set():
            target_session.cancellation_requested = True

        if getattr(target_session, "cancellation_requested", False):
            return True

        if target_db:
            try:
                db_cancelled = await is_cancellation_requested(target_session.id, target_db)
                if db_cancelled:
                    target_session.cancellation_requested = True
                    return True
            except Exception:
                pass

        return bool(getattr(target_session, "cancellation_requested", False))

    async def abort_cancelled_session(
        self,
        session: Optional[ResearchSession] = None,
        db: Optional[AsyncSession] = None,
    ) -> ResearchSession:
        """Safely abort in-flight session operations and update state to CANCELLED."""
        target_session = session or self.session
        target_db = db or self.db

        if not target_session or not target_db:
            raise ValueError("Session and DB are required to abort cancelled session.")

        if target_session.status not in TERMINAL_STATES:
            try:
                target_session.status = validate_state_transition(
                    target_session.status, ResearchAgentState.CANCELLED
                )
            except InvalidStateTransitionError:
                target_session.status = ResearchAgentState.CANCELLED.value

            target_session.completed_at = datetime.now(timezone.utc)
            if not target_session.error_message:
                target_session.error_message = "Execution cancelled by user request."

        # Check for existing cancellation artifact; create if missing
        stmt = select(ResearchArtifact).where(
            ResearchArtifact.session_id == target_session.id,
            ResearchArtifact.type == "cancellation",
        )
        res = await target_db.execute(stmt)
        existing_artifact = res.scalars().first()

        if not existing_artifact:
            cancel_artifact = ResearchArtifact(
                session_id=target_session.id,
                type="cancellation",
                content=json.dumps({
                    "event": "cancellation_aborted",
                    "session_id": target_session.id,
                    "step_count": target_session.step_count,
                    "tool_call_count": target_session.tool_call_count,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "reason": "Execution engine aborted in-flight operations due to cancellation request",
                }),
            )
            target_db.add(cancel_artifact)

        await target_db.commit()
        await target_db.refresh(target_session)
        return target_session

    async def check_budget(
        self,
        session: Optional[ResearchSession] = None,
        db: Optional[AsyncSession] = None,
    ) -> bool:
        """Check if budget limits are exceeded. If exceeded, transition state to FAILED and halt."""
        target_session = session or self.session
        target_db = db or self.db

        if not target_session or not target_db:
            return False

        tracker = self.budget_tracker or BudgetTracker.from_session(target_session)
        exceeded, reason = tracker.is_budget_exceeded()

        if not exceeded:
            reason = check_budget_exceeded(target_session)
            if reason:
                exceeded = True

        if exceeded and reason:
            target_session.error_message = reason
            target_session.completed_at = datetime.now(timezone.utc)

            current_state = target_session.status
            try:
                target_state = validate_state_transition(
                    current_state, ResearchAgentState.FAILED
                )
            except InvalidStateTransitionError:
                target_state = ResearchAgentState.FAILED.value

            target_session.status = target_state

            artifact = ResearchArtifact(
                session_id=target_session.id,
                type="budget_exhausted",
                content=json.dumps({
                    "event": "budget_exceeded",
                    "status": target_state,
                    "reason": reason,
                    "error": reason,
                    "step_count": target_session.step_count,
                    "tool_call_count": target_session.tool_call_count,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }),
            )
            target_db.add(artifact)
            await target_db.commit()
            await target_db.refresh(target_session)
            return True
        return False

    async def execute_tool_call(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        session: Optional[ResearchSession] = None,
        db: Optional[AsyncSession] = None,
        user_id: Optional[str] = None,
    ) -> ToolObservation:
        """Execute a tool, increment step & tool call counters, and persist artifacts."""
        target_session = session or self.session
        target_db = db or self.db
        target_user_id = user_id or self.user_id

        if not target_session and self.session_id and self.db and self.user_id:
            target_session = await self.load_session()
            target_db = self.db
            target_user_id = self.user_id

        if not target_session or not target_db or not target_user_id:
            raise ValueError("session, db, and user_id are required to execute tool call.")

        ctx = ToolExecutionContext(
            user_id=target_user_id,
            project_id=target_session.project_id,
            session_id=target_session.id,
            db=target_db,
        )

        tool_call_artifact = ResearchArtifact(
            session_id=target_session.id,
            type="tool_call",
            content=json.dumps({
                "tool_name": tool_name,
                "parameters": parameters,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }),
        )
        target_db.add(tool_call_artifact)

        obs: ToolObservation = await execute_tool(
            tool_name=tool_name,
            parameters=parameters,
            context=ctx,
            db=target_db,
            registry=self.registry,
        )

        if self.budget_tracker:
            self.budget_tracker.increment_step()
            self.budget_tracker.increment_tool_call()
            self.budget_tracker.sync_to_session(target_session)
        else:
            target_session.step_count += 1
            target_session.tool_call_count += 1

        obs_artifact = ResearchArtifact(
            session_id=target_session.id,
            type="observation",
            content=json.dumps(obs.model_dump() if hasattr(obs, "model_dump") else obs.dict(), default=str),
        )
        target_db.add(obs_artifact)
        await target_db.commit()
        return obs

    async def step(self) -> ResearchSession:
        """Advance the execution state machine by a single step."""
        if not self.session:
            await self.load_session()

        if self.session.status in TERMINAL_STATES:
            return self.session

        # 1. Check cancellation before step execution
        if await self.check_cancellation():
            return await self.abort_cancelled_session()

        # 2. Check budget before step execution
        if await self.check_budget():
            return self.session

        current_state = self.session.status

        if current_state in (ResearchAgentState.CREATED.value, "CREATED"):
            next_state = validate_state_transition(
                current_state, ResearchAgentState.PLANNING
            )
            self.session.status = next_state
            await self.db.commit()

        elif current_state in (ResearchAgentState.PLANNING.value, "PLANNING"):
            plan = generate_initial_plan(self.session.goal or "Research Goal")
            self.plan = plan

            plan_artifact = ResearchArtifact(
                session_id=self.session.id,
                type="plan",
                content=plan.to_json(),
            )
            self.db.add(plan_artifact)

            if self.budget_tracker:
                self.budget_tracker.increment_step()
                self.budget_tracker.sync_to_session(self.session)
            else:
                self.session.step_count += 1

            next_state = validate_state_transition(
                current_state, ResearchAgentState.RETRIEVING
            )
            self.session.status = next_state
            await self.db.commit()

        elif current_state in (ResearchAgentState.RETRIEVING.value, "RETRIEVING"):
            if await self.check_cancellation():
                return await self.abort_cancelled_session()

            params = {
                "query": self.session.goal or "research",
                "limit": 5,
            }
            await self.execute_tool_call("SEARCH_PROJECT_KNOWLEDGE", params)

            next_state = validate_state_transition(
                current_state, ResearchAgentState.ANALYZING
            )
            self.session.status = next_state
            await self.db.commit()

        elif current_state in (ResearchAgentState.ANALYZING.value, "ANALYZING"):
            if await self.check_cancellation():
                return await self.abort_cancelled_session()

            params = {
                "question": self.session.goal or "research",
                "chunk_ids": [],
            }
            await self.execute_tool_call("ASK_GROUNDED_RESEARCH_ENGINE", params)

            next_state = validate_state_transition(
                current_state, ResearchAgentState.VERIFYING
            )
            self.session.status = next_state
            await self.db.commit()

        elif current_state in (ResearchAgentState.VERIFYING.value, "VERIFYING"):
            if self.budget_tracker:
                self.budget_tracker.increment_step()
                self.budget_tracker.sync_to_session(self.session)
            else:
                self.session.step_count += 1

            final_artifact = ResearchArtifact(
                session_id=self.session.id,
                type="final_artifact",
                content=json.dumps({
                    "session_id": self.session.id,
                    "goal": self.session.goal,
                    "status": "COMPLETED",
                    "summary": f"Structured research assessment complete for: {self.session.goal}",
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                }),
            )
            self.db.add(final_artifact)
            self.session.completed_at = datetime.now(timezone.utc)

            next_state = validate_state_transition(
                current_state, ResearchAgentState.COMPLETED
            )
            self.session.status = next_state
            await self.db.commit()

        await self.db.refresh(self.session)
        return self.session

    async def run(self) -> ResearchSession:
        """Run execution loop until terminal state or budget/cancellation halt."""
        if not self.session:
            await self.load_session()

        while self.session.status not in TERMINAL_STATES:
            if await self.check_cancellation():
                await self.abort_cancelled_session()
                break

            if await self.check_budget():
                break

            await self.step()

        return self.session

    async def run_session(
        self,
        session_id: str,
        db: AsyncSession,
        user_id: str,
        cancellation_token: Optional[asyncio.Event] = None,
    ) -> ResearchSession:
        """Run execution loop for session_id, db, user_id with optional cancellation token."""
        await self.load_session(session_id=session_id, db=db, user_id=user_id)

        while self.session.status not in TERMINAL_STATES:
            if cancellation_token and cancellation_token.is_set():
                self.session.cancellation_requested = True

            if await self.check_cancellation(cancellation_token=cancellation_token):
                await self.abort_cancelled_session()
                break

            if await self.check_budget():
                break

            await self.step()

        return self.session

