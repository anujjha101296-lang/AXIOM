"""Production security configuration audit (TSS §4, §12, §25)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from axiom.config.settings import AxiomSettings

INSECURE_JWT_DEFAULT = "CHANGE-ME-IN-PRODUCTION-use-openssl-rand-hex-32"
INSECURE_API_TOKEN_DEFAULT = "axiom-dev-token"

# Route groups intentionally public in development; must be locked in production.
UNAUTHENTICATED_ROUTE_GROUPS = ("eval", "gcp", "provenance")


@dataclass
class SecurityFinding:
    id: str
    severity: str  # critical, high, medium, low
    component: str
    message: str
    remediation: str = ""


def audit_security_config(settings: Any) -> list[SecurityFinding]:
    """Audit settings for insecure production configuration."""
    findings: list[SecurityFinding] = []

    jwt_secret = getattr(settings, "jwt_secret_key", "")
    api_token = getattr(settings, "axiom_api_token", INSECURE_API_TOKEN_DEFAULT)

    if jwt_secret == INSECURE_JWT_DEFAULT:
        findings.append(
            SecurityFinding(
                id="TSS-SEC-001",
                severity="critical" if settings.environment == "production" else "medium",
                component="authentication",
                message="JWT secret uses insecure default value",
                remediation="Set JWT_SECRET_KEY via environment (openssl rand -hex 32)",
            )
        )

    if api_token == INSECURE_API_TOKEN_DEFAULT:
        findings.append(
            SecurityFinding(
                id="TSS-SEC-002",
                severity="critical" if settings.environment == "production" else "medium",
                component="authentication",
                message="API bearer token uses insecure default (axiom-dev-token)",
                remediation="Set AXIOM_API_TOKEN to a strong random value in production",
            )
        )

    if settings.environment == "production":
        auth_flags = {
            "eval": getattr(settings, "require_auth_for_eval_routes", False),
            "gcp": getattr(settings, "require_auth_for_gcp_routes", False),
            "provenance": getattr(settings, "require_auth_for_provenance_routes", False),
        }
        for group, enabled in auth_flags.items():
            if not enabled:
                findings.append(
                    SecurityFinding(
                        id=f"TSS-SEC-010-{group}",
                        severity="high",
                        component="authorization",
                        message=f"/{group} routes are publicly accessible in production",
                        remediation=f"Set REQUIRE_AUTH_FOR_{group.upper()}_ROUTES=true",
                    )
                )

        if getattr(settings, "debug", False):
            findings.append(
                SecurityFinding(
                    id="TSS-SEC-003",
                    severity="high",
                    component="application",
                    message="Debug mode enabled in production",
                    remediation="Set DEBUG=false",
                )
            )

    return findings


def enforce_production_security(settings: "AxiomSettings") -> None:
    """Raise if production has critical misconfiguration and blocking is enabled."""
    if settings.environment != "production":
        return
    if not getattr(settings, "block_insecure_production_config", True):
        return

    findings = audit_security_config(settings)
    critical = [f for f in findings if f.severity == "critical"]
    if critical:
        messages = "; ".join(f.message for f in critical)
        raise RuntimeError(f"Refusing to start with insecure production config: {messages}")
