# AXIOM Master Build & Evolution Loop

**Status:** PERMANENT OPERATING DIRECTIVE  
**Last cycle:** 2026-08-09

## Operating Cycle

```text
DISCOVER → AUDIT → PRIORITIZE → DESIGN → IMPLEMENT → INTEGRATE → TEST
→ SECURITY TEST → BENCHMARK → DOCUMENT → RELEASE → REASSESS → REPEAT
```

## Artifacts

| Phase | Artifact |
|-------|----------|
| 0–2 | `AXIOM_CAPABILITY_MATRIX.md` |
| 3 | `AXIOM_TARGET_ARCHITECTURE.md` |
| 4 | Dependency graph in target architecture doc |
| 5 | Rankings in capability matrix |
| 28 | Loop health gates: `make *-health` |
| 31 | `CURRENT_STATE.md`, `CHANGELOG.md`, `TASK_QUEUE.md` |

## Health Gates

```bash
make erl-health simr-health fmtp-health sec-health frce-health skai-health cel-health
```

## Anti-Patterns (never)

- Mark documentation as implementation
- Create fake APIs or disconnected UI
- Suppress errors to pass tests
- Claim discovery without verification
- Declare milestones complete without E2E validation

## Stop Conditions (founder input required)

Product strategy, pricing, major architectural pivot, legal/compliance,
production destructive actions, major cloud costs, external credentials,
scientific claims requiring expert judgment, potential major discoveries.

## Last Cycle Report

See commit message and `AXIOM_CAPABILITY_MATRIX.md` for full audit.

**Recommended next initiative:** P0-WEB — honest public landing (highest product leverage, unblocked).
