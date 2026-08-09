# Infrastructure Security

**Last updated:** 2026-08-08

## Deployed infrastructure (as documented in repo)

| Component | Present | Security notes |
|-----------|---------|----------------|
| Docker multi-stage build | ✅ | Non-root `axiom` user |
| docker-compose | ✅ | Local dev stack |
| GitHub Actions CI | ✅ | Lint, test, security audit |
| Kubernetes | ❌ | Not in repository |

## Docker review

| Check | Status |
|-------|--------|
| Minimal base (`python:3.11-slim`) | ✅ |
| Multi-stage build | ✅ |
| Non-root execution | ✅ |
| No embedded secrets | ✅ (env at runtime) |
| Health check | ✅ |
| Read-only root filesystem | ❌ Not configured |
| Image scanning | ❌ Manual only |

## CI/CD

| Workflow | Purpose |
|----------|---------|
| `ci.yml` | Tests and lint |
| `security.yml` | `pip-audit` dependency scan |
| `cd.yml` | Deployment (review before production use) |

## Cloud resources

Not inventoried — no cloud IaC in repository. Do not invent infrastructure.

## Recommendations

1. Add container image scanning to CI when publishing images
2. Pin Docker base image digests for reproducibility
3. Add `npm audit` for UI pipeline
