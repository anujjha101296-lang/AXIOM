# Scope: Milestone 1 — EGS Mathematical Ontology & Database Migrations

## Status: **DONE** (Verified & Approved via Gate Iteration 2)

## Architecture
- `axiom/core/knowledge_graph/schema.py`: Extended Pydantic models with `MathematicalObjectNode`, `DefinitionNode`, `OpenProblemNode`, `ConjectureNode`, and edges (`EQUIVALENT_TO`, `DEPENDS_ON`, `PROVES`).
- `axiom/core/knowledge_graph/migrations.py`: Added `_v4_mathematical_ontology` migration creating `mathematical_objects`, `definitions`, `equivalent_statements`, `memory_snapshots`, `failed_proof_attempts`. Added thread-safe `BEGIN IMMEDIATE` transaction locking & retry logic for concurrent migration execution.
- `axiom/core/knowledge_graph/db.py`: Updated `EpistemicStore._init_db()` to invoke `run_migrations(self.conn)`. Added `informal_description` parameter support to `add_definition()` and direct table CRUD / query helpers.

## Scope Items
1. Migration `v4`: Execute DDL for `mathematical_objects`, `definitions`, `equivalent_statements`, `memory_snapshots`, `failed_proof_attempts`. [DONE]
2. Schema Models: Update `NodeType`, `EdgeType`, Pydantic models, and `ScientificNode` Union. [DONE]
3. Unit Tests: Test migration execution and schema validation in `tests/test_mde_ontology.py`. [DONE]

## Verification Criteria
- [x] All SQLite tables created cleanly without FK errors.
- [x] Schema models serialize/deserialize polymorphic JSON payload correctly.
- [x] Concurrent multi-thread migration execution succeeds idempotently with zero errors.
- [x] Bulk CASCADE deletion purges 7,000+ child records without leaving orphans.
- [x] All 23 tests in `tests/test_mde_ontology.py` and `tests/test_epistemic_layer.py` pass cleanly.
- [x] Forensic Auditor confirmed 100% CLEAN (zero hardcoded test outputs or facade implementations).
