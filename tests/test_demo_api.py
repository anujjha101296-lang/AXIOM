"""Tests for Golden Demo API (Milestone 006)."""

from fastapi.testclient import TestClient

from axiom.services.api_gateway.main import app

client = TestClient(app)


def test_demo_health():
    res = client.get("/demo/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ready"
    assert data["version"] == "0.5-demo"


def test_demo_state():
    res = client.get("/demo/state")
    assert res.status_code == 200
    data = res.json()
    assert data["mode"] == "golden"
    assert data["project"]["name"]
    assert len(data["papers"]) == 3
    assert len(data["knowledge_nodes"]) >= 5
    assert len(data["hypotheses"]) >= 2
    assert data["report"]["title"]
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
