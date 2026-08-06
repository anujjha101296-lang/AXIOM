"""Authentication routes — register, login, and session info."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from axiom.config import settings
from axiom.observability.logger import get_logger
from axiom.services.api_gateway.auth import Role, TokenPayload, create_jwt_token, verify_user
from axiom.services.api_gateway.user_store import User, UserStore

logger = get_logger("axiom.api.auth")

router = APIRouter(prefix="/auth", tags=["auth"])

_store: UserStore | None = None


def get_user_store() -> UserStore:
    global _store
    if _store is None:
        _store = UserStore(settings.db_path)
    return _store


class RegisterRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=254)
    password: str = Field(..., min_length=8, max_length=128)
    name: str = Field(..., min_length=1, max_length=120)


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=254)
    password: str = Field(..., min_length=1, max_length=128)


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


def _user_response(user: User) -> UserResponse:
    return UserResponse(id=user.id, email=user.email, name=user.name, role=user.role)


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterRequest,
    store: UserStore = Depends(get_user_store),
) -> AuthResponse:
    try:
        user = store.register(payload.email, payload.password, payload.name)
        token = create_jwt_token(user.id, Role(user.role))
        logger.info("Registration successful", extra={"user_id": user.id})
        return AuthResponse(access_token=token, user=_user_response(user))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("Registration failed", extra={"error": str(exc)}, exc_info=True)
        raise HTTPException(status_code=500, detail="Registration failed") from exc


@router.post("/login", response_model=AuthResponse)
def login(
    payload: LoginRequest,
    store: UserStore = Depends(get_user_store),
) -> AuthResponse:
    try:
        user = store.authenticate(payload.email, payload.password)
        token = create_jwt_token(user.id, Role(user.role))
        logger.info("Login successful", extra={"user_id": user.id})
        return AuthResponse(access_token=token, user=_user_response(user))
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except Exception as exc:
        logger.error("Login failed", extra={"error": str(exc)}, exc_info=True)
        raise HTTPException(status_code=500, detail="Login failed") from exc


@router.get("/me", response_model=UserResponse)
def get_me(user: TokenPayload = Depends(verify_user)) -> UserResponse:
    store = get_user_store()
    try:
        account = store.get_by_id(user.sub)
        return _user_response(account)
    except KeyError:
        if user.sub == "dev":
            return UserResponse(id="dev", email="dev@axiom.local", name="Developer", role="ADMIN")
        raise HTTPException(status_code=404, detail="User not found")
