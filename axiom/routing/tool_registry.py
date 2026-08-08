"""Tool registry — unified catalog of scientific tools (SIMR §2)."""

from __future__ import annotations

from axiom.routing.models import ToolSpec
from axiom.security.tool_permissions import ToolRiskClass

_TOOL_CATALOG: dict[str, ToolSpec] = {
    "literature_search": ToolSpec(
        tool_id="literature_search",
        name="Literature Search",
        category="literature",
        capabilities=["literature_synthesis", "citation"],
        inputs=["query"],
        outputs=["papers", "citations"],
        risk_class=ToolRiskClass.READ_ONLY.value,
        verification_level="retrieval",
        module_path="axiom.core.parser.arxiv_parser",
    ),
    "vector_retrieval": ToolSpec(
        tool_id="vector_retrieval",
        name="Vector Retrieval",
        category="retrieval",
        capabilities=["literature_synthesis", "knowledge_quality"],
        inputs=["query", "corpus"],
        outputs=["chunks", "scores"],
        risk_class=ToolRiskClass.READ_ONLY.value,
        verification_level="retrieval",
    ),
    "knowledge_graph": ToolSpec(
        tool_id="knowledge_graph",
        name="Epistemic Knowledge Graph",
        category="knowledge",
        capabilities=["knowledge_quality", "literature_synthesis"],
        inputs=["query"],
        outputs=["nodes", "edges"],
        risk_class=ToolRiskClass.READ_ONLY.value,
        verification_level="structured",
        module_path="axiom.core.knowledge_graph.db",
    ),
    "python_exec": ToolSpec(
        tool_id="python_exec",
        name="Python Execution",
        category="computation",
        capabilities=["mathematical_reasoning", "research_productivity"],
        inputs=["code"],
        outputs=["stdout", "result"],
        risk_class=ToolRiskClass.HIGH_RISK_WRITE.value,
        cost_estimate=0.01,
        verification_level="execution",
    ),
    "sympy_engine": ToolSpec(
        tool_id="sympy_engine",
        name="Symbolic Algebra (SymPy)",
        category="symbolic",
        capabilities=["mathematical_reasoning", "counterexample_search"],
        inputs=["expression"],
        outputs=["simplified", "proof_steps"],
        risk_class=ToolRiskClass.LOW_RISK_WRITE.value,
        verification_level="symbolic",
    ),
    "smt_gateway": ToolSpec(
        tool_id="smt_gateway",
        name="SMT Solver Gateway",
        category="verification",
        capabilities=["proof_verification", "counterexample_search"],
        inputs=["conjecture", "constraints"],
        outputs=["sat", "unsat", "model"],
        risk_class=ToolRiskClass.READ_ONLY.value,
        reliability_score=0.7,
        verification_level="smt",
        module_path="axiom.core.verification.smt_gateway",
    ),
    "lean_exporter": ToolSpec(
        tool_id="lean_exporter",
        name="Lean Proof Exporter",
        category="formal",
        capabilities=["proof_verification", "formalization"],
        inputs=["theorem"],
        outputs=["lean_code"],
        risk_class=ToolRiskClass.LOW_RISK_WRITE.value,
        verification_level="formal_export",
        module_path="axiom.core.verification.lean_exporter",
    ),
    "scep_benchmarks": ToolSpec(
        tool_id="scep_benchmarks",
        name="SCEP Benchmark Suite",
        category="benchmark",
        capabilities=["mathematical_reasoning", "research_planning"],
        inputs=["dimension"],
        outputs=["scores", "evidence_tier"],
        risk_class=ToolRiskClass.READ_ONLY.value,
        verification_level="measured",
        module_path="axiom.evaluation.benchmarks.suite",
    ),
    "hypothesis_engine": ToolSpec(
        tool_id="hypothesis_engine",
        name="Hypothesis Engine",
        category="reasoning",
        capabilities=["conjecture_generation", "research_planning"],
        inputs=["context"],
        outputs=["hypotheses"],
        risk_class=ToolRiskClass.LOW_RISK_WRITE.value,
        module_path="axiom.core.reasoning.hypothesis_engine",
    ),
    "workflow_engine": ToolSpec(
        tool_id="workflow_engine",
        name="Workflow Engine",
        category="orchestration",
        capabilities=["research_planning", "research_productivity"],
        inputs=["workflow_spec"],
        outputs=["run_id", "artifacts"],
        risk_class=ToolRiskClass.HIGH_RISK_WRITE.value,
        module_path="axiom.workflow",
    ),
    "eval_api": ToolSpec(
        tool_id="eval_api",
        name="Capability Evaluation API",
        category="benchmark",
        capabilities=["research_productivity"],
        inputs=["benchmark_suite"],
        outputs=["snapshot", "provenance"],
        risk_class=ToolRiskClass.READ_ONLY.value,
        module_path="axiom.services.api_gateway.routes.eval_api",
    ),
    "provenance_records": ToolSpec(
        tool_id="provenance_records",
        name="Run Provenance Store",
        category="observability",
        capabilities=["research_productivity"],
        inputs=["run_type", "run_id"],
        outputs=["provenance_envelope"],
        risk_class=ToolRiskClass.READ_ONLY.value,
        module_path="axiom.observability.run_provenance",
    ),
}


def list_tools() -> list[ToolSpec]:
    tools = list(_TOOL_CATALOG.values())
    try:
        from axiom.workflow.registry import get_registry

        for worker in get_registry().list_all():
            wid = f"worker_{worker['worker_type']}"
            if wid not in _TOOL_CATALOG:
                tools.append(
                    ToolSpec(
                        tool_id=wid,
                        name=f"Workflow Worker: {worker['worker_type']}",
                        category="workflow",
                        capabilities=worker.get("capabilities", []),
                        inputs=["task_context"],
                        outputs=["result"],
                        risk_class=ToolRiskClass.LOW_RISK_WRITE.value,
                        module_path="axiom.workflow.registry",
                    )
                )
    except ImportError:
        pass
    return tools


def get_tool(tool_id: str) -> ToolSpec | None:
    for tool in list_tools():
        if tool.tool_id == tool_id:
            return tool
    return None


def tools_for_capability(capability: str) -> list[ToolSpec]:
    matched = [t for t in list_tools() if capability in t.capabilities]
    matched.sort(key=lambda t: t.reliability_score, reverse=True)
    return matched
