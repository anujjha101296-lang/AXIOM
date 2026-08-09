"""Compute environment fingerprinting (SEC §3)."""

from __future__ import annotations

import platform
import sys
from typing import Any

from axiom.config import settings


def capture_environment(env_type: str = "python") -> dict[str, Any]:
    """Capture runtime environment for experiment provenance."""
    env: dict[str, Any] = {
        "environment_type": env_type,
        "os": platform.system(),
        "os_version": platform.release(),
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "app_version": settings.app_version,
        "deployment_environment": settings.environment,
    }
    try:
        import numpy  # noqa: F401
        env["numpy_version"] = numpy.__version__
    except ImportError:
        pass
    try:
        import sympy  # noqa: F401
        env["sympy_version"] = sympy.__version__
    except ImportError:
        pass
    return env
