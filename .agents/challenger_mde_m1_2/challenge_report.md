# Challenge Report: EGS Mathematical Ontology & Database Migrations (Milestone 1)

**Agent:** Challenger 2 (`challenger_mde_m1_2`) — Empirical Challenger  
**Working Directory:** `/Users/itachiuchiha/.gemini/antigravity/scratch/axiom/.agents/challenger_mde_m1_2`  
**Target:** Milestone 1 (EGS Mathematical Ontology & Database Migrations)  
**Date:** 2026-08-05  
**Final Verdict:** `REQUEST_CHANGES`

---

## 1. Challenge Summary

**Overall Risk Assessment:** **MEDIUM**

While the core SQLite schema DDL, foreign key cascade behavior, and basic unit test suite pass cleanly, empirical stress testing revealed two key issues:
1. **Concurrent Migration Race Condition (`IntegrityError` / `OperationalError`)**: Concurrent execution of `run_migrations()` across multiple threads/processes causes primary key collisions on `_schema_migrations.version` and database locking errors.
2. **API Parameter Naming Inconsistency (`TypeError`)**: `DefinitionNode` in `schema.py` defines `informal_description`, whereas `EpistemicStore.add_definition()` in `db.py` names its parameter `informal_definition`.

---

## 2. Challenges & Findings

### [High] Challenge 1: Concurrent `run_migrations()` Execution Race Condition

- **Assumption Challenged:** `run_migrations(conn)` assumes single-threaded, sequential database initialization.
- **Attack Scenario:** When multiple application threads or worker processes instantiate `EpistemicStore(db_path)` simultaneously on startup (a common multi-worker/server scenario), each instance calls `run_migrations(self.conn)`. Threads read `_applied_versions()` concurrently, detect pending migrations, and attempt to insert identical version numbers into `_schema_migrations`.
- **Observed Empirical Failure:**
  ```text
  sqlite3.IntegrityError: UNIQUE constraint failed: _schema_migrations.version
  sqlite3.OperationalError: database is locked
  ```
- **Blast Radius:** System crash or uncaught database exception on multi-worker application startup.
- **Mitigation:**
  - Wrap `run_migrations` steps in `BEGIN IMMEDIATE;` or use `INSERT OR IGNORE INTO _schema_migrations` when recording applied migrations.
  - Alternatively, acquire an explicit file lock or handle `IntegrityError` / `OperationalError` by re-checking `_applied_versions()`.

---

### [Medium] Challenge 2: Parameter Naming Mismatch (`informal_description` vs `informal_definition`)

- **Assumption Challenged:** Function signatures in `db.py` match model field definitions in `schema.py`.
- **Attack Scenario:** Standard callers passing `DefinitionNode.informal_description` to `EpistemicStore.add_definition(..., informal_description=...)` encounter a runtime `TypeError`.
- **Observed Empirical Failure:**
  ```text
  TypeError: EpistemicStore.add_definition() got an unexpected keyword argument 'informal_description'
  ```
- **Blast Radius:** Callers using keyword arguments matching the Pydantic schema model fail at runtime.
- **Mitigation:** Standardize parameter naming in `EpistemicStore.add_definition()` to `informal_description` to match `DefinitionNode.informal_description`.

---

## 3. Stress Test Results Summary

An empirical stress script (`db_stress.py`) was executed to evaluate SQLite concurrency, foreign key cascade integrity, and migration idempotency.

| Test Scenario | Description | Verdict | Details / Empirical Output |
|---|---|---|---|
| **Unit Test Suite** | Full suite `pytest tests/test_mde_ontology.py -v` | **PASS** | 16/16 unit tests passed cleanly. |
| **SQLite Concurrency Stress** | 500 transactions across 10 concurrent threads inserting into all 5 v4 tables (`mathematical_objects`, `definitions`, `equivalent_statements`, `memory_snapshots`, `failed_proof_attempts`) | **PASS** | Completed in 0.75s with WAL mode enabled. Row counts verified: 500 math objects, 500 definitions, 500 equivalent statements, 500 snapshots, 500 failed proof attempts. |
| **Bulk FK Cascade Delete Stress** | Inserted 500 parent nodes and child records across 5 tables; bulk deleted 250 parent nodes via `DELETE FROM nodes WHERE id IN (...)` | **PASS** | Remaining claims: 250. Zero orphan records detected (`orphan_mo: 0, orphan_def: 0, orphan_eq: 0, orphan_failed: 0, orphan_edges: 0`). |
| **Sequential Migration Idempotency** | Executed `run_migrations` 50 consecutive times | **PASS** | All migrations skipped cleanly; schema version remained 4. |
| **Legacy Schema Transition (v1 -> v4)** | Applied `run_migrations` to raw v1 schema (nodes + edges) | **PASS** | Applied v2, v3, v4 successfully in order. |
| **Legacy Schema Transition (v3 -> v4)** | Applied `run_migrations` to raw v3 schema (`memory_snapshots` without `domain` column) | **PASS** | Safely executed `ALTER TABLE memory_snapshots ADD COLUMN domain TEXT;` preserving pre-existing snapshot data. |
| **Concurrent Migration Trigger** | 10 concurrent threads invoking `run_migrations` on fresh file database | **FAIL** | Failed with `IntegrityError: UNIQUE constraint failed: _schema_migrations.version` and `OperationalError: database is locked`. |

---

## 4. Unchallenged Areas

- **NetworkX Performance at Scale (100k+ nodes)**: Tested NetworkX conversion for small to medium graphs (~1,000 nodes); extreme scale benchmarks (100k+ nodes) left for M2 integration benchmarks.

---

## 5. Required Action Items for Worker / Sub-Orchestrator

1. **Fix `run_migrations` Concurrency Safety in `axiom/core/knowledge_graph/migrations.py`**:
   Use `INSERT OR IGNORE INTO _schema_migrations` or transaction-level lock handling (`BEGIN IMMEDIATE`) to prevent concurrent version insertion conflicts.
2. **Align `EpistemicStore.add_definition` Signature in `axiom/core/knowledge_graph/db.py`**:
   Change parameter name `informal_definition` to `informal_description` (or accept `informal_description` as alias) to match `DefinitionNode` field in `schema.py`.
