# AXIOM — Autonomous eXploration of Ideas, Observations & Models

> **The world's first AI Scientific Discovery Platform**

AXIOM is a continuously self-improving system built to accelerate genuine scientific discovery, with the long-term objective of contributing to officially recognized prize-backed open problems.

---

## Architecture at a Glance

```
axiom/
├── core/
│   ├── knowledge_graph/    # Epistemic Graph Store (SQLite + NetworkX)
│   ├── parser/             # LaTeX / arXiv ingestion engine
│   ├── reasoning/          # MCTS proof search, hypothesis engine, self-improvement loop
│   ├── memory/             # Session working memory
│   └── verification/       # Z3 SMT gateway, Lean 4 exporter
├── services/
│   ├── api_gateway/        # FastAPI REST gateway
│   └── model_gateway/      # LLM model client
├── evaluation/             # Prize readiness scorer, benchmarks
├── observability/          # Structured logging, Prometheus metrics
└── config/                 # Pydantic settings, secrets management
ui/                         # Next.js spatial canvas dashboard
tests/                      # pytest suite (193+ core tests; e2e optional)
```

## Quick Start

```bash
# One-command setup
make setup

# Start development server
make dev

# Run all tests
make test

# Run linter
make lint

# Build Docker image
make docker-build

# Start full stack (API + UI + Monitoring)
make docker-up
```

## Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

## Testing

```bash
# Full test suite
make test

# With coverage
make test-coverage

# Benchmark only
pytest tests/test_benchmark.py -v
```

## Prize Readiness

```bash
python3 -m axiom.evaluation.prize_readiness
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Metrics**: http://localhost:8000/metrics

## Contributing

See **`CONTRIBUTOR_GUIDE.md`** for day-1 onboarding, repository map, and development workflow.

```bash
make setup && make check   # install + lint + test-core
```

See `CONTRIBUTING.md` for commit conventions and `ARCHITECTURE_DECISION_RECORDS/` for design decisions.

## License

Proprietary — AXIOM Labs. All rights reserved.
