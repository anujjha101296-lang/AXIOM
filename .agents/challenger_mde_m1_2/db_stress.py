"""
Empirical SQLite DB Stress Harness for MDE Milestone 1
======================================================
Focus areas:
1. Concurrency: Multi-threaded insertion & query stress on file-based SQLite DB across all v4 tables.
2. FK Cascade Integrity: Bulk deletion of parent nodes and verification of child record cascades.
3. Migration Idempotency & Legacy Transition: Repeated execution, migration from legacy v1/v2/v3 schemas, and concurrent migration triggers.
"""

import sys
import os
import sqlite3
import tempfile
import threading
import time
import json
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
SHIMS_DIR = os.path.join(AGENT_DIR, "shims")
PROJECT_ROOT = os.path.abspath(os.path.join(AGENT_DIR, "../.."))

sys.path.insert(0, SHIMS_DIR)
sys.path.insert(0, PROJECT_ROOT)

from axiom.core.knowledge_graph.schema import (
    MathematicalObjectNode,
    DefinitionNode,
    MathematicalClaimNode,
    OpenProblemNode,
    ConjectureNode,
    Edge,
    EdgeType,
)
from axiom.core.knowledge_graph.db import EpistemicStore
from axiom.core.knowledge_graph.migrations import run_migrations, migration_status, MIGRATIONS

class StressTestRunner:
    def __init__(self):
        self.results = {}

    def report(self, test_name, success, details):
        status_str = "PASS" if success else "FAIL"
        print(f"[{status_str}] {test_name}: {details}")
        self.results[test_name] = {"success": success, "details": details}

# ─────────────────────────────────────────────────────────────────────────────
# 1. CONCURRENCY STRESS TEST
# ─────────────────────────────────────────────────────────────────────────────
def test_sqlite_concurrency():
    print("\n--- 1. Multi-Threaded SQLite Concurrency Stress Test ---")
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    try:
        # Initialize schema via standard EpistemicStore init
        init_store = EpistemicStore(db_path)
        # Enable WAL mode and set busy timeout for concurrency
        init_store.conn.execute("PRAGMA journal_mode = WAL;")
        init_store.conn.execute("PRAGMA busy_timeout = 5000;")
        init_store.close()

        num_threads = 10
        records_per_thread = 50

        errors = []
        start_time = time.time()

        def worker_task(thread_id):
            conn = sqlite3.connect(db_path, timeout=10.0)
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute("PRAGMA busy_timeout = 10000;")
            
            store = EpistemicStore.__new__(EpistemicStore)
            store.db_path = db_path
            store.conn = conn

            for i in range(records_per_thread):
                node_prefix = f"t{thread_id}_item{i}"
                
                # 1. Add claim node
                claim = MathematicalClaimNode(
                    id=f"claim_{node_prefix}",
                    name=f"Claim {node_prefix}",
                    statement=f"Statement for {node_prefix}"
                )
                store.add_node(claim)

                # 2. Add math object node & table record
                mo_node = MathematicalObjectNode(
                    id=f"mo_{node_prefix}",
                    name=f"Math Obj {node_prefix}",
                    domain="ALGEBRA",
                    symbolic_representation=f"X_{thread_id}_{i}"
                )
                store.add_mathematical_object(
                    node=mo_node,
                    object_type="GROUP",
                    formal_symbol=f"G_{thread_id}_{i}",
                    domain="ALGEBRA",
                    properties={"order": i, "thread": thread_id}
                )

                # 3. Add definition record (using parameter informal_definition)
                def_node = DefinitionNode(
                    id=f"def_{node_prefix}",
                    name=f"Def {node_prefix}",
                    term=f"Term_{thread_id}_{i}",
                    formal_definition=f"def_{i}"
                )
                store.add_definition(
                    node=def_node,
                    term=f"Term_{thread_id}_{i}",
                    formal_definition=f"def_{i}",
                    informal_definition=f"Desc {i}"
                )

                # 4. Add equivalent statement record
                store.add_equivalent_statement(
                    statement_a_id=f"claim_{node_prefix}",
                    statement_b_id=f"def_{node_prefix}",
                    equivalence_type="LOGICAL"
                )

                # 5. Add memory snapshot
                store.save_memory_snapshot(
                    session_id=f"session_{thread_id}",
                    snapshot_data={"step": i, "status": "active"},
                    domain="ALGEBRA"
                )

                # 6. Add failed proof attempt
                store.add_failed_proof_attempt(
                    claim_id=f"claim_{node_prefix}",
                    tactic_sequence=["simp", "auto"],
                    verifier="SMT",
                    error_message="timeout"
                )

            conn.close()

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(worker_task, t) for t in range(num_threads)]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as ex:
                    err_formatted = f"{type(ex).__name__}: {str(ex)}"
                    errors.append(err_formatted)

        duration = time.time() - start_time

        # Verify final database counts and integrity
        verify_conn = sqlite3.connect(db_path)
        cursor = verify_conn.cursor()

        cursor.execute("SELECT count(*) FROM nodes;")
        nodes_count = cursor.fetchone()[0]

        cursor.execute("SELECT count(*) FROM mathematical_objects;")
        mo_count = cursor.fetchone()[0]

        cursor.execute("SELECT count(*) FROM definitions;")
        def_count = cursor.fetchone()[0]

        cursor.execute("SELECT count(*) FROM equivalent_statements;")
        eq_count = cursor.fetchone()[0]

        cursor.execute("SELECT count(*) FROM memory_snapshots;")
        snap_count = cursor.fetchone()[0]

        cursor.execute("SELECT count(*) FROM failed_proof_attempts;")
        failed_count = cursor.fetchone()[0]

        verify_conn.close()

        expected_obj_count = num_threads * records_per_thread
        success = (
            len(errors) == 0
            and mo_count == expected_obj_count
            and def_count == expected_obj_count
            and eq_count == expected_obj_count
            and snap_count == expected_obj_count
            and failed_count == expected_obj_count
        )

        sample_errors = list(set(errors))[:3]
        details = (
            f"Processed {num_threads * records_per_thread} transaction sets across {num_threads} threads in {duration:.2f}s. "
            f"Errors: {len(errors)} (Sample errors: {sample_errors}). Row counts -> math_obj: {mo_count}/{expected_obj_count}, "
            f"defs: {def_count}/{expected_obj_count}, eq_stmts: {eq_count}/{expected_obj_count}, "
            f"snapshots: {snap_count}/{expected_obj_count}, failed_proofs: {failed_count}/{expected_obj_count}."
        )
        return success, details

    finally:
        if os.path.exists(db_path):
            os.remove(db_path)

# ─────────────────────────────────────────────────────────────────────────────
# 2. BULK CASCADE DELETE STRESS TEST
# ─────────────────────────────────────────────────────────────────────────────
def test_bulk_cascade_delete():
    print("\n--- 2. Bulk Foreign Key Cascade Delete Stress Test ---")
    store = EpistemicStore(":memory:")
    
    num_nodes = 500
    delete_count = 250
    
    # 1. Insert parent nodes and populate all v4 child tables
    for i in range(num_nodes):
        claim_id = f"bulk_claim_{i}"
        claim_node = MathematicalClaimNode(id=claim_id, name=f"Claim {i}", statement=f"Statement {i}")
        store.add_node(claim_node)

        mo_id = f"bulk_mo_{i}"
        mo_node = MathematicalObjectNode(id=mo_id, name=f"Object {i}")
        store.add_mathematical_object(mo_node, object_type="CONCEPT", domain="GEOMETRY")

        def_id = f"bulk_def_{i}"
        def_node = DefinitionNode(id=def_id, name=f"Def {i}", term=f"Term {i}", formal_definition=f"def_{i}")
        store.add_definition(def_node, term=f"Term {i}", formal_definition=f"def_{i}")

        # Edge between claim and mo
        store.add_edge(Edge(source_id=claim_id, target_id=mo_id, type=EdgeType.DEPENDS_ON))

        # Equivalence between claim and def
        store.add_equivalent_statement(claim_id, def_id)

        # Failed proof attempt on claim
        store.add_failed_proof_attempt(claim_id, ["intro", "cases"], "LEAN", "Goal not solved")

    cursor = store.conn.cursor()

    # Target nodes to delete (first 250 claims)
    to_delete = [f"bulk_claim_{i}" for i in range(delete_count)]

    # Execute bulk deletion of parent nodes
    with store.conn:
        placeholders = ",".join("?" * len(to_delete))
        store.conn.execute(f"DELETE FROM nodes WHERE id IN ({placeholders});", to_delete)

    # Post-delete counts
    cursor.execute("SELECT count(*) FROM nodes WHERE id LIKE 'bulk_claim_%';")
    remaining_claims = cursor.fetchone()[0]

    cursor.execute("SELECT count(*) FROM mathematical_objects WHERE node_id NOT IN (SELECT id FROM nodes);")
    orphan_mo = cursor.fetchone()[0]

    cursor.execute("SELECT count(*) FROM definitions WHERE node_id NOT IN (SELECT id FROM nodes);")
    orphan_def = cursor.fetchone()[0]

    cursor.execute("SELECT count(*) FROM equivalent_statements WHERE statement_a_id NOT IN (SELECT id FROM nodes) OR statement_b_id NOT IN (SELECT id FROM nodes);")
    orphan_eq = cursor.fetchone()[0]

    cursor.execute("SELECT count(*) FROM failed_proof_attempts WHERE claim_id NOT IN (SELECT id FROM nodes);")
    orphan_failed = cursor.fetchone()[0]

    cursor.execute("SELECT count(*) FROM edges WHERE source_id NOT IN (SELECT id FROM nodes) OR target_id NOT IN (SELECT id FROM nodes);")
    orphan_edges = cursor.fetchone()[0]

    store.close()

    success = (
        remaining_claims == (num_nodes - delete_count)
        and orphan_mo == 0
        and orphan_def == 0
        and orphan_eq == 0
        and orphan_failed == 0
        and orphan_edges == 0
    )

    details = (
        f"Inserted {num_nodes} claim & object pairs with child records across all 5 tables. "
        f"Bulk deleted {delete_count} parent nodes. Remaining claims: {remaining_claims}. "
        f"Orphans detected -> mo: {orphan_mo}, def: {orphan_def}, eq_stmts: {orphan_eq}, "
        f"failed_proofs: {orphan_failed}, edges: {orphan_edges}."
    )
    return success, details

# ─────────────────────────────────────────────────────────────────────────────
# 3. MIGRATION IDEMPOTENCY & LEGACY SCHEMA TRANSITION STRESS TEST
# ─────────────────────────────────────────────────────────────────────────────
def test_migration_idempotency_and_legacy():
    print("\n--- 3. Migration Idempotency & Legacy Schema Transition Stress Test ---")
    
    # 3a. Repeated sequential migrations
    conn = sqlite3.connect(":memory:")
    for _ in range(50):
        run_migrations(conn)

    status = migration_status(conn)
    v4_applied = all(m["status"] == "applied" for m in status) and len(status) == 4
    conn.close()

    # 3b. Transition from raw v1 schema
    conn_v1 = sqlite3.connect(":memory:")
    conn_v1.execute("PRAGMA foreign_keys = ON;")
    conn_v1.execute("CREATE TABLE nodes (id TEXT PRIMARY KEY, type TEXT NOT NULL, name TEXT NOT NULL, data TEXT NOT NULL);")
    conn_v1.execute("CREATE TABLE edges (source_id TEXT NOT NULL, target_id TEXT NOT NULL, type TEXT NOT NULL, confidence REAL, provenance TEXT, PRIMARY KEY (source_id, target_id, type));")
    conn_v1.execute("CREATE TABLE _schema_migrations (version INTEGER PRIMARY KEY, description TEXT, applied_at TEXT DEFAULT (datetime('now')));")
    conn_v1.execute("INSERT INTO _schema_migrations (version, description) VALUES (1, 'Initial schema');")
    conn_v1.commit()

    run_migrations(conn_v1)
    status_v1 = migration_status(conn_v1)
    v1_transition_ok = len(status_v1) == 4 and all(s["status"] == "applied" for s in status_v1)
    conn_v1.close()

    # 3c. Transition from raw v3 schema (where memory_snapshots exists WITHOUT domain column)
    conn_v3 = sqlite3.connect(":memory:")
    conn_v3.execute("PRAGMA foreign_keys = ON;")
    conn_v3.execute("CREATE TABLE _schema_migrations (version INTEGER PRIMARY KEY, description TEXT, applied_at TEXT DEFAULT (datetime('now')));")
    for v in (1, 2, 3):
        conn_v3.execute("INSERT INTO _schema_migrations (version, description) VALUES (?, ?);", (v, f"v{v}"))
    conn_v3.execute("CREATE TABLE nodes (id TEXT PRIMARY KEY, type TEXT NOT NULL, name TEXT NOT NULL, data TEXT NOT NULL);")
    conn_v3.execute("CREATE TABLE memory_snapshots (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT NOT NULL, snapshot TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT (datetime('now')));")
    conn_v3.execute("INSERT INTO memory_snapshots (session_id, snapshot) VALUES ('v3_session', '{\"key\": \"val\"}');")
    conn_v3.commit()

    run_migrations(conn_v3)
    cursor = conn_v3.cursor()
    cursor.execute("PRAGMA table_info(memory_snapshots);")
    columns = {row[1] for row in cursor.fetchall()}
    has_domain = "domain" in columns

    cursor.execute("SELECT session_id, snapshot, domain FROM memory_snapshots WHERE session_id = 'v3_session';")
    row = cursor.fetchone()
    data_intact = row is not None and row[0] == "v3_session" and row[2] is None
    conn_v3.close()

    # 3d. Concurrent migration execution on fresh file DB
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        concurrent_db = tmp.name

    conc_errors = []
    def migrate_worker():
        try:
            c = sqlite3.connect(concurrent_db, timeout=10.0)
            run_migrations(c)
            c.close()
        except Exception as e:
            conc_errors.append(f"{type(e).__name__}: {str(e)}")

    threads = [threading.Thread(target=migrate_worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    c_verify = sqlite3.connect(concurrent_db)
    status_conc = migration_status(c_verify)
    conc_ok = len(status_conc) == 4 and all(s["status"] == "applied" for s in status_conc) and len(conc_errors) == 0
    c_verify.close()
    if os.path.exists(concurrent_db):
        os.remove(concurrent_db)

    success = v4_applied and v1_transition_ok and has_domain and data_intact and conc_ok
    sample_conc_errors = list(set(conc_errors))[:3]
    details = (
        f"50x sequential re-run: {'OK' if v4_applied else 'FAIL'}. "
        f"v1 legacy transition: {'OK' if v1_transition_ok else 'FAIL'}. "
        f"v3 memory_snapshots domain column ALTER & data integrity: {'OK' if (has_domain and data_intact) else 'FAIL'}. "
        f"10-thread concurrent migration trigger: {'OK' if conc_ok else 'FAIL'} (errors: {len(conc_errors)}, samples: {sample_conc_errors})."
    )
    return success, details

# ─────────────────────────────────────────────────────────────────────────────
# MAIN STRESS HARNESS ENTRYPOINT
# ─────────────────────────────────────────────────────────────────────────────
def main():
    runner = StressTestRunner()
    
    # Run 1: Concurrency
    s1, d1 = test_sqlite_concurrency()
    runner.report("SQLite Concurrency Stress", s1, d1)

    # Run 2: Cascade Delete Stress
    s2, d2 = test_bulk_cascade_delete()
    runner.report("Bulk FK Cascade Delete Stress", s2, d2)

    # Run 3: Migration Idempotency
    s3, d3 = test_migration_idempotency_and_legacy()
    runner.report("Migration Idempotency & Legacy Transition", s3, d3)

    all_passed = all(r["success"] for r in runner.results.values())
    print("\n=======================================================")
    print(f"EMPIRICAL STRESS TEST SUITE VERDICT: {'ALL PASSED' if all_passed else 'FAILURE DETECTED'}")
    print("=======================================================")
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
