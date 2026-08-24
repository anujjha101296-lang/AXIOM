"""
AXIOM Phase 17 — Long-Horizon Mathematical Research Engine E2E & Security Tests
================================================================================
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
from axiom.long_horizon.models import (
    ApproachMemory,
    ApproachStatus,
    CriticRecommendation,
    ResearchProblem,
    TaskState,
)
from axiom.long_horizon.decomposition import ProblemDecompositionEngine
from axiom.long_horizon.memory import ApproachMemoryEngine
from axiom.long_horizon.critic import ResearchCriticEngine


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
async def test_long_horizon_core_engines():
    decomposer = ProblemDecompositionEngine()
    memory_engine = ApproachMemoryEngine()
    critic = ResearchCriticEngine()

    # 1. Decomposition test
    subs = decomposer.decompose_problem("p1", "Twin Prime Conjecture", "Infinitely many primes differ by 2.")
    assert len(subs) == 3

    # 2. Memory hash & duplicate check
    h = memory_engine.compute_approach_hash("Induction", "Base case")
    mem = ApproachMemory(problem_id="p1", approach_hash=h, summary="[Induction] Base case", status=ApproachStatus.FAILED)
    is_dup, _ = memory_engine.check_duplicate_attempt([mem], "Induction", "Base case")
    assert is_dup is True


@pytest.mark.asyncio
async def test_long_horizon_rest_api_and_security(test_app, async_session):
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
        # User A creates long-horizon research problem -> 201 Created
        res_prob = await client.post(
            "/api/v1/long-horizon/problem",
            json={
                "project_id": "proj-a",
                "title": "Collatz Conjecture Bounded Trajectories",
                "description": "Analyze 3n+1 orbits up to 10^18",
            },
            headers={"Authorization": f"Bearer {token_a}", "X-User-Id": "user-a"},
        )
        assert res_prob.status_code == 201
        data = res_prob.json()
        assert data["subproblems_count"] == 3

        # User B attempts to access Project A research problems -> 403 Forbidden
        res_sec = await client.get(
            "/api/v1/long-horizon/project/proj-a",
            headers={"Authorization": f"Bearer {token_b}", "X-User-Id": "user-b"},
        )
        assert res_sec.status_code == 403
