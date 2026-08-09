# Experiment Security

**Last updated:** 2026-08-09  
**Loop:** SEC (integrates with TSS)

## Sandbox controls

| Control | Status |
|---------|--------|
| Static analysis | ✅ Forbidden imports/calls |
| Subprocess isolation | ✅ Not in-app exec |
| Execution timeout | ✅ Configurable |
| Network policy | ✅ Disabled by default |
| Forbidden imports | ✅ os, subprocess, socket, etc. |

## Threat mitigations

- No arbitrary code in application environment
- No production credentials inherited
- Resource budget enforcement with termination
- Failed static analysis blocks execution

## Open gaps (TD-008)

- Container-level isolation
- Memory cgroup limits
- Full agent execution budgets

## Refresh

```bash
make sec-health
make tss-security
```
