#!/usr/bin/env bash
# scripts/setup.sh — One-command AXIOM development environment setup
set -euo pipefail

BOLD="\033[1m"
GREEN="\033[32m"
CYAN="\033[36m"
RESET="\033[0m"

echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${BOLD}   AXIOM Development Environment Setup   ${RESET}"
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"

PYTHON=${PYTHON:-python3}

# ── Python check ──────────────────────────────────────────────────────────────
echo -e "\n${CYAN}[1/5] Checking Python version...${RESET}"
$PYTHON -c "import sys; assert sys.version_info >= (3, 10), f'Python 3.10+ required, got {sys.version}'"
echo -e "${GREEN}✓ Python OK: $($PYTHON --version)${RESET}"

# ── Virtual environment ───────────────────────────────────────────────────────
echo -e "\n${CYAN}[2/5] Creating virtual environment...${RESET}"
if [ ! -d ".venv" ]; then
    $PYTHON -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
echo -e "${GREEN}✓ .venv activated${RESET}"

# ── Dependencies ──────────────────────────────────────────────────────────────
echo -e "\n${CYAN}[3/5] Installing Python dependencies...${RESET}"
pip install --quiet --upgrade pip
pip install --quiet \
    fastapi uvicorn[standard] pydantic pydantic-settings \
    networkx sympy pylatexenc requests z3-solver anyio 'httpx>=0.27.0,<0.28.0' \
    pytest pytest-cov pytest-anyio ruff mypy
echo -e "${GREEN}✓ Python dependencies installed${RESET}"

# ── Environment file ──────────────────────────────────────────────────────────
echo -e "\n${CYAN}[4/5] Setting up environment...${RESET}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ .env created from .env.example${RESET}"
    echo -e "  Edit .env to configure your secrets."
else
    echo -e "${GREEN}✓ .env already exists${RESET}"
fi

# ── Node / UI dependencies ────────────────────────────────────────────────────
echo -e "\n${CYAN}[5/5] Installing UI dependencies...${RESET}"
if command -v npm &>/dev/null && [ -f "ui/package.json" ]; then
    (cd ui && npm install --silent)
    echo -e "${GREEN}✓ UI dependencies installed${RESET}"
else
    echo -e "  Skipping UI setup (npm not found or ui/package.json missing)"
fi

echo -e "\n${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${GREEN}${BOLD}✓ AXIOM setup complete!${RESET}"
echo -e ""
echo -e "  ${CYAN}Start API:${RESET}          make dev"
echo -e "  ${CYAN}Run tests:${RESET}          make test"
echo -e "  ${CYAN}Lint:${RESET}               make lint"
echo -e "  ${CYAN}Prize readiness:${RESET}    make prize-readiness"
echo -e "  ${CYAN}Full stack:${RESET}         make docker-up"
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
