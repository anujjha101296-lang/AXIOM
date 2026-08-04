"""
tests/conftest.py — Shared pytest fixtures for the AXIOM test suite.

All fixtures are session-scoped by default to minimise I/O.
Use function-scoped overrides where test isolation requires fresh state.
"""

from __future__ import annotations

import os
import pytest

# ── Ensure test environment uses in-memory DB ─────────────────────────────────
os.environ.setdefault("DB_PATH", ":memory:")
os.environ.setdefault("AXIOM_API_TOKEN", "test_token")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
os.environ.setdefault("LOG_FORMAT", "console")
os.environ.setdefault("LOG_LEVEL", "WARNING")

from axiom.core.knowledge_graph.db import EpistemicStore
from axiom.core.knowledge_graph.schema import (
    MathematicalClaimNode, ConceptNode, PaperNode,
    EpistemicStatus, VerificationTier, NodeType, Edge, EdgeType,
)
from axiom.core.reasoning.hypothesis_engine import HypothesisEngine
from axiom.core.memory.working_memory import WorkingMemory
from axiom.core.reasoning.self_improvement import SelfImprovementLoop
from axiom.evaluation.prize_readiness import PrizeReadinessScorer


# ── Stores ────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def empty_store() -> EpistemicStore:
    """A fresh in-memory EpistemicStore with no data."""
    return EpistemicStore(db_path=":memory:")


@pytest.fixture(scope="function")
def seeded_store() -> EpistemicStore:
    """
    An in-memory store pre-seeded with 5 verified theorem nodes,
    2 concept nodes, and 1 paper + 1 edge.
    Used across benchmark and reasoning tests.
    """
    store = EpistemicStore(db_path=":memory:")

    theorems = [
        ("thm-fermat",   "For n > 2, x^n + y^n = z^n has no positive integer solutions."),
        ("thm-euler",    "e^(iπ) + 1 = 0"),
        ("thm-pythagor", "a^2 + b^2 = c^2 for a right triangle."),
        ("thm-bayes",    "P(A|B) = P(B|A) * P(A) / P(B)"),
        ("thm-gauss",    "The sum of the first n integers equals n*(n+1)/2."),
    ]
    for tid, stmt in theorems:
        store.add_node(MathematicalClaimNode(
            id=tid,
            name=f"Theorem: {stmt[:30]}",
            statement=stmt,
            status=EpistemicStatus.VERIFIED,
            tier=VerificationTier.TIER_2_PROVEN,
            metadata={"source": "conftest_seed"},
        ))

    for cid, cname, cdef in [
        ("con-prime", "Prime Number", "An integer > 1 with no positive divisors other than 1 and itself."),
        ("con-field", "Field (Algebra)", "A set with addition and multiplication satisfying field axioms."),
    ]:
        store.add_node(ConceptNode(id=cid, name=cname, definition=cdef, metadata={}))

    store.add_node(PaperNode(
        id="paper-wiles", name="Wiles 1995 — Proof of FLT", metadata={}
    ))
    store.add_edge(Edge(
        source_id="paper-wiles",
        target_id="thm-fermat",
        type=EdgeType.PROVES,
        confidence=1.0,
        provenance={"source": "conftest"},
    ))

    return store


# ── Domain objects ────────────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def hypothesis_engine(seeded_store: EpistemicStore) -> HypothesisEngine:
    return HypothesisEngine(seeded_store)


@pytest.fixture(scope="function")
def working_memory() -> WorkingMemory:
    return WorkingMemory()


@pytest.fixture(scope="function")
def prize_scorer() -> PrizeReadinessScorer:
    return PrizeReadinessScorer()


@pytest.fixture(scope="function")
def self_improvement(tmp_path) -> SelfImprovementLoop:
    return SelfImprovementLoop(workspace_root=str(tmp_path))
