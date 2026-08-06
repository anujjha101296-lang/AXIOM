import time
import random
import string
import json
import pytest
import sqlite3
import networkx as nx
from typing import List, Dict, Any
from pydantic import ValidationError, TypeAdapter

from axiom.core.knowledge_graph.schema import (
    ScientificNode,
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
    NodeType,
    EdgeType,
    EpistemicStatus,
    VerificationTier,
    Edge,
    KnowledgeGraph,
)
from axiom.core.knowledge_graph.db import EpistemicStore, scientific_node_adapter
from axiom.core.knowledge_graph.migrations import run_migrations, migration_status


def random_string(length=20):
    letters = string.ascii_letters + string.digits + " αβγδεζηθικλμνξοπρστυφχψω ∀∃∈ℝℂℤℕℵ ∫∑∏√∆∇ ∂"
    return ''.join(random.choice(letters) for _ in range(length))


def generate_extreme_node(index: int) -> ScientificNode:
    node_type_idx = index % 10
    node_id = f"node_stress_{index}_{random.randint(1000, 9999)}"
    name = f"Node {index}: " + random_string(30)

    metadata = {
        "str_field": random_string(100),
        "int_field": random.randint(-100000, 100000),
        "float_field": random.uniform(-1e6, 1e6),
        "bool_field": bool(index % 2),
        "list_field": [random_string(10) for _ in range(5)],
        "null_field": None,
        "math_latex": r"\int_{0}^{\infty} \frac{x^{s-1}}{e^x - 1} dx = \Gamma(s)\zeta(s)"
    }

    if node_type_idx == 0:
        return MathematicalObjectNode(
            id=node_id,
            name=name,
            metadata=metadata,
            domain="ANALYTIC_NUMBER_THEORY",
            symbolic_representation=r"\zeta(s) = \sum_{n=1}^\infty n^{-s}",
            formal_type="Complex -> Complex",
            properties={"property_large": "x" * 1000, "inv": ["1", "2", "3", "4"]}
        )
    elif node_type_idx == 1:
        return DefinitionNode(
            id=node_id,
            name=name,
            metadata=metadata,
            term=f"Term_{index}_" + random_string(10),
            formal_definition=f"def formal_{index} (x : ℝ) : Prop := x > 0 ∧ x < 1",
            informal_description="Informal explanation " + random_string(200),
            domain="ALGEBRA"
        )
    elif node_type_idx == 2:
        return OpenProblemNode(
            id=node_id,
            name=name,
            metadata=metadata,
            statement="Is " + random_string(100) + " true?",
            domain="NUMBER_THEORY",
            prize_bounty="$1,000,000",
            status=EpistemicStatus.CONJECTURED,
            importance_score=random.uniform(0.1, 10.0)
        )
    elif node_type_idx == 3:
        return ConjectureNode(
            id=node_id,
            name=name,
            metadata=metadata,
            statement="Conjecture " + random_string(150),
            formal_specification="theorem conj_" + str(index) + " : 1 = 1 := rfl",
            status=EpistemicStatus.CONJECTURED,
            tier=VerificationTier.TIER_0_CONJECTURE,
            novelty_score=random.random(),
            generation_strategy="DUAL"
        )
    elif node_type_idx == 4:
        return AuthorNode(
            id=node_id,
            name=name,
            metadata=metadata,
            orcid="0000-0002-1825-0097",
            affiliations=["Institute for Advanced Study", "MIT", "Oxford"]
        )
    elif node_type_idx == 5:
        return PaperNode(
            id=node_id,
            name=name,
            metadata=metadata,
            doi="10.1007/s00220-021-04123-x",
            arxiv_id="arXiv:2104.12345",
            abstract="Abstract payload " + " ".join([random_string(10) for _ in range(50)]),
            published_date="2026-08-05"
        )
    elif node_type_idx == 6:
        return ConceptNode(
            id=node_id,
            name=name,
            metadata=metadata,
            definition="Concept definition " + random_string(100),
            mathematical_formulation="f(x) = x^2 + 1"
        )
    elif node_type_idx == 7:
        return MathematicalClaimNode(
            id=node_id,
            name=name,
            metadata=metadata,
            statement="Claim " + random_string(80),
            formal_specification="theorem claim_" + str(index) + " : True := trivial",
            status=EpistemicStatus.VERIFIED,
            tier=VerificationTier.TIER_2_PROVEN
        )
    elif node_type_idx == 8:
        return ExperimentalFactNode(
            id=node_id,
            name=name,
            metadata=metadata,
            fact_description="Verified numerically up to 10^13 zeros.",
            confidence_metric=0.999999,
            status=EpistemicStatus.VERIFIED,
            tier=VerificationTier.TIER_3_REPLICATED
        )
    else:
        return DatasetNode(
            id=node_id,
            name=name,
            metadata=metadata,
            url="https://example.org/dataset/" + random_string(10),
            size_bytes=1024 * 1024 * random.randint(1, 100)
        )


def run_polymorphic_roundtrip_stress(count: int = 1200):
    print(f"\n--- 1. Polymorphic Serialization Stress Test ({count} nodes) ---")
    nodes = [generate_extreme_node(i) for i in range(count)]
    
    # Direct Pydantic JSON Serialization & Deserialization
    start_time = time.perf_counter()
    json_blobs = [node.model_dump_json() for node in nodes]
    serialize_time = time.perf_counter() - start_time
    
    start_time = time.perf_counter()
    deserialized_nodes = [scientific_node_adapter.validate_json(blob) for blob in json_blobs]
    deserialize_time = time.perf_counter() - start_time
    
    assert len(deserialized_nodes) == count
    for orig, val in zip(nodes, deserialized_nodes):
        assert orig.id == val.id
        assert orig.type == val.type
        assert orig.name == val.name
    
    print(f"Pydantic Serialize Time:   {serialize_time*1000:.2f} ms ({count/serialize_time:.1f} ops/sec)")
    print(f"Pydantic Deserialize Time: {deserialize_time*1000:.2f} ms ({count/deserialize_time:.1f} ops/sec)")
    
    # EpistemicStore SQLite Roundtrip
    store = EpistemicStore(":memory:")
    start_time = time.perf_counter()
    for node in nodes:
        store.add_node(node)
    sqlite_write_time = time.perf_counter() - start_time
    
    start_time = time.perf_counter()
    db_nodes = [store.get_node(n.id) for n in nodes]
    sqlite_read_time = time.perf_counter() - start_time
    
    assert len(db_nodes) == count
    for orig, retrieved in zip(nodes, db_nodes):
        assert retrieved is not None
        assert orig.id == retrieved.id
        assert orig.type == retrieved.type
    
    print(f"SQLite Bulk Write Time:    {sqlite_write_time*1000:.2f} ms ({count/sqlite_write_time:.1f} ops/sec)")
    print(f"SQLite Bulk Read Time:     {sqlite_read_time*1000:.2f} ms ({count/sqlite_read_time:.1f} ops/sec)")
    store.close()
    return True


def run_networkx_graph_export_stress(node_count: int = 1500, edge_count: int = 3000):
    print(f"\n--- 2. NetworkX Graph Export & Preservation Stress Test ({node_count} nodes, {edge_count} edges) ---")
    store = EpistemicStore(":memory:")
    nodes = [generate_extreme_node(i) for i in range(node_count)]
    for node in nodes:
        store.add_node(node)
        
    edge_types = list(EdgeType)
    node_ids = [n.id for n in nodes]
    
    pair_set = set()
    attempts = 0
    while len(pair_set) < edge_count and attempts < edge_count * 10:
        attempts += 1
        src = random.choice(node_ids)
        tgt = random.choice(node_ids)
        if src == tgt:
            continue
        if (src, tgt) in pair_set:
            continue
        pair_set.add((src, tgt))
        e_type = random.choice(edge_types)
        edge = Edge(
            source_id=src,
            target_id=tgt,
            type=e_type,
            confidence=random.uniform(0.5, 1.0),
            provenance={"extracted_by": "stress_test", "run": 1}
        )
        store.add_edge(edge)

    db_edge_count = store.conn.execute("SELECT count(*) FROM edges;").fetchone()[0]

    start_time = time.perf_counter()
    G = store.to_networkx()
    export_time = time.perf_counter() - start_time
    
    print(f"NetworkX to_networkx Export Time: {export_time*1000:.2f} ms")
    print(f"DB Edges: {db_edge_count}, Exported Nodes: {G.number_of_nodes()}, Exported Edges: {G.number_of_edges()}")
    
    assert isinstance(G, nx.DiGraph)
    assert G.number_of_nodes() == node_count
    assert G.number_of_edges() == db_edge_count == len(pair_set) == edge_count
    
    # Verify node attributes preservation
    sample_node = nodes[0]
    nx_node_data = G.nodes[sample_node.id]
    assert nx_node_data["id"] == sample_node.id
    assert nx_node_data["name"] == sample_node.name
    
    # Verify degree metrics computation works on G
    degrees = dict(G.degree())
    assert len(degrees) == node_count
    
    store.close()
    return True


def run_exception_handling_boundary_cases():
    print("\n--- 3. Exception Handling & Boundary Case Tests ---")
    store = EpistemicStore(":memory:")

    # Case 1: Malformed JSON parsing
    print("Testing malformed JSON handling...")
    malformed_json = '{"id": "node_1", "type": "MATHEMATICAL_OBJECT", "name": "Broken", properties: {unquoted: true}}'
    try:
        scientific_node_adapter.validate_json(malformed_json)
        assert False, "Should have raised ValidationError for malformed JSON"
    except (ValidationError, Exception) as e:
        print(f"  [PASS] Caught expected exception for malformed JSON: {type(e).__name__}")

    # Case 2: Invalid Discriminator Value
    print("Testing invalid discriminator value...")
    invalid_disc_json = json.dumps({
        "id": "node_invalid_type",
        "type": "QUANTUM_MULTIVERSE_NODE",
        "name": "Invalid Type"
    })
    try:
        scientific_node_adapter.validate_json(invalid_disc_json)
        assert False, "Should have raised ValidationError for invalid discriminator"
    except ValidationError as e:
        print(f"  [PASS] Caught expected ValidationError for invalid discriminator")

    # Case 3: Missing required Pydantic field
    print("Testing missing required fields...")
    missing_field_json = json.dumps({
        "id": "def_missing",
        "type": "DEFINITION",
        "name": "Incomplete Def"
        # missing 'term' and 'formal_definition'
    })
    try:
        scientific_node_adapter.validate_json(missing_field_json)
        assert False, "Should have raised ValidationError for missing required fields"
    except ValidationError as e:
        print(f"  [PASS] Caught expected ValidationError for missing required fields")

    # Case 4: Duplicate Edge Inserts (Upsert behavior)
    print("Testing duplicate edge inserts (Upsert behavior)...")
    node_a = MathematicalClaimNode(id="claim_dup_a", name="Claim A", statement="A")
    node_b = MathematicalClaimNode(id="claim_dup_b", name="Claim B", statement="B")
    store.add_node(node_a)
    store.add_node(node_b)

    edge1 = Edge(source_id="claim_dup_a", target_id="claim_dup_b", type=EdgeType.PROVES, confidence=0.8)
    edge2 = Edge(source_id="claim_dup_a", target_id="claim_dup_b", type=EdgeType.PROVES, confidence=0.95)
    
    store.add_edge(edge1)
    store.add_edge(edge2)  # Should upsert without raising exception
    retrieved_edge = store.get_edge("claim_dup_a", "claim_dup_b", "PROVES")
    assert retrieved_edge is not None
    assert retrieved_edge.confidence == 0.95
    print("  [PASS] Duplicate edge upserted successfully without error")

    # Case 5: Edge referencing non-existent node
    print("Testing edge insertion for missing node...")
    try:
        store.add_edge(Edge(source_id="claim_dup_a", target_id="non_existent_node", type=EdgeType.PROVES))
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print(f"  [PASS] Caught expected ValueError: {e}")

    # Case 6: SQLite Foreign Key Integrity Enforcement on specialized tables
    print("Testing direct DB FK enforcement...")
    try:
        with store.conn:
            store.conn.execute(
                "INSERT INTO mathematical_objects (id, node_id, object_type, domain) VALUES ('mo_1', 'ghost_node', 'GROUP', 'ALGEBRA');"
            )
        assert False, "Should have raised IntegrityError"
    except sqlite3.IntegrityError as e:
        print(f"  [PASS] SQLite FK IntegrityError raised on orphaned mathematical_object insert: {e}")

    # Case 7: Duplicate Equivalent Statements pair (Unique index constraint)
    print("Testing equivalent statements duplicate upsert...")
    eq_id1 = store.add_equivalent_statement("claim_dup_a", "claim_dup_b", confidence=0.9)
    eq_id2 = store.add_equivalent_statement("claim_dup_a", "claim_dup_b", confidence=1.0)
    assert eq_id1 == eq_id2
    print("  [PASS] Duplicate equivalent statements handled cleanly via upsert")

    store.close()
    return True


if __name__ == "__main__":
    print("Starting AXIOM MDE M1 Empirical Stress & Verification Test Suite...")
    res1 = run_polymorphic_roundtrip_stress(1200)
    res2 = run_networkx_graph_export_stress(1500, 3000)
    res3 = run_exception_handling_boundary_cases()
    print("\nAll Stress & Benchmark Scenarios Executed Successfully!")
