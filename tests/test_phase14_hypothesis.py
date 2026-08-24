"""
AXIOM Phase 14 — Hypothesis & Scientific Reasoning Engine E2E & Security Tests
=============================================================================
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
from axiom.hypothesis.models import (
    CritiqueStatus,
    Hypothesis,
    HypothesisStatus,
)
from axiom.hypothesis.generator import HypothesisGenerator
from axiom.hypothesis.critic import ScientificCritic
from axiom.hypothesis.prediction import PredictionGenerator
from axiom.hypothesis.falsification import FalsificationEngine
from axiom.hypothesis.ranking import HypothesisRanker
from axiom.hypothesis.planner import VerificationPlanner
from axiom.hypothesis.bounded_loop import BoundedScientificLoop


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
async def test_hypothesis_generator_and_critic():
    gen = HypothesisGenerator()
    critic = ScientificCritic()

    hyps = gen.generate_hypotheses("proj-1", "How do neural networks generalize under distribution shift?")
    assert len(hyps) >= 1
    assert hyps[0].status == HypothesisStatus.PROPOSED

    critique = critic.critique_hypothesis(hyps[0])
    assert critique.status in (CritiqueStatus.VALID, CritiqueStatus.NEEDS_REVISION)


@pytest.mark.asyncio
async def test_prediction_generator_and_falsifier():
    pred_gen = PredictionGenerator()
    falsifier = FalsificationEngine()

    h = Hypothesis(project_id="proj-1", claim="Method X reduces memory consumption.")
    preds = pred_gen.generate_predictions(h)
    assert len(preds) == 2

    # Falsification check
    ev_pool = [{"text": "Method X disproves memory reduction, increasing memory usage by 50%."}]
    h_updated, counter_ev = falsifier.search_counterevidence(h, ev_pool)
    assert h_updated.status in (HypothesisStatus.CONTRADICTED, HypothesisStatus.FALSIFIED)


@pytest.mark.asyncio
async def test_bounded_scientific_loop():
    loop = BoundedScientificLoop(max_iterations=3)
    res = loop.run_scientific_loop("proj-1", "What limits quantum coherence time?")
    assert res["iterations_executed"] <= 3
    assert len(res["hypotheses"]) >= 1


@pytest.mark.asyncio
async def test_hypothesis_rest_api_and_security(test_app, async_session):
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
        # User A generates hypotheses for Project A -> 201 Created
        res_gen = await client.post(
            "/api/v1/hypothesis/generate",
            json={
                "project_id": "proj-a",
                "question": "How does attention scaling affect token efficiency?",
            },
            headers={"Authorization": f"Bearer {token_a}", "X-User-Id": "user-a"},
        )
        assert res_gen.status_code == 201
        created_data = res_gen.json()
        assert len(created_data) >= 1

        # User A lists hypotheses for Project A -> 200 OK
        res_list = await client.get(
            "/api/v1/hypothesis/project/proj-a",
            headers={"Authorization": f"Bearer {token_a}", "X-User-Id": "user-a"},
        )
        assert res_list.status_code == 200
        summary_data = res_list.json()
        assert summary_data["total_hypotheses"] >= 1

        # User B attempts to access Project A hypotheses -> 403 Forbidden
        res_sec = await client.get(
            "/api/v1/hypothesis/project/proj-a",
            headers={"Authorization": f"Bearer {token_b}", "X-User-Id": "user-b"},
        )
        assert res_sec.status_code == 403
