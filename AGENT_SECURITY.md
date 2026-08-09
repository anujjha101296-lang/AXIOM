# Agent Security

**Last updated:** 2026-08-08

## Policy

Agents must NOT automatically receive unrestricted shell, filesystem, network, database, cloud, or production access.

## Tool risk classification

Implemented in `axiom/security/tool_permissions.py`:

| Class | Examples | Authorization |
|-------|----------|---------------|
| READ_ONLY | Read paper, query graph | None |
| LOW_RISK_WRITE | Create research note | None |
| HIGH_RISK_WRITE | Execute generated code | **Required** |
| DESTRUCTIVE | Delete data | **Required** |
| PRIVILEGED | Change infrastructure | **Required** |
| EXTERNAL_SIDE_EFFECT | Send external message | **Required** |

## Required agent envelope (target state)

Every long-running agent process should declare:

- Identity and role
- Allowed tools and resources
- Execution/token/time budgets
- Max iterations and parallel workers
- Allowed file paths and network destinations
- Termination conditions and emergency stop

## Current state

| Capability | Status |
|------------|--------|
| Tool risk enum | ✅ Implemented |
| Agent identity/RBAC | ⚠️ Partial (API roles exist) |
| Execution budgets | ❌ Not enforced |
| Code execution sandbox | ❌ Not implemented |
| MCP tool policy | ❌ Document when integrated |

## Abnormal behavior response

STOP → PRESERVE STATE → REPORT → DO NOT CONTINUE BLINDLY
