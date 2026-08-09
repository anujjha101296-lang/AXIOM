"""Strategy generation and selection (SIMR §6–7)."""

from __future__ import annotations

import uuid

from axiom.routing.capability_graph import resolve_capability_graph
from axiom.routing.model_registry import get_fallback_model, list_models, models_for_capability
from axiom.routing.models import (
    ProblemProfile,
    ResearchStrategy,
    StrategyType,
    VerificationRequirement,
)
from axiom.routing.tool_registry import tools_for_capability


def generate_strategies(profile: ProblemProfile) -> list[ResearchStrategy]:
    """Generate candidate research strategies — do not commit to the first."""
    graph = resolve_capability_graph(profile)
    primary_cap = profile.required_capabilities[0] if profile.required_capabilities else "research_planning"
    top_models = [m.model_id for m in models_for_capability(primary_cap)[:2]]
    top_tools = [t.tool_id for t in tools_for_capability(primary_cap)[:3]]

    strategies = [
        ResearchStrategy(
            strategy_id=f"str_{uuid.uuid4().hex[:8]}",
            strategy_type=StrategyType.LITERATURE_FIRST,
            description="Survey literature and prior results before reasoning",
            models=top_models[:1],
            tools=["literature_search", "knowledge_graph", "vector_retrieval"],
            verifiers=["primary_source_check"],
            estimated_cost=0.05,
            estimated_minutes=20,
            confidence=0.6 if profile.requires_literature else 0.35,
        ),
        ResearchStrategy(
            strategy_id=f"str_{uuid.uuid4().hex[:8]}",
            strategy_type=StrategyType.FORMAL_MATHEMATICS,
            description="Formal proof path with symbolic and SMT verification",
            models=top_models,
            tools=["sympy_engine", "smt_gateway", "lean_exporter"],
            verifiers=["smt_gateway", "lean_exporter"],
            estimated_cost=0.15,
            estimated_minutes=60,
            confidence=0.7 if profile.requires_formal else 0.3,
        ),
        ResearchStrategy(
            strategy_id=f"str_{uuid.uuid4().hex[:8]}",
            strategy_type=StrategyType.COMPUTATIONAL_EXPLORATION,
            description="Numerical and computational experimentation",
            models=top_models[:1],
            tools=["python_exec", "sympy_engine", "scep_benchmarks"],
            verifiers=["scep_benchmarks", "reproduction_compare"],
            estimated_cost=0.08,
            estimated_minutes=profile.expected_runtime_minutes,
            confidence=0.65 if profile.requires_experiment else 0.4,
        ),
        ResearchStrategy(
            strategy_id=f"str_{uuid.uuid4().hex[:8]}",
            strategy_type=StrategyType.COUNTEREXAMPLE_SEARCH,
            description="Search for counterexamples to test claims",
            models=top_models[:1],
            tools=["sympy_engine", "smt_gateway"],
            verifiers=["smt_gateway"],
            estimated_cost=0.06,
            estimated_minutes=30,
            confidence=0.5,
            novelty_potential=0.6,
        ),
        ResearchStrategy(
            strategy_id=f"str_{uuid.uuid4().hex[:8]}",
            strategy_type=StrategyType.HYBRID,
            description="Combine literature, computation, and verification",
            models=top_models,
            tools=list(dict.fromkeys(top_tools + ["scep_benchmarks", "provenance_records"])),
            verifiers=_verifiers_for_profile(profile),
            estimated_cost=0.20,
            estimated_minutes=max(profile.expected_runtime_minutes, 45),
            confidence=0.55,
            novelty_potential=0.5,
        ),
        ResearchStrategy(
            strategy_id=f"str_{uuid.uuid4().hex[:8]}",
            strategy_type=StrategyType.MULTI_MODEL,
            description="Independent multi-model consensus for high-value claims",
            models=[m.model_id for m in list_models()[:3] if m.model_id != "mock-model"][:2] or top_models,
            tools=top_tools,
            verifiers=["independent_verification", "differential_check"],
            estimated_cost=0.25,
            estimated_minutes=60,
            confidence=0.45,
            novelty_potential=0.4,
        ),
    ]
    return strategies


def evaluate_strategies(
    strategies: list[ResearchStrategy],
    profile: ProblemProfile,
) -> list[tuple[ResearchStrategy, float]]:
    """Score strategies before execution."""
    scored: list[tuple[ResearchStrategy, float]] = []
    for strategy in strategies:
        score = strategy.confidence
        if profile.requires_formal and strategy.strategy_type == StrategyType.FORMAL_MATHEMATICS:
            score += 0.25
        if profile.requires_literature and strategy.strategy_type == StrategyType.LITERATURE_FIRST:
            score += 0.2
        if profile.requires_experiment and strategy.strategy_type == StrategyType.COMPUTATIONAL_EXPLORATION:
            score += 0.2
        if profile.uncertainty > 0.6 and strategy.strategy_type in (
            StrategyType.HYBRID,
            StrategyType.MULTI_MODEL,
        ):
            score += 0.15
        if profile.difficulty.value == "frontier":
            score -= 0.1
        scored.append((strategy, round(min(score, 1.0), 3)))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored


def select_strategies(
    profile: ProblemProfile,
    *,
    max_strategies: int = 2,
) -> list[ResearchStrategy]:
    """Select top strategies; use multiple when uncertainty is high."""
    candidates = generate_strategies(profile)
    scored = evaluate_strategies(candidates, profile)
    n = max_strategies if profile.uncertainty > 0.55 else 1
    return [s for s, _ in scored[:n]]


def _verifiers_for_profile(profile: ProblemProfile) -> list[str]:
    if profile.verification_requirement == VerificationRequirement.FORMAL:
        return ["lean_exporter", "smt_gateway"]
    if profile.verification_requirement == VerificationRequirement.REPRODUCTION:
        return ["provenance_records", "reproduction_compare"]
    if profile.verification_requirement == VerificationRequirement.INDEPENDENT:
        return ["primary_source_check", "independent_verification"]
    return ["scep_benchmarks"]
