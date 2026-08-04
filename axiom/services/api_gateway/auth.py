"""
Authentication & Authorization — AXIOM API Gateway
====================================================
Provides:
  1. Bearer token verification (simple static token for MVP/single-tenant)
  2. JWT-based token generation and validation (multi-user production path)
  3. Role-Based Access Control (RBAC) with roles: ADMIN, RESEARCHER, READONLY

Usage:
    # Simple bearer token (MVP)
    @app.get("/protected")
    def protected(token: str = Depends(verify_token)):
        ...

    # Role-based
    @app.post("/admin-only")
    def admin_only(user: TokenPayload = Depends(require_role(Role.ADMIN))):
        ...
"""

from __future__ import annotations

import os
import time
from enum import Enum
from typing import Optional

from fastapi import Depends, Header, HTTPException, status
from pydantic import BaseModel


# ── Configuration ─────────────────────────────────────────────────────────────
SECRET_TOKEN = os.getenv("AXIOM_API_TOKEN", "axiom-dev-token")
JWT_SECRET   = os.getenv("JWT_SECRET_KEY",  "CHANGE-ME-IN-PRODUCTION")
JWT_ALGO     = "HS256"
JWT_EXPIRY   = int(os.getenv("JWT_EXPIRY_MINUTES", "60")) * 60  # seconds


# ── Roles ─────────────────────────────────────────────────────────────────────

class Role(str, Enum):
    ADMIN       = "ADMIN"        # Full access: read + write + admin operations
    RESEARCHER  = "RESEARCHER"   # Read + write scientific data; no admin ops
    READONLY    = "READONLY"     # Read-only access to graph and benchmark data


# Role hierarchy: higher index = more permissions
_ROLE_LEVEL = {Role.READONLY: 0, Role.RESEARCHER: 1, Role.ADMIN: 2}


class TokenPayload(BaseModel):
    """Decoded JWT payload."""
    sub: str                        # user identifier
    role: Role = Role.RESEARCHER
    exp: Optional[float] = None
    iat: Optional[float] = None


# ── Simple Bearer Token (MVP / single-tenant) ─────────────────────────────────

def verify_token(authorization: str = Header(None)) -> str:
    """
    FastAPI dependency: verifies the `Authorization: Bearer <token>` header.
    Used on every protected endpoint. Returns the raw token string.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header must follow format: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = parts[1]
    if token != SECRET_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


# ── JWT Utilities (production multi-user path) ────────────────────────────────

def _encode_jwt(payload: dict) -> str:
    """Encode a JWT without external libraries using HMAC-SHA256."""
    import base64
    import hashlib
    import hmac
    import json

    def b64url(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

    header = b64url(json.dumps({"alg": JWT_ALGO, "typ": "JWT"}).encode())
    body   = b64url(json.dumps(payload).encode())
    signing_input = f"{header}.{body}".encode()
    signature = b64url(
        hmac.new(JWT_SECRET.encode(), signing_input, hashlib.sha256).digest()
    )
    return f"{header}.{body}.{signature}"


def _decode_jwt(token: str) -> dict:
    """Decode and verify a JWT. Raises ValueError on invalid/expired tokens."""
    import base64
    import hashlib
    import hmac
    import json

    def b64url_decode(s: str) -> bytes:
        pad = "=" * (4 - len(s) % 4)
        return base64.urlsafe_b64decode(s + pad)

    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Invalid JWT structure")

    header_b64, body_b64, sig_b64 = parts
    signing_input = f"{header_b64}.{body_b64}".encode()
    expected_sig = base64.urlsafe_b64encode(
        hmac.new(JWT_SECRET.encode(), signing_input, hashlib.sha256).digest()
    ).rstrip(b"=").decode()

    if not hmac.compare_digest(sig_b64, expected_sig):
        raise ValueError("JWT signature verification failed")

    payload = json.loads(b64url_decode(body_b64))
    if "exp" in payload and payload["exp"] < time.time():
        raise ValueError("JWT token has expired")

    return payload


def create_jwt_token(user_id: str, role: Role = Role.RESEARCHER) -> str:
    """Generate a signed JWT for the given user/role."""
    now = time.time()
    return _encode_jwt({
        "sub": user_id,
        "role": role.value,
        "iat": now,
        "exp": now + JWT_EXPIRY,
    })


def decode_jwt_token(token: str) -> TokenPayload:
    """Decode and validate a JWT, returning the payload."""
    try:
        data = _decode_jwt(token)
        return TokenPayload(**data)
    except (ValueError, KeyError, TypeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ── RBAC Dependency Factory ───────────────────────────────────────────────────

def require_role(minimum_role: Role):
    """
    FastAPI dependency factory for role-based access control.

    Example:
        @app.post("/admin")
        def admin_endpoint(user = Depends(require_role(Role.ADMIN))):
            ...
    """
    def _check(authorization: str = Header(None)) -> TokenPayload:
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header missing",
            )
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Bearer token required",
            )
        # First try static token (dev mode) — grants ADMIN
        if parts[1] == SECRET_TOKEN:
            return TokenPayload(sub="dev", role=Role.ADMIN)
        # Otherwise try JWT
        payload = decode_jwt_token(parts[1])
        if _ROLE_LEVEL[payload.role] < _ROLE_LEVEL[minimum_role]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{payload.role}' lacks permission. Required: '{minimum_role}'",
            )
        return payload
    return _check
