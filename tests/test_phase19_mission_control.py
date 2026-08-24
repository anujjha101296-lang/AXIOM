"""
AXIOM Phase 19 — Autonomous Research Mission Control E2E & Security Tests
==========================================================================
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from axiom.core.database import get_db, Base
from axiom.core.models import User, Project
from axiom.services.api_gateway.main import app
from axiom.services.api_gateway.auth import create_jwt_token
from axiom.mission_control.models import MissionBudget, MissionState, ResearchMission
from axiom.mission_control.controller import MissionController
from axiom.mission_control.checkpoint import CheckpointManager


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
async def test_mission_control_core_engines():
    controller = MissionController()
    chk_mgr = CheckpointManager()

    m = ResearchMission(project_id="proj-1", name="M1", objective="O1", budget=MissionBudget(max_iterations=3))
    m, chk1 = controller.start_mission(m)
    assert m.state == MissionState.RUNNING
    assert chk1.checkpoint_hash != ""

    cont, msg, chk2 = controller.step_mission(m)
    assert cont is True
    assert m.current_iteration == 1

    m, chk3 = controller.emergency_stop(m)
    assert m.state == MissionState.EMERGENCY_STOPPED


@pytest.mark.asyncio
async def test_mission_control_rest_api_and_security(test_app, async_session):
    # Setup User A and User B
    u_a = User(id="user-a", email="usera@axiom.com", hashed_password="pw")
    u_b = User(id="user-b", email="userb@axiom.com", hashed_password="pw")
    proj_a = Project(id="proj-a", owner_id="user-a", name="Project A")
    proj_b = Project(id="proj-b", owner_id="user-b", name="Project B")
    async_session.add_all([u_a, u_b, proj_a, proj_b])
    await async_session.commit()

    token_a = create_jwt_token("usera@axiom.com")
    token_b = create_jwt_token("userb@axiom.com")

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # User A creates mission -> 201 Created
        res_m = await client.post(
            "/api/v1/missions",
            json={
                "project_id": "proj-a",
                "name": "Mission Alpha",
                "objective": "Systematic Goldbach research",
            },
            headers={"Authorization": f"Bearer {token_a}", "X-User-Id": "user-a"},
        )
        assert res_m.status_code == 201
        m_id = res_m.json()["mission"]["id"]

        # User A starts mission -> 200 OK
        res_start = await client.post(
            f"/api/v1/missions/{m_id}/start",
            headers={"Authorization": f"Bearer {token_a}"},
        )
        assert res_start.status_code == 200
        assert res_start.json()["mission"]["state"] == "RUNNING"

        # User A triggers emergency stop -> 200 OK
        res_stop = await client.post(
            f"/api/v1/missions/{m_id}/emergency-stop",
            headers={"Authorization": f"Bearer {token_a}"},
        )
        assert res_stop.status_code == 200
        assert res_stop.json()["mission"]["state"] == "EMERGENCY_STOPPED"

        # User B attempts to access Project A missions -> 403 Forbidden
        res_sec = await client.get(
            "/api/v1/missions/project/proj-a",
            headers={"Authorization": f"Bearer {token_b}", "X-User-Id": "user-b"},
        )
        assert res_sec.status_code == 403
