"""Tests for MVP authentication (register, login, JWT access)."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

from axiom.services.api_gateway.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_path = str(tmp_path / "auth_test.db")
    monkeypatch.setenv("DB_PATH", db_path)
    monkeypatch.setenv("AXIOM_API_TOKEN", "test_token")

    import axiom.services.api_gateway.routes.auth_api as auth_routes

    auth_routes._store = None

    return TestClient(app)


class TestMvpAuth:
    def test_register_and_login(self, client):
        reg = client.post(
            "/auth/register",
            json={
                "email": "researcher@example.com",
                "password": "securepass1",
                "name": "Test Researcher",
            },
        )
        assert reg.status_code == 201, reg.text
        data = reg.json()
        assert data["access_token"]
        assert data["user"]["email"] == "researcher@example.com"
        assert data["user"]["name"] == "Test Researcher"

        login = client.post(
            "/auth/login",
            json={"email": "researcher@example.com", "password": "securepass1"},
        )
        assert login.status_code == 200
        assert login.json()["access_token"]

    def test_register_duplicate_email(self, client):
        payload = {
            "email": "dup@example.com",
            "password": "securepass1",
            "name": "First",
        }
        assert client.post("/auth/register", json=payload).status_code == 201
        dup = client.post("/auth/register", json={**payload, "name": "Second"})
        assert dup.status_code == 400
        assert "already exists" in dup.json()["detail"]

    def test_login_invalid_credentials(self, client):
        client.post(
            "/auth/register",
            json={"email": "user@example.com", "password": "securepass1", "name": "User"},
        )
        bad = client.post(
            "/auth/login",
            json={"email": "user@example.com", "password": "wrongpassword"},
        )
        assert bad.status_code == 401

    def test_jwt_accesses_research_api(self, client, tmp_path, monkeypatch):
        monkeypatch.setenv("RESEARCH_UPLOAD_DIR", str(tmp_path / "uploads"))

        import axiom.services.api_gateway.routes.research as research_routes

        research_routes._store = None

        reg = client.post(
            "/auth/register",
            json={
                "email": "jwt@example.com",
                "password": "securepass1",
                "name": "JWT User",
            },
        )
        token = reg.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        res = client.post(
            "/research/projects",
            json={"name": "JWT Project"},
            headers=headers,
        )
        assert res.status_code == 201, res.text

        me = client.get("/auth/me", headers=headers)
        assert me.status_code == 200
        assert me.json()["email"] == "jwt@example.com"

    def test_me_requires_auth(self, client):
        res = client.get("/auth/me")
        assert res.status_code == 401

    def test_static_token_still_works(self, client):
        headers = {"Authorization": f"Bearer {os.environ.get('AXIOM_API_TOKEN', 'test_token')}"}
        res = client.get("/auth/me", headers=headers)
        assert res.status_code == 200
        assert res.json()["id"] == "dev"

    def test_register_password_too_short(self, client):
        res = client.post(
            "/auth/register",
            json={"email": "short@example.com", "password": "short", "name": "Short"},
        )
        assert res.status_code == 422
