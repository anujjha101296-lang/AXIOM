"""
Empirical Stress Test & Benchmark Harness for MDE Ontology & EGS Database (Milestone 1)
========================================================================================
Challenger: challenger_mde_m1_1
Target: axiom/core/knowledge_graph (schema.py, db.py, migrations.py)

Tests:
1. Polymorphic node roundtrips with random & extreme payloads across 1000+ nodes.
2. NetworkX graph export performance and structural preservation.
3. Edge cases and exception handling:
   - Malformed JSON parsing
   - Invalid discriminator value deserialization
   - Duplicate edge upserts (ON CONFLICT behavior)
   - Foreign key constraint violations
   - Missing required node fields
   - Duplicate equivalent statement pairs
"""

import sys
import os
import json
import time
import random
import string
import traceback
from typing import Dict, List, Any

# Ensure project root is in sys.path
PROJECT_ROOT = "/Users/itachiuchiha/.gemini/antigravity/scratch/axiom"
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import networkx as nx
from pydantic import ValidationError

from axiom.core.knowledge_graph.schema import (
    NodeType,
    EdgeType,
    EpistemicStatus,
    VerificationTier,
    AuthorNode,
    PaperNode,
    ConceptNode,
    MathematicalClaimNode,
    ExperimentalFactNode,
    DatasetNode,
    MathematicalObjectNode,
    DefinitionNode,
    OpenProblemNode,
    ConjectureNode,
    Edge,
    KnowledgeGraph,
    scientific_node_adapter,
)
from axiom.core.knowledge_graph.db import EpistemicStore
from axiom.core.knowledge_graph.migrations import run_migrations, migration_status


def generate_random_string(length: int = 20) -> str:
    alphabet = string.ascii_letters + string.digits + " αβγδεζηθικλμνξοπρστυφχψω ∑∏∫√∞≈≠≤≥∈∉⊂⊃∪∩"
    return "".join(random.choices(alphabet, k=length))


def run_benchmark():
    print("=" * 80)
    print("STARTING EMPIRICAL STRESS TEST & BENCHMARK HARNESS")
    print("=" * 80)

    results = {
        "polymorphic_roundtrip": False,
        "nodes_tested": 0,
        "roundtrip_time_sec": 0.0,
        "networkx_export": False,
        "edges_tested": 0,
        "export_time_sec": 0.0,
        "exception_handling": False,
        "failed_checks": [],
    }

    store = EpistemicStore(":memory:")

    # --------------------------------------------------------------------------
    # TEST 1: Polymorphic Node Roundtrips with 1000+ Nodes & Extreme Payloads
    # --------------------------------------------------------------------------
    print("\n--- TEST 1: Polymorphic Serialization across 1000+ Nodes & Extreme Payloads ---")
    start_time = time.time()

    total_nodes = 1200
    created_nodes = []

    # 1. Extreme payload nodes
    # 100KB string payload
    huge_string = "∀x ∈ ℝ, " + ("f(x) = ∫_{0}^{∞} t^{x-1} e^{-t} dt + " * 3000)
    extreme_obj = MathematicalObjectNode(
        id="extreme_huge_payload",
        name="Huge Mathematical Object",
        domain="ANALYTIC_NUMBER_THEORY",
        symbolic_representation=huge_string,
        formal_type="Complex -> Complex",
        properties={
            "huge_text": huge_string[:10000],
            "nested_dict": {"a": {"b": {"c": [1, 2, 3, "deep_string", True, None]}}},
            "unicode_symbols": "Riemann Zeta ζ(s) = ∑_{n=1}^∞ n^{-s} | ℜ(s) > 1 | 𝔽_q",
            "special_json_chars": 'Quotes "double" and \'single\', backslash \\, newline \n, tab \t',
            "large_list": list(range(100)),
            "floats": [1e-10, 1e10, -3.141592653589793, 0.0],
            "booleans": [True, False],
            "null_value": None,
        }
    )
    created_nodes.append(extreme_obj)
    store.add_node(extreme_obj)

    # Empty payload node
    empty_def = DefinitionNode(
        id="extreme_empty_payload",
        name="",
        term="",
        formal_definition="",
        informal_description=None,
        domain=None
    )
    created_nodes.append(empty_def)
    store.add_node(empty_def)

    # 1198 random / diverse nodes across all 10 types
    node_classes = [
        AuthorNode,
        PaperNode,
        ConceptNode,
        MathematicalClaimNode,
        ExperimentalFactNode,
        DatasetNode,
        MathematicalObjectNode,
        DefinitionNode,
        OpenProblemNode,
        ConjectureNode,
    ]

    for i in range(2, total_nodes):
        n_cls = node_classes[i % len(node_classes)]
        nid = f"node_{i:04d}_{n_cls.__name__}"
        name = f"Node {i} - {n_cls.__name__} {generate_random_string(10)}"

        if n_cls == AuthorNode:
            node = AuthorNode(id=nid, name=name, orcid=f"0000-0002-{i:04d}-0000", affiliations=[generate_random_string(15)])
        elif n_cls == PaperNode:
            node = PaperNode(id=nid, name=name, arxiv_id=f"2408.{i:05d}", abstract=generate_random_string(100))
        elif n_cls == ConceptNode:
            node = ConceptNode(id=nid, name=name, definition=generate_random_string(50))
        elif n_cls == MathematicalClaimNode:
            node = MathematicalClaimNode(id=nid, name=name, statement=f"Statement {i}: " + generate_random_string(40))
        elif n_cls == ExperimentalFactNode:
            node = ExperimentalFactNode(id=nid, name=name, fact_description=generate_random_string(60), confidence_metric=random.random())
        elif n_cls == DatasetNode:
            node = DatasetNode(id=nid, name=name, url=f"https://data.example.org/{i}", size_bytes=i * 1024)
        elif n_cls == MathematicalObjectNode:
            node = MathematicalObjectNode(
                id=nid,
                name=name,
                domain=random.choice(["ALGEBRA", "NUMBER_THEORY", "TOPOLOGY", "ANALYSIS"]),
                symbolic_representation=f"\\hat{{A}}_{{{i}}}",
                formal_type="Type -> Prop",
                properties={"index": i, "random_prop": generate_random_string(20)}
            )
        elif n_cls == DefinitionNode:
            node = DefinitionNode(
                id=nid,
                name=name,
                term=f"Term_{i}",
                formal_definition=f"def_{i} : Prop := True",
                informal_description=generate_random_string(30),
                domain="NUMBER_THEORY"
            )
        elif n_cls == OpenProblemNode:
            node = OpenProblemNode(
                id=nid,
                name=name,
                statement=f"Is P = NP for i={i}?",
                prize_bounty=f"${i * 1000}",
                importance_score=random.uniform(0.1, 10.0)
            )
        elif n_cls == ConjectureNode:
            node = ConjectureNode(
                id=nid,
                name=name,
                statement=f"Conjecture {i} holds for all prime factors",
                novelty_score=random.random(),
                generation_strategy=random.choice(["MCTS", "SYMPY", "DUAL"])
            )

        created_nodes.append(node)
        store.add_node(node)

    insert_time = time.time() - start_time
    print(f"-> Inserted {len(created_nodes)} nodes into SQLite in {insert_time:.3f} seconds ({len(created_nodes)/insert_time:.1f} nodes/sec)")

    # Retrieve and verify roundtrip for all 1200 nodes
    fetch_start = time.time()
    roundtrip_mismatches = 0

    for orig_node in created_nodes:
        retrieved = store.get_node(orig_node.id)
        if retrieved is None:
            roundtrip_mismatches += 1
            results["failed_checks"].append(f"Node {orig_node.id} returned None")
            continue

        if type(retrieved) != type(orig_node):
            roundtrip_mismatches += 1
            results["failed_checks"].append(f"Node {orig_node.id} type mismatch: expected {type(orig_node)}, got {type(retrieved)}")
            continue

        # Check model dump equality
        if retrieved.model_dump() != orig_node.model_dump():
            roundtrip_mismatches += 1
            results["failed_checks"].append(f"Node {orig_node.id} dump mismatch")

    fetch_time = time.time() - fetch_start
    print(f"-> Retrieved & verified {len(created_nodes)} nodes in {fetch_time:.3f} seconds ({len(created_nodes)/fetch_time:.1f} nodes/sec)")

    # Verify type query performance & completeness
    for ntype in NodeType:
        nodes_of_type = store.get_nodes_by_type(ntype)
        expected_count = sum(1 for n in created_nodes if n.type == ntype)
        if len(nodes_of_type) != expected_count:
            results["failed_checks"].append(f"get_nodes_by_type({ntype}) count mismatch: expected {expected_count}, got {len(nodes_of_type)}")
            roundtrip_mismatches += 1

    if roundtrip_mismatches == 0:
        results["polymorphic_roundtrip"] = True
        results["nodes_tested"] = len(created_nodes)
        results["roundtrip_time_sec"] = round(insert_time + fetch_time, 4)
        print("-> PASS: All 1200 polymorphic node roundtrips verified with 0 mismatches!")
    else:
        print(f"-> FAIL: {roundtrip_mismatches} roundtrip mismatches detected!")

    # --------------------------------------------------------------------------
    # TEST 2: NetworkX Graph Export & Structural Preservation across 1500+ Edges
    # --------------------------------------------------------------------------
    print("\n--- TEST 2: NetworkX Graph Export & Structural Preservation ---")
    edge_start = time.time()

    created_edges = []
    node_ids = [n.id for n in created_nodes]
    edge_types = list(EdgeType)

    # Generate 1500 random directed edges
    random.seed(42)
    edge_set = set()
    for i in range(1500):
        src = random.choice(node_ids)
        tgt = random.choice(node_ids)
        if src == tgt:
            continue
        etype = random.choice(edge_types)
        pair = (src, tgt, etype.value)
        if pair in edge_set:
            continue
        edge_set.add(pair)

        edge = Edge(
            source_id=src,
            target_id=tgt,
            type=etype,
            confidence=round(random.uniform(0.5, 1.0), 3),
            provenance={"step": i, "method": "stress_harness", "latin": "Q.E.D. ∞"}
        )
        created_edges.append(edge)
        store.add_edge(edge)

    edge_insert_time = time.time() - edge_start
    print(f"-> Inserted {len(created_edges)} edges into SQLite in {edge_insert_time:.3f} seconds")

    # Time NetworkX graph export
    nx_start = time.time()
    G = store.to_networkx()
    nx_export_time = time.time() - nx_start

    print(f"-> Exported to NetworkX graph in {nx_export_time:.4f} seconds")

    nx_errors = 0
    # Structural checks
    if G.number_of_nodes() != len(created_nodes):
        nx_errors += 1
        results["failed_checks"].append(f"NetworkX node count mismatch: SQLite {len(created_nodes)} vs NetworkX {G.number_of_nodes()}")

    if G.number_of_edges() != len(created_edges):
        nx_errors += 1
        results["failed_checks"].append(f"NetworkX edge count mismatch: SQLite {len(created_edges)} vs NetworkX {G.number_of_edges()}")

    # Attribute preservation check on 100 sample nodes & edges
    for sample_node in random.sample(created_nodes, 100):
        if not G.has_node(sample_node.id):
            nx_errors += 1
            results["failed_checks"].append(f"NetworkX missing node {sample_node.id}")
        else:
            nx_attr = G.nodes[sample_node.id]
            if nx_attr.get("id") != sample_node.id or nx_attr.get("type") != sample_node.type.value:
                nx_errors += 1
                results["failed_checks"].append(f"NetworkX node attribute mismatch for {sample_node.id}")

    for sample_edge in random.sample(created_edges, 100):
        if not G.has_edge(sample_edge.source_id, sample_edge.target_id):
            nx_errors += 1
            results["failed_checks"].append(f"NetworkX missing edge {sample_edge.source_id} -> {sample_edge.target_id}")
        else:
            edge_attr = G.edges[sample_edge.source_id, sample_edge.target_id]
            if edge_attr.get("type") != sample_edge.type.value or edge_attr.get("confidence") != sample_edge.confidence:
                nx_errors += 1
                results["failed_checks"].append(f"NetworkX edge attribute mismatch for {sample_edge.source_id} -> {sample_edge.target_id}")

    if nx_errors == 0:
        results["networkx_export"] = True
        results["edges_tested"] = len(created_edges)
        results["export_time_sec"] = round(nx_export_time, 4)
        print(f"-> PASS: NetworkX export verified! Nodes={G.number_of_nodes()}, Edges={G.number_of_edges()}, Time={nx_export_time:.4f}s")
    else:
        print(f"-> FAIL: {nx_errors} NetworkX structural errors detected!")

    # --------------------------------------------------------------------------
    # TEST 3: Edge Cases & Exception Handling
    # --------------------------------------------------------------------------
    print("\n--- TEST 3: Exception Handling & Boundary Cases ---")
    exc_errors = []

    # 3.1 Malformed JSON in nodes table
    try:
        with store.conn:
            store.conn.execute("INSERT INTO nodes (id, type, name, data) VALUES (?, ?, ?, ?);", ("malformed_json_node", "CONCEPT", "Bad Node", "{invalid_json:"))
        try:
            store.get_node("malformed_json_node")
            exc_errors.append("Malformed JSON did NOT raise JSONDecodeError / ValidationError on get_node")
        except Exception as e:
            print(f"-> Caught expected exception for malformed JSON: {type(e).__name__}")
    except Exception as e:
        exc_errors.append(f"Unexpected error in malformed JSON setup: {e}")

    # 3.2 Invalid discriminator value
    try:
        invalid_type_json = json.dumps({"id": "inv_disc_1", "type": "NON_EXISTENT_TYPE", "name": "Invalid Node"})
        try:
            scientific_node_adapter.validate_json(invalid_type_json)
            exc_errors.append("Invalid discriminator type did NOT raise ValidationError")
        except ValidationError as ve:
            print(f"-> Caught expected ValidationError for invalid discriminator: {ve.errors()[0]['type']}")
    except Exception as e:
        exc_errors.append(f"Unexpected error in invalid discriminator test: {e}")

    # 3.3 Duplicate edge insert (ON CONFLICT DO UPDATE behavior)
    try:
        edge_dup = Edge(source_id="node_0002_AuthorNode", target_id="node_0003_PaperNode", type=EdgeType.CITES, confidence=0.7, provenance={"step": 1})
        store.add_edge(edge_dup)

        # Upsert duplicate with higher confidence
        edge_dup_updated = Edge(source_id="node_0002_AuthorNode", target_id="node_0003_PaperNode", type=EdgeType.CITES, confidence=0.99, provenance={"step": 2})
        store.add_edge(edge_dup_updated)

        retrieved_edge = store.get_edge("node_0002_AuthorNode", "node_0003_PaperNode", "CITES")
        if not retrieved_edge or retrieved_edge.confidence != 0.99 or retrieved_edge.provenance != {"step": 2}:
            exc_errors.append("Duplicate edge ON CONFLICT DO UPDATE failed to update confidence/provenance")
        else:
            print("-> PASS: Duplicate edge upsert (ON CONFLICT DO UPDATE) updated record correctly without duplicating rows.")
    except Exception as e:
        exc_errors.append(f"Unexpected error in duplicate edge test: {e}")

    # 3.4 Foreign key constraint on add_edge with missing node
    try:
        missing_edge = Edge(source_id="non_existent_src", target_id="node_0002_AuthorNode", type=EdgeType.PROVES)
        try:
            store.add_edge(missing_edge)
            exc_errors.append("add_edge with non-existent source node did NOT raise ValueError")
        except ValueError as ve:
            print(f"-> Caught expected ValueError for non-existent node in add_edge: {ve}")
    except Exception as e:
        exc_errors.append(f"Unexpected error in FK add_edge test: {e}")

    # 3.5 Missing required field in node model instantiation
    try:
        try:
            DefinitionNode(id="def_missing", name="Missing Term")  # missing required 'term' and 'formal_definition'
            exc_errors.append("DefinitionNode instantiation with missing required fields did NOT raise ValidationError")
        except ValidationError as ve:
            print(f"-> Caught expected ValidationError for missing node fields: {len(ve.errors())} missing field errors")
    except Exception as e:
        exc_errors.append(f"Unexpected error in missing fields test: {e}")

    # 3.6 Unique index on equivalent_statements
    try:
        node_a = MathematicalClaimNode(id="eq_claim_a", name="A", statement="A")
        node_b = MathematicalClaimNode(id="eq_claim_b", name="B", statement="B")
        store.add_node(node_a)
        store.add_node(node_b)

        store.add_equivalent_statement("eq_claim_a", "eq_claim_b", equivalence_type="LOGICAL", confidence=0.8)
        # Duplicate equivalence insertion should update via ON CONFLICT(id)
        store.add_equivalent_statement("eq_claim_a", "eq_claim_b", equivalence_type="LOGICAL", confidence=0.95)

        eq_list = store.get_equivalent_statements("eq_claim_a")
        if eq_list != ["eq_claim_b"]:
            exc_errors.append(f"Equivalent statements list returned incorrect contents: {eq_list}")
        else:
            print("-> PASS: Equivalent statements duplicate insertion handled cleanly.")
    except Exception as e:
        exc_errors.append(f"Unexpected error in equivalent statements test: {e}")

    if len(exc_errors) == 0:
        results["exception_handling"] = True
        print("-> PASS: All exception handling and boundary case tests passed!")
    else:
        results["failed_checks"].extend(exc_errors)
        print(f"-> FAIL: {len(exc_errors)} exception handling errors detected!")

    store.close()

    print("\n" + "=" * 80)
    print("STRESS TEST SUMMARY")
    print("=" * 80)
    print(f"Polymorphic Serialization (1200 nodes): {'PASSED' if results['polymorphic_roundtrip'] else 'FAILED'}")
    print(f"NetworkX Export & Preservation (1500 edges): {'PASSED' if results['networkx_export'] else 'FAILED'}")
    print(f"Exception Handling & Edge Cases: {'PASSED' if results['exception_handling'] else 'FAILED'}")
    print(f"Total Elapsed Time: {insert_time + fetch_time + edge_insert_time + nx_export_time:.3f} seconds")
    if results["failed_checks"]:
        print("Failures:")
        for fc in results["failed_checks"]:
            print(f"  - {fc}")
    print("=" * 80)

    return results


if __name__ == "__main__":
    res = run_benchmark()
    if not (res["polymorphic_roundtrip"] and res["networkx_export"] and res["exception_handling"]):
        sys.exit(1)
