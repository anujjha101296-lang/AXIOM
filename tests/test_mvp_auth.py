"""Tests for MVP auth — signup, login, JWT access to research."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

from axiom.identity import IdentityStore, hash_password, verify_password
from axiom.services.api_gateway.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    db = str(tmp_path / "auth.db")
    monkeypatch.setenv("AXIOM_DB_PATH", db)
    # Settings is cached — patch identity store path via settings.db_path
    from axiom.config import settings

    monkeypatch.setattr(settings, "db_path", db)
    return TestClient(app)


def test_password_hash_roundtrip():
    encoded = hash_password("securepass1")
    assert verify_password("securepass1", encoded)
    assert not verify_password("wrongpass1", encoded)


def test_identity_store_create_and_auth(tmp_path):
    store = IdentityStore(str(tmp_path / "id.db"))
    user = store.create_user("alice@example.com", "securepass1", display_name="Alice")
    assert user.user_id.startswith("usr_")
    assert store.authenticate("alice@example.com", "securepass1")
    assert store.authenticate("alice@example.com", "badpassword") is None
    with pytest.raises(ValueError, match="already registered"):
        store.create_user("alice@example.com", "securepass1")


def test_signup_login_me(client: TestClient):
    resp = client.post(
        "/auth/signup",
        json={"email": "bob@example.com", "password": "securepass1", "display_name": "Bob"},
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["user"]["email"] == "bob@example.com"
    token = data["access_token"]
    assert token.count(".") == 2

    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["user"]["email"] == "bob@example.com"
    assert me.json()["auth_mode"] == "jwt"

    login = client.post(
        "/auth/login",
        json={"email": "bob@example.com", "password": "securepass1"},
    )
    assert login.status_code == 200
    assert login.json()["access_token"]


def test_jwt_can_access_research(client: TestClient):
    signup = client.post(
        "/auth/signup",
        json={"email": "carol@example.com", "password": "securepass1"},
    )
    token = signup.json()["access_token"]
    resp = client.get(
        "/research/projects",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200


def test_bad_login(client: TestClient):
    client.post(
        "/auth/signup",
        json={"email": "dave@example.com", "password": "securepass1"},
    )
    resp = client.post(
        "/auth/login",
        json={"email": "dave@example.com", "password": "wrongpass1"},
    )
    assert resp.status_code == 401


def test_static_token_still_works(client: TestClient):
    from axiom.config import settings

    token = settings.api_token
    resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["auth_mode"] == "static_token"


def test_auth_health(client: TestClient):
    resp = client.get("/auth/health")
    assert resp.status_code == 200
    assert resp.json()["ok"] is True
