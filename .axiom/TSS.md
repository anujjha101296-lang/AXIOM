# Trust, Security & Safety Loop (TSS)

AXIOM continuously discovers, measures, reduces, and documents security and safety risk. Security is not a release-stage activity.

## Mission

Make AXIOM secure, trustworthy, privacy-preserving, resilient, and safe for increasingly autonomous scientific research — without claiming "secure" without evidence.

## Continuous loop

```text
DISCOVER → THREAT MODEL → SCAN → PRIORITIZE → FIX → TEST
  → RED TEAM → BENCHMARK → DEPLOY (safe env) → OBSERVE
  → REVIEW → DOCUMENT → COMMIT → repeat
```

## Operational artifacts

| Artifact | Purpose |
|----------|---------|
| `SECURITY_STATUS.md` | Current security posture |
| `THREAT_MODEL.md` | Living threat model |
| `DEPENDENCY_SECURITY.md` | Supply chain status |
| `AGENT_SECURITY.md` | Agent/tool boundaries |
| `INFRA_SECURITY.md` | Docker/CI posture |
| `INCIDENTS.md` | Security incident log |
| `SECURITY_SCORECARD.md` | Measurable maturity |
| `SECURITY_INCIDENT_RUNBOOK.md` | Response procedures |
| `scripts/tss_security_check.py` | Automated TSS gate |

## Code modules

- `axiom/security/production_guard.py` — production config audit
- `axiom/security/secret_scan.py` — repository secret pattern scan
- `axiom/security/tool_permissions.py` — tool risk classification
- `axiom/security/content_trust.py` — untrusted content isolation heuristics
- `axiom/security/deps.py` — optional route authentication

## Production requirements

Set before `ENVIRONMENT=production`:

```bash
JWT_SECRET_KEY=$(openssl rand -hex 32)
AXIOM_API_TOKEN=$(openssl rand -hex 32)
REQUIRE_AUTH_FOR_EVAL_ROUTES=true
REQUIRE_AUTH_FOR_GCP_ROUTES=true
REQUIRE_AUTH_FOR_PROVENANCE_ROUTES=true
DEBUG=false
```

## Constraints

Do NOT automatically: rotate production credentials, delete production resources, expose services publicly, or disable security controls to pass tests.

High-impact changes require human approval.

## Relationship to CEL and AOL

- **CEL** — capability engineering
- **AOL** — platform operations health
- **TSS** — trust, security, and safety (this loop)
