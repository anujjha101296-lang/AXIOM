# Contributing to AXIOM

> **Start here:** [`CONTRIBUTOR_GUIDE.md`](CONTRIBUTOR_GUIDE.md) — full day-1 onboarding guide.

Thank you for contributing to the AXIOM research platform.

## Core Principle

> Every line of code must exist because it improves scientific capability — honestly measured.

Before submitting any change, ask: **Does this increase AXIOM's ability to help researchers, and are capability claims truthful?**

## Quick Commands

```bash
make setup      # Install deps, copy .env.example
make test-core  # Core tests (CI gate)
make check      # lint + type-check + test-core
make dev        # API server :8000
```

## Development Setup

See `CONTRIBUTOR_GUIDE.md` for prerequisites, repository structure, and architecture overview.

## Branch Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Production-ready code. Protected. CI must pass. |
| `cursor/<name>-dc7e` | Cloud agent feature branches |
| `sprint/<name>` | Sprint feature branches |
| `fix/<name>` | Bug fixes |
| `docs/<name>` | Documentation only |

## Commit Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(research): add per-project note tagging
fix(demo): clarify Demo Mode banner text
docs(contributor): update CI section
test(workflow): add Workflow model unit tests
ci: align coverage gate with pyproject.toml
```

**Types**: `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `ci`, `chore`

## Pull Request Process

1. Branch off `main`
2. Run `make check`
3. Open PR — fill in `.github/pull_request_template.md`
4. Significant design changes: add or update ADR in `ARCHITECTURE_DECISION_RECORDS/`

## Code Standards

- **Python 3.10+** with type annotations on public APIs
- **Pydantic v2** for data models
- **ruff** for lint + format
- **Tests** for new behavior in `tests/test_<module>.py`
- **Coverage** ≥70% on `axiom/` (CI enforced)

## Architecture Decisions

Important design choices are recorded in `ARCHITECTURE_DECISION_RECORDS/`.

- Auth and modes (ADR-0003, ADR-0005 in `ARCHITECTURE_DECISION_RECORDS/`)
- Verification labeling (ADR-0004)
- Runtime baseline (ADR-0002)

## Security

- Never commit secrets — see `docs/SECURITY.md`
- Run `make security-audit` before releases

## Documentation

- Public API: OpenAPI at `/docs` and `docs/api.md`
- Operation modes: `docs/MODES.md`
- Observability: `docs/OBSERVABILITY.md`
