# Security Incident Runbook

## 1. Detection

Sources: monitoring alerts, `make tss-security`, CI failures, user reports, secret scanner hits.

## 2. Containment

1. Identify affected systems and blast radius.
2. If secret exposed: rotate credential (human approval for production).
3. If active abuse: disable affected route or revoke tokens.
4. Preserve logs and provenance records — do not delete evidence.

## 3. Investigation

- Determine root cause, timeline, and data accessed.
- Check `run_provenance` and application logs.
- Record findings in `INCIDENTS.md`.

## 4. Eradication

- Apply permanent fix with regression test.
- Remove exposed secrets from repository history if committed (human approval).

## 5. Recovery

- Verify fix in safe environment.
- Run full test suite and `make tss-security`.
- Restore service with hardened configuration.

## 6. Communication

- Internal: update `SECURITY_STATUS.md` and `CURRENT_STATE.md`.
- External: founder approval required for any user/legal communication.

## 7. Postmortem

Every serious incident produces:

- Root cause analysis
- Impact assessment
- Regression test
- Runbook update
- Architecture or threat model update if needed

## Escalation

Pause autonomous remediation and request human approval for:

- Production credential rotation
- Production resource deletion
- Public service exposure changes
- Disabling security controls
