"""
AXIOM Phase 15 — Computational Experiment & Verification Engine E2E & Security Tests
====================================================================================
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
from axiom.experiment.models import (
    ExperimentStatus,
    ReproducibilityStatus,
    VerificationStatus,
)
from axiom.experiment.sandbox import SecureSandbox
from axiom.experiment.designer import ExperimentDesigner
from axiom.experiment.executor import ExperimentExecutor
from axiom.experiment.reproducibility import ReproducibilityEngine
from axiom.experiment.independent_verifier import IndependentVerifier


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
async def test_sandbox_security_attacks():
    sandbox = SecureSandbox(timeout_seconds=1.0)

    # 1. Prohibited import attack
    res_import = sandbox.execute_code("import subprocess\nsubprocess.run(['ls'])")
    assert res_import["status"] == ExperimentStatus.SECURITY_VIOLATION

    # 2. Network socket attack
    res_net = sandbox.execute_code("import socket\ns = socket.socket()")
    assert res_net["status"] == ExperimentStatus.SECURITY_VIOLATION

    # 3. Timeout attack
    res_timeout = sandbox.execute_code("while True: pass")
    assert res_timeout["status"] in (ExperimentStatus.TIMEOUT, ExperimentStatus.FAILED)


@pytest.mark.asyncio
async def test_experiment_executor_reproducibility_and_verifier():
    designer = ExperimentDesigner()
    executor = ExperimentExecutor()
    repro = ReproducibilityEngine()
    verifier = IndependentVerifier()

    exp = designer.design_experiment("proj-1", name="Numerical Test", code_body="import math\nresult = {'v': math.sqrt(25)}")
    run = executor.run_experiment(exp)
    assert run.status == ExperimentStatus.COMPLETED
    assert run.result_data.get("v") == 5.0

    # Reproducibility
    r_status, r1, r2 = repro.test_reproducibility(exp, seed=123)
    assert r_status == ReproducibilityStatus.REPRODUCIBLE

    # Independent Verification
    v = verifier.verify_run(exp.id, run)
    assert v.verification_status == VerificationStatus.VERIFIED


@pytest.mark.asyncio
async def test_experiment_rest_api_and_security(test_app, async_session):
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
        # User A designs experiment -> 201 Created
        res_design = await client.post(
            "/api/v1/experiment/design",
            json={
                "project_id": "proj-a",
                "name": "Integration Test Exp",
                "code_body": "result = {'sum': sum([1, 2, 3])}",
            },
            headers={"Authorization": f"Bearer {token_a}", "X-User-Id": "user-a"},
        )
        assert res_design.status_code == 201
        exp_data = res_design.json()
        exp_id = exp_data["id"]

        # User A runs experiment -> 200 OK
        res_run = await client.post(
            f"/api/v1/experiment/{exp_id}/run",
            headers={"Authorization": f"Bearer {token_a}", "X-User-Id": "user-a"},
        )
        assert res_run.status_code == 200
        run_data = res_run.json()
        assert run_data["status"] == "COMPLETED"
        assert run_data["result_data"]["sum"] == 6

        # User B attempts to access Project A experiments -> 403 Forbidden
        res_sec = await client.get(
            "/api/v1/experiment/project/proj-a",
            headers={"Authorization": f"Bearer {token_b}", "X-User-Id": "user-b"},
        )
        assert res_sec.status_code == 403
