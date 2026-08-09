"""Tests for AXIOM Verification Factory."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from axiom.vfactory.journeys import ALL_JOURNEYS
from axiom.vfactory.models import TestLevel, VerificationState
from axiom.vfactory.orchestrator import VFactoryOrchestrator
from axiom.vfactory.registry import DEFAULT_CAPABILITIES
from axiom.vfactory.roles import default_verification_roles
from axiom.vfactory.scorer import compute_all_scores
from axiom.vfactory.store import get_vfactory_store


@pytest.fixture
def orch() -> VFactoryOrchestrator:
    return VFactoryOrchestrator(":memory:")


def test_default_capabilities_catalog():
    assert len(DEFAULT_CAPABILITIES) >= 14
    ids = {c["capability_id"] for c in DEFAULT_CAPABILITIES}
    assert "cap_vfactory" in ids
    assert "cap_frce" in ids


def test_bootstrap_seeds_registry(orch: VFactoryOrchestrator):
    boot = orch.bootstrap()
    assert boot["capabilities_seeded"] >= 14
    caps = orch.registry_store.list_capabilities()
    assert len(caps) == boot["capabilities_seeded"]


def test_bootstrap_idempotent(orch: VFactoryOrchestrator):
    first = orch.bootstrap()["capabilities_seeded"]
    second = orch.bootstrap()["capabilities_seeded"]
    assert first == second


def test_verification_roles():
    roles = default_verification_roles()
    assert len(roles) == 12
    assert roles[0]["role"] == "test_architect"


def test_compute_scores(orch: VFactoryOrchestrator):
    caps = orch.registry_store.list_capabilities()
    if not caps:
        orch.bootstrap()
        caps = orch.registry_store.list_capabilities()
    scores = compute_all_scores(caps)
    assert any(s.domain.value == "overall" for s in scores)
    overall = next(s for s in scores if s.domain.value == "overall")
    assert 0.0 <= overall.score <= 1.0


def test_journey_a_research_workspace():
    result = ALL_JOURNEYS["journey_a"](":memory:")
    assert result.passed
    assert result.steps_completed == result.steps_total


def test_journey_b_campaign():
    result = ALL_JOURNEYS["journey_b"](":memory:")
    assert result.passed
    assert result.steps_total >= 4


def test_journey_c_formal_math():
    result = ALL_JOURNEYS["journey_c"](":memory:")
    assert result.passed


def test_journey_d_sandbox_recovery():
    result = ALL_JOURNEYS["journey_d"](":memory:")
    assert result.passed


def test_verification_cycle_journeys_only(orch: VFactoryOrchestrator):
    orch.bootstrap()
    vrun = orch.run_verification_cycle(run_pyramid=False, run_journeys=True)
    assert vrun.overall_passed
    assert vrun.verification_run_id.startswith("vrun_")


def test_discover_affected_capabilities(orch: VFactoryOrchestrator):
    orch.bootstrap()
    affected = orch.discover_affected_capabilities(["axiom/campaign/orchestrator.py"])
    assert "cap_frce" in affected


def test_store_persistence():
    store = get_vfactory_store(":memory:")
    from axiom.vfactory.models import TestRunResult, _new_id
    from axiom.vfactory.registry import seed_registry

    seed_registry(store)
    tr = TestRunResult(
        run_id=_new_id("trun"),
        level=TestLevel.UNIT,
        test_name="test",
        passed=True,
        duration_seconds=0.1,
    )
    store.save_test_run(tr)
    runs = store.list_test_runs(limit=1)
    assert len(runs) == 1
    assert runs[0].passed


def test_update_capability_status(orch: VFactoryOrchestrator):
    from axiom.vfactory.registry import update_capability_status

    orch.bootstrap()
    cap = update_capability_status(
        orch.registry_store, "cap_frce", passed=True, evidence_id="ev_test"
    )
    assert cap is not None
    assert cap.status == VerificationState.VERIFIED
    assert "ev_test" in cap.verification_evidence


def test_vfactory_api_routes():
    from axiom.services.api_gateway.main import app

    client = TestClient(app)
    resp = client.get("/vfactory/manifest")
    assert resp.status_code == 200
    data = resp.json()
    assert "pyramid_levels" in data
    assert "journey_a" in data["journeys"]

    resp = client.get("/vfactory/status")
    assert resp.status_code == 200
    assert "scores" in resp.json()

    resp = client.get("/vfactory/capabilities")
    assert resp.status_code == 200
    assert resp.json()["count"] >= 14

    resp = client.post(
        "/vfactory/run/journey",
        json={"journey_key": "journey_a"},
    )
    assert resp.status_code == 200
    assert resp.json()["passed"] is True
