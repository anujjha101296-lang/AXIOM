"""Tests for Golden Demo API (Milestone 006)."""

from fastapi.testclient import TestClient

from axiom.services.api_gateway.main import app

client = TestClient(app)


def test_demo_health():
    res = client.get("/demo/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ready"
    assert data["operation_mode"] == "demo"
    assert data["represents_scientific_capability"] is False


def test_demo_mode_contract():
    res = client.get("/demo/mode")
    assert res.status_code == 200
    data = res.json()
    assert data["mode"] == "demo"
    assert data["represents_scientific_capability"] is False
    assert data["uses_curated_data"] is True
    assert data["uses_live_models"] is False
    assert "DEMO MODE" in data["disclaimer"]


def test_research_mode_contract():
    res = client.get("/research/mode")
    assert res.status_code == 200
    data = res.json()
    assert data["mode"] == "research"
    assert data["represents_scientific_capability"] is True
    assert data["uncertainty_expected"] is True
    assert data["evidence_required"] is True


def test_research_loop_mode_contract():
    res = client.get("/research-loop/mode")
    assert res.status_code == 200
    data = res.json()
    assert data["mode"] == "research"
    assert data["uncertainty_expected"] is True


def test_demo_state():
    res = client.get("/demo/state")
    assert res.status_code == 200
    data = res.json()
    assert data["operation_mode"]["mode"] == "demo"
    assert data["operation_mode"]["represents_scientific_capability"] is False
    assert data["project"]["name"]
    assert len(data["papers"]) == 3
    assert len(data["knowledge_nodes"]) >= 5
    assert len(data["hypotheses"]) >= 2
    assert data["report"]["title"]
    assert data["report"]["illustrative_only"] is True
    assert "DEMO MODE" in data["report"]["mode_notice"]
    assert data["stats"]["papers_ingested"] == 3


def test_demo_tour():
    res = client.get("/demo/tour")
    assert res.status_code == 200
    steps = res.json()
    assert len(steps) >= 8
    assert steps[0]["title"]
    assert steps[0]["highlight"]


def test_demo_state_evidence_graph():
    res = client.get("/demo/state")
    data = res.json()
    node_ids = {n["id"] for n in data["knowledge_nodes"]}
    for edge in data["knowledge_edges"]:
        assert edge["source"] in node_ids
        assert edge["target"] in node_ids


def test_demo_contradictions_have_resolution():
    res = client.get("/demo/state")
    for c in res.json()["contradictions"]:
        assert c["resolution"]
        assert c["claim_a"] and c["claim_b"]
