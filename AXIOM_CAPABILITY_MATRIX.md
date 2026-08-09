# AXIOM Capability Matrix

**Last audited:** 2026-08-09  
**Audit method:** Full repository trace + test execution (278/281 core tests pass)  
**Auditor:** Master Build & Evolution Loop (Phase 0–2)

## Classification Legend

| State | Meaning |
|-------|---------|
| **FULL** | Real implementation, API, tests, health gate where applicable |
| **PARTIAL** | Substantial code; stubs, simulation, or integration gaps remain |
| **PROTOTYPE** | Demo-quality; not production-ready |
| **SCAFFOLD** | Structure exists; core behavior missing |
| **DOC_ONLY** | Documentation without matching implementation |
| **BROKEN** | Implementation exists but fails tests/runtime |
| **MISSING** | Not present in codebase |

## Executive Summary

| Layer | FULL | PARTIAL | PROTOTYPE/SCAFFOLD | MISSING |
|-------|------|---------|-------------------|---------|
| Research Loops (7) | 3 | 4 | 0 | 0 |
| Product | 1 | 2 | 0 | 1 |
| Infrastructure | 1 | 4 | 0 | 1 |
| Frontend | 0 | 2 | 1 | 0 |

**Critical blockers identified:**
1. ~~TestClient/httpx incompatibility~~ — **FIXED** (httpx pinned `<0.28`)
2. Workflow API unmounted — **FIXED** (this cycle)
3. E2E suite excluded from CI (59 errors when run; harness partially fixed)
4. P0-WEB landing page mock data / dead waitlist
5. Discovery `/query` returns empty results
6. MIP v5 migration not auto-run on startup

---

## RESEARCH LOOPS

### E&R — Evidence & Reproducibility | **FULL**
| Item | Detail |
|------|--------|
| Code | `axiom/evidence/` — registry, discovery_gate, integrity, reproduction |
| API | `/evidence/*` (12 endpoints) |
| Tests | 12/12 pass |
| Health | `make erl-health` PASS |
| Gap | EGS nodes not auto-synced to claims on ingest |

### SIMR — Model/Tool Routing | **FULL**
| Item | Detail |
|------|--------|
| Code | `axiom/routing/` — selector, compiler, registries, failure memory |
| API | `/routing/*` (14 endpoints) |
| Tests | 14/14 pass |
| Health | `make simr-health` PASS |
| Gap | Falls back to `mock-model` without API keys (by design v1) |

### FMTP — Formal Mathematics | **PARTIAL**
| Item | Detail |
|------|--------|
| Code | `axiom/formal_math/` — formalization, proof search, compilation gate |
| API | `/formal/*` (18 endpoints) |
| Tests | 17/17 pass |
| Health | `make fmtp-health` PASS |
| Gap | Lean required for real verification; Coq/Isabelle export stubs |

### SEC — Experimentation & Compute | **FULL**
| Item | Detail |
|------|--------|
| Code | `axiom/experiment/` — sandbox, executor, integrity gate |
| API | `/experiments/*` (15 endpoints) |
| Tests | 12/12 pass |
| Health | `make sec-health` PASS |
| Gap | Subprocess sandbox only (TD-008: no cgroup/container) |

### FRCE — Campaign Engine | **PARTIAL**
| Item | Detail |
|------|--------|
| Code | `axiom/campaign/` — orchestrator, graph, pivot, gates |
| API | `/frce/*` (14 endpoints) |
| Tests | 14/14 pass |
| Health | `make frce-health` PASS |
| Gap | Computational track uses demo code; no UI dashboard |

### SKAI — Knowledge Acquisition | **PARTIAL**
| Item | Detail |
|------|--------|
| Code | `axiom/skai/` — orchestrator, extractor, conflicts, gaps, bridge |
| API | `/skai/*` (12 endpoints) |
| Tests | 12/12 pass |
| Health | `make skai-health` PASS |
| Gap | Regex extraction; arXiv not wired through SKAI orchestrator |

### GCP — Grand Challenge Program | **PARTIAL**
| Item | Detail |
|------|--------|
| Code | `axiom/grand_challenge/` — engine, registry, gates |
| API | `/gcp/*` (14 endpoints) |
| Tests | 12/12 pass (after httpx fix) |
| Health | `run_gcp_benchmark.py` only |
| Gap | Tier 2+ challenges need workflow/SEC integration |

---

## KNOWLEDGE & MEMORY

| Capability | State | Evidence | Gap |
|------------|-------|----------|-----|
| Epistemic Graph Store (EGS) | **FULL** | `axiom/core/knowledge_graph/`, 23 tests | No dedicated health gate |
| SKAI knowledge graph | **PARTIAL** | `axiom/skai/store.py` | Not unified with EGS |
| Research workspace FTS | **FULL** | `axiom/research/store.py`, 10 tests | No health gate |
| Working memory | **PARTIAL** | `axiom/core/memory/` | Session-scoped only |
| MIP episodic memory | **PARTIAL** | `axiom/mip/memory/` | Manual v5 migration |
| FRCE global memory | **PARTIAL** | `frce_global_memory` table | No UI |
| Campaign memory | **PARTIAL** | `axiom/campaign/memory.py` | — |

---

## REASONING & PLANNING

| Capability | State | Evidence | Gap |
|------------|-------|----------|-----|
| Hypothesis engine | **PARTIAL** | Template-based from EGS | Not ML-driven |
| MCTS solver | **PROTOTYPE** | Regex rewrite rules only | `/verify/proof` limited |
| Research compiler (SIMR) | **FULL** | `compile_research_plan()` | — |
| Campaign planner | **PARTIAL** | FRCE `planner.py` | — |
| Discovery query `/query` | **SCAFFOLD** | Returns `[]` always | Needs SKAI retrieval |
| Self-improvement loop | **PARTIAL** | `self_improvement.py` | Audit only |

---

## MULTI-AGENT & WORKFLOW

| Capability | State | Evidence | Gap |
|------------|-------|----------|-----|
| Workflow engine | **PARTIAL** | `axiom/workflow/` | Workers have stubs |
| Workflow API | **PARTIAL** | `/workflows/*` mounted this cycle | No dedicated tests |
| Research roles (FRCE) | **PARTIAL** | Role definitions only | Not separate agent processes |
| Agent sandbox | **PARTIAL** | SEC subprocess | TD-008 full isolation |

---

## PRODUCT

| Capability | State | Evidence | Gap |
|------------|-------|----------|-----|
| Research workspace API | **FULL** | `/research/*`, 15 tests | — |
| Research workspace UI | **PARTIAL** | `ui/src/app/research/` | Mock LLM without keys |
| Graph workspace UI | **PARTIAL** | `ui/src/app/workspace/` | Hardcoded API URL |
| Public landing (P0-WEB) | **SCAFFOLD** | `ui/src/app/page.tsx` | Mock metrics, dead waitlist |
| Campaign dashboard UI | **MISSING** | — | API-only |
| Evidence inspection UI | **MISSING** | — | — |

---

## INFRASTRUCTURE

| Capability | State | Evidence | Gap |
|------------|-------|----------|-----|
| API Docker image | **FULL** | `Dockerfile` | No editable install |
| Docker Compose | **PARTIAL** | `docker-compose.yml` | Missing `ui/Dockerfile`, Grafana |
| Kubernetes | **MISSING** | — | Not required yet |
| CI (Python) | **PARTIAL** | `.github/workflows/ci.yml` | E2E excluded; 3 SCEP failures |
| CD | **PARTIAL** | `cd.yml` | API image only |
| Security scan | **PARTIAL** | `security.yml` | pip-audit only |
| CEL health | **FULL** | 278 tests pass | — |
| Observability | **PARTIAL** | `/metrics`, provenance | Grafana missing; counters underused |

---

## SECURITY

| Capability | State | Evidence | Gap |
|------------|-------|----------|-----|
| TSS production guard | **FULL** | `production_guard.py` | — |
| Optional route auth | **FULL** | 10 loop auth flags | `/mip/*` unauthenticated |
| Secret scanner | **FULL** | `make tss-security` | Not in CI |
| SEC sandbox | **PARTIAL** | subprocess + AST | No cgroup |
| Scope isolation (SKAI) | **PARTIAL** | `KnowledgeScope` enum | Enforcement partial |

---

## SCIENTIFIC CAMPAIGNS (Ladder)

| Level | State | Evidence |
|-------|-------|----------|
| 0 — Basic reasoning | **FULL** | GCP Tier 0, SCEP benchmarks |
| 1 — Known-answer math | **PARTIAL** | GCP Tier 1, FMTP |
| 2 — Formal reproduction | **PARTIAL** | FMTP compilation gate |
| 3 — Paper reproduction | **SCAFFOLD** | Workflow demo only |
| 4 — Research benchmarks | **PARTIAL** | SCEP suite |
| 5–9 | **DOC_ONLY** | Ladder defined in FRCE; not executed |

---

## Priority Rankings (Phase 5)

| Rank | Initiative | Leverage | Effort | Dependencies |
|------|-----------|----------|--------|--------------|
| **1** | P0-WEB honest landing | Product unlock | Medium | UI only |
| **2** | Wire `/query` to SKAI retrieval | Research unlock | Low | SKAI |
| **3** | GCP-2 Tier 1 campaign execution | Scientific validation | High | FRCE+SKAI+founder approval |
| **4** | MIP v5 auto-migration | API integrity | Low | — |
| **5** | Discovery & Hypothesis Engine | Next loop | High | SKAI gaps |
| **6** | E2E harness + CI inclusion | Quality gate | Medium | httpx fixed |
| **7** | Campaign/experiment UI | Product | High | APIs exist |
| **8** | Container sandbox (TD-008) | Security | High | SEC |

---

## Test Evidence (2026-08-09)

```
Core suite (excl e2e): 278 passed, 3 failed, 0 errors
Loop health gates: ERL, SIMR, FMTP, SEC, FRCE, SKAI — all PASS
CEL health: PASS
Failed: test_evaluation_platform (audit doc), test_scep_e2e (2)
```

---

## Acceptance Criteria for "Research Platform v1"

- [x] 6 research loops with APIs and health gates
- [x] Campaign engine orchestrating loops
- [x] Knowledge acquisition with provenance
- [ ] End-to-end user journey (landing → research → campaign)
- [ ] GCP-2 campaign executed with evidence
- [ ] E2E tests in CI
- [ ] All API routes authenticated in production config
