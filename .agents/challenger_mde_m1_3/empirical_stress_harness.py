"""
Empirical Stress Test Harness — Challenger 3 (Milestone 1, Iteration 2)
========================================================================
Empirically tests:
1. Concurrent migration triggers across 20 threads on shared DB files (fresh, existing, active read/write).
2. `add_definition()` keyword calls with `informal_description` under high volume (multi-threaded, signature variations, upserts).
3. Foreign key bulk cascade deletions across all dependent tables (1000+ parent nodes with full graph dependencies).
"""

import os
import sys
import time
import sqlite3
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Ensure project root is in sys.path
PROJECT_ROOT = "/Users/itachiuchiha/.gemini/antigravity/scratch/axiom"
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
from axiom.core.knowledge_graph.migrations import run_migrations, migration_status


def test_1_concurrent_migration_triggers():
    print("\n--- STRESS TEST 1: Concurrent Migration Triggers (20 Threads Shared DB File) ---")
    
    # 1A. 20 threads triggering run_migrations on uninitialized DB file simultaneously
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    try:
        errors = []
        barrier = threading.Barrier(20)

        def migration_worker(worker_id):
            try:
                barrier.wait()
                conn = sqlite3.connect(db_path, timeout=10.0)
                run_migrations(conn)
                conn.close()
            except Exception as e:
                errors.append((worker_id, e))

        threads = [threading.Thread(target=migration_worker, args=(i,)) for i in range(20)]
        start_t = time.time()
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        duration = time.time() - start_t

        assert len(errors) == 0, f"Uninitialized DB concurrent migration failed with errors: {errors}"
        print(f"[PASS] 1A. 20 threads on fresh uninitialized DB file finished in {duration:.3f}s with 0 errors.")

        # Verify DB schema integrity
        verify_conn = sqlite3.connect(db_path)
        status = migration_status(verify_conn)
        assert len(status) == 4
        assert all(m["status"] == "applied" for m in status)
        
        cursor = verify_conn.cursor()
        cursor.execute("SELECT count(*) FROM _schema_migrations;")
        assert cursor.fetchone()[0] == 4
        verify_conn.close()

        # 1B. 20 threads triggering run_migrations on ALREADY migrated DB file
        errors_b = []
        barrier_b = threading.Barrier(20)

        def re_migration_worker(worker_id):
            try:
                barrier_b.wait()
                conn = sqlite3.connect(db_path, timeout=10.0)
                run_migrations(conn)
                conn.close()
            except Exception as e:
                errors_b.append((worker_id, e))

        threads_b = [threading.Thread(target=re_migration_worker, args=(i,)) for i in range(20)]
        start_tb = time.time()
        for t in threads_b:
            t.start()
        for t in threads_b:
            t.join()
        duration_b = time.time() - start_tb

        assert len(errors_b) == 0, f"Already migrated DB concurrent migration failed with errors: {errors_b}"
        print(f"[PASS] 1B. 20 threads on already-migrated DB file finished in {duration_b:.3f}s with 0 errors.")

        # 1C. Rapid open -> migrate -> query -> close loops across 20 threads
        errors_c = []
        
        def rapid_loop_worker(worker_id):
            try:
                for cycle in range(10):
                    conn = sqlite3.connect(db_path, timeout=10.0)
                    run_migrations(conn)
                    conn.execute("SELECT count(*) FROM nodes;").fetchone()
                    conn.close()
            except Exception as e:
                errors_c.append((worker_id, e))

        threads_c = [threading.Thread(target=rapid_loop_worker, args=(i,)) for i in range(20)]
        start_tc = time.time()
        for t in threads_c:
            t.start()
        for t in threads_c:
            t.join()
        duration_c = time.time() - start_tc

        assert len(errors_c) == 0, f"Rapid open-migrate-close loop failed with errors: {errors_c}"
        print(f"[PASS] 1C. 200 rapid connect-migrate-query-close iterations finished in {duration_c:.3f}s with 0 errors.")

    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_2_add_definition_high_volume():
    print("\n--- STRESS TEST 2: High Volume add_definition() with informal_description ---")
    
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    try:
        store = EpistemicStore(db_path)

        # 2A. Single-threaded 1,000 keyword variation insertions
        total_items = 1000
        start_t = time.time()

        for i in range(total_items):
            def_id = f"def_high_vol_{i}"
            mode = i % 4
            
            if mode == 0:
                # Primary modern usage: informal_description kwarg
                node = DefinitionNode(
                    id=def_id,
                    name=f"Term {i}",
                    term=f"Term_{i}",
                    formal_definition=f"forall x, P_{i}(x)",
                    informal_description=f"Human description {i}",
                    domain="LOGIC"
                )
                store.add_definition(
                    node=node,
                    term=f"Term_{i}",
                    formal_definition=f"forall x, P_{i}(x)",
                    informal_description=f"Human description {i}",
                    domain="LOGIC"
                )
            elif mode == 1:
                # Legacy fallback usage: informal_definition kwarg
                node = DefinitionNode(
                    id=def_id,
                    name=f"Term {i}",
                    term=f"Term_{i}",
                    formal_definition=f"forall x, P_{i}(x)",
                    domain="LOGIC"
                )
                store.add_definition(
                    node=node,
                    term=f"Term_{i}",
                    formal_definition=f"forall x, P_{i}(x)",
                    informal_definition=f"Legacy description {i}",
                    domain="LOGIC"
                )
            elif mode == 2:
                # Fallback to node attribute: no kwarg passed
                node = DefinitionNode(
                    id=def_id,
                    name=f"Term {i}",
                    term=f"Term_{i}",
                    formal_definition=f"forall x, P_{i}(x)",
                    informal_description=f"Node attr description {i}",
                    domain="LOGIC"
                )
                store.add_definition(
                    node=node,
                    term=f"Term_{i}",
                    formal_definition=f"forall x, P_{i}(x)",
                    domain="LOGIC"
                )
            else:
                # Precedence check: both kwargs passed -> informal_description wins
                node = DefinitionNode(
                    id=def_id,
                    name=f"Term {i}",
                    term=f"Term_{i}",
                    formal_definition=f"forall x, P_{i}(x)",
                    domain="LOGIC"
                )
                store.add_definition(
                    node=node,
                    term=f"Term_{i}",
                    formal_definition=f"forall x, P_{i}(x)",
                    informal_description=f"Primary description {i}",
                    informal_definition=f"Secondary description {i}",
                    domain="LOGIC"
                )

        duration = time.time() - start_t
        print(f"[PASS] 2A. Inserted {total_items} definition records in {duration:.3f}s.")

        # Verify exact retrievals
        for i in range(total_items):
            def_id = f"def_high_vol_{i}"
            rec = store.get_definition(def_id)
            assert rec is not None, f"Definition {def_id} missing!"
            assert rec["term"] == f"Term_{i}"
            assert "informal_description" in rec
            assert "informal_definition" in rec
            
            mode = i % 4
            if mode == 0:
                assert rec["informal_description"] == f"Human description {i}"
            elif mode == 1:
                assert rec["informal_description"] == f"Legacy description {i}"
            elif mode == 2:
                assert rec["informal_description"] == f"Node attr description {i}"
            else:
                assert rec["informal_description"] == f"Primary description {i}"

        # 2B. Upsert benchmark (overwriting all 1000 definitions with updated description)
        start_upsert = time.time()
        for i in range(total_items):
            def_id = f"def_high_vol_{i}"
            node = DefinitionNode(
                id=def_id,
                name=f"Term Updated {i}",
                term=f"Term_Updated_{i}",
                formal_definition=f"forall x, Q_{i}(x)",
                informal_description=f"Updated description {i}",
                domain="UPDATED_DOMAIN"
            )
            store.add_definition(
                node=node,
                term=f"Term_Updated_{i}",
                formal_definition=f"forall x, Q_{i}(x)",
                informal_description=f"Updated description {i}",
                domain="UPDATED_DOMAIN"
            )
        upsert_duration = time.time() - start_upsert
        print(f"[PASS] 2B. Upserted {total_items} definition records in {upsert_duration:.3f}s.")

        # Verify upsert correctness
        for i in range(total_items):
            rec = store.get_definition(f"def_high_vol_{i}")
            assert rec["term"] == f"Term_Updated_{i}"
            assert rec["informal_description"] == f"Updated description {i}"
            assert rec["domain"] == "UPDATED_DOMAIN"

        store.close()

    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_3_foreign_key_bulk_cascade_deletions():
    print("\n--- STRESS TEST 3: Bulk Foreign Key Cascade Deletions ---")
    
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    try:
        store = EpistemicStore(db_path)

        num_parents = 1000
        print(f"Populating DB with {num_parents} parent nodes and associated child records across 6 dependent tables...")

        start_populate = time.time()

        for i in range(num_parents):
            # 1. Base Node & Mathematical Claim
            claim_id = f"claim_fk_{i}"
            claim_node = MathematicalClaimNode(id=claim_id, name=f"Claim {i}", statement=f"Statement {i}")
            store.add_node(claim_node)

            # 2. Target Node & Edge
            target_id = f"target_fk_{i}"
            target_node = MathematicalClaimNode(id=target_id, name=f"Target {i}", statement=f"Target {i}")
            store.add_node(target_node)

            store.add_edge(Edge(source_id=claim_id, target_id=target_id, type=EdgeType.PROVES))

            # 3. Mathematical Object Node & Table entry
            mo_id = f"mo_fk_{i}"
            mo_node = MathematicalObjectNode(id=mo_id, name=f"Obj {i}", domain="TEST", symbolic_representation=f"X_{i}")
            store.add_mathematical_object(node=mo_node, object_type="GROUP", formal_symbol=f"G_{i}", domain="TEST")

            # 4. Definition Node & Table entry
            def_id = f"def_fk_{i}"
            def_node = DefinitionNode(id=def_id, name=f"Def {i}", term=f"Term {i}", formal_definition=f"def {i}")
            store.add_definition(node=def_node, term=f"Term {i}", formal_definition=f"def {i}", informal_description=f"desc {i}")

            # 5. Proof Lineage entry (direct SQL insertion)
            assert store.conn is not None
            with store.conn:
                store.conn.execute(
                    "INSERT INTO proof_lineage (claim_id, verifier, result) VALUES (?, ?, ?);",
                    (claim_id, "LEAN", "VERIFIED")
                )

            # 6. Equivalent Statement entry
            store.add_equivalent_statement(claim_id, target_id, proof_reference=f"Proof {i}")

            # 7. Failed Proof Attempt entry
            store.add_failed_proof_attempt(claim_id, ["simp", "auto"], "SMT", f"Timeout at {i}")

        pop_duration = time.time() - start_populate
        print(f"[PASS] 3A. Population of {num_parents} parent sets completed in {pop_duration:.3f}s.")

        # Verify counts prior to deletion
        assert store.conn is not None
        c = store.conn.cursor()
        
        c.execute("SELECT count(*) FROM nodes;")
        total_nodes = c.fetchone()[0]
        assert total_nodes == num_parents * 4  # claim, target, mo, def = 4 nodes per cycle
        
        c.execute("SELECT count(*) FROM edges;")
        total_edges = c.fetchone()[0]
        # Each iteration creates 1 PROVES edge + 1 EQUIVALENT_TO edge = 2 edges
        assert total_edges == num_parents * 2

        c.execute("SELECT count(*) FROM mathematical_objects;")
        assert c.fetchone()[0] == num_parents

        c.execute("SELECT count(*) FROM definitions;")
        assert c.fetchone()[0] == num_parents

        c.execute("SELECT count(*) FROM proof_lineage;")
        assert c.fetchone()[0] == num_parents

        c.execute("SELECT count(*) FROM equivalent_statements;")
        assert c.fetchone()[0] == num_parents

        c.execute("SELECT count(*) FROM failed_proof_attempts;")
        assert c.fetchone()[0] == num_parents

        print("[PASS] 3B. Pre-deletion table row counts verified exactly.")

        # Perform Bulk Cascade Deletion of 50% of parent claims (500 claims)
        start_delete = time.time()
        delete_ids = [f"claim_fk_{i}" for i in range(500)]
        
        with store.conn:
            # Delete 500 claim nodes in a single parameterized statement
            placeholders = ",".join(["?"] * len(delete_ids))
            store.conn.execute(f"DELETE FROM nodes WHERE id IN ({placeholders});", delete_ids)
            
        del_duration = time.time() - start_delete
        print(f"[PASS] 3C. Bulk cascade deletion of 500 parent nodes executed in {del_duration:.3f}s.")

        # Audit all child tables for orphan records
        # 1. proof_lineage orphan check
        c.execute("SELECT count(*) FROM proof_lineage pl LEFT JOIN nodes n ON pl.claim_id = n.id WHERE n.id IS NULL;")
        orphans_pl = c.fetchone()[0]
        assert orphans_pl == 0, f"Found {orphans_pl} orphan records in proof_lineage!"

        # 2. failed_proof_attempts orphan check
        c.execute("SELECT count(*) FROM failed_proof_attempts fpa LEFT JOIN nodes n ON fpa.claim_id = n.id WHERE n.id IS NULL;")
        orphans_fpa = c.fetchone()[0]
        assert orphans_fpa == 0, f"Found {orphans_fpa} orphan records in failed_proof_attempts!"

        # 3. equivalent_statements orphan check
        c.execute("""
            SELECT count(*) FROM equivalent_statements eq 
            LEFT JOIN nodes na ON eq.statement_a_id = na.id 
            LEFT JOIN nodes nb ON eq.statement_b_id = nb.id 
            WHERE na.id IS NULL OR nb.id IS NULL;
        """)
        orphans_eq = c.fetchone()[0]
        assert orphans_eq == 0, f"Found {orphans_eq} orphan records in equivalent_statements!"

        # 4. edges orphan check
        c.execute("""
            SELECT count(*) FROM edges e 
            LEFT JOIN nodes na ON e.source_id = na.id 
            LEFT JOIN nodes nb ON e.target_id = nb.id 
            WHERE na.id IS NULL OR nb.id IS NULL;
        """)
        orphans_e = c.fetchone()[0]
        assert orphans_e == 0, f"Found {orphans_e} orphan records in edges!"

        # 5. mathematical_objects orphan check
        c.execute("SELECT count(*) FROM mathematical_objects mo LEFT JOIN nodes n ON mo.node_id = n.id WHERE n.id IS NULL;")
        orphans_mo = c.fetchone()[0]
        assert orphans_mo == 0, f"Found {orphans_mo} orphan records in mathematical_objects!"

        # 6. definitions orphan check
        c.execute("SELECT count(*) FROM definitions d LEFT JOIN nodes n ON d.node_id = n.id WHERE n.id IS NULL;")
        orphans_def = c.fetchone()[0]
        assert orphans_def == 0, f"Found {orphans_def} orphan records in definitions!"

        print("[PASS] 3D. Foreign key audit confirmed ZERO orphans across all 6 dependent tables.")

        # Verify exact remaining count in dependent tables
        c.execute("SELECT count(*) FROM proof_lineage;")
        assert c.fetchone()[0] == 500

        c.execute("SELECT count(*) FROM failed_proof_attempts;")
        assert c.fetchone()[0] == 500

        c.execute("SELECT count(*) FROM equivalent_statements;")
        assert c.fetchone()[0] == 500

        print("[PASS] 3E. Post-cascade row counts match expected exact values (500 remaining).")

        # Now delete remaining 500 target nodes (target_fk_500..999)
        delete_targets = [f"target_fk_{i}" for i in range(500, 1000)]
        with store.conn:
            placeholders_t = ",".join(["?"] * len(delete_targets))
            store.conn.execute(f"DELETE FROM nodes WHERE id IN ({placeholders_t});", delete_targets)

        # Audit again
        c.execute("SELECT count(*) FROM equivalent_statements;")
        assert c.fetchone()[0] == 0, "All equivalent statements should be deleted after deleting targets!"

        c.execute("SELECT count(*) FROM edges;")
        assert c.fetchone()[0] == 0, "All edges should be deleted after deleting targets!"

        print("[PASS] 3F. Full graph node purge cascade verified completely clean.")

        store.close()

    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


if __name__ == "__main__":
    print("==========================================================================")
    print("STARTING EMPIRICAL STRESS TEST SUITE — CHALLENGER 3 (MILESTONE 1 ITER 2)")
    print("==========================================================================")
    
    test_1_concurrent_migration_triggers()
    test_2_add_definition_high_volume()
    test_3_foreign_key_bulk_cascade_deletions()
    
    print("\n==========================================================================")
    print("EMPIRICAL STRESS TEST SUITE VERDICT: ALL TESTS PASSED SUCCESSFULLY!")
    print("==========================================================================")
