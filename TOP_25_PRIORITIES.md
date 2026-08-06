# Top 25 Engineering Priorities

**Generated:** 2026-08-06T17:52:19Z

## Ranked Priorities

| Rank | Priority | Action |
|-----:|----------|--------|
| 1 | No per-user data isolation | Scope all research queries by user_id before any external pilot |
| 2 | Shared SQLite store (no tenancy) | Partition research data by authenticated user_id. |
| 3 | No production JWT secret enforcement | Add environment check in settings startup validation |
| 4 | S0-E4 EPIC-002 evidence gate open | Implement evidence_state, benchmark_count, limitations on all capability scores. |
| 5 | MDE API surface gap (26 e2e failures) | Mount remaining MDE routes or narrow e2e scope with honest docs. |
| 6 | E2E test gap: MDE API surface | Mount MDE routes or mark e2e as xfail with honest tracking |
| 7 | Vulnerable dependency: ansible==9.2.0 | Upgrade ansible to a patched version |
| 8 | Vulnerable dependency: ansible-core==2.16.3 | Upgrade ansible-core to a patched version |
| 9 | Benchmark regression: knowledge_quality | Investigate knowledge_quality benchmark cases; add regression test |
| 10 | Benchmark regression: literature_synthesis | Investigate literature_synthesis benchmark cases; add regression test |
| 11 | [Frontend Lead] Fix waitlist form; add UI Dockerfile; wire demo/research mode banners consistently. | UI npm high/critical vulns: 0.0; landing waitlist is non-functional. |
| 12 | [Infrastructure Lead] Complete Grafana provisioning; add governance CI job; lazy-import heavy scientific libs. | Cold import 564ms; compose stack incomplete for full observability. |
| 13 | Workflow engine has no core tests | Add unit tests for workflow engine state transitions. |
| 14 | Mock LLM default for Q&A/summaries | Document mock default; add integration path for production LLM. |
| 15 | UI Dockerfile missing | Add ui/Dockerfile and wire docker-compose service. |
| 16 | No dedicated tests for axiom/workflow/ | Add tests/test_workflow_engine.py |
| 17 | [Platform Lead] Audit router mounting in api_gateway/main.py; align e2e expectations with production surface. | 4.0 routers mounted; MDE and workflow routes partially exposed. |
| 18 | [Backend Lead] Add user_id scoping to research store and workflow engine unit tests. | Line coverage at 72.5%; tenancy gap is the highest backend risk. |
| 19 | [QA Lead] Maintain 70% coverage gate; add workflow tests; track e2e gap separately in governance reports. | 165.0 core tests collected; e2e documents platform surface debt honestly. |
| 20 | [Product Engineering Lead] Ship contributor onboarding docs; resolve P0 MVP blockers before public alpha. | Missing required docs: 0.0; workspace wedge is demo-ready, not production-ready. |
| 21 | Missing debt reference doc: MVP_READINESS.md | Restore or create MVP_READINESS.md |
| 22 | Missing debt reference doc: MASTER_PROGRESS.md | Restore or create MASTER_PROGRESS.md |
| 23 | Missing debt reference doc: ENGINEERING_SCORECARD.md | Restore or create ENGINEERING_SCORECARD.md |
| 24 | Potential code duplication detected | Consolidate shared logic into axiom/core or shared utilities |
| 25 | 1 route module(s) may be unmounted | Audit axiom/services/api_gateway/main.py router includes |

## ONE Initiative — Highest Long-Term Leverage

### S0-E4 — EPIC-002 Evidence Integration Gate

Completing S0-E4 is the highest-leverage engineering investment because it establishes evidence_state, benchmark_count, and stated limitations on every capability score. Without this gate, evaluation outputs, governance metrics, and research claims cannot be trusted — undermining every downstream initiative including H1-OBS provenance, autonomous loop credibility, and external pilot readiness. It is reversible, testable, and already ranked #6 (ready) in TASK_QUEUE.md with S0-E2 and S0-E3 complete.

> **Note:** Only ONE initiative is recommended per engineering cycle. All other priorities support or follow this gate.

---
*Priorities ranked by severity, score impact, and council review.*