##############################################################################
# AXIOM — Development Makefile
# Usage: make <target>
##############################################################################

.PHONY: help setup dev test test-coverage lint lint-fix type-check \
        docker-build docker-up docker-down docker-logs \
        prize-readiness self-improve engineering-health research-validation clean format

PYTHON := python3
PYTEST := $(PYTHON) -m pytest
PIP    := $(PYTHON) -m pip
RUFF   := $(PYTHON) -m ruff
MYPY   := $(PYTHON) -m mypy

# ── Colours ───────────────────────────────────────────────────────────────────
BOLD  := \033[1m
RESET := \033[0m
GREEN := \033[32m
CYAN  := \033[36m

help:  ## Show this help
	@echo "$(BOLD)AXIOM Development Commands$(RESET)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CYAN)%-22s$(RESET) %s\n", $$1, $$2}'

# ── Setup ─────────────────────────────────────────────────────────────────────
setup: ## One-command dev setup (install deps + pre-commit hooks)
	@echo "$(BOLD)Setting up AXIOM development environment...$(RESET)"
	$(PIP) install --upgrade pip
	$(PIP) install \
		fastapi uvicorn pydantic pydantic-settings \
		networkx sympy pylatexenc requests \
		z3-solver anyio httpx \
		pytest pytest-cov pytest-anyio \
		ruff mypy
	@cp -n .env.example .env 2>/dev/null || true
	@echo "$(GREEN)✓ Setup complete. Edit .env with your configuration.$(RESET)"

# ── Development ───────────────────────────────────────────────────────────────
dev: ## Start API server in hot-reload dev mode
	@echo "$(BOLD)Starting AXIOM API Gateway on :8000...$(RESET)"
	PYTHONPATH=. $(PYTHON) -m uvicorn axiom.services.api_gateway.main:app \
		--host 0.0.0.0 --port 8000 --reload

dev-ui: ## Start Next.js frontend on :3000
	@echo "$(BOLD)Starting AXIOM UI on :3000...$(RESET)"
	cd ui && npm run dev

# ── Testing ───────────────────────────────────────────────────────────────────
test: ## Run full test suite
	PYTHONPATH=. $(PYTEST) tests/ -v

test-coverage: ## Run tests with coverage report (minimum 70%)
	PYTHONPATH=. $(PYTEST) tests/ -v \
		--cov=axiom \
		--cov-report=term-missing \
		--cov-report=html:htmlcov \
		--cov-fail-under=70

test-benchmark: ## Run scientific capability benchmark only
	PYTHONPATH=. $(PYTEST) tests/test_benchmark.py -v -s

test-fast: ## Run tests excluding slow integration tests
	PYTHONPATH=. $(PYTEST) tests/ -v -m "not slow"

# ── Code Quality ──────────────────────────────────────────────────────────────
lint: ## Run ruff linter
	$(RUFF) check axiom/ tests/

lint-fix: ## Run ruff with auto-fix
	$(RUFF) check --fix axiom/ tests/

format: ## Format code with ruff formatter
	$(RUFF) format axiom/ tests/

type-check: ## Run mypy type checker
	$(MYPY) axiom/ --ignore-missing-imports --no-strict-optional

check: lint type-check test ## Run all checks (lint + types + tests)

# ── Docker ────────────────────────────────────────────────────────────────────
docker-build: ## Build the AXIOM Docker image
	docker build -t axiom-api:latest .

docker-up: ## Start full stack (API + UI + monitoring)
	docker compose up -d
	@echo "$(GREEN)✓ AXIOM stack running:$(RESET)"
	@echo "  API:      http://localhost:8000"
	@echo "  Docs:     http://localhost:8000/docs"
	@echo "  Metrics:  http://localhost:8000/metrics"
	@echo "  UI:       http://localhost:3000"

docker-down: ## Stop all Docker services
	docker compose down

docker-logs: ## Tail logs from all services
	docker compose logs -f

docker-restart: docker-down docker-up ## Restart all Docker services

# ── AXIOM Science Commands ────────────────────────────────────────────────────
prize-readiness: ## Print Prize Readiness scores for all Millennium Problems
	PYTHONPATH=. $(PYTHON) -m axiom.evaluation.prize_readiness

self-improve: ## Trigger self-improvement audit and regenerate roadmap.md
	@echo "$(BOLD)Running AXIOM Self-Improvement Loop...$(RESET)"
	PYTHONPATH=. $(PYTHON) -c \
		"from axiom.core.reasoning.self_improvement import SelfImprovementLoop; \
		 loop = SelfImprovementLoop('.'); \
		 path = loop.run(); \
		 print(f'Roadmap written to: {path}')"
	@echo "$(GREEN)✓ roadmap.md updated.$(RESET)"

engineering-health: ## Run engineering governance review and generate health reports
	@echo "$(BOLD)Running AXIOM Engineering Governance Review...$(RESET)"
	PYTHONPATH=. $(PYTHON) scripts/run_engineering_review.py
	@echo "$(GREEN)✓ Reports: ENGINEERING_HEALTH.md, PRODUCT_HEALTH.md, RESEARCH_HEALTH.md, TECH_DEBT_BOARD.md, TOP_25_PRIORITIES.md$(RESET)"

research-validation: ## Run Research Validation Program and generate reports
	@echo "$(BOLD)Running AXIOM Research Validation Program...$(RESET)"
	PYTHONPATH=. $(PYTHON) scripts/run_research_validation.py
	@echo "$(GREEN)✓ Reports: RESEARCH_VALIDATION.md, BENCHMARK_RESULTS.md, CAPABILITY_SCORE.md, NEXT_RESEARCH_TARGETS.md$(RESET)"

# ── Database ──────────────────────────────────────────────────────────────────
db-migrate: ## Run database migrations
	PYTHONPATH=. $(PYTHON) -c \
		"import sqlite3; \
		 from axiom.core.knowledge_graph.migrations import run_migrations; \
		 conn = sqlite3.connect('axiom.db'); \
		 run_migrations(conn); \
		 conn.close(); \
		 print('Migrations complete.')"

db-status: ## Show database migration status
	PYTHONPATH=. $(PYTHON) -c \
		"import sqlite3; \
		 from axiom.core.knowledge_graph.migrations import migration_status; \
		 conn = sqlite3.connect('axiom.db'); \
		 rows = migration_status(conn); \
		 [print(r) for r in rows]; \
		 conn.close()"

# ── Utilities ─────────────────────────────────────────────────────────────────
clean: ## Clean generated artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache htmlcov .coverage .mypy_cache .ruff_cache
	rm -rf /tmp/axiom_proofs

clean-all: clean ## Deep clean (also remove venv)
	rm -rf .venv node_modules ui/.next

loc: ## Count lines of code
	find axiom/ tests/ -name "*.py" | xargs wc -l | tail -1
