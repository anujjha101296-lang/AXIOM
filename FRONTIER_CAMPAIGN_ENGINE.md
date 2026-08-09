# Frontier Campaign Engine Status

**Version:** 1.0  
**Status:** Operational (integration layer)

## Capabilities

| Capability | Status |
|------------|--------|
| Campaign as first-class object | ✅ |
| State machine (PROPOSED → … → terminal) | ✅ |
| Research graph with decomposition | ✅ |
| Multi-agent research roles | ✅ (role definitions) |
| SIMR strategy generation | ✅ |
| SEC sandboxed experiments | ✅ |
| FMTP formalization track | ✅ |
| E&R claim/evidence registration | ✅ |
| GCP campaign linking | ✅ (optional) |
| Immutable checkpoints | ✅ |
| Human review gates | ✅ |
| Pivot mechanism | ✅ |
| Exploit/explore resource allocation | ✅ |
| Global research memory compounding | ✅ |
| Challenge ladder levels 0–9 | ✅ |
| Graduated contribution levels | ✅ |

## API

Prefix: `/frce/*`

Key endpoints:
- `POST /frce/campaigns` — create campaign
- `POST /frce/campaigns/{id}/scope` — decompose problem
- `POST /frce/campaigns/{id}/plan` — generate strategies via SIMR
- `POST /frce/campaigns/{id}/cycle` — run one research cycle
- `GET /frce/campaigns/{id}/dashboard` — researcher-facing status

## Verification

```bash
make frce-health
cd /tmp && pytest /workspace/tests/test_frce_campaign.py -q
```

## Known limitations (v1)

- Literature investigation track is stub (records observation, no arXiv integration in cycle)
- Workflow engine not yet bound to campaign execution
- Dashboard is API-only (no UI)
- Independent replicator role not fully automated
- Millennium gate requires human strategic approval
