# Dependency Security

**Last updated:** 2026-08-08

## Inventory

| Ecosystem | Manifest | Lock file |
|-----------|----------|-----------|
| Python | `pyproject.toml` | Poetry (no poetry.lock in repo) |
| Node/Next.js | `ui/package.json` | `ui/package-lock.json` |

## Automated scanning

| Tool | Trigger | Workflow |
|------|---------|----------|
| `pip-audit` | Push to main, weekly cron | `.github/workflows/security.yml` |
| `tss_security_check.py` secret patterns | `make tss-security` | Local + recommended CI |

## Known gaps

- No automated `npm audit` in CI for UI dependencies
- Python dependencies not fully pinned in `pyproject.toml` (caret ranges)
- No SBOM generation yet

## Upgrade policy

Do NOT blindly upgrade. For each upgrade:

1. Compatibility review
2. Unit + integration tests
3. Security regression check
4. Document in CHANGELOG

## Refresh

```bash
pip install pip-audit && pip-audit
cd ui && npm audit
make tss-security
```
