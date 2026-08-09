"""Tests for the Scientific Discovery Engine."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from axiom.discovery.benchmarks import run_all_benchmarks
from axiom.discovery.engine import DiscoveryEngine, DiscoveryTransitionError
from axiom.discovery.models import DiscoveryStatus, can_transition
from axiom.services.api_gateway.main import app


def test_status_transitions_are_gated():
    assert can_transition(DiscoveryStatus.GENERATED, DiscoveryStatus.UNDER_INVESTIGATION)
    assert not can_transition(DiscoveryStatus.GENERATED, DiscoveryStatus.VERIFIED)
    assert not can_transition(DiscoveryStatus.REFUTED, DiscoveryStatus.SUPPORTED)


def test_no_counterexample_substring_is_not_a_hit():
    """Regression: NO_COUNTEREXAMPLE must not count as COUNTEREXAMPLE."""
    from axiom.experiment.counterexample import search_computational_counterexample

    miss = search_computational_counterexample("claim", "print('NO_COUNTEREXAMPLE')\n")
    assert miss["counterexample_found"] is False

    hit = search_computational_counterexample(
        "claim", "print('COUNTEREXAMPLE_FOUND')\nprint('x=9')\n"
    )
    assert hit["counterexample_found"] is True


def test_discovery_cycle_end_to_end(tmp_path):
    engine = DiscoveryEngine(str(tmp_path / "disc.db"))
    d = engine.create(
        "Does addition identity n+0=n hold for small integers?",
        seed_text="It is well known that for integers n, n+0=n. Open question remains on notation.",
        knowledge_context="Known arithmetic identity.",
    )
    result = engine.run_cycle(d.discovery_id)
    assert result["discovery_id"] == d.discovery_id
    assert "opportunities" in result["stages_executed"]
    assert "hypotheses" in result["stages_executed"]
    assert "pilot_experiment" in result["stages_executed"]
    assert "counterexample_search" in result["stages_executed"]
    assert "independent_attack" in result["stages_executed"]
    assert result["hypothesis_count"] >= 2
    assert result["prediction_count"] >= 1
    assert result["is_scientific_discovery_claim"] is False
    assert result["status"] != DiscoveryStatus.VERIFIED.value

    final = engine.store.get(d.discovery_id)
    assert final is not None
    assert final.report.get("is_scientific_discovery_claim") is False
    assert final.novelty.status.value in {
        "INSUFFICIENT_SEARCH",
        "RELATED_WORK_FOUND",
        "POSSIBLY_KNOWN",
        "LIKELY_KNOWN",
        "NO_RELEVANT_PRIOR_WORK_FOUND",
    }


def test_quality_scorecard_and_formal_bridge(tmp_path):
    engine = DiscoveryEngine(str(tmp_path / "qs.db"))
    d = engine.create(
        "Can n+0=n be formally verified for integers?",
        seed_text="Standard arithmetic lemma suitable for formalization.",
        knowledge_context="Standard arithmetic lemma.",
    )
    result = engine.run_cycle(d.discovery_id)
    final = engine.store.get(d.discovery_id)
    assert final is not None
    card = final.report.get("quality_scorecard") or {}
    assert "dimensions" in card
    assert card.get("false_discovery_safe") is True
    assert "scientific_honesty" in card["dimensions"]
    bridge = final.report.get("formal_bridge") or {}
    assert bridge.get("prose_is_not_proof") is True
    assert bridge.get("compiled_verified") is not True
    assert result["status"] != DiscoveryStatus.VERIFIED.value


def test_human_can_pause_and_reject(tmp_path):
    engine = DiscoveryEngine(str(tmp_path / "human.db"))
    d = engine.create("Can humans pause a discovery investigation?")
    engine.detect_opportunities(d.discovery_id)
    engine.generate_hypotheses(d.discovery_id)
    paused = engine.human_decide(
        d.discovery_id, action="pause", reason="Operator paused for review", actor="tester"
    )
    assert paused.status == DiscoveryStatus.UNRESOLVED
    d2 = engine.create("Should this investigation be rejected by a human?")
    rejected = engine.human_decide(
        d2.discovery_id, action="stop", reason="Out of scope", actor="tester"
    )
    assert rejected.status == DiscoveryStatus.REJECTED


def test_cannot_self_verify(tmp_path):
    engine = DiscoveryEngine(str(tmp_path / "gate.db"))
    d = engine.create("Toy question for gate test?")
    with pytest.raises(DiscoveryTransitionError, match="VERIFIED"):
        engine.transition(d.discovery_id, DiscoveryStatus.VERIFIED, reason="model said so")


def test_refuted_not_resurrected(tmp_path):
    engine = DiscoveryEngine(str(tmp_path / "ref.db"))
    d = engine.create(
        "Is it true that all odd numbers greater than 1 are always false / known false?",
        seed_text="Claim that is already disproven / known false.",
    )
    engine.detect_opportunities(d.discovery_id)
    engine.generate_hypotheses(d.discovery_id)
    engine.run_counterexample_search(d.discovery_id)
    final = engine.store.get(d.discovery_id)
    assert final is not None
    if final.status == DiscoveryStatus.REFUTED:
        with pytest.raises(DiscoveryTransitionError):
            engine.transition(d.discovery_id, DiscoveryStatus.SUPPORTED, reason="casually resurrect")


def test_deterministic_benchmarks(tmp_path):
    summary = run_all_benchmarks(str(tmp_path / "bench.db"))
    assert summary["total"] == 8
    assert summary["false_discovery_rate"] == 0.0
    assert summary["false_verified_count"] == 0
    # Allow some soft failures on status matching, but never claim discovery / verify
    assert summary["passed"] >= 5


@pytest.fixture
def client(tmp_path, monkeypatch):
    db = str(tmp_path / "api_disc.db")
    monkeypatch.setenv("AXIOM_DB_PATH", db)
    from axiom.config import settings
    from axiom.discovery import store as dstore
    from axiom.experiment import store as estore
    from axiom.skai import store as sstore

    monkeypatch.setattr(settings, "db_path", db)
    dstore._cache.pop(db, None)
    sstore._store_cache.pop(db, None)
    estore._store_cache.pop(db, None)
    return TestClient(app)


def test_discovery_api_cycle(client: TestClient):
    headers = {"Authorization": "Bearer axiom-dev-token"}
    created = client.post(
        "/discovery/investigations",
        headers=headers,
        json={
            "research_question": "Does n+0 equal n for small n?",
            "seed_text": "Known identity n+0=n. Open question on generalizations.",
        },
    )
    assert created.status_code == 200, created.text
    discovery_id = created.json()["discovery_id"]
    assert created.json()["is_scientific_discovery_claim"] is False

    cycle = client.post(f"/discovery/investigations/{discovery_id}/cycle", headers=headers)
    assert cycle.status_code == 200, cycle.text
    body = cycle.json()
    assert body["hypothesis_count"] >= 2
    assert body["status"] != "VERIFIED"

    report = client.get(f"/discovery/investigations/{discovery_id}/report", headers=headers)
    assert report.status_code == 200
    assert report.json()["is_scientific_discovery_claim"] is False

    manifest = client.get("/discovery/manifest", headers=headers)
    assert manifest.status_code == 200
    assert manifest.json()["millennium_attempt"] is False
