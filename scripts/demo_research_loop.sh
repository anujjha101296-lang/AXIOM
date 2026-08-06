#!/usr/bin/env bash
# Demo: Autonomous Research Loop v1 (Milestone 005)
set -euo pipefail

API="${API_URL:-http://localhost:8000}"
TOKEN="${AXIOM_API_TOKEN:-axiom-dev-token}"
AUTH="Authorization: Bearer ${TOKEN}"

echo "=== AXIOM Autonomous Research Loop Demo ==="
echo

echo "1. List agent roles..."
curl -sf "$API/research-loop/roles" -H "$AUTH" | python3 -c "
import sys, json
roles = json.load(sys.stdin)
print(f'   {len(roles)} specialized roles:')
for r in roles:
    print(f'   - {r[\"name\"]} ({r[\"worker_type\"]})')
"

echo
echo "2. List historical benchmarks (solutions hidden)..."
curl -sf "$API/research-loop/benchmarks" -H "$AUTH" | python3 -c "
import sys, json
for b in json.load(sys.stdin):
    print(f'   - {b[\"id\"]}: {b[\"title\"]}')
"

echo
echo "3. Run benchmark: Sum of First n Integers..."
RUN=$(curl -sf -X POST "$API/research-loop/benchmarks/run" \
  -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"benchmark_id":"bench_sum_formula","max_iterations":3}')
RUN_ID=$(echo "$RUN" | python3 -c "import sys,json; print(json.load(sys.stdin)['run_id'])")
echo "   Run ID: $RUN_ID"

echo "4. Waiting for run to complete..."
for i in $(seq 1 30); do
  DETAIL=$(curl -sf "$API/research-loop/runs/$RUN_ID" -H "$AUTH")
  STATUS=$(echo "$DETAIL" | python3 -c "import sys,json; print(json.load(sys.stdin)['status'])")
  PHASE=$(echo "$DETAIL" | python3 -c "import sys,json; print(json.load(sys.stdin)['state']['current_phase'])")
  echo "   [$i] status=$STATUS phase=$PHASE"
  if [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ] || [ "$STATUS" = "cancelled" ]; then
    break
  fi
  sleep 2
done

echo
echo "5. Run summary:"
curl -sf "$API/research-loop/runs/$RUN_ID" -H "$AUTH" | python3 -c "
import sys, json
d = json.load(sys.stdin)
s = d['state']
print(f'   Question: {s[\"research_question\"][:80]}...')
print(f'   Iterations: {s[\"current_iteration\"]}/{s[\"max_iterations\"]}')
print(f'   Confidence: {s[\"confidence\"]:.2f}')
print(f'   Subproblems: {len(s[\"subproblems\"])}')
print(f'   Hypotheses: {len(s[\"hypotheses\"])}')
print(f'   Claims: {len(s[\"claims\"])}')
print(f'   Failed attempts: {len(s[\"failed_attempts\"])}')
print(f'   Timeline events: {len(s[\"timeline\"])}')
if s.get('final_report'):
    lines = s['final_report'].split('\n')
    print('   Report preview:')
    for line in lines[:8]:
        print(f'     {line}')
"

echo
echo "=== Demo complete ==="
echo "UI: http://localhost:3000/research/runs"
