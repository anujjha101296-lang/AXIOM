"""
Empirical SQLite Database Stress Harness for Milestone 1 (MDE Ontology & Migrations)
======================================================================================
Tests SQLite concurrency, bulk foreign key cascade deletion, migration idempotency,
and schema integrity under stress.
"""

import os
import sys
import time
import tempfile
import sqlite3
import concurrent.futures
from typing import List

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

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
from axiom.core.knowledge_graph.migrations import run_migrations, migration_status, MIGRATIONS


def test_concurrency_stress(db_path: str, num_threads: int = 10, items_per_thread: int = 50):
    """
    Stress test concurrent insertions into v4 tables across multiple threads
    writing to the same file-backed SQLite database.
    """
    print(f"--- 1. Testing Database Concurrency ({num_threads} threads, {items_per_thread} items/thread) ---")
    
    # Initialize store to set up schema & WAL mode if needed
    store = EpistemicStore(db_path)
    # Enable WAL mode for better concurrency performance in file-backed SQLite
    store.conn.execute("PRAGMA journal_mode = WAL;")
    store.conn.execute("PRAGMA busy_timeout = 5000;")
    store.close()

    errors = []
    start_time = time.time()

    def worker_task(thread_id: int):
        # Each thread opens its own connection
        t_store = EpistemicStore(db_path)
        t_store.conn.execute("PRAGMA busy_timeout = 5000;")
        
        try:
            for i in range(items_per_thread):
                node_id = f"thread_{thread_id}_node_{i}"
                claim = MathematicalClaimNode(
                    id=node_id,
                    name=f"Claim {thread_id}-{i}",
                    statement=f"Statement {thread_id}-{i}"
                )
                t_store.add_node(claim)

                # Add math object
                obj_node = MathematicalObjectNode(
                    id=f"obj_{node_id}",
                    name=f"Obj {thread_id}-{i}",
                    domain="ALGEBRA",
                    symbolic_representation=f"x_{thread_id}_{i}"
                )
                t_store.add_mathematical_object(
                    node=obj_node,
                    object_type="VARIABLE",
                    formal_symbol=f"x_{thread_id}_{i}",
                    domain="ALGEBRA",
                    properties={"thread": thread_id, "index": i}
                )

                # Add definition
                def_node = DefinitionNode(
                    id=f"def_{node_id}",
                    name=f"Def {thread_id}-{i}",
                    term=f"Term_{thread_id}_{i}",
                    formal_definition=f"Def formal {thread_id}-{i}"
                )
                t_store.add_definition(
                    node=def_node,
                    term=f"Term_{thread_id}_{i}",
                    formal_definition=f"Def formal {thread_id}-{i}",
                    domain="ALGEBRA"
                )

                # Save memory snapshot
                t_store.save_memory_snapshot(
                    session_id=f"session_{thread_id}",
                    snapshot_data={"step": i, "status": "ok"},
                    domain="ALGEBRA"
                )

                # Add failed proof attempt
                t_store.add_failed_proof_attempt(
                    claim_id=node_id,
                    tactic_sequence=["simp", f"tactic_{i}"],
                    verifier="LEAN",
                    error_message=f"Error in thread {thread_id} item {i}"
                )

                # Add equivalent statement if not first item
                if i > 0:
                    prev_id = f"thread_{thread_id}_node_{i-1}"
                    t_store.add_equivalent_statement(
                        statement_a_id=node_id,
                        statement_b_id=prev_id,
                        proof_reference=f"Ref {i}"
                    )
        except Exception as e:
            errors.append(f"Thread {thread_id} failed: {e}")
        finally:
            t_store.close()

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(worker_task, tid) for tid in range(num_threads)]
        concurrent.futures.wait(futures)

    duration = time.time() - start_time
    total_ops = num_threads * items_per_thread

    # Verification
    verify_store = EpistemicStore(db_path)
    cur = verify_store.conn.cursor()

    cur.execute("SELECT COUNT(*) FROM nodes;")
    node_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM mathematical_objects;")
    math_obj_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM definitions;")
    def_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM memory_snapshots;")
    snap_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM failed_proof_attempts;")
    failed_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM equivalent_statements;")
    eq_count = cur.fetchone()[0]

    # Integrity check
    fk_errors = cur.execute("PRAGMA foreign_key_check;").fetchall()
    verify_store.close()

    print(f"Concurrency Duration: {duration:.2f}s across {num_threads} threads ({total_ops} records per table)")
    print(f"Errors encountered: {len(errors)}")
    if errors:
        for err in errors[:5]:
            print(f"  - {err}")
    print(f"Nodes count: {node_count}")
    print(f"Math Objects count: {math_obj_count}")
    print(f"Definitions count: {def_count}")
    print(f"Memory Snapshots count: {snap_count}")
    print(f"Failed Proof Attempts count: {failed_count}")
    print(f"Equivalent Statements count: {eq_count}")
    print(f"Foreign Key Violations: {len(fk_errors)}")

    assert len(errors) == 0, f"Concurrency test had {len(errors)} errors"
    assert len(fk_errors) == 0, f"Foreign key violations found: {fk_errors}"
    print("PASS: Concurrency Stress Test\n")


def test_bulk_cascade_delete_stress(db_path: str, num_nodes: int = 1000):
    """
    Stress test cascade deletion when parent nodes in `nodes` table are deleted
    under bulk conditions (1,000+ nodes with associated child records).
    """
    print(f"--- 2. Testing Bulk Cascade Delete ({num_nodes} nodes) ---")
    store = EpistemicStore(db_path)
    cur = store.conn.cursor()

    # Populate 1,000 parent nodes and associated child records
    with store.conn:
        for i in range(num_nodes):
            parent_id = f"bulk_parent_{i}"
            store.conn.execute(
                "INSERT INTO nodes (id, type, name, data) VALUES (?, ?, ?, ?);",
                (parent_id, "MATHEMATICAL_CLAIM", f"Parent {i}", "{}")
            )
            store.conn.execute(
                "INSERT INTO mathematical_objects (id, node_id, object_type, domain) VALUES (?, ?, ?, ?);",
                (f"obj_{i}", parent_id, "CONCEPT", "NUMBER_THEORY")
            )
            store.conn.execute(
                "INSERT INTO definitions (id, node_id, term, formal_definition) VALUES (?, ?, ?, ?);",
                (f"def_{i}", parent_id, f"Term_{i}", f"Def_{i}")
            )
            store.conn.execute(
                "INSERT INTO failed_proof_attempts (claim_id, tactic_sequence, verifier) VALUES (?, ?, ?);",
                (parent_id, '["simp"]', "LEAN")
            )

        # Create equivalent statements between adjacent pairs
        for i in range(num_nodes - 1):
            store.conn.execute(
                "INSERT INTO equivalent_statements (id, statement_a_id, statement_b_id) VALUES (?, ?, ?);",
                (f"eq_bulk_{i}", f"bulk_parent_{i}", f"bulk_parent_{i+1}")
            )

    # Verify insertion counts
    mo_cnt_before = cur.execute("SELECT COUNT(*) FROM mathematical_objects;").fetchone()[0]
    def_cnt_before = cur.execute("SELECT COUNT(*) FROM definitions;").fetchone()[0]
    failed_cnt_before = cur.execute("SELECT COUNT(*) FROM failed_proof_attempts;").fetchone()[0]
    eq_cnt_before = cur.execute("SELECT COUNT(*) FROM equivalent_statements;").fetchone()[0]
    print(f"Before delete child record counts: mo={mo_cnt_before}, def={def_cnt_before}, failed={failed_cnt_before}, eq={eq_cnt_before}")

    # Perform bulk delete of half the nodes
    half = num_nodes // 2
    start_time = time.time()
    with store.conn:
        cur.execute(f"DELETE FROM nodes WHERE id LIKE 'bulk_parent_%' AND CAST(SUBSTR(id, 13) AS INTEGER) < {half};")
    delete_duration = time.time() - start_time

    print(f"Deleted {half} parent nodes in {delete_duration:.4f}s")

    # Check child table counts after deleting half
    mo_cnt_mid = cur.execute("SELECT COUNT(*) FROM mathematical_objects WHERE node_id LIKE 'bulk_parent_%';").fetchone()[0]
    def_cnt_mid = cur.execute("SELECT COUNT(*) FROM definitions WHERE node_id LIKE 'bulk_parent_%';").fetchone()[0]
    failed_cnt_mid = cur.execute("SELECT COUNT(*) FROM failed_proof_attempts WHERE claim_id LIKE 'bulk_parent_%';").fetchone()[0]
    eq_cnt_mid = cur.execute("SELECT COUNT(*) FROM equivalent_statements WHERE statement_a_id LIKE 'bulk_parent_%' OR statement_b_id LIKE 'bulk_parent_%';").fetchone()[0]

    print(f"After deleting half, remaining bulk child records: mo={mo_cnt_mid}, def={def_cnt_mid}, failed={failed_cnt_mid}, eq={eq_cnt_mid}")
    assert mo_cnt_mid == num_nodes - half
    assert def_cnt_mid == num_nodes - half
    assert failed_cnt_mid == num_nodes - half

    # Perform delete of remaining nodes
    with store.conn:
        cur.execute("DELETE FROM nodes WHERE id LIKE 'bulk_parent_%';")

    mo_cnt_after = cur.execute("SELECT COUNT(*) FROM mathematical_objects WHERE node_id LIKE 'bulk_parent_%';").fetchone()[0]
    def_cnt_after = cur.execute("SELECT COUNT(*) FROM definitions WHERE node_id LIKE 'bulk_parent_%';").fetchone()[0]
    failed_cnt_after = cur.execute("SELECT COUNT(*) FROM failed_proof_attempts WHERE claim_id LIKE 'bulk_parent_%';").fetchone()[0]
    eq_cnt_after = cur.execute("SELECT COUNT(*) FROM equivalent_statements WHERE statement_a_id LIKE 'bulk_parent_%' OR statement_b_id LIKE 'bulk_parent_%';").fetchone()[0]

    fk_errors = cur.execute("PRAGMA foreign_key_check;").fetchall()
    store.close()

    print(f"After full delete, remaining bulk child records: mo={mo_cnt_after}, def={def_cnt_after}, failed={failed_cnt_after}, eq={eq_cnt_after}")
    print(f"Foreign Key Violations: {len(fk_errors)}")

    assert mo_cnt_after == 0
    assert def_cnt_after == 0
    assert failed_cnt_after == 0
    assert eq_cnt_after == 0
    assert len(fk_errors) == 0
    print("PASS: Bulk Cascade Delete Stress Test\n")


def test_migration_v4_idempotency_and_upgrades():
    """
    Test Migration v4 idempotency:
    1. Executed multiple times in sequence on the same DB connection.
    2. Applied onto pre-existing v1, v2, v3 schemas.
    3. Multi-connection concurrent migration invocation.
    """
    print("--- 3. Testing Migration v4 Idempotency & Upgrades ---")
    
    # 3.1 Repeated execution (10 times)
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON;")
    for i in range(10):
        run_migrations(conn)
    status = migration_status(conn)
    assert len(status) == len(MIGRATIONS)
    assert all(s["status"] == "applied" for s in status)
    print("  [✓] 10 consecutive run_migrations() calls succeeded without error")
    conn.close()

    # 3.2 Upgrade path from v1 -> v2 -> v3 -> v4
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON;")
    # Manually run v1, v2, v3
    from axiom.core.knowledge_graph.migrations import (
        _create_migration_table, _v1_initial_schema, _v2_proof_lineage, _v3_working_memory_snapshots, _v4_mathematical_ontology
    )
    _create_migration_table(conn)
    _v1_initial_schema(conn)
    conn.execute("INSERT INTO _schema_migrations (version, description) VALUES (1, 'Initial schema');")
    _v2_proof_lineage(conn)
    conn.execute("INSERT INTO _schema_migrations (version, description) VALUES (2, 'Proof lineage');")
    _v3_working_memory_snapshots(conn)
    conn.execute("INSERT INTO _schema_migrations (version, description) VALUES (3, 'Memory snapshots');")
    conn.commit()

    # Insert mock data in v3 memory_snapshots (without domain column)
    conn.execute("INSERT INTO memory_snapshots (session_id, snapshot) VALUES ('v3_session', '{\"data\": 1}');")
    conn.commit()

    # Now run_migrations should apply v4 safely and add 'domain' column
    run_migrations(conn)

    cur = conn.cursor()
    cur.execute("SELECT id, session_id, snapshot, domain FROM memory_snapshots WHERE session_id = 'v3_session';")
    row = cur.fetchone()
    assert row is not None
    assert row[1] == 'v3_session'
    assert row[3] is None  # domain defaulted to None for legacy row

    # Run run_migrations again to test idempotency after upgrade
    run_migrations(conn)
    status = migration_status(conn)
    assert status[3]["status"] == "applied"
    print("  [✓] Upgrade path v1->v2->v3->v4 and ALTER TABLE memory_snapshots succeeded")
    conn.close()

    # 3.3 Concurrent migration execution across threads on a file-backed DB
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        file_db = f.name

    try:
        def migration_worker():
            m_conn = sqlite3.connect(file_db, timeout=10.0)
            m_conn.execute("PRAGMA busy_timeout = 5000;")
            run_migrations(m_conn)
            m_conn.close()

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(migration_worker) for _ in range(5)]
            concurrent.futures.wait(futures)

        final_conn = sqlite3.connect(file_db)
        status = migration_status(final_conn)
        assert len(status) == len(MIGRATIONS)
        assert all(s["status"] == "applied" for s in status)
        final_conn.close()
        print("  [✓] Concurrent multi-thread migration execution on file DB succeeded")
    finally:
        if os.path.exists(file_db):
            os.remove(file_db)

    print("PASS: Migration v4 Idempotency & Upgrades Test\n")


def run_all_stress_tests():
    print("=======================================================================")
    print("STARTING EMPIRICAL DB STRESS SUITE (Milestone 1)")
    print("=======================================================================")
    
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    try:
        test_concurrency_stress(db_path, num_threads=10, items_per_thread=50)
        test_bulk_cascade_delete_stress(db_path, num_nodes=1000)
        test_migration_v4_idempotency_and_upgrades()
        print("=======================================================================")
        print("ALL EMPIRICAL DB STRESS TESTS PASSED SUCCESSFULLY!")
        print("=======================================================================")
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


if __name__ == "__main__":
    run_all_stress_tests()
