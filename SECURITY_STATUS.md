# Security Status

**Last updated:** 2026-08-08  
**Loop:** TSS (Trust, Security & Safety)

## Posture summary

| Area | Status | Notes |
|------|--------|-------|
| Authentication | ⚠️ Partial | Bearer token + JWT RBAC on core routes |
| Authorization | ⚠️ Partial | `/eval`, `/gcp`, `/provenance` optional auth (dev default: open) |
| Secrets | ⚠️ Partial | Defaults documented; production guard blocks insecure startup |
| Document upload | ✅ | PDF-only, 20MB limit, auth required |
| Research workspace | ✅ | All `/research/*` routes require bearer token |
| Agent tooling | ⚠️ New | `ToolRiskClass` classification added; enforcement pending |
| Prompt injection | ⚠️ New | Heuristic detection + content wrapping utilities |
| Dependency scan | ✅ | `pip-audit` in CI (weekly) |
| Container | ✅ | Non-root runtime user in Dockerfile |
| Kubernetes | — | Not deployed |

**Overall maturity:** Early — foundations in place; production hardening required.

## Implemented controls (TSS-1)

- Production configuration audit on API startup
- Optional authentication for eval/GCP/provenance route groups
- Repository secret pattern scanner (`make tss-security`)
- Tool risk classification enum for agent safety
- Untrusted research content wrapping heuristics

## Open risks

See `SECURITY_SCORECARD.md` and `THREAT_MODEL.md`.

## Refresh

```bash
make tss-security
```
