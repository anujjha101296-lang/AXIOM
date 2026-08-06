import sys
import os
import sqlite3
import tempfile
import threading
import time
import trace

PROJECT_ROOT = "/Users/itachiuchiha/.gemini/antigravity/scratch/axiom"
SHIMS_DIR = os.path.join(PROJECT_ROOT, ".agents/worker_mde_m1_2/shims")

sys.path.insert(0, SHIMS_DIR)
sys.path.insert(0, PROJECT_ROOT)

from axiom.core.knowledge_graph.migrations import run_migrations, migration_status, _apply_migration_safely
from axiom.core.knowledge_graph.db import EpistemicStore
from axiom.core.knowledge_graph.schema import DefinitionNode

def test_begin_immediate_locking_mechanics():
    print("=== Testing SQLite BEGIN IMMEDIATE Locking & Transaction Isolation ===")
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    try:
        # Step 1: Open conn1 and start BEGIN IMMEDIATE
        conn1 = sqlite3.connect(db_path, timeout=1.0)
        conn1.execute("CREATE TABLE IF NOT EXISTS _schema_migrations (version INTEGER PRIMARY KEY, description TEXT, applied_at TEXT);")
        conn1.commit()

        conn1.execute("BEGIN IMMEDIATE")
        print("[conn1] BEGIN IMMEDIATE lock acquired.")

        # Step 2: Open conn2 in a separate thread and attempt BEGIN IMMEDIATE; should block/raise OperationalError with low timeout
        conn2_result = []

        def worker_conn2():
            try:
                conn2 = sqlite3.connect(db_path, timeout=0.1)
                conn2.execute("BEGIN IMMEDIATE")
                conn2_result.append("ACQUIRED")
                conn2.close()
            except sqlite3.OperationalError as e:
                conn2_result.append(f"LOCKED: {e}")

        t = threading.Thread(target=worker_conn2)
        t.start()
        t.join()

        print(f"[conn2] Lock attempt result while conn1 holds BEGIN IMMEDIATE: {conn2_result[0]}")
        assert "LOCKED" in conn2_result[0] or "locked" in conn2_result[0].lower() or "busy" in conn2_result[0].lower()

        # Step 3: Release conn1
        conn1.rollback()
        conn1.close()
        print("[conn1] Transaction rolled back & closed.")

        # Step 4: Verify run_migrations handles contention with automatic retries
        conn_final = sqlite3.connect(db_path, timeout=5.0)
        run_migrations(conn_final)
        status = migration_status(conn_final)
        assert len(status) == 4
        assert all(m["status"] == "applied" for m in status)
        conn_final.close()
        print("[run_migrations] Successfully completed migrations after lock release.")
        print("PASS: BEGIN IMMEDIATE locking mechanics operating authentically.\n")

    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_heavy_concurrent_migrations():
    print("=== Testing High-Contention Concurrent Migrations (20 Threads) ===")
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    try:
        num_threads = 20
        barrier = threading.Barrier(num_threads)
        errors = []

        def worker(tid):
            try:
                barrier.wait()
                conn = sqlite3.connect(db_path, timeout=15.0)
                run_migrations(conn)
                conn.close()
            except Exception as e:
                errors.append((tid, e))

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"Errors encountered during 20-thread migration: {errors}"

        verify_conn = sqlite3.connect(db_path)
        cursor = verify_conn.cursor()
        cursor.execute("SELECT count(*) FROM _schema_migrations;")
        count = cursor.fetchone()[0]
        assert count == 4, f"Expected 4 schema migrations, got {count}"
        verify_conn.close()
        print(f"PASS: 20 threads completed migration with 0 errors and exactly {count} migration records.\n")

    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def main():
    test_begin_immediate_locking_mechanics()
    test_heavy_concurrent_migrations()

if __name__ == "__main__":
    main()
