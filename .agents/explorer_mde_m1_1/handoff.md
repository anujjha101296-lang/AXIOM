# Handoff Report: EGS Mathematical Ontology & v4 Database Migration Design

**Agent:** Explorer 1 (Milestone 1 — EGS Mathematical Ontology & Database Migrations)  
**Working Directory:** `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/explorer_mde_m1_1`  
**Target Files:** `axiom/core/knowledge_graph/migrations.py`, `axiom/core/knowledge_graph/db.py`, `axiom/core/knowledge_graph/schema.py`  
**Date:** 2026-08-05  

---

## 1. Observation

1. **Migration Architecture in `axiom/core/knowledge_graph/migrations.py`:**
   - Lines 25–33: `_create_migration_table(conn)` initializes `_schema_migrations (version INTEGER PRIMARY KEY, description TEXT NOT NULL, applied_at TEXT NOT NULL DEFAULT (datetime('now')))`.
   - Lines 36–38: `_applied_versions(conn)` queries `SELECT version FROM _schema_migrations`.
   - Lines 43–118: Existing migration functions:
     - `_v1_initial_schema`: Creates `nodes`, `edges` tables and indices `idx_nodes_type`, `idx_edges_source`, `idx_edges_target`.
     - `_v2_proof_lineage`: Creates `proof_lineage` table and indices `idx_lineage_claim_id`, `idx_lineage_verifier`.
     - `_v3_working_memory_snapshots`: Creates `memory_snapshots` table and index `idx_snapshots_session`.
   - Lines 114–118: `MIGRATIONS` registry currently contains:
     ```python
     MIGRATIONS: List[Migration] = [
         (1, "Initial schema: nodes + edges",         _v1_initial_schema),
         (2, "Add proof_lineage table",               _v2_proof_lineage),
         (3, "Add memory_snapshots table",            _v3_working_memory_snapshots),
     ]
     ```
   - Lines 121–140: `run_migrations(conn)` executes `PRAGMA foreign_keys = ON;`, runs unapplied migrations in version sequence, records entries in `_schema_migrations`, and commits.

2. **Schema & DB Layer Context:**
   - In `axiom/core/knowledge_graph/schema.py` (lines 5–21), current node types include `PAPER`, `AUTHOR`, `CONCEPT`, `MATHEMATICAL_CLAIM`, `EXPERIMENTAL_FACT`, `DATASET`.
   - In `axiom/core/knowledge_graph/db.py` (lines 28–53), `EpistemicStore._init_db()` currently initializes `nodes` and `edges` inline using `CREATE TABLE IF NOT EXISTS`.

3. **Requirements for Milestone 1 v4 Migration:**
   - As specified in `PROJECT.md` (lines 20, 46) and `SCOPE.md` (lines 5, 9), `v4_mathematical_ontology` must create 5 tables:
     - `mathematical_objects`
     - `definitions`
     - `equivalent_statements`
     - `memory_snapshots`
     - `failed_proof_attempts`

---

## 2. Logic Chain

1. **Observation Ref 1 & 3:** The existing migration mechanism in `migrations.py` is versioned and idempotent. Adding `(4, "Mathematical ontology & memory schema", _v4_mathematical_ontology)` to `MIGRATIONS` ensures automatic execution when `run_migrations(conn)` is called.
2. **Observation Ref 1 & 2:** Tables extending `nodes` (`mathematical_objects`, `definitions`, `equivalent_statements`, `failed_proof_attempts`) require foreign key constraints pointing to `nodes(id)` with `ON DELETE CASCADE`. This ensures relational integrity when parent graph nodes are removed.
3. **Observation Ref 1:** `memory_snapshots` was created in `_v3_working_memory_snapshots` with `(id, session_id, snapshot, created_at)`. In `_v4_mathematical_ontology`, using `CREATE TABLE IF NOT EXISTS memory_snapshots` alongside an `ALTER TABLE memory_snapshots ADD COLUMN domain TEXT;` column check guarantees seamless backwards compatibility whether v3 was previously run or not.
4. **Observation Ref 3:** `equivalent_statements` requires dual foreign keys (`statement_a_id`, `statement_b_id`) referencing `nodes(id)` and a unique composite index on `(statement_a_id, statement_b_id, equivalence_type)` to eliminate duplicate equivalence declarations.
5. **Observation Ref 3:** `failed_proof_attempts` requires indexing on `(claim_id, verifier)` to optimize tactic failure lookup during MCTS search tree expansion and pruning.

---

## 3. Caveats

- **SQLite In-Memory Connections:** In-memory databases (`:memory:`) exist only while the connection is open. Unit tests and database initializations must call `run_migrations(conn)` on active connection objects.
- **FK Enforcement:** SQLite foreign keys are disabled by default per session unless `PRAGMA foreign_keys = ON;` is explicitly executed on the connection. `run_migrations(conn)` handles this at start.
- **Pydantic Model Co-dependence:** Implementers must ensure `MathematicalObjectNode`, `DefinitionNode`, `OpenProblemNode`, and `ConjectureNode` are added to `schema.py` and included in `ScientificNode` Union so that `EpistemicStore.get_node()` deserialization operates smoothly alongside the DB tables.

---

## 4. Conclusion

The `v4_mathematical_ontology` migration design is fully specified, idempotent, and ready for implementation in `axiom/core/knowledge_graph/migrations.py`. It adds the required 5 tables (`mathematical_objects`, `definitions`, `equivalent_statements`, `memory_snapshots`, `failed_proof_attempts`) with complete primary keys, foreign keys (`ON DELETE CASCADE`), indices, and backwards compatibility safeguards.

---

## 5. Verification Method

1. **Detailed Analysis Location:**
   - `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/explorer_mde_m1_1/analysis.md`

2. **Automated Test Execution Command:**
   ```bash
   pytest /Users/itachiuchiha/.gemini/antigravity/scratch/axiom/tests/test_mde_ontology.py -v
   ```

3. **Manual SQL Schema Verification:**
   Run Python interactive check or pytest assertion:
   ```python
   import sqlite3
   from axiom.core.knowledge_graph.migrations import run_migrations, migration_status
   conn = sqlite3.connect(":memory:")
   run_migrations(conn)
   cursor = conn.cursor()
   cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
   tables = {row[0] for row in cursor.fetchall()}
   assert {"mathematical_objects", "definitions", "equivalent_statements", "memory_snapshots", "failed_proof_attempts"}.issubset(tables)
   ```

4. **Invalidation Conditions:**
   - Failure of `run_migrations(conn)` to create all 5 tables in a fresh SQLite database.
   - Any `sqlite3.OperationalError` or `sqlite3.IntegrityError` when executing `run_migrations` idempotently.
