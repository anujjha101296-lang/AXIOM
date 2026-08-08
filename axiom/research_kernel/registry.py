"""Research domain plugin registry."""

from __future__ import annotations

from typing import Any

from axiom.research_kernel.models import PluginDescriptor
from axiom.research_kernel.plugin import ResearchDomainPlugin
from axiom.research_kernel.plugins.computer_science import ComputerSciencePlugin
from axiom.research_kernel.plugins.mathematics import MathematicsPlugin
from axiom.research_kernel.plugins.vlsi_hardware import VlsiHardwarePlugin

_BUILTIN_PLUGINS: dict[str, ResearchDomainPlugin] = {
    "mathematics": MathematicsPlugin(),
    "computer_science": ComputerSciencePlugin(),
    "vlsi_hardware": VlsiHardwarePlugin(),
}


def register_plugin(plugin: ResearchDomainPlugin) -> None:
    """Register a domain plugin by plugin_id."""
    _BUILTIN_PLUGINS[plugin.plugin_id] = plugin


def get_plugin(plugin_id: str) -> ResearchDomainPlugin:
    if plugin_id not in _BUILTIN_PLUGINS:
        available = ", ".join(sorted(_BUILTIN_PLUGINS))
        raise KeyError(f"Unknown plugin '{plugin_id}'. Available: {available}")
    return _BUILTIN_PLUGINS[plugin_id]


def list_plugins() -> list[PluginDescriptor]:
    return [
        PluginDescriptor(
            plugin_id=p.plugin_id,
            domain=p.domain,
            name=p.name,
            version=p.version,
            description=p.description,
            benchmark_count=len(p.benchmarks()),
        )
        for p in _BUILTIN_PLUGINS.values()
    ]


def kernel_manifest() -> dict[str, Any]:
    """Return full kernel manifest for API consumers."""
    from axiom.research_kernel.models import STAGE_ORDER

    return {
        "name": "AXIOM Research Kernel",
        "version": "1.0.0",
        "stages": [
            {"order": i + 1, "stage": s.value, "name": s.name}
            for i, s in enumerate(STAGE_ORDER)
        ],
        "plugins": [p.model_dump() for p in list_plugins()],
        "integrations": {
            "aca": "axiom.cognitive — 9-layer cognitive architecture",
            "sme": "axiom.scientific_method — 10-phase scientific method",
            "workflow": "axiom.workflow — multi-agent task scheduling",
            "rvp": "axiom.research_validation — known-answer benchmarks",
            "provenance": "axiom.observability.run_provenance — H1-OBS records",
        },
    }
