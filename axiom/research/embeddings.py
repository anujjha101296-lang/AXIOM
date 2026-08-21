"""Embedding providers for semantic document retrieval.

EMBEDDING_PROVIDER controls which backend is used:
  - openai   → OpenAI text-embedding-3-small (requires OPENAI_API_KEY)
  - gemini   → Google textembedding-gecko (requires GEMINI_API_KEY)
  - test     → Deterministic MockEmbeddingProvider (no network, for tests only)

In production, omitting EMBEDDING_PROVIDER and lacking credentials will raise
an explicit ConfigurationError rather than silently returning random vectors.
"""

import os
import random
from abc import ABC, abstractmethod
from typing import List

try:
    import openai
except ImportError:
    openai = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None


EMBEDDING_DIM_OPENAI = 1536     # text-embedding-3-small
EMBEDDING_DIM_GEMINI = 768      # textembedding-gecko
EMBEDDING_DIM_TEST = 1536       # same dimension as OpenAI for test interoperability


class EmbeddingConfigurationError(RuntimeError):
    """Raised when production embedding provider is misconfigured."""
    pass


class EmbeddingProvider(ABC):
    """Abstract base class for all embedding backends."""

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Output embedding dimension."""

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of texts; returns a list of float vectors."""


class MockEmbeddingProvider(EmbeddingProvider):
    """Deterministic test provider — NEVER use in production.

    Produces pseudo-random but reproducible vectors based on text content hash.
    This ensures retrieval results are deterministic in tests without network calls.
    """

    dimension = EMBEDDING_DIM_TEST

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        results = []
        for text in texts:
            rng = random.Random(hash(text))
            results.append([rng.uniform(-1, 1) for _ in range(self.dimension)])
        return results


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """Production provider using OpenAI Embeddings API."""

    dimension = EMBEDDING_DIM_OPENAI

    def __init__(self, model: str = "text-embedding-3-small"):
        if not openai:
            raise EmbeddingConfigurationError(
                "openai package is not installed. Run: pip install openai"
            )
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise EmbeddingConfigurationError(
                "OPENAI_API_KEY environment variable is not set. "
                "Real embeddings cannot be generated without an API key."
            )
        self.client = openai.Client(api_key=api_key)
        self.model = model

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        response = self.client.embeddings.create(input=texts, model=self.model)
        return [data.embedding for data in response.data]


class GeminiEmbeddingProvider(EmbeddingProvider):
    """Production provider using Google Gemini Embeddings API."""

    dimension = EMBEDDING_DIM_GEMINI

    def __init__(self, model: str = "models/embedding-001"):
        if not genai:
            raise EmbeddingConfigurationError(
                "google-generativeai package is not installed. "
                "Run: pip install google-generativeai"
            )
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise EmbeddingConfigurationError(
                "GEMINI_API_KEY environment variable is not set. "
                "Real embeddings cannot be generated without an API key."
            )
        genai.configure(api_key=api_key)
        self.model = model

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        results = []
        for text in texts:
            result = genai.embed_content(model=self.model, content=text)
            results.append(result["embedding"])
        return results


def get_embedding_provider() -> EmbeddingProvider:
    """Factory: select embedding provider from EMBEDDING_PROVIDER env var.

    Raises EmbeddingConfigurationError in production if provider is
    misconfigured rather than silently falling back to fake vectors.
    """
    provider = os.getenv("EMBEDDING_PROVIDER", "").lower().strip()

    if provider == "test":
        return MockEmbeddingProvider()

    if provider == "openai":
        return OpenAIEmbeddingProvider(
            model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        )

    if provider == "gemini":
        return GeminiEmbeddingProvider(
            model=os.getenv("EMBEDDING_MODEL", "models/embedding-001")
        )

    # No provider set — decide based on available credentials
    if os.getenv("OPENAI_API_KEY"):
        return OpenAIEmbeddingProvider()

    if os.getenv("GEMINI_API_KEY"):
        return GeminiEmbeddingProvider()

    # No credentials at all — check if this is an explicit test environment
    if os.getenv("ENVIRONMENT", "").lower() in ("test", "testing", "ci"):
        return MockEmbeddingProvider()

    # Production with no credentials: fail loudly
    raise EmbeddingConfigurationError(
        "No embedding provider configured. "
        "Set EMBEDDING_PROVIDER=openai (with OPENAI_API_KEY) "
        "or EMBEDDING_PROVIDER=gemini (with GEMINI_API_KEY) "
        "or EMBEDDING_PROVIDER=test for deterministic test execution."
    )
