"""
AXIOM Phase 18 — Mathematical Research Challenge Harness E2E & Security Tests
==============================================================================
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from axiom.core.database import get_db, Base
from axiom.services.api_gateway.main import app
from axiom.services.api_gateway.auth import create_jwt_token
from axiom.challenge_harness.models import ChallengeLevel, EvaluationOutcome, FailureClass
from axiom.challenge_harness.curator import ProblemCurator
from axiom.challenge_harness.evaluator import IndependentEvaluator
from axiom.challenge_harness.anti_gaming import AntiGamingEngine


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
async def test_challenge_harness_core_engines():
    curator = ProblemCurator()
    evaluator = IndependentEvaluator()
    anti_gaming = AntiGamingEngine()

    challs = curator.get_golden_challenges()
    assert len(challs) >= 4

    # Evaluate blind run
    run = evaluator.evaluate_run(challs[0], "Research output", "theorem thm (n : Nat) : n + 0 = n := by rfl")
    assert run.outcome == EvaluationOutcome.SOLVED
    assert run.proof_verified is True

    # Anti-gaming inspection
    is_g, _ = anti_gaming.inspect_output("hardcoded_answer_flag used")
    assert is_g is True


@pytest.mark.asyncio
async def test_challenge_harness_rest_api(test_app, async_session):
    token = create_jwt_token("admin@axiom.com")

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # GET /api/v1/benchmarks/challenges -> 200 OK
        res_ch = await client.get("/api/v1/benchmarks/challenges", headers={"Authorization": f"Bearer {token}"})
        assert res_ch.status_code == 200
        data_ch = res_ch.json()
        assert data_ch["total_challenges"] >= 4
        ch_id = data_ch["challenges"][0]["id"]

        # POST /api/v1/benchmarks/evaluate -> 201 Created
        res_ev = await client.post(
            "/api/v1/benchmarks/evaluate",
            json={
                "challenge_id": ch_id,
                "agent_output": "Research output",
                "proof_script": "theorem thm (n : Nat) : n + 0 = n := by rfl",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res_ev.status_code == 201
        run_data = res_ev.json()
        assert run_data["proof_verified"] is True

        # GET /api/v1/benchmarks/results -> 200 OK
        res_res = await client.get("/api/v1/benchmarks/results", headers={"Authorization": f"Bearer {token}"})
        assert res_res.status_code == 200
        assert res_res.json()["total_runs"] >= 1
