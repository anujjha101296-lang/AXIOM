"""
AXIOM Phase 20 — Research Operating System / Production Control Plane E2E & Security Tests
==========================================================================================
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from axiom.core.database import get_db, Base
from axiom.services.api_gateway.main import app
from axiom.services.api_gateway.auth import create_jwt_token
from axiom.control_plane.models import WorkerStatus
from axiom.control_plane.registry import AgentRegistry
from axiom.control_plane.policy_engine import ToolPolicyEngine
from axiom.control_plane.model_router import ModelRouter
from axiom.control_plane.state_machine import StateMachineEngine
from axiom.control_plane.worker import WorkerEngine


@pytest_asyncio.fixture
async def async_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_factory() as session:
        yield session

    await engine.dispose()


@pytest_asyncio.fixture
async def test_app(async_session):
    async def _override_get_db():
        yield async_session

    app.dependency_overrides[get_db] = _override_get_db
    yield app
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_control_plane_core_engines():
    registry = AgentRegistry()
    policy = ToolPolicyEngine()
    sm = StateMachineEngine()
    worker_engine = WorkerEngine()

    profiles = registry.list_profiles()
    assert len(profiles) == 9

    auth, _ = policy.authorize_and_validate("user-1", "m-1", "MATHEMATICIAN", "formulate_lemma", {})
    assert auth is True

    valid, _ = sm.validate_mission_transition("RUNNING", "COMPLETED")
    assert valid is True

    w = worker_engine.register_worker("w-test")
    assert w.status == WorkerStatus.AVAILABLE


@pytest.mark.asyncio
async def test_control_plane_rest_api(test_app, async_session):
    token = create_jwt_token("admin@axiom.com")

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # GET /api/v1/control-plane/agents -> 200 OK
        res_ag = await client.get("/api/v1/control-plane/agents", headers={"Authorization": f"Bearer {token}"})
        assert res_ag.status_code == 200
        assert res_ag.json()["total_agents"] == 9

        # POST /api/v1/control-plane/events -> 201 Created
        res_ev = await client.post(
            "/api/v1/control-plane/events",
            json={
                "project_id": "proj-1",
                "mission_id": "m-1",
                "event_type": "MISSION_CREATED",
                "actor": "admin",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res_ev.status_code == 201
        assert res_ev.json()["event_type"] == "MISSION_CREATED"

        # GET /api/v1/control-plane/events -> 200 OK
        res_evs = await client.get("/api/v1/control-plane/events", headers={"Authorization": f"Bearer {token}"})
        assert res_evs.status_code == 200
        assert res_evs.json()["total_events"] >= 1
