import pytest
import sqlite3
import json
import networkx as nx
import threading
import tempfile
import os

from axiom.core.knowledge_graph.schema import (
    NodeType,
    EdgeType,
    EpistemicStatus,
    VerificationTier,
    MathematicalObjectNode,
    DefinitionNode,
    OpenProblemNode,
    ConjectureNode,
    MathematicalClaimNode,
    Edge,
)
from axiom.core.knowledge_graph.db import EpistemicStore
from axiom.core.knowledge_graph.migrations import run_migrations, migration_status


@pytest.fixture
def temp_db():
    store = EpistemicStore(":memory:")
    yield store
    store.close()


def test_v4_migration_creates_all_tables(temp_db):
    cursor = temp_db.conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = {row[0] for row in cursor.fetchall()}
    
    expected_tables = {
        "_schema_migrations",
        "nodes",
        "edges",
        "proof_lineage",
        "memory_snapshots",
        "mathematical_objects",
        "definitions",
        "equivalent_statements",
        "failed_proof_attempts",
    }
    assert expected_tables.issubset(tables)
    
    status = migration_status(temp_db.conn)
    v4_status = next((m for m in status if m["version"] == 4), None)
    assert v4_status is not None
    assert v4_status["status"] == "applied"


def test_migrations_idempotent(temp_db):
    run_migrations(temp_db.conn)
    run_migrations(temp_db.conn)
    
    status = migration_status(temp_db.conn)
    assert len(status) >= 4
    for m in status:
        assert m["status"] == "applied"


def test_fk_constraint_enforcement(temp_db):
    node_a = MathematicalClaimNode(id="claim_1", name="Claim 1", statement="1+1=2")
    temp_db.add_node(node_a)
    
    # Edge referencing non-existent target node
    with pytest.raises(ValueError):
        temp_db.add_edge(Edge(source_id="claim_1", target_id="missing_node", type=EdgeType.PROVES))
        
    # Direct DB execution without parent node triggers SQLite FK violation
    with pytest.raises(sqlite3.IntegrityError):
        with temp_db.conn:
            temp_db.conn.execute(
                "INSERT INTO failed_proof_attempts (claim_id, tactic_sequence, verifier) VALUES (?, ?, ?);",
                ("non_existent_claim", "[]", "LEAN")
            )


def test_cascade_delete_removes_related_records(temp_db):
    claim_id = "claim_cascade_test"
    claim_node = MathematicalClaimNode(id=claim_id, name="Cascade Test", statement="Test")
    temp_db.add_node(claim_node)
    
    target_node = MathematicalClaimNode(id="target_claim", name="Target Claim", statement="Target")
    temp_db.add_node(target_node)
    
    temp_db.add_edge(Edge(source_id=claim_id, target_id="target_claim", type=EdgeType.PROVES))
    temp_db.add_failed_proof_attempt(claim_id, ["simp", "ring"], "LEAN")
    
    assert len(temp_db.get_failed_proof_attempts(claim_id)) == 1
    assert temp_db.get_edge(claim_id, "target_claim", "PROVES") is not None
    
    with temp_db.conn:
        temp_db.conn.execute("DELETE FROM nodes WHERE id = ?;", (claim_id,))
        
    assert len(temp_db.get_failed_proof_attempts(claim_id)) == 0
    assert temp_db.get_edge(claim_id, "target_claim", "PROVES") is None


def test_mathematical_object_node_roundtrip(temp_db):
    obj_node = MathematicalObjectNode(
        id="obj_riemann_zeta",
        name="Riemann Zeta Function",
        domain="ANALYTIC_NUMBER_THEORY",
        symbolic_representation=r"\zeta(s)",
        formal_type="Complex -> Complex",
        properties={"analytic_continuation": True, "euler_product": True}
    )
    temp_db.add_node(obj_node)
    
    retrieved = temp_db.get_node("obj_riemann_zeta")
    assert retrieved is not None
    assert isinstance(retrieved, MathematicalObjectNode)
    assert retrieved.name == "Riemann Zeta Function"
    assert retrieved.domain == "ANALYTIC_NUMBER_THEORY"
    assert retrieved.symbolic_representation == r"\zeta(s)"
    assert retrieved.formal_type == "Complex -> Complex"
    assert retrieved.properties["analytic_continuation"] is True


def test_definition_node_roundtrip(temp_db):
    def_node = DefinitionNode(
        id="def_zeta_zero",
        name="Non-trivial Zero",
        term="Zeta Zero",
        formal_definition=r"\zeta(s) = 0 \land 0 < \text{Re}(s) < 1",
        informal_description="A zero s of zeta(s) lying in the critical strip 0 < Re(s) < 1.",
        domain="ANALYTIC_NUMBER_THEORY"
    )
    temp_db.add_node(def_node)
    
    retrieved = temp_db.get_node("def_zeta_zero")
    assert retrieved is not None
    assert isinstance(retrieved, DefinitionNode)
    assert retrieved.term == "Zeta Zero"
    assert retrieved.formal_definition == r"\zeta(s) = 0 \land 0 < \text{Re}(s) < 1"
    assert retrieved.informal_description == "A zero s of zeta(s) lying in the critical strip 0 < Re(s) < 1."


def test_open_problem_node_roundtrip(temp_db):
    problem_node = OpenProblemNode(
        id="prob_riemann_hypothesis",
        name="Riemann Hypothesis",
        statement=r"\forall s \in \mathbb{C}, (\zeta(s) = 0 \land 0 < \text{Re}(s) < 1) \implies \text{Re}(s) = 1/2",
        domain="ANALYTIC_NUMBER_THEORY",
        prize_bounty="$1,000,000 Clay Millennium Prize",
        status=EpistemicStatus.CONJECTURED,
        importance_score=1.0
    )
    temp_db.add_node(problem_node)
    
    retrieved = temp_db.get_node("prob_riemann_hypothesis")
    assert retrieved is not None
    assert isinstance(retrieved, OpenProblemNode)
    assert retrieved.prize_bounty == "$1,000,000 Clay Millennium Prize"
    assert retrieved.importance_score == 1.0


def test_conjecture_node_roundtrip(temp_db):
    conj_node = ConjectureNode(
        id="conj_dirichlet_l",
        name="Generalized Riemann Hypothesis",
        statement="All non-trivial zeros of Dirichlet L-functions have real part 1/2.",
        formal_specification="def grh : Prop := ...",
        status=EpistemicStatus.CONJECTURED,
        tier=VerificationTier.TIER_0_CONJECTURE,
        novelty_score=0.95,
        generation_strategy="DUAL"
    )
    temp_db.add_node(conj_node)
    
    retrieved = temp_db.get_node("conj_dirichlet_l")
    assert retrieved is not None
    assert isinstance(retrieved, ConjectureNode)
    assert retrieved.status == EpistemicStatus.CONJECTURED
    assert retrieved.novelty_score == 0.95
    assert retrieved.generation_strategy == "DUAL"


def test_get_nodes_by_type(temp_db):
    obj = MathematicalObjectNode(id="obj_1", name="Group", domain="ALGEBRA", symbolic_representation="G")
    def_node = DefinitionNode(id="def_1", name="Ring Def", term="Ring", formal_definition="Ring formal def")
    temp_db.add_node(obj)
    temp_db.add_node(def_node)
    
    objects = temp_db.get_nodes_by_type(NodeType.MATHEMATICAL_OBJECT)
    assert len(objects) == 1
    assert objects[0].id == "obj_1"
    
    definitions = temp_db.get_nodes_by_type(NodeType.DEFINITION)
    assert len(definitions) == 1
    assert definitions[0].id == "def_1"


def test_get_edges_by_type(temp_db):
    node1 = MathematicalClaimNode(id="c1", name="Claim 1", statement="s1")
    node2 = MathematicalClaimNode(id="c2", name="Claim 2", statement="s2")
    temp_db.add_node(node1)
    temp_db.add_node(node2)
    
    edge_eq = Edge(source_id="c1", target_id="c2", type=EdgeType.EQUIVALENT_TO)
    edge_dep = Edge(source_id="c2", target_id="c1", type=EdgeType.DEPENDS_ON)
    temp_db.add_edge(edge_eq)
    temp_db.add_edge(edge_dep)
    
    eq_edges = temp_db.get_edges_by_type(EdgeType.EQUIVALENT_TO)
    assert len(eq_edges) == 1
    assert eq_edges[0].source_id == "c1"
    assert eq_edges[0].target_id == "c2"
    
    dep_edges = temp_db.get_edges_by_type(EdgeType.DEPENDS_ON)
    assert len(dep_edges) == 1
    assert dep_edges[0].source_id == "c2"
    assert dep_edges[0].target_id == "c1"


def test_specialized_mathematical_object_operations(temp_db):
    obj_node = MathematicalObjectNode(
        id="obj_field",
        name="Galois Field",
        domain="ALGEBRA",
        symbolic_representation="GF(p^n)"
    )
    temp_db.add_mathematical_object(
        node=obj_node,
        object_type="FIELD",
        formal_symbol="GF(p^n)",
        domain="ALGEBRA",
        properties={"characteristic": "p", "finite": True}
    )
    
    mo_record = temp_db.get_mathematical_object("obj_field")
    assert mo_record is not None
    assert mo_record["object_type"] == "FIELD"
    assert mo_record["properties"]["finite"] is True
    assert mo_record["node"].name == "Galois Field"


def test_specialized_definition_operations(temp_db):
    def_node = DefinitionNode(
        id="def_prime",
        name="Prime Number",
        term="Prime",
        formal_definition=r"p > 1 \land (d | p \implies d = 1 \lor d = p)"
    )
    temp_db.add_definition(
        node=def_node,
        term="Prime",
        formal_definition=r"p > 1 \land (d | p \implies d = 1 \lor d = p)",
        informal_definition="A prime number",
        domain="NUMBER_THEORY"
    )
    
    def_record = temp_db.get_definition("def_prime")
    assert def_record is not None
    assert def_record["term"] == "Prime"
    assert def_record["domain"] == "NUMBER_THEORY"


def test_equivalent_statements_operations(temp_db):
    stmt1 = MathematicalClaimNode(id="stmt_1", name="RH Form 1", statement="Zeta zero real part is 1/2")
    stmt2 = MathematicalClaimNode(id="stmt_2", name="RH Form 2", statement="Robin's Inequality")
    temp_db.add_node(stmt1)
    temp_db.add_node(stmt2)
    
    eq_id = temp_db.add_equivalent_statement("stmt_1", "stmt_2", proof_reference="Robin 1984")
    assert eq_id == "eq_stmt_1_stmt_2"
    
    equivs1 = temp_db.get_equivalent_statements("stmt_1")
    assert "stmt_2" in equivs1
    
    equivs2 = temp_db.get_equivalent_statements("stmt_2")
    assert "stmt_1" in equivs2


def test_memory_snapshot_operations(temp_db):
    session_id = "session_mcts_rh"
    snap_data = {"current_node": "lemma_1", "depth": 3, "open_goals": ["Re(s) = 1/2"]}
    
    snap_id = temp_db.save_memory_snapshot(session_id, snap_data, domain="ANALYTIC_NUMBER_THEORY")
    assert snap_id > 0
    
    snapshots = temp_db.get_memory_snapshots(session_id)
    assert len(snapshots) == 1
    assert snapshots[0]["session_id"] == session_id
    assert snapshots[0]["snapshot"]["current_node"] == "lemma_1"
    assert snapshots[0]["domain"] == "ANALYTIC_NUMBER_THEORY"


def test_failed_proof_attempt_operations(temp_db):
    claim = MathematicalClaimNode(id="claim_failed", name="False Lemma", statement="0 = 1")
    temp_db.add_node(claim)
    
    attempt_id = temp_db.add_failed_proof_attempt(
        claim_id="claim_failed",
        tactic_sequence=["simp", "ring"],
        verifier="LEAN",
        error_message="tactic 'ring' failed to simplify goal 0 = 1"
    )
    assert attempt_id > 0
    
    failed_attempts = temp_db.get_failed_proof_attempts("claim_failed")
    assert len(failed_attempts) == 1
    assert failed_attempts[0]["tactic_sequence"] == ["simp", "ring"]
    assert failed_attempts[0]["verifier"] == "LEAN"


def test_to_networkx_with_mde_ontology(temp_db):
    obj = MathematicalObjectNode(id="obj_nx", name="Zeta", domain="ANT", symbolic_representation=r"\zeta")
    def_node = DefinitionNode(id="def_nx", name="Def Zeta", term="Zeta", formal_definition="def")
    temp_db.add_node(obj)
    temp_db.add_node(def_node)
    
    edge = Edge(source_id="def_nx", target_id="obj_nx", type=EdgeType.DEPENDS_ON)
    temp_db.add_edge(edge)
    
    G = temp_db.to_networkx()
    assert isinstance(G, nx.DiGraph)
    assert G.has_node("obj_nx")
    assert G.has_node("def_nx")
    assert G.has_edge("def_nx", "obj_nx")
    assert G.edges["def_nx", "obj_nx"]["type"] == "DEPENDS_ON"


def test_concurrent_migrations_across_threads():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    try:
        errors = []
        barrier = threading.Barrier(10)

        def worker():
            try:
                barrier.wait()
                conn = sqlite3.connect(db_path, timeout=10.0)
                run_migrations(conn)
                conn.close()
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"Concurrent migration errors: {errors}"

        verify_conn = sqlite3.connect(db_path)
        status = migration_status(verify_conn)
        assert len(status) == 4
        assert all(m["status"] == "applied" for m in status)

        cursor = verify_conn.cursor()
        cursor.execute("SELECT count(*) FROM _schema_migrations;")
        assert cursor.fetchone()[0] == 4
        verify_conn.close()
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_add_definition_informal_description_kwarg(temp_db):
    def_node = DefinitionNode(
        id="def_field_ext",
        name="Field Extension",
        term="Extension",
        formal_definition="F \\subseteq K",
        informal_description="A field K containing F as a subfield",
        domain="ALGEBRA"
    )
    # Test passing informal_description as keyword argument
    temp_db.add_definition(
        node=def_node,
        term="Extension",
        formal_definition="F \\subseteq K",
        informal_description="A field K containing F as a subfield",
        domain="ALGEBRA"
    )
    
    def_record = temp_db.get_definition("def_field_ext")
    assert def_record is not None
    assert def_record["term"] == "Extension"
    assert def_record["informal_description"] == "A field K containing F as a subfield"
    assert def_record["informal_definition"] == "A field K containing F as a subfield"

    # Test fallback to node.informal_description when neither kwarg is passed
    def_node_2 = DefinitionNode(
        id="def_group_hom",
        name="Group Homomorphism",
        term="Homomorphism",
        formal_definition="f(ab) = f(a)f(b)",
        informal_description="A structure-preserving map between groups",
        domain="ALGEBRA"
    )
    temp_db.add_definition(
        node=def_node_2,
        term="Homomorphism",
        formal_definition="f(ab) = f(a)f(b)",
        domain="ALGEBRA"
    )
    def_record_2 = temp_db.get_definition("def_group_hom")
    assert def_record_2 is not None
    assert def_record_2["informal_description"] == "A structure-preserving map between groups"

