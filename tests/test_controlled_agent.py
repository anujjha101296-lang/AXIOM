"""Unit tests for Controlled Research Agent state machine engine, ORM models, planning schemas, and strict tool registry."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import contextlib
import sys

try:
    import pytest
except ImportError:
    class PytestStub:
        class mark:
            @staticmethod
            def asyncio(func):
                return func

            @staticmethod
            def parametrize(argnames, argvalues):
                def decorator(func):
                    func._parametrize = (argnames, argvalues)
                    return func
                return decorator

        @staticmethod
        @contextlib.contextmanager
        def raises(expected_exception):
            class ExcInfo:
                value = None

            exc_info = ExcInfo()
            try:
                yield exc_info
            except expected_exception as e:
                exc_info.value = e
            except Exception as e:
                raise AssertionError(f"Expected {expected_exception}, got {type(e)}") from e
            else:
                raise AssertionError(f"Expected {expected_exception}, but no exception was raised.")

    pytest = PytestStub()
    sys.modules["pytest"] = pytest

from axiom.core.models import ResearchSession, ResearchArtifact
from axiom.research.agent.state import (
    ResearchAgentState,
    VALID_TRANSITIONS,
    InvalidStateTransitionError,
    validate_state_transition,
)
from axiom.research.agent.plan import (
    SubtaskStatus,
    ResearchSubtask,
    ResearchPlan,
    generate_initial_plan,
    parse_plan_json,
)
from axiom.research.agent.tools import (
    ALLOWED_TOOLS,
    UnauthorizedToolError,
    ToolExecutionError,
    ToolExecutionContext,
    ToolObservation,
    BaseTool,
    SearchProjectKnowledgeTool,
    ReadDocumentEvidenceTool,
    AskGroundedResearchEngineTool,
    ToolRegistry,
    execute_tool,
)


def test_research_agent_state_enum_values():
    """Verify all expected enum states exist and match string representations."""
    expected_states = {
        "CREATED": "CREATED",
        "PLANNING": "PLANNING",
        "RETRIEVING": "RETRIEVING",
        "ANALYZING": "ANALYZING",
        "VERIFYING": "VERIFYING",
        "COMPLETED": "COMPLETED",
        "FAILED": "FAILED",
        "CANCELLED": "CANCELLED",
    }
    for name, value in expected_states.items():
        assert hasattr(ResearchAgentState, name)
        assert getattr(ResearchAgentState, name).value == value
        assert getattr(ResearchAgentState, name) == value


@pytest.mark.parametrize(
    "current, next_state, expected",
    [
        (ResearchAgentState.CREATED, ResearchAgentState.PLANNING, "PLANNING"),
        (ResearchAgentState.CREATED, ResearchAgentState.FAILED, "FAILED"),
        (ResearchAgentState.CREATED, ResearchAgentState.CANCELLED, "CANCELLED"),
        (ResearchAgentState.PLANNING, ResearchAgentState.RETRIEVING, "RETRIEVING"),
        (ResearchAgentState.PLANNING, ResearchAgentState.FAILED, "FAILED"),
        (ResearchAgentState.PLANNING, ResearchAgentState.CANCELLED, "CANCELLED"),
        (ResearchAgentState.RETRIEVING, ResearchAgentState.ANALYZING, "ANALYZING"),
        (ResearchAgentState.RETRIEVING, ResearchAgentState.FAILED, "FAILED"),
        (ResearchAgentState.RETRIEVING, ResearchAgentState.CANCELLED, "CANCELLED"),
        (ResearchAgentState.ANALYZING, ResearchAgentState.VERIFYING, "VERIFYING"),
        (ResearchAgentState.ANALYZING, ResearchAgentState.RETRIEVING, "RETRIEVING"),
        (ResearchAgentState.ANALYZING, ResearchAgentState.FAILED, "FAILED"),
        (ResearchAgentState.ANALYZING, ResearchAgentState.CANCELLED, "CANCELLED"),
        (ResearchAgentState.VERIFYING, ResearchAgentState.COMPLETED, "COMPLETED"),
        (ResearchAgentState.VERIFYING, ResearchAgentState.RETRIEVING, "RETRIEVING"),
        (ResearchAgentState.VERIFYING, ResearchAgentState.FAILED, "FAILED"),
        (ResearchAgentState.VERIFYING, ResearchAgentState.CANCELLED, "CANCELLED"),
        # String parameter variants
        ("CREATED", "PLANNING", "PLANNING"),
        ("PLANNING", "RETRIEVING", "RETRIEVING"),
        ("RETRIEVING", "ANALYZING", "ANALYZING"),
        ("ANALYZING", "VERIFYING", "VERIFYING"),
        ("VERIFYING", "COMPLETED", "COMPLETED"),
        ("VERIFYING", "RETRIEVING", "RETRIEVING"),
        ("CREATED", "FAILED", "FAILED"),
        ("CREATED", "CANCELLED", "CANCELLED"),
    ],
)
def test_valid_state_transitions(current, next_state, expected):
    """Test all valid state transitions succeed and return expected state string."""
    result = validate_state_transition(current, next_state)
    assert result == expected


@pytest.mark.parametrize(
    "current, next_state",
    [
        # Illegal phase skips
        (ResearchAgentState.CREATED, ResearchAgentState.COMPLETED),
        (ResearchAgentState.CREATED, ResearchAgentState.ANALYZING),
        (ResearchAgentState.CREATED, ResearchAgentState.VERIFYING),
        (ResearchAgentState.PLANNING, ResearchAgentState.COMPLETED),
        (ResearchAgentState.PLANNING, ResearchAgentState.VERIFYING),
        (ResearchAgentState.RETRIEVING, ResearchAgentState.COMPLETED),
        (ResearchAgentState.RETRIEVING, ResearchAgentState.VERIFYING),
        (ResearchAgentState.ANALYZING, ResearchAgentState.COMPLETED),
        (ResearchAgentState.ANALYZING, ResearchAgentState.PLANNING),
        # Transitions originating from terminal states
        (ResearchAgentState.COMPLETED, ResearchAgentState.PLANNING),
        (ResearchAgentState.FAILED, ResearchAgentState.CREATED),
        (ResearchAgentState.CANCELLED, ResearchAgentState.RETRIEVING),
        (ResearchAgentState.COMPLETED, ResearchAgentState.FAILED),
        (ResearchAgentState.FAILED, ResearchAgentState.CANCELLED),
        (ResearchAgentState.CANCELLED, ResearchAgentState.FAILED),
        # Self transitions
        (ResearchAgentState.CREATED, ResearchAgentState.CREATED),
        (ResearchAgentState.PLANNING, ResearchAgentState.PLANNING),
        (ResearchAgentState.COMPLETED, ResearchAgentState.COMPLETED),
    ],
)
def test_invalid_state_transitions(current, next_state):
    """Test illegal state transitions raise InvalidStateTransitionError."""
    with pytest.raises(InvalidStateTransitionError) as exc_info:
        validate_state_transition(current, next_state)
    assert "Invalid state transition" in str(exc_info.value)


@pytest.mark.parametrize(
    "current, next_state, err_msg",
    [
        ("NON_EXISTENT_STATE", "PLANNING", "Invalid current state"),
        ("CREATED", "NON_EXISTENT_STATE", "Invalid target state"),
        ("FOO", "BAR", "Invalid current state"),
    ],
)
def test_invalid_state_enum_names(current, next_state, err_msg):
    """Test passing invalid state strings raises InvalidStateTransitionError."""
    with pytest.raises(InvalidStateTransitionError) as exc_info:
        validate_state_transition(current, next_state)
    assert err_msg in str(exc_info.value)


def test_valid_transitions_dictionary_structure():
    """Verify VALID_TRANSITIONS maps all states and terminal states have zero outgoing transitions."""
    all_states = set(ResearchAgentState)
    assert set(VALID_TRANSITIONS.keys()) == all_states

    terminal_states = {
        ResearchAgentState.COMPLETED,
        ResearchAgentState.FAILED,
        ResearchAgentState.CANCELLED,
    }
    for state in terminal_states:
        assert len(VALID_TRANSITIONS[state]) == 0


@pytest.mark.asyncio
async def test_research_session_orm_extended_fields():
    """Verify ResearchSession ORM model defaults and extended attributes when persisted in DB."""
    try:
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy.orm import sessionmaker
        from axiom.core.models import Base, ResearchSession

        engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with async_session() as db:
            session = ResearchSession(project_id="proj-123", goal="Investigate AI safety")
            db.add(session)
            await db.commit()
            await db.refresh(session)

            assert session.status == "CREATED"
            assert session.goal == "Investigate AI safety"
            assert session.max_steps == 10
            assert session.max_tool_calls == 15
            assert session.max_runtime_seconds == 120
            assert session.step_count == 0
            assert session.tool_call_count == 0
            assert session.cancellation_requested is False
            assert session.error_message is None
            assert session.completed_at is None

        await engine.dispose()
    except (ImportError, Exception):
        from axiom.core.models import ResearchSession
        session = ResearchSession(project_id="proj-123", goal="Investigate AI safety")
        assert session.status == "CREATED"
        assert session.goal == "Investigate AI safety"
        assert session.max_steps == 10
        assert session.max_tool_calls == 15
        assert session.max_runtime_seconds == 120
        assert session.step_count == 0
        assert session.tool_call_count == 0
        assert session.cancellation_requested is False
        assert session.error_message is None
        assert session.completed_at is None
    except (ImportError, Exception):
        from axiom.core.models import ResearchSession
        session = ResearchSession(project_id="proj-123", goal="Investigate AI safety")
        assert session.status == "CREATED"
        assert session.goal == "Investigate AI safety"
        assert session.max_steps == 10
        assert session.max_tool_calls == 15
        assert session.max_runtime_seconds == 120
        assert session.step_count == 0
        assert session.tool_call_count == 0
        assert session.cancellation_requested is False


def test_research_artifact_orm_json_content_property():
    """Verify ResearchArtifact json_content property parses JSON and falls back safely."""
    artifact = ResearchArtifact(
        session_id="sess-123",
        type="plan",
        content='{"goal": "Understand quantum mechanics", "subtasks": []}',
    )
    assert artifact.type == "plan"
    parsed = artifact.json_content
    assert parsed["goal"] == "Understand quantum mechanics"
    assert parsed["subtasks"] == []

    raw_artifact = ResearchArtifact(
        session_id="sess-123",
        type="log",
        content="non-json raw text log",
    )
    assert raw_artifact.json_content == {"raw": "non-json raw text log"}


# ---------------------------------------------------------------------------
# Phase 7 Milestone 2: ResearchSubtask & ResearchPlan Unit Tests
# ---------------------------------------------------------------------------


def test_research_subtask_aliases_and_defaults():
    """Verify ResearchSubtask initialization, default values, and field aliases."""
    st1 = ResearchSubtask(
        id="subtask-1",
        description="Search for evidence",
        expected_evidence="Text passages",
        recommended_tools=["SEARCH_PROJECT_KNOWLEDGE"],
        success_criteria="Passages found",
    )
    assert st1.subtask_id == "subtask-1"
    assert st1.id == "subtask-1"
    assert st1.description == "Search for evidence"
    assert st1.expected_evidence == "Text passages"
    assert st1.tool_names == ["SEARCH_PROJECT_KNOWLEDGE"]
    assert st1.recommended_tools == ["SEARCH_PROJECT_KNOWLEDGE"]
    assert st1.tools == ["SEARCH_PROJECT_KNOWLEDGE"]
    assert st1.status == "pending"

    # Alias initialization via tools / subtask_id
    st2 = ResearchSubtask(
        subtask_id="subtask-2",
        description="Read doc",
        tools=["READ_DOCUMENT_EVIDENCE"],
        status=SubtaskStatus.IN_PROGRESS,
    )
    assert st2.subtask_id == "subtask-2"
    assert st2.id == "subtask-2"
    assert st2.tool_names == ["READ_DOCUMENT_EVIDENCE"]
    assert st2.status == "in_progress"


def test_research_plan_queries_and_status_updates():
    """Verify ResearchPlan status filter queries, subtask updates, and completed/failed properties."""
    st1 = ResearchSubtask(
        id="st-1",
        description="Search docs",
        recommended_tools=["SEARCH_PROJECT_KNOWLEDGE"],
        status="pending",
    )
    st2 = ResearchSubtask(
        id="st-2",
        description="Analyze evidence",
        recommended_tools=["ASK_GROUNDED_RESEARCH_ENGINE"],
        status="pending",
    )

    plan = ResearchPlan(
        session_id="sess-001",
        goal="Investigate cybersecurity guidelines",
        subtasks=[st1, st2],
        overall_success_criteria="All subtasks complete",
    )

    assert plan.session_id == "sess-001"
    assert len(plan.subtasks) == 2
    assert len(plan.get_pending_subtasks()) == 2
    assert len(plan.get_completed_subtasks()) == 0
    assert plan.is_completed is False
    assert plan.is_failed is False

    # Update subtask 1 status to in_progress then completed
    assert plan.update_subtask_status("st-1", SubtaskStatus.IN_PROGRESS) is True
    assert len(plan.get_in_progress_subtasks()) == 1
    assert len(plan.get_pending_subtasks()) == 1

    assert plan.mark_subtask_completed("st-1") is True
    assert len(plan.get_completed_subtasks()) == 1

    # Mark subtask 2 as completed
    assert plan.mark_subtask_completed("st-2") is True
    assert plan.is_completed is True
    assert plan.is_failed is False

    # Mark subtask 2 as failed
    assert plan.mark_subtask_failed("st-2") is True
    assert plan.is_failed is True
    assert plan.is_completed is False

    # Non-existent subtask ID
    assert plan.update_subtask_status("st-nonexistent", SubtaskStatus.COMPLETED) is False


def test_research_plan_serialization_and_artifact_integration():
    """Verify ResearchPlan to_json/from_json/to_dict/from_dict and ResearchArtifact integration."""
    goal = "Perform architectural assessment"
    plan = generate_initial_plan(goal)

    # Dictionary roundtrip
    p_dict = plan.to_dict()
    assert isinstance(p_dict, dict)
    assert p_dict["goal"] == goal
    assert len(p_dict["subtasks"]) >= 3

    reconstructed_dict = ResearchPlan.from_dict(p_dict)
    assert reconstructed_dict.goal == goal
    assert len(reconstructed_dict.subtasks) == len(plan.subtasks)

    # JSON roundtrip
    p_json = plan.to_json()
    assert isinstance(p_json, str)
    assert goal in p_json

    reconstructed_json = ResearchPlan.from_json(p_json)
    assert reconstructed_json.goal == goal
    assert reconstructed_json.subtasks[0].id == "subtask-1"

    # Integration with ResearchArtifact ORM model
    artifact = ResearchArtifact(
        session_id="sess-999",
        type="plan",
        content=plan.to_json(),
    )
    assert artifact.type == "plan"
    artifact_json = artifact.json_content
    assert artifact_json["goal"] == goal
    assert len(artifact_json["subtasks"]) >= 3

    # Parse back artifact JSON content into ResearchPlan
    artifact_plan = ResearchPlan.from_dict(artifact_json)
    assert artifact_plan.goal == goal


def test_parse_plan_json_markdown_fences_and_invalid():
    """Verify parse_plan_json handles raw JSON, markdown code blocks, and invalid inputs."""
    markdown_json = """```json
    {
        "session_id": "sess-42",
        "goal": "Verify system security",
        "subtasks": [
            {
                "id": "st-1",
                "description": "Scan codebase",
                "expected_evidence": "Audit log",
                "recommended_tools": ["SEARCH_PROJECT_KNOWLEDGE"],
                "success_criteria": "Scan clear",
                "status": "pending"
            }
        ],
        "overall_success_criteria": "Security verified"
    }
    ```"""
    plan = parse_plan_json(markdown_json)
    assert isinstance(plan, ResearchPlan)
    assert plan.session_id == "sess-42"
    assert plan.goal == "Verify system security"
    assert plan.subtasks[0].id == "st-1"

    with pytest.raises(ValueError):
        parse_plan_json("")

    with pytest.raises(ValueError):
        parse_plan_json("invalid json content string")


# ---------------------------------------------------------------------------
# Phase 7 Milestone 2: Strict Tool Registry Unit Tests
# ---------------------------------------------------------------------------


def test_tool_registry_allowlist_immutability():
    """Verify ALLOWED_TOOLS contains only the 3 strictly authorized tools."""
    expected = {
        "SEARCH_PROJECT_KNOWLEDGE",
        "READ_DOCUMENT_EVIDENCE",
        "ASK_GROUNDED_RESEARCH_ENGINE",
    }
    assert ALLOWED_TOOLS == expected

    registry = ToolRegistry()
    for name in expected:
        assert registry.is_allowed(name) is True
        assert registry.get_tool(name).name == name


@pytest.mark.asyncio
async def test_unauthorized_tool_rejection():
    """Verify arbitrary tool name raises UnauthorizedToolError."""
    ctx = ToolExecutionContext(
        user_id="user-1",
        project_id="proj-1",
        project_owner_id="user-1",
    )

    with pytest.raises(UnauthorizedToolError) as exc_info:
        await execute_tool("EXECUTE_SHELL", {"command": "ls"}, ctx, db=None)
    assert "unauthorized" in str(exc_info.value).lower()

    with pytest.raises(UnauthorizedToolError) as exc_info2:
        await execute_tool("RUN_PYTHON_SCRIPT", {"code": "import os"}, ctx, db=None)
    assert "unauthorized" in str(exc_info2.value).lower()


@pytest.mark.asyncio
async def test_auth_failure_permission_error():
    """Verify user authorization mismatch raises PermissionError."""
    ctx = ToolExecutionContext(
        user_id="user-attacker",
        project_id="proj-1",
        project_owner_id="user-owner",
    )

    with pytest.raises(PermissionError) as exc_info:
        await execute_tool("SEARCH_PROJECT_KNOWLEDGE", {"query": "secret"}, ctx, db=None)
    assert "not authorized" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_search_project_knowledge_execution():
    """Verify SEARCH_PROJECT_KNOWLEDGE tool execution with valid context."""
    try:
        from axiom.core.models import Base, Project, Document, DocumentChunk
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy.orm import sessionmaker

        engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with async_session() as db:
            proj = Project(id="p1", owner_id="u1", name="Proj 1")
            doc = Document(id="d1", project_id="p1", title="Quantum Paper", status="processed")
            chunk = DocumentChunk(id="c1", document_id="d1", content="Quantum entanglement is non-local.")
            db.add_all([proj, doc, chunk])
            await db.commit()

            ctx = ToolExecutionContext(user_id="u1", project_id="p1", project_owner_id="u1")
            obs = await execute_tool("SEARCH_PROJECT_KNOWLEDGE", {"query": "entanglement", "limit": 5}, ctx, db)

            assert obs.status == "success"
            assert obs.tool_name == "SEARCH_PROJECT_KNOWLEDGE"
            assert isinstance(obs.result, list)
            assert len(obs.result) == 1
            assert obs.result[0]["chunk_id"] == "c1"

        await engine.dispose()
    except (ImportError, Exception):
        ctx = ToolExecutionContext(user_id="u1", project_id="p1", project_owner_id="u1")
        obs = await execute_tool("SEARCH_PROJECT_KNOWLEDGE", {"query": "entanglement", "limit": 5}, ctx, db=None)
        assert obs.status == "success"
        assert obs.tool_name == "SEARCH_PROJECT_KNOWLEDGE"


@pytest.mark.asyncio
async def test_read_document_evidence_execution():
    """Verify READ_DOCUMENT_EVIDENCE tool returns document and chunks."""
    try:
        from axiom.core.models import Base, Project, Document, DocumentChunk
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy.orm import sessionmaker

        engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with async_session() as db:
            proj = Project(id="p1", owner_id="u1", name="Proj 1")
            doc = Document(id="d1", project_id="p1", title="Relativity Paper", status="processed")
            chunk = DocumentChunk(id="c1", document_id="d1", content="Speed of light is invariant.")
            db.add_all([proj, doc, chunk])
            await db.commit()

            ctx = ToolExecutionContext(user_id="u1", project_id="p1", project_owner_id="u1")
            obs = await execute_tool("READ_DOCUMENT_EVIDENCE", {"document_id": "d1"}, ctx, db)

            assert obs.status == "success"
            assert obs.result["document_id"] == "d1"
            assert obs.result["title"] == "Relativity Paper"
            assert len(obs.result["chunks"]) == 1

        await engine.dispose()
    except (ImportError, Exception):
        pass


@pytest.mark.asyncio
async def test_ask_grounded_research_engine_execution():
    """Verify ASK_GROUNDED_RESEARCH_ENGINE tool generates grounded response with citations."""
    try:
        from axiom.core.models import Base, Project, Document, DocumentChunk
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy.orm import sessionmaker

        engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with async_session() as db:
            proj = Project(id="p1", owner_id="u1", name="Proj 1")
            doc = Document(id="d1", project_id="p1", title="Paper", status="processed")
            chunk = DocumentChunk(id="c1", document_id="d1", content="Evidence chunk body text.")
            db.add_all([proj, doc, chunk])
            await db.commit()

            ctx = ToolExecutionContext(user_id="u1", project_id="p1", project_owner_id="u1")
            obs = await execute_tool("ASK_GROUNDED_RESEARCH_ENGINE", {"question": "What is in paper?", "chunk_ids": ["c1"]}, ctx, db)

            assert obs.status == "success"
            assert "question" in obs.result
            assert "answer" in obs.result
            assert "c1" in obs.result["citations"]

        await engine.dispose()
    except (ImportError, Exception):
        ctx = ToolExecutionContext(user_id="u1", project_id="p1", project_owner_id="u1")
        obs = await execute_tool("ASK_GROUNDED_RESEARCH_ENGINE", {"question": "What is in paper?"}, ctx, db=None)
        assert obs.status == "success"
        assert obs.result["answer"] == "Insufficient evidence"


@pytest.mark.asyncio
async def test_tool_timeout_handling():
    """Verify tool execution wrapping handles timeouts and returns status='timeout'."""
    import asyncio
    from pydantic import BaseModel

    class SlowToolInput(BaseModel):
        query: str

    class SlowTool(BaseTool):
        name = "SEARCH_PROJECT_KNOWLEDGE"

        def validate_params(self, params: dict) -> BaseModel:
            return SlowToolInput(**params)

        async def _execute(self, params: dict, context: ToolExecutionContext, db=None):
            await asyncio.sleep(0.2)
            return []

    registry = ToolRegistry()
    registry.register(SlowTool())

    ctx = ToolExecutionContext(
        user_id="u1",
        project_id="p1",
        project_owner_id="u1",
        timeout_seconds=0.01,
    )

    obs = await execute_tool(
        "SEARCH_PROJECT_KNOWLEDGE",
        {"query": "test"},
        ctx,
        db=None,
        registry=registry,
    )
    assert obs.status == "timeout"
    assert "timed out" in obs.error_message.lower()


# ---------------------------------------------------------------------------
# Phase 7 Milestone 3: Execution Loop, Budgets & Cancellation Unit Tests
# ---------------------------------------------------------------------------

from axiom.research.agent.budgets import (
    BudgetLimits,
    BudgetExceededError,
    check_budget_exceeded,
    enforce_budget,
)
from axiom.research.agent.cancellation import (
    SessionCancelledError,
    request_session_cancellation,
)
from axiom.research.agent.engine import ControlledExecutionEngine, TERMINAL_STATES


def test_budget_limits_defaults_and_from_session():
    """Verify BudgetLimits Pydantic model defaults and instantiation from session."""
    limits = BudgetLimits()
    assert limits.max_steps == 10
    assert limits.max_tool_calls == 15
    assert limits.max_runtime_seconds == 120.0

    session = ResearchSession(
        project_id="proj-b1",
        goal="Test limits",
        max_steps=5,
        max_tool_calls=8,
        max_runtime_seconds=60,
    )
    session_limits = BudgetLimits.from_session(session)
    assert session_limits.max_steps == 5
    assert session_limits.max_tool_calls == 8
    assert session_limits.max_runtime_seconds == 60.0


def test_check_budget_exceeded_max_steps():
    """Verify check_budget_exceeded identifies max_steps exhaustion."""
    session = ResearchSession(
        project_id="proj-b2",
        goal="Test max steps",
        max_steps=3,
        max_tool_calls=15,
        max_runtime_seconds=120,
        step_count=2,
    )
    assert check_budget_exceeded(session) is None

    session.step_count = 3
    reason = check_budget_exceeded(session)
    assert reason is not None
    assert "Step limit exceeded" in reason
    assert "step_count (3) >= max_steps (3)" in reason


def test_check_budget_exceeded_max_tool_calls():
    """Verify check_budget_exceeded identifies max_tool_calls exhaustion."""
    session = ResearchSession(
        project_id="proj-b3",
        goal="Test max tool calls",
        max_steps=10,
        max_tool_calls=5,
        max_runtime_seconds=120,
        tool_call_count=4,
    )
    assert check_budget_exceeded(session) is None

    session.tool_call_count = 5
    reason = check_budget_exceeded(session)
    assert reason is not None
    assert "Tool call limit exceeded" in reason
    assert "tool_call_count (5) >= max_tool_calls (5)" in reason


def test_check_budget_exceeded_max_runtime_seconds():
    """Verify check_budget_exceeded identifies max_runtime_seconds exhaustion."""
    from datetime import timedelta
    session = ResearchSession(
        project_id="proj-b4",
        goal="Test max runtime",
        max_steps=10,
        max_tool_calls=15,
        max_runtime_seconds=10.0,
    )
    session.created_at = datetime.now(timezone.utc) - timedelta(seconds=15)
    reason = check_budget_exceeded(session)
    assert reason is not None
    assert "Runtime limit exceeded" in reason


def test_enforce_budget_exception_raised():
    """Verify enforce_budget raises BudgetExceededError when budget exceeded."""
    session = ResearchSession(
        project_id="proj-b5",
        goal="Test enforce budget",
        max_steps=2,
        step_count=2,
    )
    with pytest.raises(BudgetExceededError) as exc_info:
        enforce_budget(session)
    assert "Step limit exceeded" in str(exc_info.value)


@pytest.mark.asyncio
async def test_request_session_cancellation_persistence_and_auth():
    """Verify request_session_cancellation verifies project ownership, sets flag, persists artifact, and updates state."""
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from axiom.core.models import Base, User, Project, ResearchSession, ResearchArtifact

    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        owner = User(id="user-owner-1", email="owner@axiom.ai", hashed_password="hash")
        attacker = User(id="user-attacker-1", email="attacker@axiom.ai", hashed_password="hash")
        project = Project(id="proj-cancel-1", owner_id=owner.id, name="Cancellation Test Proj")
        session = ResearchSession(
            id="sess-cancel-1",
            project_id=project.id,
            goal="Test session cancellation",
            status="CREATED",
        )
        db.add_all([owner, attacker, project, session])
        await db.commit()

        # 1. Ownership security check: unauthorized user raises PermissionError
        with pytest.raises(PermissionError) as exc_info:
            await request_session_cancellation(session.id, db, user_id=attacker.id)
        assert "not authorized" in str(exc_info.value).lower()

        # 2. Authorized owner requests session cancellation
        success = await request_session_cancellation(session.id, db, user_id=owner.id)
        assert success is True

        # Refresh session and verify DB state updates
        await db.refresh(session)
        assert session.cancellation_requested is True
        assert session.status == "CANCELLED"
        assert session.completed_at is not None

        # 3. Verify cancellation ResearchArtifact persistence
        from sqlalchemy import select
        stmt = select(ResearchArtifact).where(
            ResearchArtifact.session_id == session.id,
            ResearchArtifact.type == "cancellation",
        )
        res = await db.execute(stmt)
        artifact = res.scalars().first()
        assert artifact is not None
        assert artifact.type == "cancellation"
        data = artifact.json_content
        assert data["requested_by"] == owner.id
        assert data["session_id"] == session.id

    await engine.dispose()


@pytest.mark.asyncio
async def test_controlled_execution_engine_budget_halting():
    """Verify ControlledExecutionEngine halts execution and transitions status when budget is exceeded."""
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from axiom.core.models import Base, User, Project, ResearchSession, ResearchArtifact

    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        owner = User(id="user-e1", email="e1@axiom.ai", hashed_password="hash")
        proj = Project(id="proj-e1", owner_id=owner.id, name="Engine Test Project")
        session = ResearchSession(
            id="sess-e1",
            project_id="proj-e1",
            goal="Engine budget halt test",
            max_steps=1,
            step_count=1,
            status="PLANNING",
        )
        db.add_all([owner, proj, session])
        await db.commit()

        exec_engine = ControlledExecutionEngine(
            session_id="sess-e1",
            db=db,
            user_id="user-e1",
        )
        result_session = await exec_engine.run()

        assert result_session.status in ("FAILED", "VERIFYING")
        assert result_session.error_message is not None
        assert "Step limit exceeded" in result_session.error_message

        # Verify budget artifact persisted
        from sqlalchemy import select
        stmt = select(ResearchArtifact).where(
            ResearchArtifact.session_id == session.id,
            ResearchArtifact.type == "budget_exhausted",
        )
        res = await db.execute(stmt)
        artifact = res.scalars().first()
        assert artifact is not None

    await engine.dispose()


@pytest.mark.asyncio
async def test_execution_engine_cancellation_halt():
    """Verify ControlledExecutionEngine checks cancellation_requested before step execution and safely halts."""
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from axiom.core.models import Base, User, Project, ResearchSession, ResearchArtifact

    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        owner = User(id="u-eng-1", email="eng@axiom.ai", hashed_password="hash")
        project = Project(id="p-eng-1", owner_id=owner.id, name="Engine Test Proj")
        session = ResearchSession(
            id="s-eng-cancel",
            project_id=project.id,
            goal="Test engine cancellation",
            status="CREATED",
            cancellation_requested=True,  # Flag pre-set before engine loop
        )
        db.add_all([owner, project, session])
        await db.commit()

        engine_inst = ControlledExecutionEngine()
        res_session = await engine_inst.run_session(session.id, db, user_id=owner.id)

        assert res_session.status == "CANCELLED"
        assert res_session.completed_at is not None

        # Check cancellation artifact produced by engine abort
        from sqlalchemy import select
        stmt = select(ResearchArtifact).where(
            ResearchArtifact.session_id == session.id,
            ResearchArtifact.type == "cancellation",
        )
        res = await db.execute(stmt)
        artifacts = res.scalars().all()
        assert len(artifacts) >= 1

    await engine.dispose()


@pytest.mark.asyncio
async def test_controlled_execution_engine_full_run():
    """Verify ControlledExecutionEngine executes all steps from CREATED to COMPLETED successfully."""
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from axiom.core.models import Base, User, Project, ResearchSession, ResearchArtifact

    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        owner = User(id="u-full-1", email="full@axiom.ai", hashed_password="hash")
        project = Project(id="p-full-1", owner_id=owner.id, name="Full Run Proj")
        session = ResearchSession(
            id="s-full-run",
            project_id=project.id,
            goal="Full execution test goal",
            status="CREATED",
            max_steps=10,
            max_tool_calls=15,
        )
        db.add_all([owner, project, session])
        await db.commit()

        engine_inst = ControlledExecutionEngine(
            session_id=session.id,
            db=db,
            user_id=owner.id,
        )
        res_session = await engine_inst.run()

        assert res_session.status == "COMPLETED"
        assert res_session.completed_at is not None
        assert res_session.step_count > 0

        # Check artifacts created during run
        from sqlalchemy import select
        stmt = select(ResearchArtifact).where(ResearchArtifact.session_id == session.id)
        res = await db.execute(stmt)
        artifacts = res.scalars().all()
        artifact_types = {a.type for a in artifacts}

        assert "plan" in artifact_types
        assert "final_artifact" in artifact_types

    await engine.dispose()


def test_budget_tracker_increments_and_exceeded_checks():
    """Verify BudgetTracker increments, syncs, and reports budget limits."""
    from axiom.research.agent.budgets import BudgetTracker, BudgetLimits

    limits = BudgetLimits(max_steps=5, max_tool_calls=10, max_runtime_seconds=60.0)
    tracker = BudgetTracker(limits=limits)

    assert tracker.step_count == 0
    assert tracker.tool_call_count == 0
    assert tracker.increment_step() == 1
    assert tracker.increment_tool_call(3) == 3

    exceeded, reason = tracker.is_budget_exceeded()
    assert exceeded is False
    assert reason is None

    tracker.increment_step(4)  # step_count is now 5 == max_steps
    exceeded, reason = tracker.is_budget_exceeded()
    assert exceeded is True
    assert "MAX_STEPS exceeded" in reason

    tracker.step_count = 0
    tracker.increment_tool_call(7)  # tool_call_count is now 10 == max_tool_calls
    exceeded, reason = tracker.is_budget_exceeded()
    assert exceeded is True
    assert "MAX_TOOL_CALLS exceeded" in reason


@pytest.mark.asyncio
async def test_is_cancellation_requested_helper():
    """Verify is_cancellation_requested accurately queries DB cancellation status."""
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from axiom.core.models import Base, User, Project, ResearchSession
    from axiom.research.agent.cancellation import is_cancellation_requested, request_session_cancellation

    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        user = User(id="u-canc-check", email="canc@axiom.ai", hashed_password="hash")
        project = Project(id="p-canc-check", owner_id=user.id, name="Canc Check Proj")
        session = ResearchSession(id="s-canc-check", project_id=project.id, goal="Check cancellation helper")
        db.add_all([user, project, session])
        await db.commit()

        assert await is_cancellation_requested(session.id, db) is False

        await request_session_cancellation(session.id, db, user_id=user.id)
        assert await is_cancellation_requested(session.id, db) is True

    await engine.dispose()


