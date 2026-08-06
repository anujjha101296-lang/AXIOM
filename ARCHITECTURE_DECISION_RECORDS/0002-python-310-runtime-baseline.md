# ADR-0002: Python 3.10+ Runtime Baseline

**Status:** Accepted  
**Date:** 2026-08-06  
**Supersedes:** Stale blocker note in `ARCHITECTURE.md` (Python 3.9)

## Context

AXIOM uses Pydantic v2 and modern type syntax (`str | None`). Python 3.9 fails during test collection. Sprint 0 (S0-E2) established 3.10+ as the supported runtime.

## Decision

- **Minimum:** Python 3.10
- **Recommended:** Python 3.11 (CI and Docker use 3.11)
- Type annotations use PEP 604 unions; no `Optional` workarounds for 3.9
- CI, Dockerfile, and `make setup` target 3.11

## Consequences

- **Positive:** Trustworthy test baseline; simpler type hints
- **Positive:** Aligns with FastAPI/Pydantic ecosystem defaults
- **Negative:** Contributors on 3.9 must upgrade
- **Verification:** `make test-core` must pass on 3.11 in CI
