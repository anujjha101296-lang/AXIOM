# AXIOM Security Guide for Contributors

Security expectations for code review and local development.

---

## Secrets Management

| Rule | Detail |
|------|--------|
| Never commit secrets | `.env` is gitignored; use `.env.example` for templates |
| JWT secret | Set `JWT_SECRET_KEY` via `openssl rand -hex 32` in production |
| API token | `AXIOM_API_TOKEN` for dev/static auth |
| LLM keys | Configure via environment — not in source |

**CI uses test-only values** (`JWT_SECRET_KEY=ci-test-secret`).

---

## Authentication

- Research routes require JWT or static bearer token (`verify_token` dependency)
- Demo routes (`/demo/*`) are **public by design** — curated data only
- Workflow router currently lacks auth — known debt; do not expose publicly without review

---

## Dependency Auditing

```bash
make security-audit      # Python (pip-audit)
make security-audit-ui   # Node (npm audit)
```

CI runs `security.yml` on push to `main` and weekly.

---

## Security Review Checklist (PR authors)

Before requesting review:

- [ ] No hardcoded credentials, API keys, or tokens
- [ ] User input validated via Pydantic models
- [ ] File uploads restricted (PDF only on research routes)
- [ ] SQL uses parameterized queries (no string interpolation)
- [ ] Error responses do not leak stack traces in production (`ENVIRONMENT=production`)
- [ ] New public endpoints documented with auth requirements
- [ ] Demo Mode outputs labeled `represents_scientific_capability: false`
- [ ] Verification results include `evidence_mode` (ADR-0004)

---

## Known Security Debt

See `MVP_READINESS.md` P0 items:

1. No per-user data isolation
2. Default JWT secret in development
3. No HTTPS/TLS in local stack
4. No rate limiting on auth endpoints
5. Workflow router unauthenticated

Do not worsen these; prefer fixes in focused PRs.

---

## Reporting Vulnerabilities

Do not open public issues for security vulnerabilities. Contact maintainers directly with:

- Description and reproduction steps
- Affected component and severity assessment
- Suggested fix if known

---

## Related

- `docs/adr/0004-verification-truthfulness.md`
- `docs/adr/0003-demo-vs-research-modes.md`
- `.github/workflows/security.yml`
