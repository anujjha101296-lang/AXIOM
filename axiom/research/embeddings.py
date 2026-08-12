import os
import random
from abc import ABC, abstractmethod
from typing import List

try:
    import openai
except ImportError:
    openai = None

class EmbeddingProvider(ABC):
    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        pass

class MockEmbeddingProvider(EmbeddingProvider):
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        results = []
        for text in texts:
            # Deterministic pseudo-random based on the hash of the text
            rng = random.Random(hash(text))
            results.append([rng.uniform(-1, 1) for _ in range(1536)])
        return results

class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self):
        if not openai:
            raise ImportError("openai package is required for OpenAIEmbeddingProvider")
        self.client = openai.Client()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        
        response = self.client.embeddings.create(
            input=texts,
            model="text-embedding-3-small" # using a standard default, could also be text-embedding-ada-002
        )
        return [data.embedding for data in response.data]

def get_embedding_provider() -> EmbeddingProvider:
    if os.getenv("ENVIRONMENT") == "test" or not os.getenv("OPENAI_API_KEY"):
        return MockEmbeddingProvider()
    return OpenAIEmbeddingProvider()
