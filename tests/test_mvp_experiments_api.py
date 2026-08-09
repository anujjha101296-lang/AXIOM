"""API smoke for Experiments UI path — create → run → inspect."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from axiom.services.api_gateway.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    db = str(tmp_path / "exp_ui.db")
    monkeypatch.setenv("AXIOM_DB_PATH", db)
    from axiom.config import settings
    from axiom.experiment import store as exp_store

    monkeypatch.setattr(settings, "db_path", db)
    # Ensure fresh store for this DB path
    exp_store._store_cache.pop(db, None)
    return TestClient(app)


def test_experiment_create_run_inspect(client: TestClient):
    headers = {"Authorization": "Bearer axiom-dev-token"}
    # Prefer JWT if static token differs in env — also signup
    signup = client.post(
        "/auth/signup",
        json={"email": "expuser@example.com", "password": "securepass1"},
    )
    if signup.status_code == 201:
        headers = {"Authorization": f"Bearer {signup.json()['access_token']}"}

    created = client.post(
        "/experiments/",
        headers=headers,
        json={
            "research_question": "Does n+0 equal n?",
            "hypothesis": "Addition identity holds",
            "objective": "Verify for small n in sandbox",
            "code": "for n in range(5):\n    assert n + 0 == n\nprint('OK')",
            "timeout_seconds": 10,
            "random_seed": 42,
        },
    )
    assert created.status_code == 200, created.text
    experiment_id = created.json()["experiment_id"]
    assert created.json()["status"] == "DRAFT"

    run = client.post(f"/experiments/{experiment_id}/run", headers=headers)
    assert run.status_code == 200, run.text
    assert run.json()["status"] == "COMPLETED"
    assert run.json()["results"]["not_mathematical_proof"] is True

    got = client.get(f"/experiments/{experiment_id}", headers=headers)
    assert got.status_code == 200
    assert got.json()["status"] == "COMPLETED"

    listed = client.get("/experiments/", headers=headers)
    assert listed.status_code == 200
    assert any(e["experiment_id"] == experiment_id for e in listed.json()["experiments"])
