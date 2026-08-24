"""
AXIOM Phase 13 — Scientific Knowledge Graph & Claim Graph E2E & Security Tests
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
from axiom.services.api_gateway.auth import SECRET_TOKEN, create_jwt_token
from axiom.knowledge_graph.models import (
    ClaimType,
    EntityType,
    EpistemicStatus,
    GraphClaim,
    GraphClaimEvidence,
    GraphEntity,
    GraphEntityAlias,
    GraphRelationship,
    GraphResearchGap,
    PredicateType,
)
from axiom.knowledge_graph.extractor import ClaimExtractor, EntityExtractor
from axiom.knowledge_graph.entity_resolution import ConservativeEntityResolver
from axiom.knowledge_graph.provenance import ProvenanceVerifier
from axiom.knowledge_graph.contradictions import ContradictionDetector
from axiom.knowledge_graph.research_gaps import ResearchGapAnalyzer


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
async def test_claim_and_entity_extractor():
    c_ext = ClaimExtractor()
    claims = c_ext.extract_claims("proj-1", "Method A improves speedup by 40%.", chunk_id="chk-1")
    assert len(claims) == 1
    assert claims[0][0].claim_type == ClaimType.QUANTITATIVE

    e_ext = EntityExtractor()
    entities = e_ext.extract_entities("proj-1", "The Riemann Zeta Function is studied in mathematics.")
    assert len(entities) >= 1


@pytest.mark.asyncio
async def test_conservative_entity_resolution():
    resolver = ConservativeEntityResolver()
    e1 = GraphEntity(project_id="proj-1", name="Satisfiability Modulo Theories", entity_type=EntityType.CONCEPT)
    e2 = GraphEntity(project_id="proj-1", name="SMT", entity_type=EntityType.CONCEPT)

    resolved, alias, is_new = resolver.resolve_entity(e2, [e1], [])
    assert not is_new
    assert resolved.id == e1.id
    assert alias is not None
    assert alias.alias == "SMT"


@pytest.mark.asyncio
async def test_provenance_verifier():
    verifier = ProvenanceVerifier()
    c = GraphClaim(project_id="proj-1", claim_text="Valid claim")
    ev_valid = GraphClaimEvidence(claim_id=c.id, chunk_id="chk-1", snippet="Valid evidence snippet")
    ev_invalid = GraphClaimEvidence(claim_id=c.id, snippet="")

    assert verifier.verify_claim_provenance(c, [ev_valid]) is True
    assert verifier.verify_claim_provenance(c, [ev_invalid]) is False


@pytest.mark.asyncio
async def test_contradiction_detector():
    detector = ContradictionDetector()
    c1 = GraphClaim(project_id="proj-1", claim_text="Algorithm X improves precision.")
    c2 = GraphClaim(project_id="proj-1", claim_text="Algorithm X does not improve precision.")

    cd = detector.detect_contradiction(c1, c2)
    assert cd is not None
    assert cd.contradiction_type == "DIRECT_NEGATION"
    assert c1.epistemic_status == EpistemicStatus.CONTRADICTED


@pytest.mark.asyncio
async def test_research_gap_analyzer():
    analyzer = ResearchGapAnalyzer()
    e = GraphEntity(project_id="proj-1", name="Isolated Concept")
    c = GraphClaim(project_id="proj-1", claim_text="Unproven claim")

    gaps = analyzer.analyze_gaps("proj-1", [e], [c], [], [], [])
    assert len(gaps) >= 2


@pytest.mark.asyncio
async def test_knowledge_graph_rest_api_and_security(test_app, async_session):
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
        # User A extracts graph into Project A
        res_ext = await client.post(
            "/api/v1/knowledge-graph/extract",
            json={
                "project_id": "proj-a",
                "text": "The Prime Number Theorem describes the asymptotic distribution of prime numbers.",
            },
            headers={"Authorization": f"Bearer {token_a}", "X-User-Id": "user-a"},
        )
        assert res_ext.status_code == 201

        # User A fetches summary for Project A -> 200 OK
        res_sum = await client.get(
            "/api/v1/knowledge-graph/summary/proj-a",
            headers={"Authorization": f"Bearer {token_a}", "X-User-Id": "user-a"},
        )
        assert res_sum.status_code == 200
        summary_data = res_sum.json()
        assert summary_data["total_claims"] >= 1

        # User B attempts to fetch summary for Project A -> 403 Forbidden
        res_sec = await client.get(
            "/api/v1/knowledge-graph/summary/proj-a",
            headers={"Authorization": f"Bearer {token_b}", "X-User-Id": "user-b"},
        )
        assert res_sec.status_code == 403
