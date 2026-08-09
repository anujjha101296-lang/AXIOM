"""Domain plugin interfaces (SEC §28–29)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ScientificDomainPlugin(ABC):
    """Stable interface for future scientific domain integrations."""

    domain_id: str = "base"

    @abstractmethod
    def supported_experiment_types(self) -> list[str]:
        ...

    @abstractmethod
    def validate_spec(self, spec: dict[str, Any]) -> list[str]:
        ...

    @abstractmethod
    def execute(self, spec: dict[str, Any]) -> dict[str, Any]:
        ...


class VLSIResearchPlugin(ScientificDomainPlugin):
    """Optional VLSI/hardware research plugin interface (SEC §29)."""

    domain_id = "vlsi"

    def supported_experiment_types(self) -> list[str]:
        return [
            "rtl_simulation",
            "formal_hardware_verification",
            "synthesis",
            "timing_analysis",
            "architecture_simulation",
            "fpga_experimentation",
        ]

    def validate_spec(self, spec: dict[str, Any]) -> list[str]:
        errors = []
        if not spec.get("tool_config"):
            errors.append("VLSI experiments require tool_config with external tool reference")
        return errors

    def execute(self, spec: dict[str, Any]) -> dict[str, Any]:
        return {
            "status": "not_configured",
            "message": "VLSI tool integration not configured — provide tool_config",
            "evidence_class": "computational_evidence",
        }


_PLUGINS: dict[str, ScientificDomainPlugin] = {
    "vlsi": VLSIResearchPlugin(),
}


def get_plugin(domain_id: str) -> ScientificDomainPlugin | None:
    return _PLUGINS.get(domain_id)


def list_plugins() -> list[dict[str, Any]]:
    return [
        {
            "domain_id": p.domain_id,
            "experiment_types": p.supported_experiment_types(),
        }
        for p in _PLUGINS.values()
    ]
