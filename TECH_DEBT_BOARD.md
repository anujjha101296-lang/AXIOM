# Technical Debt Board

**Generated:** 2026-08-06T17:52:19Z
**Technical Debt Score:** **95/100** (higher = more debt)

## Active Debt Items

| Severity | Item | Source | Recommendation |
|----------|------|--------|----------------|
| critical | No per-user data isolation | MVP_READINESS.md P0 | Add user_id scoping to research store queries and migrations. |
| critical | Shared SQLite store (no tenancy) | MVP_READINESS.md | Partition research data by authenticated user_id. |
| high | S0-E4 EPIC-002 evidence gate open | TASK_QUEUE.md | Implement evidence_state, benchmark_count, limitations on all capability scores. |
| high | MDE API surface gap (26 e2e failures) | MASTER_PROGRESS.md | Mount remaining MDE routes or narrow e2e scope with honest docs. |
| medium | Workflow engine has no core tests | MASTER_PROGRESS.md | Add unit tests for workflow engine state transitions. |
| medium | Mock LLM default for Q&A/summaries | MVP_READINESS.md | Document mock default; add integration path for production LLM. |
| medium | UI Dockerfile missing | ENGINEERING_SCORECARD.md | Add ui/Dockerfile and wire docker-compose service. |
| medium | Missing debt reference doc: MVP_READINESS.md | governance | Restore or create MVP_READINESS.md |
| medium | Missing debt reference doc: MASTER_PROGRESS.md | governance | Restore or create MASTER_PROGRESS.md |
| medium | Missing debt reference doc: ENGINEERING_SCORECARD.md | governance | Restore or create ENGINEERING_SCORECARD.md |
| low | Debt marker in TEST_INFRA.md:381 | TEST_INFRA.md | Resolve or track in TECH_DEBT_BOARD.md |
| low | Debt marker in tests/e2e/test_m6_m7_e2e.py:1460 | tests/e2e/test_m6_m7_e2e.py | Resolve or track in TECH_DEBT_BOARD.md |
| low | Debt marker in tests/e2e/test_m6_m7_e2e.py:1466 | tests/e2e/test_m6_m7_e2e.py | Resolve or track in TECH_DEBT_BOARD.md |
| low | Debt marker in .agents/explorer_e2e_survey_2/analysis.md:674 | .agents/explorer_e2e_survey_2/analysis.md | Resolve or track in TECH_DEBT_BOARD.md |
| low | Debt marker in axiom/evaluation/prize_readiness.py:2 | axiom/evaluation/prize_readiness.py | Resolve or track in TECH_DEBT_BOARD.md |
| low | Debt marker in axiom/evaluation/prize_readiness.py:20 | axiom/evaluation/prize_readiness.py | Resolve or track in TECH_DEBT_BOARD.md |
| low | Debt marker in axiom/governance/collectors/debt.py:16 | axiom/governance/collectors/debt.py | Resolve or track in TECH_DEBT_BOARD.md |
| low | Grafana provisioning incomplete | ENGINEERING_SCORECARD.md | Add provisioning configs under monitoring/. |

## What should be refactored?

- Research store: add user_id column and query scoping
- Eval API: replace hardcoded `/eval/scores` fallback with evidence-gated responses
- MDE router: consolidate stub routes vs production mounting

## What should be deleted?

- Stale capability delta reports (`docs/capability_delta_*.md`) — do not bulk-commit
- Unused graph workspace code paths if not on roadmap
- Duplicate ruff/mypy config if consolidated in pyproject.toml

## What is duplicated?

- Two UI surfaces: `/workspace` graph vs `/research` workspace (no shared context)
- Eval framework vs hardcoded score endpoints
- Demo scripts overlapping MVP and research workspace flows

---
*Debt board is regenerated each engineering cycle from repo evidence.*