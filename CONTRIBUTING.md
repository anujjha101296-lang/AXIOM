# Contributing to AXIOM

Thank you for contributing to the world's first AI Scientific Discovery Platform.

## Core Principle

> Every line of code must exist because it improves scientific capability.

Before submitting any change, ask: **Does this increase AXIOM's probability of making genuine scientific discoveries?**

## Development Setup

```bash
make setup   # Install deps, set up pre-commit hooks
make dev     # Start the API server in dev mode
make test    # Run the full test suite
make lint    # Run ruff + mypy
```

## Branch Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Production-ready code. Protected. CI must pass. |
| `sprint/<name>` | Sprint feature branches |
| `fix/<name>` | Bug fixes |
| `docs/<name>` | Documentation only |

## Commit Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(EIE): add LaTeX macro expansion to arXiv parser
fix(MCTS): correct boundary regex for identity rewrite rules
docs(API): add /hypothesize endpoint documentation
test(benchmark): add Dimension F: Lean tactic synthesis coverage
```

**Types**: `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `ci`, `chore`

**Scopes** (use AXIOM module codes):
- `EIE` — Epistemic Ingest Engine
- `EGS` — Epistemic Graph Store
- `LRK` — Lean 4 reasoning/exporter
- `AVT` — Verification (SMT, Z3)
- `MCTS` — Monte Carlo proof search
- `HYP` — Hypothesis Engine
- `MEM` — Working Memory
- `SIL` — Self-Improvement Loop
- `PRS` — Prize Readiness Scorer
- `API` — API Gateway
- `UI` — Frontend canvas
- `OBS` — Observability (logging, metrics)
- `CFG` — Configuration

## Pull Request Process

1. Branch off `main` with `git checkout -b sprint/<name>`
2. Make changes. Write/update tests. Update docs.
3. Run `make test` — all tests must pass.
4. Run `make lint` — zero violations.
5. Open a PR. Fill in the PR template.
6. Request review. Address feedback.
7. Squash and merge.

## Code Standards

- **Python 3.10+** with full type annotations
- **Pydantic v2** for all data models
- **ruff** for linting (zero violations)
- **mypy** in strict mode
- **Docstrings**: every public class and function
- **Tests**: every new feature must include a pytest test
- **Coverage**: maintain ≥ 80% overall

## Testing Requirements

- Unit tests go in `tests/test_<module>.py`
- Integration tests go in `tests/test_<feature>_integration.py`
- Benchmark tests go in `tests/test_benchmark.py`
- Fixtures go in `tests/conftest.py`

## Security

- **Never commit secrets, API keys, or credentials** — use `.env` (gitignored)
- Secrets are managed via Pydantic `BaseSettings` reading from environment
- Report vulnerabilities privately to the maintainers

## Documentation

- Every public API endpoint must have an OpenAPI docstring
- Every new module must have a docstring at the top explaining its purpose
- Significant architectural changes require updating `docs/architecture.md`
