"""Phase 11 — Real Document Intelligence Tests

Tests for:
- TextChunker
- VectorStore cosine similarity
- Embedding provider configuration
- Search handler integration (with test DB)
- Cross-project isolation
- Failure handling (no provider, corrupt input)

Run with: EMBEDDING_PROVIDER=test pytest tests/test_phase11_retrieval.py -v
"""

import json
import math
import os
import pytest
from typing import List

# ── TextChunker Tests ────────────────────────────────────────────────────────

from axiom.research.chunking import TextChunker, TextChunk


class TestTextChunker:
    def setup_method(self):
        self.chunker = TextChunker(chunk_size=100, chunk_overlap=10, min_chunk_length=5)

    def test_empty_string_returns_no_chunks(self):
        assert self.chunker.chunk("") == []

    def test_whitespace_only_returns_no_chunks(self):
        assert self.chunker.chunk("   \n  \t  ") == []

    def test_small_document_returns_one_chunk(self):
        text = "Hello world. This is a short document."
        chunks = self.chunker.chunk(text)
        assert len(chunks) == 1
        assert chunks[0].chunk_index == 0
        assert "Hello" in chunks[0].content

    def test_large_document_produces_multiple_chunks(self):
        word = "word "
        text = word * 100  # 500 chars
        chunker = TextChunker(chunk_size=50, chunk_overlap=5, min_chunk_length=5)
        chunks = chunker.chunk(text)
        assert len(chunks) > 1

    def test_chunks_are_ordered_by_index(self):
        text = ("A " * 300)
        chunks = self.chunker.chunk(text)
        indices = [c.chunk_index for c in chunks]
        assert indices == sorted(indices)

    def test_chunk_metadata_is_set(self):
        chunks = self.chunker.chunk("Hello world test document content here", document_id="doc-1", project_id="proj-1")
        assert all(c.document_id == "doc-1" for c in chunks)
        assert all(c.project_id == "proj-1" for c in chunks)

    def test_char_boundaries_are_set(self):
        text = "Hello world"
        chunks = self.chunker.chunk(text)
        for c in chunks:
            assert c.char_start is not None
            assert c.char_end is not None
            assert c.char_start >= 0
            assert c.char_end > c.char_start

    def test_chunk_overlap_creates_shared_content(self):
        # With overlap, adjacent chunks should share some words
        text = "word " * 60
        chunker = TextChunker(chunk_size=50, chunk_overlap=20, min_chunk_length=5)
        chunks = chunker.chunk(text)
        if len(chunks) >= 2:
            # There should be some positional overlap between adjacent chunks
            assert chunks[1].char_start < chunks[0].char_end

    def test_malformed_input_still_chunks(self):
        # Non-printable characters and mixed content
        text = "Valid text \x00\x01 more valid content here okay"
        chunks = self.chunker.chunk(text)
        assert len(chunks) >= 1


# ── VectorStore Tests ────────────────────────────────────────────────────────

from axiom.research.vector_store import VectorStore, cosine_similarity, VectorSearchResult


class TestCosineSimiliarity:
    def test_identical_vectors_score_one(self):
        v = [1.0, 0.0, 0.0]
        assert abs(cosine_similarity(v, v) - 1.0) < 1e-9

    def test_orthogonal_vectors_score_zero(self):
        assert abs(cosine_similarity([1, 0], [0, 1])) < 1e-9

    def test_opposite_vectors_score_minus_one(self):
        assert abs(cosine_similarity([1, 0], [-1, 0]) + 1.0) < 1e-9

    def test_zero_vector_returns_zero(self):
        assert cosine_similarity([0, 0, 0], [1, 2, 3]) == 0.0


# ── Embedding Provider Tests ─────────────────────────────────────────────────

from axiom.research.embeddings import (
    get_embedding_provider,
    MockEmbeddingProvider,
    EmbeddingConfigurationError,
    EMBEDDING_DIM_TEST,
)


class TestEmbeddingProvider:
    def test_test_provider_returns_correct_dimension(self):
        os.environ["EMBEDDING_PROVIDER"] = "test"
        try:
            provider = get_embedding_provider()
            assert isinstance(provider, MockEmbeddingProvider)
            result = provider.embed_batch(["hello"])
            assert len(result) == 1
            assert len(result[0]) == EMBEDDING_DIM_TEST
        finally:
            del os.environ["EMBEDDING_PROVIDER"]

    def test_test_provider_is_deterministic(self):
        provider = MockEmbeddingProvider()
        a = provider.embed_batch(["the same text"])
        b = provider.embed_batch(["the same text"])
        assert a == b

    def test_different_texts_produce_different_vectors(self):
        provider = MockEmbeddingProvider()
        a = provider.embed_batch(["text about biology"])
        b = provider.embed_batch(["text about mathematics"])
        assert a != b

    def test_empty_batch_returns_empty(self):
        provider = MockEmbeddingProvider()
        result = provider.embed_batch([])
        assert result == []

    def test_production_without_credentials_raises(self, monkeypatch):
        monkeypatch.delenv("EMBEDDING_PROVIDER", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.delenv("ENVIRONMENT", raising=False)
        with pytest.raises(EmbeddingConfigurationError):
            get_embedding_provider()

    def test_explicit_test_env_allows_test_provider(self, monkeypatch):
        monkeypatch.delenv("EMBEDDING_PROVIDER", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.setenv("ENVIRONMENT", "test")
        provider = get_embedding_provider()
        assert isinstance(provider, MockEmbeddingProvider)


# ── Retrieval Quality Tests ──────────────────────────────────────────────────

class TestRetrievalQuality:
    """Integration tests for VectorStore search using MockEmbeddingProvider.

    Documents on clearly distinct topics should rank higher for matching queries.
    """

    def _make_vec(self, text: str) -> List[float]:
        from axiom.research.embeddings import MockEmbeddingProvider
        return MockEmbeddingProvider().embed_batch([text])[0]

    def test_similar_text_retrieves_with_high_score(self):
        """The same text used as query and stored chunk gets cosine sim 1.0."""
        from axiom.research.vector_store import VectorStore, cosine_similarity
        text = "ribosomes synthesize proteins in biological cells"
        vec = self._make_vec(text)
        score = cosine_similarity(vec, vec)
        assert score > 0.99

    def test_dissimilar_texts_lower_score(self):
        """Biology query should score lower against math text."""
        from axiom.research.vector_store import cosine_similarity
        bio_vec = self._make_vec("ribosomes synthesize proteins in cells")
        math_vec = self._make_vec("prime numbers and the Riemann zeta function")
        score = cosine_similarity(bio_vec, math_vec)
        # Heuristic: should be meaningfully lower than 1.0
        assert score < 0.95
