# AXIOM Private Alpha Support & SLA Policy

## 1. Support Severity Matrix

| Severity Level | Definition | Target First Response | Resolution Target |
| :--- | :--- | :--- | :--- |
| **P0 — Critical** | System unavailable, security issue, or authentication outage | **< 1 Hour** | **< 4 Hours** |
| **P1 — High** | Core research, sandbox execution, or Lean 4 verification workflow broken | **< 4 Hours** | **< 24 Hours** |
| **P2 — Medium** | Degraded functionality or minor API routing slowdown | **< 12 Hours** | **< 48 Hours** |
| **P3 — Low** | Cosmetic UI display issue or non-blocking feature request | **< 24 Hours** | Next Sprint |

## 2. Escalation & Triage Workflow
1. **Capture**: User reports issue via post-session feedback modal or support ticket with safe `request_id`.
2. **Reproduce**: Support engineer executes `axiom/demo/seed.py` and attempts reproduction on staging environment.
3. **Fix**: Patch submitted via pull request; full regression suite run (`pytest`).
4. **Deploy & Verify**: Release candidate tag deployed and confirmed with reporting user.
