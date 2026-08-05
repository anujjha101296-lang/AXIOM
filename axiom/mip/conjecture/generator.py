"""
Department D — Conjecture Discovery
Autonomous conjecture generator with 5 strategies and novelty scoring.
"""
from __future__ import annotations

import hashlib
import logging
import math
import random
import re
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

# ─────────────────────── Strategy Definitions ───────────────────────


def _strategy_dual(statement: str, name: str) -> str | None:
    """DUAL: Swap ∀/∃ or reverse inequalities to form dual conjecture."""
    if "∀" in statement:
        return statement.replace("∀", "∃", 1) + " [dual-existential]"
    if "∃" in statement:
        return statement.replace("∃", "∀", 1) + " [dual-universal]"
    if "≤" in statement:
        return statement.replace("≤", "≥") + " [dual-inequality]"
    return None


def _strategy_bound(statement: str, name: str) -> str | None:
    """BOUND: Conjecture a tighter upper or lower bound."""
    if any(op in statement for op in ("≤", "≥", "<", ">", "bound")):
        return f"There exists a tight bound: {statement} [bound-tightening-conjecture]"
    if "=" in statement:
        return f"For sufficiently large n: {statement} holds asymptotically [asymptotic-bound]"
    return None


def _strategy_complex(statement: str, name: str) -> str | None:
    """COMPLEX: Extend a real-valued result to the complex plane."""
    if any(kw in statement.lower() for kw in ["real", "integer", "natural", "ℝ", "ℕ", "ℤ"]):
        return (
            f"Extension to ℂ: {statement.replace('ℝ', 'ℂ').replace('real', 'complex')}"
            " [complex-extension-conjecture]"
        )
    return None


def _strategy_general(statement: str, name: str) -> str | None:
    """GENERAL: Generalize a specific case to a broader family."""
    # Look for specific numbers and generalize
    nums = re.findall(r'\b\d+\b', statement)
    if nums and int(nums[0]) > 1:
        n = nums[0]
        generalized = statement.replace(n, "n", 1)
        return f"Generalization: For all n ≥ {n}: {generalized} [generalization-conjecture]"
    return f"General form: The property holds for a broader class: {name} [general-conjecture]"


def _strategy_compose(stmt_a: str, stmt_b: str, name_a: str, name_b: str) -> str | None:
    """COMPOSE: Compose two existing theorems to form a new conjecture."""
    return (
        f"Composition: If ({name_a}) and ({name_b}), "
        f"then the combined conclusion holds: [{stmt_a[:60]}...] ∧ [{stmt_b[:60]}...] "
        "[composition-conjecture]"
    )


STRATEGIES = {
    "DUAL": _strategy_dual,
    "BOUND": _strategy_bound,
    "COMPLEX": _strategy_complex,
    "GENERAL": _strategy_general,
}


# ─────────────────────── Novelty Scorer ───────────────────────


@dataclass
class ConjectureCandidate:
    statement: str
    strategy: str
    source_node_ids: list[str]
    novelty_score: float = 0.0
    domain: str = "unknown"
    generated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


def _fingerprint(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def _token_overlap(a: str, b: str) -> float:
    """Measure how similar two statements are (0=identical, 1=disjoint)."""
    tokens_a = set(a.lower().split())
    tokens_b = set(b.lower().split())
    if not tokens_a or not tokens_b:
        return 1.0
    intersection = tokens_a & tokens_b
    union = tokens_a | tokens_b
    jaccard = len(intersection) / len(union)
    return 1.0 - jaccard  # Higher = more novel


def _is_tautology(statement: str) -> bool:
    """Detect obvious tautologies."""
    lowered = statement.lower().strip()
    tautologies = [
        "for all x, x = x",
        "x = x",
        "a + b = b + a [dual",  # We generated a trivial dual
        "true",
        "1 = 1",
        "0 = 0",
    ]
    return any(t in lowered for t in tautologies)


def compute_novelty_score(
    candidate: str,
    existing_statements: list[str],
    domain_depth: int = 1,
) -> float:
    """
    N(C) = mean_similarity_distance × log(1 + domain_depth) × non_triviality
    Range: [0.0, 1.0]
    """
    if _is_tautology(candidate):
        return 0.0

    # Similarity distance from existing statements
    if not existing_statements:
        similarity_distance = 0.7
    else:
        distances = [_token_overlap(candidate, s) for s in existing_statements[:20]]
        similarity_distance = sum(distances) / len(distances)

    # Non-triviality: longer, more complex statements score higher
    words = len(candidate.split())
    non_triviality = min(1.0, words / 30.0)

    # Domain depth bonus (number theory = 2, algebraic geometry = 4, etc.)
    depth_bonus = math.log(1 + domain_depth) / math.log(5)

    raw = similarity_distance * 0.5 + non_triviality * 0.3 + depth_bonus * 0.2
    return round(min(1.0, max(0.0, raw)), 4)


# ─────────────────────── Main Generator ───────────────────────


class ConjectureGenerator:
    """
    Autonomous conjecture generator.
    Mines EGS theorem nodes using 5 strategies and ranks by novelty.
    """

    def __init__(self, db_path: str = "axiom.db", min_novelty: float = 0.25) -> None:
        self.db_path = db_path
        self.min_novelty = min_novelty

    def _fetch_verified_nodes(self, limit: int = 50) -> list[dict[str, Any]]:
        """Fetch verified mathematical nodes from EGS."""
        candidates: list[dict[str, Any]] = []

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            # Try MIP objects table first
            try:
                rows = conn.execute(
                    """
                    SELECT id, name, statement, domain FROM mip_objects
                    WHERE epistemic_status = 'verified'
                    ORDER BY created_at DESC LIMIT ?
                    """,
                    (limit,),
                ).fetchall()
                candidates.extend(dict(r) for r in rows)
            except sqlite3.OperationalError:
                pass

            # Fall back to legacy EGS nodes table
            if not candidates:
                try:
                    rows = conn.execute(
                        """
                        SELECT id, label as name, content as statement,
                               'unknown' as domain
                        FROM nodes
                        WHERE epistemic_status = 'verified'
                        ORDER BY created_at DESC LIMIT ?
                        """,
                        (limit,),
                    ).fetchall()
                    candidates.extend(dict(r) for r in rows)
                except sqlite3.OperationalError:
                    pass
        finally:
            conn.close()

        return candidates

    def generate(
        self, n_conjectures: int = 5, seed_domain: str | None = None
    ) -> list[ConjectureCandidate]:
        """Generate candidate conjectures from EGS patterns."""
        nodes = self._fetch_verified_nodes()

        if len(nodes) < 1:
            # Seed with basic algebraic identities as bootstrap
            logger.warning("No verified nodes found; using bootstrap seed theorems")
            nodes = [
                {"id": "bootstrap_1", "name": "commutativity", "statement": "∀ a b : ℕ, a + b = b + a", "domain": "algebra"},
                {"id": "bootstrap_2", "name": "associativity", "statement": "∀ a b c : ℕ, (a + b) + c = a + (b + c)", "domain": "algebra"},
                {"id": "bootstrap_3", "name": "distributivity", "statement": "∀ a b c : ℕ, a * (b + c) = a * b + a * c", "domain": "algebra"},
            ]

        existing_statements = [n["statement"] for n in nodes]
        candidates: list[ConjectureCandidate] = []

        # Apply single-node strategies
        for node in nodes[:10]:
            for strategy_name, strategy_fn in STRATEGIES.items():
                result = strategy_fn(node["statement"], node["name"])
                if result and not _is_tautology(result):
                    score = compute_novelty_score(result, existing_statements)
                    if score >= self.min_novelty:
                        candidates.append(ConjectureCandidate(
                            statement=result,
                            strategy=strategy_name,
                            source_node_ids=[node["id"]],
                            novelty_score=score,
                            domain=node.get("domain", "unknown"),
                        ))

        # Apply COMPOSE strategy on pairs
        if len(nodes) >= 2:
            pairs = list(zip(nodes[:5], nodes[1:6]))
            for a, b in pairs:
                result = _strategy_compose(a["statement"], b["statement"], a["name"], b["name"])
                if result:
                    score = compute_novelty_score(result, existing_statements)
                    if score >= self.min_novelty:
                        candidates.append(ConjectureCandidate(
                            statement=result,
                            strategy="COMPOSE",
                            source_node_ids=[a["id"], b["id"]],
                            novelty_score=score,
                            domain=a.get("domain", "unknown"),
                        ))

        # Sort by novelty, deduplicate, return top-n
        seen: set[str] = set()
        unique: list[ConjectureCandidate] = []
        for c in sorted(candidates, key=lambda x: x.novelty_score, reverse=True):
            fp = _fingerprint(c.statement)
            if fp not in seen:
                seen.add(fp)
                unique.append(c)

        return unique[:n_conjectures]

    def save_to_db(self, candidates: list[ConjectureCandidate]) -> list[str]:
        """Persist accepted conjectures to mip_conjectures table. Returns list of IDs."""
        import uuid
        conn = sqlite3.connect(self.db_path)
        saved_ids: list[str] = []
        now = datetime.utcnow().isoformat()
        try:
            with conn:
                for c in candidates:
                    cid = str(uuid.uuid4())
                    try:
                        conn.execute(
                            """
                            INSERT INTO mip_conjectures
                            (id, statement, domain, novelty_score, strategy_used,
                             source_nodes, status, created_at, updated_at)
                            VALUES (?, ?, ?, ?, ?, ?, 'open', ?, ?)
                            """,
                            (
                                cid,
                                c.statement,
                                c.domain,
                                c.novelty_score,
                                c.strategy,
                                ",".join(c.source_node_ids),
                                now,
                                now,
                            ),
                        )
                        saved_ids.append(cid)
                    except sqlite3.OperationalError as exc:
                        logger.warning("Could not save conjecture: %s", exc)
        finally:
            conn.close()
        return saved_ids
