# AXIOM State

**Last updated:** 2026-08-09  
**Directive:** AXIOM-MASTER-001  
**Branch:** `cursor/integrate-mainline-dc7e`

## One-line status

Integrated tip is MVP-ready for founder merge: auth, ownership, research, campaigns, experiments, docker smoke green.

## What works

| Area | Status |
|------|--------|
| Research `/research` | Live |
| Auth + logout/login persistence | Live |
| Project / FRCE / SEC ownership | Live |
| Campaigns + agent activity | Live |
| Experiments UI | Live |
| Docker compose api+ui | Live (`scripts/docker_smoke.sh`) |

## Next

1. **Founder merges PR #29 to `main`**
2. Controlled internet research polish
3. Close superseded draft PRs after merge

## Evidence

- Resource ownership tests green
- `DOCKER_SMOKE_PASSED` (api healthy + ui reachable)
- PR: https://github.com/anujjha101296-lang/AXIOM/pull/29
