"""Model provider abstraction — models are interchangeable; architecture is permanent."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from axiom.services.model_gateway.client import ModelClient


@runtime_checkable
class ModelProvider(Protocol):
    """Interchangeable model backend. ACA never depends on a specific LLM."""

    provider_id: str

    def generate(self, prompt: str, *, model: str | None = None, temperature: float = 0.7) -> str:
        ...


class DefaultModelProvider:
    """Adapter over existing ModelClient — swap providers without changing ACA."""

    provider_id = "default"

    def __init__(self, client: ModelClient | None = None) -> None:
        self._client = client or ModelClient()

    def generate(self, prompt: str, *, model: str | None = None, temperature: float = 0.7) -> str:
        return self._client.generate(prompt, model=model or "mock-model", temperature=temperature)


class HeuristicModelProvider:
    """Zero-dependency provider for offline/benchmark runs."""

    provider_id = "heuristic"

    def generate(self, prompt: str, *, model: str | None = None, temperature: float = 0.7) -> str:
        return f"[heuristic] Analysis of: {prompt[:120]}"


_PROVIDERS: dict[str, ModelProvider] = {}


def register_provider(provider: ModelProvider) -> None:
    _PROVIDERS[provider.provider_id] = provider


def get_model_provider(provider_id: str = "default") -> ModelProvider:
    if provider_id not in _PROVIDERS:
        if provider_id == "heuristic":
            register_provider(HeuristicModelProvider())
        else:
            register_provider(DefaultModelProvider())
    return _PROVIDERS[provider_id]
