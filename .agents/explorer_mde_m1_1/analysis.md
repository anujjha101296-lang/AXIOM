# Analysis: EGS Mathematical Ontology & v4 Database Migration Design

**Author:** Explorer 1 (Milestone 1 — EGS Mathematical Ontology & Database Migrations)  
**Target Files:** `axiom/core/knowledge_graph/migrations.py`, `axiom/core/knowledge_graph/db.py`, `axiom/core/knowledge_graph/schema.py`  
**Date:** 2026-08-05  

---

## Executive Summary

This report delivers the complete architectural investigation and DDL design for the `v4_mathematical_ontology` database migration in `axiom/core/knowledge_graph/migrations.py`. 

The AXIOM Epistemic Graph Store (EGS) uses versioned, idempotent SQLite migrations managed via the `_schema_migrations` table and executed through `run_migrations(conn)`. Existing migrations cover core nodes and edges (v1), proof lineage tracking (v2), and basic working memory snapshots (v3). 

To support the Mathematical Discovery Engine (MDE) requirements (R1, R8), the `v4_mathematical_ontology` migration introduces five core relational tables:
1. `mathematical_objects`: Domain entities (numbers, groups, rings, zeta zeros, operators) linked to EGS core nodes.
2. `definitions`: Formal (Lean 4/Isabelle/Coq) and informal mathematical definitions.
3. `equivalent_statements`: Bi-directional mathematical claim equivalence tracking (e.g., Riemann Hypothesis equivalences).
4. `memory_snapshots`: Enhanced working memory persistence for cross-session research state.
5. `failed_proof_attempts`: Tactic failure history for MCTS proof search pruning.

---

## 1. Existing Migration Architecture & SQLite Schema Review

### 1.1 Migration Runner Mechanism (`migrations.py`)
- **Version Tracking Table (`_schema_migrations`):**
  ```sql
  CREATE TABLE IF NOT EXISTS _schema_migrations (
      version     INTEGER PRIMARY KEY,
      description TEXT    NOT NULL,
      applied_at  TEXT    NOT NULL DEFAULT (datetime('now'))
  );
  ```
- **Execution Flow (`run_migrations`):**
  1. Executes `PRAGMA foreign_keys = ON;` to enforce relational integrity.
  2. Ensures `_schema_migrations` exists via `_create_migration_table(conn)`.
  3. Queries `SELECT version FROM _schema_migrations` to retrieve set of applied migration IDs.
  4. Iterates sequentially through the ordered `MIGRATIONS` registry: `List[Tuple[int, str, Callable[[sqlite3.Connection], None]]]`.
  5. Executes any pending migration functions, inserts recorded version into `_schema_migrations`, and commits transaction.

### 1.2 Existing Migrations Breakdown

| Version | Migration Function | Description & Created Tables | Key Columns & Foreign Keys |
| :--- | :--- | :--- | :--- |
| **v1** | `_v1_initial_schema` | Core graph schema: `nodes`, `edges` | `nodes(id PK, type, name, data)`, `edges(source_id FK, target_id FK, type, confidence, provenance)`. FKs ON DELETE CASCADE to `nodes(id)`. |
| **v2** | `_v2_proof_lineage` | Proof verification tracking: `proof_lineage` | `id PK AUTOINCREMENT`, `claim_id FK -> nodes(id) ON DELETE CASCADE`, `verifier`, `result`, `tactic_used`, `duration_ms`. |
| **v3** | `_v3_working_memory_snapshots` | Working memory snapshots: `memory_snapshots` | `id PK AUTOINCREMENT`, `session_id`, `snapshot (JSON)`, `created_at`. |

---

## 2. DDL & Schema Specification for `v4_mathematical_ontology`

The `v4_mathematical_ontology` migration creates 5 relational tables to support MDE domain entities, formal definitions, equivalent claims, working memory, and MCTS failure pruning.

### 2.1 Table Specifications

#### 1. `mathematical_objects`
Extends EGS nodes with formal mathematical object metadata (groups, rings, fields, zeta zeros, functions).
- **Columns:**
  - `id`: `TEXT PRIMARY KEY` — Unique object identifier (matches `nodes.id`).
  - `node_id`: `TEXT NOT NULL` — Foreign key referencing `nodes(id) ON DELETE CASCADE`.
  - `object_type`: `TEXT NOT NULL` — Category (e.g. `'NUMBER'`, `'GROUP'`, `'RING'`, `'FIELD'`, `'FUNCTION'`, `'ZETA_ZERO'`, `'OPERATOR'`).
  - `formal_symbol`: `TEXT` — LaTeX or formal symbol (e.g. `\zeta(s)`, `\mathbb{Z}`).
  - `domain`: `TEXT NOT NULL` — Mathematical domain (e.g. `'ANALYTIC_NUMBER_THEORY'`, `'ALGEBRA'`).
  - `properties_json`: `TEXT` — JSON metadata blob storing invariants, attributes, and bounds.
  - `created_at`: `TEXT NOT NULL DEFAULT (datetime('now'))`
- **Foreign Key:** `FOREIGN KEY (node_id) REFERENCES nodes(id) ON DELETE CASCADE`
- **Indices:**
  - `idx_math_obj_node_id` ON `mathematical_objects(node_id)`
  - `idx_math_obj_type` ON `mathematical_objects(object_type)`
  - `idx_math_obj_domain` ON `mathematical_objects(domain)`

#### 2. `definitions`
Stores formal (Lean 4, Coq, Isabelle) and LaTeX mathematical definitions.
- **Columns:**
  - `id`: `TEXT PRIMARY KEY` — Unique definition identifier (matches `nodes.id`).
  - `node_id`: `TEXT NOT NULL` — Foreign key referencing `nodes(id) ON DELETE CASCADE`.
  - `term`: `TEXT NOT NULL` — Defined mathematical term (e.g. `"Zeta Zero"`, `"Prime"`).
  - `formal_definition`: `TEXT` — Formal specification in Lean 4 / Isabelle / Coq format.
  - `informal_definition`: `TEXT` — Natural language / LaTeX description.
  - `domain`: `TEXT` — Mathematical domain.
  - `created_at`: `TEXT NOT NULL DEFAULT (datetime('now'))`
- **Foreign Key:** `FOREIGN KEY (node_id) REFERENCES nodes(id) ON DELETE CASCADE`
- **Indices:**
  - `idx_def_node_id` ON `definitions(node_id)`
  - `idx_def_term` ON `definitions(term)`
  - `idx_def_domain` ON `definitions(domain)`

#### 3. `equivalent_statements`
Tracks equivalent formulations of claims/theorems (e.g., Riemann Hypothesis equivalences such as Robin's Inequality or Mertens function bounds).
- **Columns:**
  - `id`: `TEXT PRIMARY KEY` — Equivalence record identifier (e.g., `eq_<a_id>_<b_id>`).
  - `statement_a_id`: `TEXT NOT NULL` — FK referencing `nodes(id) ON DELETE CASCADE`.
  - `statement_b_id`: `TEXT NOT NULL` — FK referencing `nodes(id) ON DELETE CASCADE`.
  - `equivalence_type`: `TEXT NOT NULL DEFAULT 'LOGICAL'` — (`'LOGICAL'`, `'SYNTACTIC'`, `'SEMANTIC'`, `'ASYMPTOTIC'`).
  - `proof_reference`: `TEXT` — Citation or proof node reference.
  - `confidence`: `REAL NOT NULL DEFAULT 1.0` — Confidence level [0.0, 1.0].
  - `created_at`: `TEXT NOT NULL DEFAULT (datetime('now'))`
- **Foreign Keys:**
  - `FOREIGN KEY (statement_a_id) REFERENCES nodes(id) ON DELETE CASCADE`
  - `FOREIGN KEY (statement_b_id) REFERENCES nodes(id) ON DELETE CASCADE`
- **Indices:**
  - `idx_eq_stmt_a` ON `equivalent_statements(statement_a_id)`
  - `idx_eq_stmt_b` ON `equivalent_statements(statement_b_id)`
  - `idx_eq_pair` UNIQUE ON `equivalent_statements(statement_a_id, statement_b_id, equivalence_type)`

#### 4. `memory_snapshots`
Ensures complete working memory snapshot storage for MDE research state. If `memory_snapshots` already exists from v3, v4 ensures idempotency and adds optional `domain` column.
- **Columns:**
  - `id`: `INTEGER PRIMARY KEY AUTOINCREMENT`
  - `session_id`: `TEXT NOT NULL` — Research session / thread identifier.
  - `snapshot`: `TEXT NOT NULL` — JSON blob encoding AST state, search trees, and tactic state.
  - `domain`: `TEXT` — Optional domain tag.
  - `created_at`: `TEXT NOT NULL DEFAULT (datetime('now'))`
- **Indices:**
  - `idx_snapshots_session` ON `memory_snapshots(session_id)`

#### 5. `failed_proof_attempts`
Records failed tactic sequences to prevent MCTS search from repeating unproductive proof branches.
- **Columns:**
  - `id`: `INTEGER PRIMARY KEY AUTOINCREMENT`
  - `claim_id`: `TEXT NOT NULL` — FK referencing `nodes(id) ON DELETE CASCADE`.
  - `tactic_sequence`: `TEXT NOT NULL` — JSON list of tactics attempted (e.g. `["simp", "ring"]`).
  - `verifier`: `TEXT NOT NULL` — Prover engine (`'LEAN'`, `'COQ'`, `'ISABELLE'`, `'SMT'`, `'MCTS'`).
  - `error_message`: `TEXT` — Diagnostic error output from prover compiler.
  - `created_at`: `TEXT NOT NULL DEFAULT (datetime('now'))`
- **Foreign Key:** `FOREIGN KEY (claim_id) REFERENCES nodes(id) ON DELETE CASCADE`
- **Indices:**
  - `idx_failed_proofs_claim` ON `failed_proof_attempts(claim_id)`
  - `idx_failed_proofs_verifier` ON `failed_proof_attempts(verifier)`
  - `idx_failed_proofs_claim_verifier` ON `failed_proof_attempts(claim_id, verifier)`

---

## 3. Implementation Blueprint for `migrations.py`

Below is the complete, Python implementation to be added to `axiom/core/knowledge_graph/migrations.py`:

```python
def _v4_mathematical_ontology(conn: sqlite3.Connection) -> None:
    """V4: EGS Mathematical Ontology tables & memory structures (R1, R8)."""
    # 1. mathematical_objects table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS mathematical_objects (
            id              TEXT PRIMARY KEY,
            node_id         TEXT NOT NULL,
            object_type     TEXT NOT NULL,
            formal_symbol   TEXT,
            domain          TEXT NOT NULL,
            properties_json TEXT,
            created_at      TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (node_id) REFERENCES nodes(id) ON DELETE CASCADE
        );
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_math_obj_node_id ON mathematical_objects(node_id);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_math_obj_type ON mathematical_objects(object_type);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_math_obj_domain ON mathematical_objects(domain);")

    # 2. definitions table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS definitions (
            id                  TEXT PRIMARY KEY,
            node_id             TEXT NOT NULL,
            term                TEXT NOT NULL,
            formal_definition   TEXT,
            informal_definition TEXT,
            domain              TEXT,
            created_at          TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (node_id) REFERENCES nodes(id) ON DELETE CASCADE
        );
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_def_node_id ON definitions(node_id);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_def_term ON definitions(term);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_def_domain ON definitions(domain);")

    # 3. equivalent_statements table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS equivalent_statements (
            id               TEXT PRIMARY KEY,
            statement_a_id   TEXT NOT NULL,
            statement_b_id   TEXT NOT NULL,
            equivalence_type TEXT NOT NULL DEFAULT 'LOGICAL',
            proof_reference  TEXT,
            confidence       REAL NOT NULL DEFAULT 1.0,
            created_at       TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (statement_a_id) REFERENCES nodes(id) ON DELETE CASCADE,
            FOREIGN KEY (statement_b_id) REFERENCES nodes(id) ON DELETE CASCADE
        );
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_eq_stmt_a ON equivalent_statements(statement_a_id);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_eq_stmt_b ON equivalent_statements(statement_b_id);")
    conn.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_eq_pair 
        ON equivalent_statements(statement_a_id, statement_b_id, equivalence_type);
    """)

    # 4. memory_snapshots table (ensure table and optional domain column exist)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS memory_snapshots (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT    NOT NULL,
            snapshot   TEXT    NOT NULL,
            domain     TEXT,
            created_at TEXT    NOT NULL DEFAULT (datetime('now'))
        );
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_session ON memory_snapshots(session_id);")
    
    # Check if domain column exists in memory_snapshots (in case v3 created it without domain)
    cursor = conn.execute("PRAGMA table_info(memory_snapshots);")
    columns = {row[1] for row in cursor.fetchall()}
    if "domain" not in columns:
        conn.execute("ALTER TABLE memory_snapshots ADD COLUMN domain TEXT;")

    # 5. failed_proof_attempts table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS failed_proof_attempts (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            claim_id        TEXT    NOT NULL,
            tactic_sequence TEXT    NOT NULL,
            verifier        TEXT    NOT NULL,
            error_message   TEXT,
            created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (claim_id) REFERENCES nodes(id) ON DELETE CASCADE
        );
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_failed_proofs_claim ON failed_proof_attempts(claim_id);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_failed_proofs_verifier ON failed_proof_attempts(verifier);")
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_failed_proofs_claim_verifier 
        ON failed_proof_attempts(claim_id, verifier);
    """)

    conn.commit()
```

And update `MIGRATIONS` in `migrations.py`:
```python
MIGRATIONS: List[Migration] = [
    (1, "Initial schema: nodes + edges",         _v1_initial_schema),
    (2, "Add proof_lineage table",               _v2_proof_lineage),
    (3, "Add memory_snapshots table",            _v3_working_memory_snapshots),
    (4, "Mathematical ontology & memory schema", _v4_mathematical_ontology),
]
```

---

## 4. Verification & Testing Strategy

To verify this migration design:
1. **Migration Execution Test:** Instantiate `EpistemicStore(":memory:")` or call `run_migrations(conn)`. Query `sqlite_master` to confirm all 5 tables (`mathematical_objects`, `definitions`, `equivalent_statements`, `memory_snapshots`, `failed_proof_attempts`) and their indices exist.
2. **Idempotency Test:** Execute `run_migrations(conn)` twice in succession. Verify zero errors occur and `_schema_migrations` contains exactly 4 applied migration records.
3. **Foreign Key Integrity Test:** Attempt to insert a record into `mathematical_objects` or `failed_proof_attempts` referencing a non-existent `node_id`. Assert that a `sqlite3.IntegrityError` is thrown.
4. **Cascade Deletion Test:** Delete a node from `nodes` and verify that referencing entries in `mathematical_objects`, `definitions`, `equivalent_statements`, and `failed_proof_attempts` are automatically deleted.
