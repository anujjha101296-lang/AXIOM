#!/usr/bin/env bash
# Golden Demo — Milestone 006
# Starts API, validates demo endpoints, prints UI URL.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

API_PORT="${API_PORT:-8000}"
UI_PORT="${UI_PORT:-3000}"
API_TOKEN="${AXIOM_API_TOKEN:-axiom-dev-token}"

echo "═══ AXIOM Golden Demo (v0.5-demo) ═══"
echo ""

# Check if API already running
if curl -sf "http://localhost:${API_PORT}/demo/health" >/dev/null 2>&1; then
  echo "✓ API already running on port ${API_PORT}"
else
  echo "Starting API on port ${API_PORT}..."
  AXIOM_API_TOKEN="$API_TOKEN" python3 -m uvicorn axiom.services.api_gateway.main:app \
    --port "$API_PORT" --host 0.0.0.0 &
  API_PID=$!
  trap 'kill $API_PID 2>/dev/null || true' EXIT

  for i in $(seq 1 30); do
    if curl -sf "http://localhost:${API_PORT}/demo/health" >/dev/null 2>&1; then
      break
    fi
    sleep 0.5
  done
fi

echo ""
echo "── Demo API Health ──"
curl -s "http://localhost:${API_PORT}/demo/health" | python3 -m json.tool

echo ""
echo "── Demo State Summary ──"
curl -s "http://localhost:${API_PORT}/demo/state" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(f'  Project: {d[\"project\"][\"name\"]}')
print(f'  Papers: {len(d[\"papers\"])}')
print(f'  Concepts: {len(d[\"knowledge_nodes\"])}')
print(f'  Hypotheses: {len(d[\"hypotheses\"])}')
print(f'  Tour steps: {len(d[\"tour_steps\"])}')
"

echo ""
echo "═══ Golden Demo Ready ═══"
echo ""
echo "  UI:  http://localhost:${UI_PORT}/demo"
echo "  API: http://localhost:${API_PORT}/demo/state"
echo ""
echo "  Start UI:  cd ui && npm run dev"
echo "  Then click ▶ Play Demo"
echo ""
echo "  Presenter notes: docs/demo/PRESENTER_NOTES.md"
echo ""
