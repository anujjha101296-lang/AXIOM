# Security Scorecard

**Period:** 2026-08-08

## Vulnerability summary

| Severity | Open | Target |
|----------|------|--------|
| Critical | 0 | 0 |
| High | 2 | 0 (config risks) |
| Medium | 3 | tracked |
| Low | — | — |

## High-priority open items

| ID | Risk | Status |
|----|------|--------|
| TSS-SEC-010-eval | `/eval/*` public when auth flags disabled | Mitigated by production flags |
| TSS-SEC-010-gcp | `/gcp/*` public when auth flags disabled | Mitigated by production flags |

## Maturity indicators

| Control | Maturity |
|---------|----------|
| Authentication | L2 — bearer + JWT |
| Authorization | L2 — RBAC + optional route groups |
| Secret management | L1 — env-based, scanner added |
| Dependency scanning | L2 — pip-audit CI |
| Agent safety | L1 — classification only |
| Prompt injection defense | L1 — heuristics |
| Audit logging | L2 — structured logs, provenance |
| Incident response | L1 — runbook defined |

## Mean time to remediation

Not measured (no incidents).

## Refresh

```bash
make tss-security
```
