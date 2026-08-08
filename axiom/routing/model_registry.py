"""Model registry — catalog of available reasoning systems (SIMR §1)."""

from __future__ import annotations

from axiom.routing.models import ModelSpec

_MODEL_CATALOG: dict[str, ModelSpec] = {
    "mock-model": ModelSpec(
        model_id="mock-model",
        name="AXIOM Mock Model",
        provider="axiom",
        version="1.0.0",
        capabilities=[
            "general_reasoning",
            "literature_synthesis",
            "summarization",
            "offline",
        ],
        context_window=8192,
        cost_per_1k_tokens=0.0,
        latency_ms_p50=10,
        limitations=["Deterministic mock only", "Not suitable for production research"],
        reliability_score=0.4,
        benchmark_scores={
            "mathematical_reasoning": 0.35,
            "literature_synthesis": 0.55,
            "research_planning": 0.45,
        },
        availability="available",
        license_notes="Internal testing only",
    ),
    "gpt-4o-mini": ModelSpec(
        model_id="gpt-4o-mini",
        name="GPT-4o Mini",
        provider="openai",
        version="2024-07-18",
        capabilities=[
            "general_reasoning",
            "coding",
            "mathematical_reasoning",
            "literature_synthesis",
            "structured_output",
        ],
        context_window=128_000,
        tool_support=True,
        structured_output=True,
        cost_per_1k_tokens=0.00015,
        latency_ms_p50=800,
        limitations=["May hallucinate citations", "Not a formal verifier"],
        reliability_score=0.75,
        benchmark_scores={
            "mathematical_reasoning": 0.72,
            "literature_synthesis": 0.78,
            "research_planning": 0.74,
            "coding": 0.80,
        },
        availability="requires_api_key",
        license_notes="OpenAI API terms",
    ),
    "gpt-4o": ModelSpec(
        model_id="gpt-4o",
        name="GPT-4o",
        provider="openai",
        version="2024-05-13",
        capabilities=[
            "general_reasoning",
            "coding",
            "mathematical_reasoning",
            "literature_synthesis",
            "long_context",
            "structured_output",
        ],
        context_window=128_000,
        tool_support=True,
        structured_output=True,
        cost_per_1k_tokens=0.005,
        latency_ms_p50=1200,
        limitations=["May hallucinate citations", "High cost"],
        reliability_score=0.82,
        benchmark_scores={
            "mathematical_reasoning": 0.80,
            "literature_synthesis": 0.85,
            "research_planning": 0.82,
            "coding": 0.88,
        },
        availability="requires_api_key",
        license_notes="OpenAI API terms",
    ),
    "gemini-1.5-flash": ModelSpec(
        model_id="gemini-1.5-flash",
        name="Gemini 1.5 Flash",
        provider="google",
        version="1.5",
        capabilities=[
            "general_reasoning",
            "coding",
            "mathematical_reasoning",
            "long_context",
        ],
        context_window=1_000_000,
        tool_support=True,
        cost_per_1k_tokens=0.000075,
        latency_ms_p50=600,
        limitations=["Citation behavior varies", "Not a formal verifier"],
        reliability_score=0.73,
        benchmark_scores={
            "mathematical_reasoning": 0.70,
            "literature_synthesis": 0.72,
            "research_planning": 0.71,
            "long_context": 0.85,
        },
        availability="requires_api_key",
        license_notes="Google API terms",
    ),
    "gemini-pro": ModelSpec(
        model_id="gemini-pro",
        name="Gemini Pro",
        provider="google",
        version="1.0",
        capabilities=[
            "general_reasoning",
            "coding",
            "mathematical_reasoning",
            "literature_synthesis",
        ],
        context_window=32_000,
        tool_support=True,
        cost_per_1k_tokens=0.0005,
        latency_ms_p50=900,
        limitations=["May hallucinate citations"],
        reliability_score=0.78,
        benchmark_scores={
            "mathematical_reasoning": 0.76,
            "literature_synthesis": 0.80,
            "research_planning": 0.77,
        },
        availability="requires_api_key",
        license_notes="Google API terms",
    ),
}


def list_models() -> list[ModelSpec]:
    return list(_MODEL_CATALOG.values())


def get_model(model_id: str) -> ModelSpec | None:
    return _MODEL_CATALOG.get(model_id)


def models_for_capability(capability: str) -> list[ModelSpec]:
    """Return models ranked by benchmark score for a capability."""
    scored = []
    for model in _MODEL_CATALOG.values():
        score = model.benchmark_scores.get(capability, 0.0)
        if capability in model.capabilities or score > 0:
            scored.append((score, model))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [m for _, m in scored]


def get_fallback_model(model_id: str) -> str | None:
    """Approved fallback chain — never silent."""
    fallbacks = {
        "gpt-4o": "gpt-4o-mini",
        "gpt-4o-mini": "mock-model",
        "gemini-pro": "gemini-1.5-flash",
        "gemini-1.5-flash": "mock-model",
    }
    return fallbacks.get(model_id, "mock-model")
