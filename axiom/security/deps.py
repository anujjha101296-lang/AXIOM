"""FastAPI dependencies for optional route authentication."""

from __future__ import annotations

from fastapi import Header

from axiom.config import settings
from axiom.services.api_gateway.auth import verify_token


def _make_optional_auth(setting_attr: str):
    def _dependency(authorization: str | None = Header(None)) -> str:
        if getattr(settings, setting_attr, False):
            return verify_token(authorization)  # type: ignore[arg-type]
        return "anonymous"

    return _dependency


eval_route_auth = _make_optional_auth("require_auth_for_eval_routes")
gcp_route_auth = _make_optional_auth("require_auth_for_gcp_routes")
provenance_route_auth = _make_optional_auth("require_auth_for_provenance_routes")
evidence_route_auth = _make_optional_auth("require_auth_for_evidence_routes")
routing_route_auth = _make_optional_auth("require_auth_for_routing_routes")
formal_math_route_auth = _make_optional_auth("require_auth_for_formal_math_routes")
experiment_route_auth = _make_optional_auth("require_auth_for_experiment_routes")
