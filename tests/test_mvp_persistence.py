"""MVP persistence smoke — logout/login must restore owned research state."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from axiom.services.api_gateway.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    db = str(tmp_path / "persist.db")
    monkeypatch.setenv("AXIOM_DB_PATH", db)
    from axiom.config import settings
    from axiom.services.api_gateway.routes import research as research_routes

    monkeypatch.setattr(settings, "db_path", db)
    monkeypatch.setattr(settings, "research_upload_dir", str(tmp_path / "uploads"))
    research_routes._store = None
    return TestClient(app)


def test_logout_login_preserves_project_and_note(client: TestClient):
    signup = client.post(
        "/auth/signup",
        json={
            "email": "persist@example.com",
            "password": "securepass1",
            "display_name": "Persist",
        },
    )
    assert signup.status_code == 201, signup.text
    token1 = signup.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    project = client.post(
        "/research/projects",
        headers=headers1,
        json={"name": "Persistent Study", "description": "Must survive re-login"},
    )
    assert project.status_code == 201, project.text
    project_id = project.json()["id"]

    note = client.post(
        f"/research/projects/{project_id}/notes",
        headers=headers1,
        json={
            "title": "Saved insight",
            "body": "This note must still exist after login.",
            "tags": ["persist"],
        },
    )
    assert note.status_code == 201, note.text
    note_id = note.json()["id"]

    # Simulate logout: discard token1; re-authenticate via login.
    login = client.post(
        "/auth/login",
        json={"email": "persist@example.com", "password": "securepass1"},
    )
    assert login.status_code == 200, login.text
    token2 = login.json()["access_token"]
    assert token2
    headers2 = {"Authorization": f"Bearer {token2}"}

    projects = client.get("/research/projects", headers=headers2)
    assert projects.status_code == 200
    assert any(p["id"] == project_id for p in projects.json())

    detail = client.get(f"/research/projects/{project_id}", headers=headers2)
    assert detail.status_code == 200, detail.text
    notes = detail.json()["notes"]
    assert any(n["id"] == note_id for n in notes)

    # me endpoint confirms session
    me = client.get("/auth/me", headers=headers2)
    assert me.status_code == 200
    assert me.json()["user"]["email"] == "persist@example.com"
