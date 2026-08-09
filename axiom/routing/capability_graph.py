"""Capability graph — problem → capabilities → models/tools (SIMR §3)."""

from __future__ import annotations

from typing import Any

from axiom.evaluation.frameworks.capability import CapabilityDimension
from axiom.routing.model_registry import models_for_capability
from axiom.routing.models import ProblemProfile
from axiom.routing.tool_registry import tools_for_capability

_CAPABILITY_TOOL_HINTS: dict[str, list[str]] = {
    CapabilityDimension.MATHEMATICAL_REASONING.value: [
        "sympy_engine",
        "python_exec",
        "scep_benchmarks",
    ],
    CapabilityDimension.PROOF_VERIFICATION.value: [
        "smt_gateway",
        "lean_exporter",
    ],
    CapabilityDimension.CONJECTURE_GENERATION.value: [
        "hypothesis_engine",
    ],
    CapabilityDimension.KNOWLEDGE_QUALITY.value: [
        "knowledge_graph",
        "vector_retrieval",
    ],
    CapabilityDimension.COUNTEREXAMPLE_SEARCH.value: [
        "sympy_engine",
        "smt_gateway",
    ],
    CapabilityDimension.RESEARCH_PLANNING.value: [
        "workflow_engine",
        "hypothesis_engine",
    ],
    CapabilityDimension.LITERATURE_SYNTHESIS.value: [
        "literature_search",
        "vector_retrieval",
        "knowledge_graph",
    ],
    CapabilityDimension.RESEARCH_PRODUCTIVITY.value: [
        "workflow_engine",
        "eval_api",
        "provenance_records",
    ],
}


def resolve_capability_graph(profile: ProblemProfile) -> dict[str, Any]:
    """Build capability → models/tools graph for a problem profile."""
    capabilities = profile.required_capabilities or _infer_capabilities(profile)
    graph: dict[str, Any] = {
        "problem_id": profile.problem_id,
        "required_capabilities": capabilities,
        "nodes": [],
    }

    for cap in capabilities:
        models = [m.to_dict() for m in models_for_capability(cap)[:3]]
        tools = [t.to_dict() for t in tools_for_capability(cap)[:5]]
        hinted = _CAPABILITY_TOOL_HINTS.get(cap, [])
        graph["nodes"].append(
            {
                "capability": cap,
                "models": models,
                "tools": tools,
                "recommended_tools": hinted,
                "verification_methods": _verification_for_capability(cap),
            }
        )
    return graph


def _infer_capabilities(profile: ProblemProfile) -> list[str]:
    caps: list[str] = []
    if profile.requires_literature:
        caps.append(CapabilityDimension.LITERATURE_SYNTHESIS.value)
    if profile.requires_formal:
        caps.extend([
            CapabilityDimension.MATHEMATICAL_REASONING.value,
            CapabilityDimension.PROOF_VERIFICATION.value,
        ])
    if profile.requires_experiment:
        caps.append(CapabilityDimension.RESEARCH_PRODUCTIVITY.value)
    if profile.domain.value == "mathematics":
        caps.append(CapabilityDimension.MATHEMATICAL_REASONING.value)
    if not caps:
        caps.append(CapabilityDimension.RESEARCH_PLANNING.value)
    return list(dict.fromkeys(caps))


def _verification_for_capability(capability: str) -> list[str]:
    mapping = {
        CapabilityDimension.PROOF_VERIFICATION.value: ["smt_gateway", "lean_exporter"],
        CapabilityDimension.MATHEMATICAL_REASONING.value: ["sympy_engine", "scep_benchmarks"],
        CapabilityDimension.LITERATURE_SYNTHESIS.value: ["primary_source_check"],
        CapabilityDimension.COUNTEREXAMPLE_SEARCH.value: ["smt_gateway", "sympy_engine"],
    }
    return mapping.get(capability, ["scep_benchmarks"])
