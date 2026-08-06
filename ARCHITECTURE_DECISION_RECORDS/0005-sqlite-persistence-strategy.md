# ADR-0005: SQLite Persistence Strategy

**Status:** Accepted  
**Date:** 2026-08-06

## Context

AXIOM needs durable storage for knowledge graph, research workspace, eval runs, and workflow state without operational complexity of a separate database server for development and demos.

## Decision

Use **SQLite** as the default persistence layer:

- `DB_PATH` setting (default `./axiom.db`)
- Tests use `:memory:` via `tests/conftest.py`
- Migrations are explicit Python modules per domain (`migrations.py`)
- No ORM — raw SQL with typed Pydantic models at boundaries

**Domains with separate schemas:**
- `axiom/core/knowledge_graph/`
- `axiom/research/`
- `axiom/research_loop/`
- Eval tables created in `eval_api.py`

## Consequences

- **Positive:** Zero-config local dev; single file backup
- **Positive:** Fast CI with in-memory databases
- **Negative:** No per-user row-level isolation yet (P0 debt — see `MVP_READINESS.md`)
- **Negative:** Concurrent write limits for multi-tenant production
- **Future:** Postgres migration requires additive schema design; document in new ADR when undertaken
