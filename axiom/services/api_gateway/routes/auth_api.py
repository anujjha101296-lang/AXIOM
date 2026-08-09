"""Auth API — signup, login, me."""

from __future__ import annotations

import os
from typing import Any

from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field

from axiom.config import settings
from axiom.identity import get_identity_store
from axiom.services.api_gateway.auth import (
    Role,
    create_jwt_token,
    decode_jwt_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])


class SignupRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=254)
    password: str = Field(..., min_length=8, max_length=128)
    display_name: str = Field(default="", max_length=80)


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=254)
    password: str = Field(..., min_length=8, max_length=128)


def _store():
    return get_identity_store(settings.db_path)


@router.post("/signup", status_code=201)
def signup(body: SignupRequest) -> dict[str, Any]:
    store = _store()
    try:
        user = store.create_user(
            body.email, body.password, display_name=body.display_name
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    token = create_jwt_token(user.user_id, Role(user.role))
    return {"user": user.public_dict(), "access_token": token, "token_type": "bearer"}


@router.post("/login")
def login(body: LoginRequest) -> dict[str, Any]:
    user = _store().authenticate(body.email, body.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    token = create_jwt_token(user.user_id, Role(user.role))
    return {"user": user.public_dict(), "access_token": token, "token_type": "bearer"}


@router.get("/me")
def me(authorization: str | None = Header(None)) -> dict[str, Any]:
    """Return current user. Accepts JWT or static MVP bearer token."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Bearer token required")
    token = parts[1]
    if token == settings.api_token or token == os.environ.get("AXIOM_API_TOKEN", "axiom-dev-token"):
        return {
            "user": {
                "user_id": "dev",
                "email": "dev@localhost",
                "display_name": "Developer",
                "role": "ADMIN",
                "created_at": None,
            },
            "auth_mode": "static_token",
        }
    payload = decode_jwt_token(token)
    user = _store().get_by_id(payload.sub)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return {"user": user.public_dict(), "auth_mode": "jwt"}


@router.get("/health")
def auth_health() -> dict[str, Any]:
    return {"ok": True, "signup": True, "login": True, "modes": ["jwt", "static_token"]}
