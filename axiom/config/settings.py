"""
AXIOM Configuration System
===========================
All configuration is loaded from environment variables (12-factor app).
Use `.env` for local development. Never commit `.env` to source control.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Annotated, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class AxiomSettings(BaseSettings):
    """
    Central configuration for the AXIOM platform.
    All values can be overridden by environment variables or a .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────────────────
    app_name: str = Field(default="AXIOM", description="Application name")
    app_version: str = Field(default="0.2.0", description="Semantic version")
    environment: Literal["development", "staging", "production"] = Field(
        default="development", description="Deployment environment"
    )
    debug: bool = Field(default=False, description="Enable debug mode")

    # ── API Gateway ───────────────────────────────────────────────────────────
    api_host: str = Field(default="0.0.0.0", description="API bind host")
    api_port: int = Field(default=8000, description="API bind port", ge=1, le=65535)
    api_workers: int = Field(default=1, description="Uvicorn worker count")
    api_reload: bool = Field(default=True, description="Auto-reload on code changes (dev only)")

    # ── Authentication ────────────────────────────────────────────────────────
    jwt_secret_key: str = Field(
        default="CHANGE-ME-IN-PRODUCTION-use-openssl-rand-hex-32",
        description="HS256 JWT signing secret",
    )
    jwt_algorithm: str = Field(default="HS256")
    jwt_expiry_minutes: int = Field(default=60, ge=1)
    axiom_api_token: str = Field(
        default="axiom-dev-token",
        description="MVP bearer token for API authentication",
    )
    require_auth_for_eval_routes: bool = Field(
        default=False,
        description="Require bearer token for /eval/* (recommended in production)",
    )
    require_auth_for_gcp_routes: bool = Field(
        default=False,
        description="Require bearer token for /gcp/* (recommended in production)",
    )
    require_auth_for_provenance_routes: bool = Field(
        default=False,
        description="Require bearer token for /provenance/* (recommended in production)",
    )
    require_auth_for_evidence_routes: bool = Field(
        default=False,
        description="Require bearer token for /evidence/* (recommended in production)",
    )
    block_insecure_production_config: bool = Field(
        default=True,
        description="Refuse startup in production when critical security misconfig is detected",
    )
    api_token: str = Field(
        default="axiom-dev-token",
        description="Static bearer token for simple single-tenant auth",
    )

    # ── Database ──────────────────────────────────────────────────────────────
    database_url: str = Field(
        default="sqlite:///./axiom.db",
        description="SQLite database path (use :memory: for tests)",
    )
    db_path: str = Field(default="./axiom.db", description="Raw SQLite file path")

    # ── Logging ───────────────────────────────────────────────────────────────
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO"
    )
    log_format: Literal["json", "console"] = Field(
        default="json",
        description="json for production, console for local dev",
    )

    # ── Monitoring ────────────────────────────────────────────────────────────
    metrics_enabled: bool = Field(default=True)
    metrics_path: str = Field(default="/metrics")

    # ── Lean 4 ───────────────────────────────────────────────────────────────
    lean_bin_path: str = Field(
        default="/usr/local/bin/lean",
        description="Path to Lean 4 compiler binary",
    )
    lean_output_dir: str = Field(
        default="/tmp/axiom_proofs",
        description="Directory for generated Lean 4 files",
    )

    # ── arXiv Ingestion ───────────────────────────────────────────────────────
    arxiv_base_url: str = Field(default="https://arxiv.org")
    arxiv_e_print_url: str = Field(default="https://arxiv.org/e-print")
    ingest_timeout_seconds: int = Field(default=30)

    # ── MCTS Reasoning ────────────────────────────────────────────────────────
    mcts_max_iterations: int = Field(default=1000)
    mcts_exploration_weight: float = Field(default=1.414)

    # ── Hypothesis Engine ─────────────────────────────────────────────────────
    hyp_max_hypotheses_per_run: int = Field(default=5)

    # ── Self-Improvement ──────────────────────────────────────────────────────
    sil_workspace_root: str = Field(default=".", description="Where to write roadmap.md")

    # ── Research Workspace ────────────────────────────────────────────────────
    research_upload_dir: str = Field(
        default="./data/research_uploads",
        description="Directory for uploaded PDF files",
    )
    research_max_upload_bytes: int = Field(
        default=20 * 1024 * 1024,
        description="Maximum PDF upload size in bytes (20 MB)",
    )

    # ── CORS ─────────────────────────────────────────────────────────────────
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="Allowed CORS origins",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value  # type: ignore[return-value]

    @field_validator("jwt_secret_key")
    @classmethod
    def warn_default_secret(cls, v: str) -> str:
        if v == "CHANGE-ME-IN-PRODUCTION-use-openssl-rand-hex-32":
            import warnings
            warnings.warn(
                "jwt_secret_key is using the default insecure value. "
                "Set JWT_SECRET_KEY in your .env for production.",
                stacklevel=2,
            )
        return v


@lru_cache(maxsize=1)
def get_settings() -> AxiomSettings:
    """Return the cached settings singleton."""
    return AxiomSettings()


# Convenience alias
settings = get_settings()
