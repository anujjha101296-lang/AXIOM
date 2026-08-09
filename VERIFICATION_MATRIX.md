# Verification Matrix

**Last updated:** 2026-08-09  
**System:** VFACTORY (Verification Factory)

## Capability registry

| ID | Name | Domain | Status | Health | Tests |
|----|------|--------|--------|--------|-------|
| cap_erl | Evidence & Reproducibility Loop | research | UNTESTED | erl-health | test_evidence_registry |
| cap_simr | Scientific Intelligence & Model Routing | ai | UNTESTED | simr-health | test_simr_routing |
| cap_fmtp | Formal Mathematics & Theorem-Proving | scientific | UNTESTED | fmtp-health | test_formal_math |
| cap_sec | Scientific Experimentation & Compute | research | UNTESTED | sec-health | test_experiment_sec |
| cap_frce | Frontier Research Campaign Engine | research | UNTESTED | frce-health | test_frce_campaign |
| cap_skai | Knowledge Acquisition & Intelligence | knowledge | UNTESTED | skai-health | test_skai_knowledge |
| cap_gcp | Grand Challenge Program | research | UNTESTED | — | test_grand_challenge |
| cap_research_ws | Research Workspace | product | UNTESTED | — | test_research_workspace |
| cap_workflow | Workflow Engine | agent | UNTESTED | — | test_workflow_mount |
| cap_egs | Epistemic Graph Store | knowledge | UNTESTED | — | test_epistemic_layer |
| cap_tss | Trust Security & Safety | security | UNTESTED | tss-security | tss_security_check |
| cap_api_gateway | API Gateway | api | UNTESTED | — | test_api |
| cap_cel | Continuous Evolution Loop | infrastructure | UNTESTED | cel-health | — |
| cap_landing | Public Landing Page | product | UNTESTED | — | — |
| cap_vfactory | Verification Factory | infrastructure | UNTESTED | vfactory-health | test_vfactory |

## Test pyramid coverage

| Level | Name | Automated | Gate |
|-------|------|-----------|------|
| 1 | Static analysis | ✅ ruff E9 | CI |
| 2 | Unit tests | ✅ pytest (excl e2e) | CI |
| 3 | Component | ✅ loop health checks | make *-health |
| 4 | API | ⚠️ Partial | test_api + route tests |
| 5 | Database | ⚠️ Partial | migration tests |
| 6 | Service integration | ⚠️ Partial | loop health checks |
| 7 | E2E | ⚠️ Harness pending | tests/e2e (excluded CI) |
| 8 | Security | ✅ tss-security | make tss-security |
| 9 | Performance | ❌ Not automated | — |
| 10 | Scientific | ⚠️ Partial | loop benchmarks |

## User journeys

| Journey | Description | Status |
|---------|-------------|--------|
| A | Research workspace (project → note → search → session) | ✅ Automated |
| B | Research campaign (create → scope → plan → cycle) | ✅ Automated |
| C | Formal math (formalize → compile gate) | ✅ Automated |
| D | Sandbox recovery (success + safe failure) | ✅ Automated |

## Refresh

```bash
make vfactory-health
curl -H "Authorization: Bearer axiom-dev-token" http://localhost:8000/vfactory/status
```
