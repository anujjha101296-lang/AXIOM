"""Tests for Open Problem Research Lab v1."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from axiom.open_problems.engine import OpenProblemError, OpenProblemLab
from axiom.open_problems.models import ResearchStatus
from axiom.services.api_gateway.main import app


def test_intake_map_decompose_strategies(tmp_path):
    lab = OpenProblemLab(str(tmp_path / "opl.db"))
    p = lab.create(
        "Odd primes known false",
        "Is it true that all odd numbers greater than 1 are prime (known false)?",
        known_info="Already disproven. Composite 9 is a counterexample.",
        stage_level=1,
    )
    assert p.understanding.required_conclusion
    assert p.known_results
    buckets = {r.bucket.value for r in p.known_results}
    assert "WHAT_IS_DISPROVEN" in buckets
    assert "WHAT_IS_UNKNOWN" in buckets
    p = lab.map_knowledge(p.problem_id)
    assert p.research_status == ResearchStatus.MAPPED
    p = lab.decompose(p.problem_id)
    assert len(p.subproblems) >= 5
    p = lab.generate_strategies(p.problem_id)
    assert len(p.strategies) >= 4
    kinds = {s.kind.value for s in p.strategies}
    assert "COUNTEREXAMPLE" in kinds
    assert "FORMAL" in kinds
    assert len(p.tracks) >= 4
    # Tracks independent
    assert all(t.contaminated_by == [] for t in p.tracks)


def test_cannot_auto_millennium(tmp_path):
    lab = OpenProblemLab(str(tmp_path / "mil.db"))
    with pytest.raises(OpenProblemError, match="Millennium"):
        lab.create("RH", "Solve the Riemann Hypothesis", stage_level=9)


def test_cannot_self_resolve(tmp_path):
    lab = OpenProblemLab(str(tmp_path / "res.db"))
    p = lab.create("Toy", "Does n+0=n for integers?", stage_level=1)
    lab.map_knowledge(p.problem_id)
    lab.generate_strategies(p.problem_id)
    with pytest.raises(OpenProblemError, match="RESOLVED"):
        lab.transition(p.problem_id, ResearchStatus.RESOLVED, reason="model said so")


def test_level1_campaign_cycle_counterexample_first(tmp_path):
    lab = OpenProblemLab(str(tmp_path / "l1.db"))
    p = lab.create(
        "Known false primes",
        "Is it true that all odd numbers greater than 1 are prime (known false)?",
        known_info="Always false / known false. 9 is composite.",
        stage_level=1,
        research_objective="Refute via counterexample-first",
    )
    result = lab.run_investigation_cycle(p.problem_id)
    assert result["is_millennium_attempt"] is False
    assert result["is_scientific_discovery_claim"] is False
    assert "discovery_cycle" in result["stages_executed"]
    final = lab.store.get(p.problem_id)
    assert final is not None
    assert final.report.get("is_scientific_discovery_claim") is False
    assert final.campaign_ids
    assert final.discovery_ids
    # Prefer REFUTED for known-false Level-1
    assert final.research_status == ResearchStatus.REFUTED
    assert final.counterexample_ids
    assert any(e.event_type == "COUNTEREXAMPLE_FOUND" for e in final.timeline)


def test_abandon_strategy(tmp_path):
    lab = OpenProblemLab(str(tmp_path / "ab.db"))
    p = lab.create("Abandon test", "Does n+0=n?", stage_level=1)
    p = lab.generate_strategies(p.problem_id)
    sid = p.strategies[0].strategy_id
    p = lab.abandon_strategy(p.problem_id, sid, "Low information value")
    assert any(s.abandoned for s in p.strategies)
    assert "Low information value" in p.stopping_reasons


@pytest.fixture
def client(tmp_path, monkeypatch):
    db = str(tmp_path / "opl_api.db")
    monkeypatch.setenv("AXIOM_DB_PATH", db)
    from axiom.config import settings
    from axiom.open_problems import store as ostore
    from axiom.discovery import store as dstore
    from axiom.campaign import store as cstore
    from axiom.skai import store as sstore
    from axiom.experiment import store as estore

    monkeypatch.setattr(settings, "db_path", db)
    ostore._cache.pop(db, None)
    dstore._cache.pop(db, None)
    cstore._store_cache.pop(db, None) if hasattr(cstore, "_store_cache") else None
    sstore._store_cache.pop(db, None)
    estore._store_cache.pop(db, None)
    return TestClient(app)


def test_level3_historical_conjecture_reproduction(tmp_path):
    lab = OpenProblemLab(str(tmp_path / "l3.db"))
    p = lab.create(
        "Euler sum of powers (historical)",
        "Euler's sum of powers conjecture (historically disproven / known false): "
        "for every integer k>2, at least k kth-powers are needed to sum to another kth-power.",
        known_info=(
            "Classical conjecture later disproven. Known false / historically disproven. "
            "Famous counterexamples exist (e.g. for fifth powers)."
        ),
        domain="number_theory",
        stage_level=3,
        research_objective="Reproduce historical disproof direction; do not claim novelty",
    )
    assert any(r.bucket.value == "WHAT_IS_DISPROVEN" for r in p.known_results)
    result = lab.run_investigation_cycle(p.problem_id)
    assert result["is_scientific_discovery_claim"] is False
    assert result["is_millennium_attempt"] is False
    final = lab.store.get(p.problem_id)
    assert final is not None
    assert final.research_status == ResearchStatus.REFUTED
    assert any(e.event_type == "RESULT_REPRODUCED" for e in final.timeline)
    assert any(e.event_type == "COUNTEREXAMPLE_FOUND" for e in final.timeline)


def test_literature_enrichment_and_level2_formal(tmp_path):
    lab = OpenProblemLab(str(tmp_path / "l2.db"))
    p = lab.create(
        "Nat add commutative",
        "Prove the known theorem: for natural numbers a,b, a+b=b+a (add_comm).",
        known_info="Standard Nat.add_comm theorem / lemma in algebra. Proven in formal libraries.",
        domain="algebra",
        stage_level=2,
        research_objective="Formalize known add_comm without claiming discovery",
        formal_statement="∀ a b : ℕ, a + b = b + a",
    )
    provenances = {e.provenance for e in p.literature}
    assert "formal_library" in provenances
    assert "placeholder" not in provenances
    assert any(r.bucket.value == "WHAT_IS_PROVEN" for r in p.known_results)
    result = lab.run_investigation_cycle(p.problem_id)
    assert result["is_scientific_discovery_claim"] is False
    final = lab.store.get(p.problem_id)
    assert final is not None
    assert any(e.event_type == "PROOF_ATTEMPTED" for e in final.timeline)
    # Formalization attempted is not RESOLVED / not VERIFIED discovery
    assert final.research_status != ResearchStatus.RESOLVED
    assert final.verification_state != "VERIFIED"


def test_open_problems_api(client: TestClient):
    headers = {"Authorization": "Bearer axiom-dev-token"}
    created = client.post(
        "/open-problems",
        headers=headers,
        json={
            "title": "API Level-1",
            "informal_statement": "Is it true that all odd numbers greater than 1 are prime (known false)?",
            "known_info": "known false / always false",
            "stage_level": 1,
        },
    )
    assert created.status_code == 200, created.text
    pid = created.json()["problem_id"]
    assert created.json()["is_millennium_attempt"] is False

    cycle = client.post(f"/open-problems/{pid}/cycle", headers=headers)
    assert cycle.status_code == 200, cycle.text
    assert cycle.json()["is_scientific_discovery_claim"] is False

    report = client.get(f"/open-problems/{pid}/report", headers=headers)
    assert report.status_code == 200
    assert report.json()["is_millennium_attempt"] is False

    manifest = client.get("/open-problems/manifest", headers=headers)
    assert manifest.status_code == 200
    assert manifest.json()["millennium_auto_start"] is False
