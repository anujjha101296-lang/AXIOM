"""
AXIOM Phase 16 — Formal Mathematics & Proof Verification Engine E2E & Security Tests
=====================================================================================
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
from axiom.formal.models import (
    FormalLanguage,
    ProofStatus,
    SMTResult,
)
from axiom.formal.parser import FormalStatementEngine
from axiom.formal.lean_engine import Lean4Engine
from axiom.formal.smt_engine import SMTGateway
from axiom.formal.counterexample import CounterexampleHunter


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
async def test_lean_verifier_and_smt_gateway():
    lean = Lean4Engine()
    smt = SMTGateway()
    hunter = CounterexampleHunter()

    # 1. Lean verification success
    p1, a1 = lean.verify_proof("thm-1", "theorem add_zero (n : Nat) : n + 0 = n := by rfl")
    assert p1.status == ProofStatus.VERIFIED
    assert p1.is_sorry_free is True

    # 2. Lean verification failure on sorry
    p2, a2 = lean.verify_proof("thm-2", "theorem unproven (n : Nat) : n = 0 := by sorry")
    assert p2.status == ProofStatus.PROOF_IN_PROGRESS
    assert p2.is_sorry_free is False

    # 3. SMT Gateway SAT / UNSAT
    res_sat, assign, _ = smt.solve_formula("x > 10")
    assert res_sat == SMTResult.SAT

    res_unsat, _, _ = smt.solve_formula("x > 0 and x < 0")
    assert res_unsat == SMTResult.UNSAT

    # 4. Counterexample hunter
    ce = hunter.find_counterexample("thm-3", "All prime numbers are odd")
    assert ce is not None
    assert ce.assignment["n"] == 2


@pytest.mark.asyncio
async def test_formal_math_rest_api_and_security(test_app, async_session):
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
        # User A formalizes theorem -> 201 Created
        res_form = await client.post(
            "/api/v1/formal-math/formalize",
            json={
                "project_id": "proj-a",
                "natural_language": "For all integers n, n + 0 = n",
                "language": "LEAN4",
            },
            headers={"Authorization": f"Bearer {token_a}", "X-User-Id": "user-a"},
        )
        assert res_form.status_code == 201
        thm_data = res_form.json()
        thm_id = thm_data["id"]

        # User A verifies Lean 4 proof -> 200 OK
        res_ver = await client.post(
            "/api/v1/formal-math/verify-lean",
            json={
                "theorem_id": thm_id,
                "proof_script": "theorem thm_test (n : Nat) : n + 0 = n := by rfl",
            },
            headers={"Authorization": f"Bearer {token_a}"},
        )
        assert res_ver.status_code == 200
        ver_data = res_ver.json()
        assert ver_data["verified"] is True

        # SMT solve endpoint -> 200 OK
        res_smt = await client.post(
            "/api/v1/formal-math/solve-smt",
            json={"formula_text": "x > 0 and x < 0"},
            headers={"Authorization": f"Bearer {token_a}"},
        )
        assert res_smt.status_code == 200
        assert res_smt.json()["result"] == "UNSAT"

        # User B attempts to access Project A formal theorems -> 403 Forbidden
        res_sec = await client.get(
            "/api/v1/formal-math/project/proj-a",
            headers={"Authorization": f"Bearer {token_b}", "X-User-Id": "user-b"},
        )
        assert res_sec.status_code == 403
