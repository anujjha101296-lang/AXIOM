"""JWT ownership isolation for FRCE campaigns and SEC experiments."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from axiom.services.api_gateway.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    db = str(tmp_path / "own2.db")
    monkeypatch.setenv("AXIOM_DB_PATH", db)
    from axiom.config import settings
    from axiom.experiment import store as exp_store
    from axiom.campaign import store as camp_store

    monkeypatch.setattr(settings, "db_path", db)
    exp_store._store_cache.pop(db, None)
    camp_store._store_cache.pop(db, None)
    return TestClient(app)


def _signup(client: TestClient, email: str) -> str:
    resp = client.post(
        "/auth/signup",
        json={"email": email, "password": "securepass1", "display_name": email.split("@")[0]},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["access_token"]


def test_frce_campaign_ownership(client: TestClient):
    token_a = _signup(client, "frce-a@example.com")
    token_b = _signup(client, "frce-b@example.com")
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    created = client.post(
        "/frce/campaigns",
        headers=headers_a,
        json={"name": "Alice Camp", "objective": "private objective"},
    )
    assert created.status_code == 200, created.text
    campaign_id = created.json()["campaign_id"]
    assert created.json()["owner_id"]

    listed_b = client.get("/frce/campaigns", headers=headers_b)
    assert listed_b.status_code == 200
    assert all(c["campaign_id"] != campaign_id for c in listed_b.json()["campaigns"])

    get_b = client.get(f"/frce/campaigns/{campaign_id}", headers=headers_b)
    assert get_b.status_code == 404

    get_a = client.get(f"/frce/campaigns/{campaign_id}", headers=headers_a)
    assert get_a.status_code == 200


def test_sec_experiment_ownership(client: TestClient):
    token_a = _signup(client, "sec-a@example.com")
    token_b = _signup(client, "sec-b@example.com")
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    created = client.post(
        "/experiments/",
        headers=headers_a,
        json={
            "research_question": "Q",
            "hypothesis": "H",
            "objective": "O",
            "code": "print(1)",
        },
    )
    assert created.status_code == 200, created.text
    experiment_id = created.json()["experiment_id"]
    assert created.json()["owner_id"]

    listed_b = client.get("/experiments/", headers=headers_b)
    assert all(e["experiment_id"] != experiment_id for e in listed_b.json()["experiments"])

    get_b = client.get(f"/experiments/{experiment_id}", headers=headers_b)
    assert get_b.status_code == 404

    run_b = client.post(f"/experiments/{experiment_id}/run", headers=headers_b)
    assert run_b.status_code == 404

    get_a = client.get(f"/experiments/{experiment_id}", headers=headers_a)
    assert get_a.status_code == 200
