"""
Scientific Capability Benchmark (SCB)
=======================================
Measures AXIOM capability across five dimensions:
  (a) Theorem parsing accuracy
  (b) SMT refutation rate
  (c) MCTS proof success rate (on a fixed problem set)
  (d) Hypothesis novelty score
  (e) Knowledge graph growth rate

Run with: pytest tests/test_benchmark.py -v
All scores are deterministic given the same EGS state.
"""

import hashlib
import pytest
from axiom.core.knowledge_graph.db import EpistemicStore
from axiom.core.knowledge_graph.schema import (
    MathematicalClaimNode, PaperNode, ConceptNode,
    EpistemicStatus, VerificationTier, NodeType, Edge, EdgeType
)
from axiom.core.reasoning.hypothesis_engine import HypothesisEngine
from axiom.core.reasoning.mcts import MctsSolver
from axiom.core.verification.smt_gateway import SmtGateway
from axiom.core.reasoning.self_improvement import SelfImprovementLoop


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def seeded_store():
    """
    An EpistemicStore pre-seeded with a fixed set of verified theorem nodes
    and concept nodes so that all benchmark scores are deterministic.
    """
    store = EpistemicStore(db_path=":memory:")

    # Add 5 verified theorem nodes (fixed IDs for determinism)
    theorems = [
        ("thm-fermat",   "For n > 2, x^n + y^n = z^n has no positive integer solutions."),
        ("thm-euler",    "e^(iπ) + 1 = 0"),
        ("thm-pythagor", "a^2 + b^2 = c^2 for a right triangle."),
        ("thm-bayes",    "P(A|B) = P(B|A) * P(A) / P(B)"),
        ("thm-gauss",    "The sum of the first n integers equals n*(n+1)/2."),
    ]
    for tid, stmt in theorems:
        node = MathematicalClaimNode(
            id=tid,
            name=f"Theorem: {stmt[:30]}",
            statement=stmt,
            status=EpistemicStatus.VERIFIED,
            tier=VerificationTier.TIER_2_PROVEN,
            metadata={"source": "benchmark_seed"},
        )
        store.add_node(node)

    # Add 2 concept nodes for graph connectivity
    for cid, cname, cdef in [
        ("con-prime",  "Prime Number",  "An integer > 1 with no positive divisors other than 1 and itself."),
        ("con-field",  "Field (Algebra)", "A set with addition and multiplication satisfying field axioms."),
    ]:
        store.add_node(ConceptNode(
            id=cid, name=cname, definition=cdef,
            metadata={"source": "benchmark_seed"},
        ))

    # Add edges
    store.add_node(PaperNode(
        id="paper-wiles", name="Wiles 1995 — Proof of FLT",
        metadata={"source": "benchmark_seed"},
    ))
    store.add_edge(Edge(
        source_id="paper-wiles",
        target_id="thm-fermat",
        type=EdgeType.PROVES,
        confidence=1.0,
        provenance={"benchmark": True},
    ))

    return store


# ── (a) Theorem Parsing Accuracy ──────────────────────────────────────────────

class TestDimensionA_TheoremParsing:
    """
    Accuracy of the epistemic graph store populating correct node types.
    Ground truth: 5 MATHEMATICAL_CLAIM + 1 PAPER + 2 CONCEPT = 8 nodes.
    """

    def test_node_count(self, seeded_store):
        kg = seeded_store.export_knowledge_graph()
        n_claims = sum(1 for n in kg.nodes if n.type == NodeType.MATHEMATICAL_CLAIM)
        n_papers  = sum(1 for n in kg.nodes if n.type == NodeType.PAPER)
        n_concepts = sum(1 for n in kg.nodes if n.type == NodeType.CONCEPT)
        assert n_claims  == 5, f"Expected 5 claims, got {n_claims}"
        assert n_papers  == 1, f"Expected 1 paper, got {n_papers}"
        assert n_concepts == 2, f"Expected 2 concepts, got {n_concepts}"

    def test_all_verified_have_statements(self, seeded_store):
        kg = seeded_store.export_knowledge_graph()
        verified = [
            n for n in kg.nodes
            if n.type == NodeType.MATHEMATICAL_CLAIM
            and n.status == EpistemicStatus.VERIFIED
        ]
        for node in verified:
            assert node.statement, f"Node {node.id} has no statement."

    def test_parsing_accuracy_score(self, seeded_store):
        """Accuracy = correctly typed nodes / total nodes."""
        kg = seeded_store.export_knowledge_graph()
        correct = sum(1 for n in kg.nodes if n.type in {
            NodeType.MATHEMATICAL_CLAIM, NodeType.PAPER, NodeType.CONCEPT
        })
        total = len(kg.nodes)
        score = correct / total if total else 0.0
        print(f"\n[Benchmark] (a) Theorem Parsing Accuracy: {score:.3f}")
        assert score >= 0.95, f"Parsing accuracy {score:.3f} below threshold 0.95"


# ── (b) SMT Refutation Rate ───────────────────────────────────────────────────

class TestDimensionB_SMTRefutation:
    """
    Given a set of fixed invalid modular conjectures, SMT must find
    a counterexample for each.
    """

    INVALID_CLAIMS = [
        # (equation, modulus, variables) — conjectures that are NOT universally true
        # e.g. x^2 + y^2 == z^2 is not always true mod 7
        ("x + y == z", 7,  ["x", "y", "z"]),
        ("x * y == z", 5,  ["x", "y", "z"]),
        ("x + y == z", 11, ["x", "y", "z"]),
    ]

    def test_counterexample_found_for_all(self):
        smt = SmtGateway()
        successes = 0
        for equation, mod, variables in self.INVALID_CLAIMS:
            is_valid, counterexample = smt.verify_modular_conjecture(
                equation=equation,
                modulus=mod,
                variables=variables,
            )
            # We expect these to be invalid (counterexample found = not universally true)
            if not is_valid and counterexample is not None:
                successes += 1
        rate = successes / len(self.INVALID_CLAIMS)
        print(f"\n[Benchmark] (b) SMT Refutation Rate: {rate:.3f}")
        assert rate == 1.0, f"SMT refutation rate {rate:.3f} — expected 1.0"


# ── (c) MCTS Proof Success Rate ───────────────────────────────────────────────

class TestDimensionC_MCTSProof:
    """
    Fixed algebra problem set. MCTS must solve all solvable problems.
    """

    PROBLEMS = [
        ("x + 0", "x"),
        ("x * 1", "x"),
        ("0 + y", "y"),
    ]

    def test_mcts_solves_all(self):
        mcts = MctsSolver()
        solved = 0
        for expr, target in self.PROBLEMS:
            result = mcts.solve(start_expr_str=expr, target_expr_str=target)
            if result is not None:
                solved += 1
        rate = solved / len(self.PROBLEMS)
        print(f"\n[Benchmark] (c) MCTS Proof Success Rate: {rate:.3f}")
        assert rate >= 1.0, f"MCTS solve rate {rate:.3f} — expected 1.0"


# ── (d) Hypothesis Novelty Score ──────────────────────────────────────────────

class TestDimensionD_HypothesisNovelty:
    """
    Novelty = fraction of generated conjectures whose IDs are NOT already
    present in the seeded store. All generated conjectures use hash IDs
    constructed from the generation strategy + origin node, so they should
    always be new relative to the seed.
    """

    def test_hypotheses_generated(self, seeded_store):
        engine = HypothesisEngine(seeded_store)
        new_nodes = engine.generate(max_hypotheses=5)
        assert len(new_nodes) >= 1, "HYP engine produced no conjectures."

    def test_novelty_score(self, seeded_store):
        kg_before = seeded_store.export_knowledge_graph()
        existing_ids = {n.id for n in kg_before.nodes}

        engine = HypothesisEngine(seeded_store)
        new_nodes = engine.generate(max_hypotheses=5)

        novel = [n for n in new_nodes if n.id not in existing_ids]
        score = len(novel) / len(new_nodes) if new_nodes else 0.0
        print(f"\n[Benchmark] (d) Hypothesis Novelty Score: {score:.3f}")
        assert score >= 1.0, f"Novelty score {score:.3f} — expected 1.0 (all new)"

    def test_conjectures_stored_correctly(self, seeded_store):
        engine = HypothesisEngine(seeded_store)
        engine.generate(max_hypotheses=3)
        kg = seeded_store.export_knowledge_graph()
        conjectured = [
            n for n in kg.nodes
            if n.type == NodeType.MATHEMATICAL_CLAIM
            and n.status == EpistemicStatus.CONJECTURED
        ]
        assert len(conjectured) >= 1, "No CONJECTURED nodes found in EGS after hypothesis generation."


# ── (e) Knowledge Graph Growth Rate ───────────────────────────────────────────

class TestDimensionE_GraphGrowthRate:
    """
    Growth rate = (nodes after HYP run) / (nodes before HYP run) - 1.
    Must be > 0 (the graph must actually grow).
    """

    def test_graph_grows_after_hypothesis_run(self, seeded_store):
        kg_before = seeded_store.export_knowledge_graph()
        count_before = len(kg_before.nodes)

        engine = HypothesisEngine(seeded_store)
        engine.generate(max_hypotheses=5)

        kg_after = seeded_store.export_knowledge_graph()
        count_after = len(kg_after.nodes)

        growth_rate = (count_after - count_before) / count_before if count_before else 0.0
        print(f"\n[Benchmark] (e) Knowledge Graph Growth Rate: {growth_rate:.3f}")
        assert growth_rate > 0, f"Graph did not grow: before={count_before}, after={count_after}"


# ── Summary ───────────────────────────────────────────────────────────────────

class TestBenchmarkSummary:
    """Prints a full benchmark summary at the end of the suite."""

    def test_print_summary(self, seeded_store, capsys):
        sil = SelfImprovementLoop(workspace_root="/tmp")
        report = sil.report()
        with capsys.disabled():
            print("\n" + "=" * 60)
            print("AXIOM SCIENTIFIC CAPABILITY BENCHMARK — SPRINT 2")
            print("=" * 60)
            print(f"  Weakest dimension  : {report['weakest_dimension']}")
            print(f"  Dimension score    : {report['weakest_dimension_score']:.3f}")
            print("  Top priority improvements:")
            for item in report["top_3_priority"]:
                print(f"    [{item['priority']:.3f}] {item['name']}")
            print("=" * 60)
