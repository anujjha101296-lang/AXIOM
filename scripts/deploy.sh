#!/usr/bin/env bash
# scripts/deploy.sh — Production deploy via docker-compose
set -euo pipefail

BOLD="\033[1m"
GREEN="\033[32m"
RED="\033[31m"
RESET="\033[0m"

echo -e "${BOLD}AXIOM Production Deployment${RESET}"

# ── Pre-flight checks ─────────────────────────────────────────────────────────
if [ ! -f ".env" ]; then
    echo -e "${RED}ERROR: .env file not found. Copy .env.example and fill in secrets.${RESET}"
    exit 1
fi

# Warn if default token
if grep -q "axiom-dev-token" .env; then
    echo -e "${RED}WARNING: Default API token detected. Change AXIOM_API_TOKEN before deploying!${RESET}"
fi

if grep -q "CHANGE-ME" .env; then
    echo -e "${RED}WARNING: Default JWT secret detected. Change JWT_SECRET_KEY before deploying!${RESET}"
fi

# ── Build ─────────────────────────────────────────────────────────────────────
echo -e "\n[1/3] Building Docker images..."
docker compose build --no-cache

# ── Deploy ────────────────────────────────────────────────────────────────────
echo -e "\n[2/3] Starting services..."
docker compose up -d

# ── Health check ──────────────────────────────────────────────────────────────
echo -e "\n[3/3] Waiting for health check..."
MAX_ATTEMPTS=30
ATTEMPT=0
until curl -sf http://localhost:8000/health > /dev/null 2>&1; do
    ATTEMPT=$((ATTEMPT + 1))
    if [ "$ATTEMPT" -ge "$MAX_ATTEMPTS" ]; then
        echo -e "${RED}ERROR: API gateway did not become healthy within 30s${RESET}"
        docker compose logs api
        exit 1
    fi
    sleep 1
done

echo -e "\n${GREEN}${BOLD}✓ AXIOM deployed successfully!${RESET}"
echo -e "  API:     http://localhost:8000"
echo -e "  Docs:    http://localhost:8000/docs"
echo -e "  Metrics: http://localhost:8000/metrics"
echo -e "  UI:      http://localhost:3000"
