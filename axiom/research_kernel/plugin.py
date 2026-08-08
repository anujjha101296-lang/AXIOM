"""Research domain plugin protocol — stable API for domain extensions."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ResearchDomainPlugin(Protocol):
    """
    Contract for research domain plugins.

    Domains implement domain-specific logic; the kernel handles orchestration.
    """

    plugin_id: str
    domain: str
    name: str
    version: str
    description: str

    def decompose_goal(self, objective: str, context: dict[str, Any]) -> dict[str, Any]:
        """Break the research objective into sub-goals and success criteria."""
        ...

    def research_plan(self, decomposition: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Produce a domain-specific research plan from decomposition."""
        ...

    def acquire_evidence(self, plan: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Gather domain evidence (literature, simulations, formal artifacts)."""
        ...

    def orchestration_tasks(self, plan: dict[str, Any], context: dict[str, Any]) -> list[dict[str, Any]]:
        """Return task definitions for multi-agent workflow scheduling."""
        ...

    def verify(self, evidence: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Domain-specific verification of acquired evidence."""
        ...

    def benchmarks(self) -> list[dict[str, Any]]:
        """Return domain benchmark definitions for kernel benchmark stage."""
        ...

    def run_benchmark(self, benchmark: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Execute a single domain benchmark and return scored result."""
        ...

    def generate_domain_report(self, context: dict[str, Any]) -> str:
        """Produce domain-specific section of the final research report."""
        ...
