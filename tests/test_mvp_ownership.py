"""Project ownership isolation — JWT users must not see each other's projects."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from axiom.services.api_gateway.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    db = str(tmp_path / "own.db")
    monkeypatch.setenv("AXIOM_DB_PATH", db)
    from axiom.config import settings
    from axiom.services.api_gateway.routes import research as research_routes

    monkeypatch.setattr(settings, "db_path", db)
    monkeypatch.setattr(settings, "research_upload_dir", str(tmp_path / "uploads"))
    # Force fresh store bound to this test DB
    research_routes._store = None
    return TestClient(app)


def _signup(client: TestClient, email: str) -> str:
    resp = client.post(
        "/auth/signup",
        json={"email": email, "password": "securepass1", "display_name": email.split("@")[0]},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["access_token"]


def test_project_ownership_isolation(client: TestClient):
    token_a = _signup(client, "alice-own@example.com")
    token_b = _signup(client, "bob-own@example.com")

    created = client.post(
        "/research/projects",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"name": "Alice Secret", "description": "private"},
    )
    assert created.status_code == 201, created.text
    project_id = created.json()["id"]
    assert created.json().get("owner_id")

    alice_list = client.get(
        "/research/projects",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert alice_list.status_code == 200
    assert any(p["id"] == project_id for p in alice_list.json())

    bob_list = client.get(
        "/research/projects",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert bob_list.status_code == 200
    assert all(p["id"] != project_id for p in bob_list.json())

    bob_get = client.get(
        f"/research/projects/{project_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert bob_get.status_code == 404

    alice_get = client.get(
        f"/research/projects/{project_id}",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert alice_get.status_code == 200
