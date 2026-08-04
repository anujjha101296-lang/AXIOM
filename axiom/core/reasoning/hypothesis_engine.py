"""
Hypothesis Engine (HYP)
=======================
Generates candidate mathematical conjectures from patterns observed in
the Epistemic Graph Store (EGS). Finds logically adjacent statements to
verified theorems and stores them as CONJECTURED nodes.
"""

import hashlib
import itertools
import re
from typing import List, Tuple, Optional
from axiom.core.knowledge_graph.db import EpistemicStore
from axiom.core.knowledge_graph.schema import (
    MathematicalClaimNode, EpistemicStatus, VerificationTier, NodeType
)


# ──────────────────────────────────────────────────────────────
# Pattern templates for conjecture generation
# Each template takes named placeholders filled from graph data.
# ──────────────────────────────────────────────────────────────
TEMPLATES = [
    # Generalisation: extend a known finite result to n
    "For all n ∈ ℕ, if {stmt_a} holds for n = {k}, then it holds for n = {k} + 1.",
    # Composition: combine two verified statements
    "If {stmt_a} and {stmt_b}, then there exists a structure satisfying both simultaneously.",
    # Duality: swap quantifier order
    "The converse of '{stmt_a}' holds: {dual_stmt_a}.",
    # Bound refinement: tighten a known inequality
    "The bound in '{stmt_a}' can be improved to {tighter_bound}.",
    # Extension to a related domain
    "The result '{stmt_a}' extends to the complex domain: {complex_ext}.",
]


def _dual(statement: str) -> str:
    """Naive dual: swap ∀ and ∃, flip ⟹ direction."""
    s = statement
    s = re.sub(r"for all", "there exists", s, flags=re.IGNORECASE)
    s = re.sub(r"there exists", "for all", s, count=1, flags=re.IGNORECASE)
    s = re.sub(r"⟹", "⟸", s)
    s = re.sub(r"implies", "is implied by", s, flags=re.IGNORECASE)
    return s if s != statement else f"¬({statement})"


def _tighter_bound(statement: str) -> str:
    """Replace ≤ C with ≤ C/2 as a heuristic tightening."""
    return re.sub(r"≤\s*(\w+)", r"≤ \1/2", statement) or f"O(log n) in: {statement}"


def _complex_extension(statement: str) -> str:
    return statement.replace("ℕ", "ℂ").replace("ℤ", "ℂ").replace("ℝ", "ℂ")


class HypothesisEngine:
    """
    Generates candidate conjectures from EGS verified theorem nodes.
    """

    def __init__(self, store: EpistemicStore):
        self.store = store

    def _fetch_verified_claims(self) -> List[MathematicalClaimNode]:
        """Pull all VERIFIED MathematicalClaimNodes from the graph store."""
        graph = self.store.export_knowledge_graph()
        return [
            n for n in graph.nodes
            if n.type == NodeType.MATHEMATICAL_CLAIM
            and n.status == EpistemicStatus.VERIFIED
        ]

    def generate(self, max_hypotheses: int = 5) -> List[MathematicalClaimNode]:
        """
        Main generation method.

        Given ≥ 1 verified claims, produce up to `max_hypotheses` new
        CONJECTURED nodes and persist them to the EGS.

        Returns the list of newly created nodes.
        """
        claims = self._fetch_verified_claims()
        if not claims:
            return []

        new_nodes: List[MathematicalClaimNode] = []
        seen_ids = set()

        # Single-claim templates
        for claim in claims:
            stmt = claim.statement or claim.name
            candidates = [
                ("DUAL",     _dual(stmt)),
                ("BOUND",    _tighter_bound(stmt)),
                ("COMPLEX",  _complex_extension(stmt)),
                ("GENERAL",  f"For all n ∈ ℕ, if [{stmt}] holds for n=1, then it holds for all n."),
            ]
            for tag, conj_stmt in candidates:
                if len(new_nodes) >= max_hypotheses:
                    break
                node_id = hashlib.sha256(
                    f"hyp:{tag}:{claim.id}:{conj_stmt}".encode()
                ).hexdigest()
                if node_id in seen_ids:
                    continue
                seen_ids.add(node_id)
                node = MathematicalClaimNode(
                    id=node_id,
                    name=f"Conjecture [{tag}] from '{claim.name}'",
                    statement=conj_stmt,
                    status=EpistemicStatus.CONJECTURED,
                    tier=VerificationTier.TIER_0_CONJECTURE,
                    metadata={
                        "origin_claim_id": claim.id,
                        "generation_strategy": tag,
                    },
                )
                self.store.add_node(node)
                new_nodes.append(node)

        # Pair-composition template (first eligible pair only)
        if len(claims) >= 2 and len(new_nodes) < max_hypotheses:
            c1, c2 = claims[0], claims[1]
            stmt1 = c1.statement or c1.name
            stmt2 = c2.statement or c2.name
            conj_stmt = (
                f"If [{stmt1}] and [{stmt2}], "
                f"then there exists a unified structure satisfying both simultaneously."
            )
            node_id = hashlib.sha256(
                f"hyp:COMPOSE:{c1.id}:{c2.id}".encode()
            ).hexdigest()
            if node_id not in seen_ids:
                seen_ids.add(node_id)
                node = MathematicalClaimNode(
                    id=node_id,
                    name=f"Conjecture [COMPOSE] '{c1.name}' ∧ '{c2.name}'",
                    statement=conj_stmt,
                    status=EpistemicStatus.CONJECTURED,
                    tier=VerificationTier.TIER_0_CONJECTURE,
                    metadata={
                        "origin_claim_ids": [c1.id, c2.id],
                        "generation_strategy": "COMPOSE",
                    },
                )
                self.store.add_node(node)
                new_nodes.append(node)

        return new_nodes
