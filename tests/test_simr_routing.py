"""Tests for SIMR routing, registries, and research compiler."""

from __future__ import annotations

import pytest

from axiom.routing.compiler import compile_research_plan
from axiom.routing.failure_memory import FailureMemory
from axiom.routing.model_registry import get_model, list_models, models_for_capability
from axiom.routing.profiler import profile_problem
from axiom.routing.selector import route_task
from axiom.routing.store import RoutingStore
from axiom.routing.strategies import generate_strategies, select_strategies
from axiom.routing.tool_registry import list_tools, tools_for_capability
from axiom.routing.context import ContextBundle, rank_memories


def test_model_registry_has_entries():
    models = list_models()
    assert len(models) >= 3
    assert get_model("mock-model") is not None


def test_tool_registry_has_scientific_tools():
    tools = list_tools()
    tool_ids = {t.tool_id for t in tools}
    assert "scep_benchmarks" in tool_ids
    assert "sympy_engine" in tool_ids


def test_profile_mathematics_problem():
    profile = profile_problem("Prove a theorem about prime distribution using formal methods")
    assert profile.domain.value == "mathematics"
    assert profile.requires_formal
    assert "mathematical_reasoning" in profile.required_capabilities


def test_generate_multiple_strategies():
    profile = profile_problem("Explore counterexamples for a number theory conjecture")
    strategies = generate_strategies(profile)
    assert len(strategies) >= 5
    types = {s.strategy_type.value for s in strategies}
    assert "counterexample_search" in types
    assert "hybrid" in types


def test_select_strategy_for_uncertain_problem():
    profile = profile_problem("Investigate an open problem in analytic number theory millennium")
    selected = select_strategies(profile, max_strategies=2)
    assert len(selected) >= 1


def test_route_task_returns_decision():
    decision = route_task("Summarize recent literature on the Riemann hypothesis")
    assert decision.selected_model
    assert decision.selected_tools
    assert decision.rationale
    assert decision.decision_id.startswith("rtd_")


def test_route_task_deterministic_for_same_input():
    stmt = "Compute numerical experiments for zeta zeros"
    d1 = route_task(stmt)
    d2 = route_task(stmt)
    assert d1.selected_model == d2.selected_model
    assert d1.metadata.get("strategy_type") == d2.metadata.get("strategy_type")


def test_failure_memory_affects_routing():
    memory = FailureMemory(":memory:")
    capability = "mathematical_reasoning"
    for _ in range(3):
        memory.record_failure(
            "gpt-4o-mini",
            "hallucination",
            "Incorrect derivation",
            capability=capability,
        )
    models = models_for_capability(capability)
    filtered = memory.filter_models(models, capability)
    assert filtered[-1].model_id == "gpt-4o-mini"


def test_routing_store_persists_decisions():
    store = RoutingStore(":memory:")
    decision = route_task("Plan a research campaign on proof verification")
    store.save_decision(decision)
    loaded = store.get_decision(decision.decision_id)
    assert loaded is not None
    assert loaded.selected_model == decision.selected_model


def test_compile_research_plan():
    plan = compile_research_plan("Formalize and verify a lemma about group theory")
    assert plan.problem_id
    assert plan.capability_requirements
    assert plan.execution_steps
    assert plan.verification_plan


def test_context_bundle_verified_before_speculative():
    bundle = ContextBundle(
        problem_statement="Test",
        known_facts=[
            {"statement": "Speculative claim", "verification_status": "speculative"},
            {"statement": "Verified fact", "verification_status": "verified"},
        ],
    )
    ctx = bundle.build_prompt_context()
    assert "Verified facts" in ctx
    assert "Speculative" in ctx


def test_rank_memories_prefers_verified():
    memories = [
        {"content": "guess", "verification_status": "speculative"},
        {"content": "fact", "verification_status": "verified"},
    ]
    ranked = rank_memories(memories)
    assert ranked[0]["verification_status"] == "verified"


def test_models_for_capability_ranked():
    models = models_for_capability("literature_synthesis")
    assert models
    scores = [m.benchmark_scores.get("literature_synthesis", 0) for m in models]
    assert scores == sorted(scores, reverse=True)


def test_tools_for_capability():
    tools = tools_for_capability("proof_verification")
    assert any(t.tool_id == "smt_gateway" for t in tools)
