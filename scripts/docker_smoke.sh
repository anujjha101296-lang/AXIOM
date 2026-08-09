#!/usr/bin/env bash
# Docker compose smoke for AXIOM MVP (api + ui).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! command -v docker >/dev/null 2>&1; then
  echo "BLOCKER: docker CLI not installed"
  exit 2
fi

if ! docker info >/dev/null 2>&1; then
  echo "BLOCKER: docker daemon not reachable (try: sudo dockerd &)"
  exit 2
fi

if [[ ! -f .env ]]; then
  cp .env.example .env 2>/dev/null || true
fi

echo "==> Building api + ui"
docker compose build api ui

echo "==> Starting api + ui"
docker compose up -d api ui

cleanup() {
  docker compose down --remove-orphans >/dev/null 2>&1 || true
}
trap cleanup EXIT

echo "==> Waiting for API health"
ok=0
for i in $(seq 1 40); do
  if curl -fsS http://localhost:8000/health >/dev/null 2>&1; then
    ok=1
    break
  fi
  sleep 2
done
if [[ "$ok" -ne 1 ]]; then
  echo "FAIL: API health never became ready"
  docker compose logs api | tail -80
  exit 1
fi

echo "==> API health OK"
curl -fsS -H "Authorization: Bearer axiom-dev-token" http://localhost:8000/health | head -c 400
echo

echo "==> Waiting for UI"
ui_ok=0
for i in $(seq 1 30); do
  if curl -fsS http://localhost:3000/ >/dev/null 2>&1; then
    ui_ok=1
    break
  fi
  sleep 2
done
if [[ "$ui_ok" -ne 1 ]]; then
  echo "FAIL: UI never became ready"
  docker compose logs ui | tail -80
  exit 1
fi

echo "==> UI OK"
echo "DOCKER_SMOKE_PASSED"
