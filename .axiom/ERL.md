# Evidence & Reproducibility Loop (E&R)

AXIOM preserves provenance, evidence, reproducibility, and independent verification for every important scientific result. The system prefers "I don't know" over a confident unsupported answer.

## Mission

Build a permanent chain from question through conclusion — with inspectable assumptions, sources, experiments, criticism, and verification — so no important result relies on an impressive-looking answer alone.

## Continuous loop

```text
RESEARCH RESULT → REGISTER → CAPTURE PROVENANCE → COLLECT EVIDENCE
  → ATTEMPT REPRODUCTION → INDEPENDENT VERIFICATION → COUNTEREXAMPLE SEARCH
  → FORMAL VERIFICATION (where possible) → HUMAN REVIEW → CLASSIFY RESULT
  → VERSION ARTIFACT → PUBLISH INTERNAL REPORT → ADD REGRESSION TEST → LEARN
  → NEXT RESEARCH CYCLE
```

## Operational artifacts

| Artifact | Purpose |
|----------|---------|
| `EVIDENCE_STATUS.md` | Current evidence posture |
| `REPRODUCIBILITY_STATUS.md` | Reproduction capability |
| `VERIFICATION_STATUS.md` | Independent verification status |
| `CLAIM_REGISTRY.md` | Claim registry overview |
| `RESEARCH_INTEGRITY.md` | Integrity principles and violations |
| `MILLENNIUM_READINESS.md` | Extreme-difficulty problem readiness |
| `scripts/erl_health_check.py` | Automated E&R gate |

## Code modules

- `axiom/evidence/models.py` — claims, evidence, experiments, statuses
- `axiom/evidence/registry.py` — SQLite claim registry and provenance graph
- `axiom/evidence/discovery_gate.py` — status upgrades and discovery labels
- `axiom/evidence/reproduction.py` — provenance run comparison
- `axiom/evidence/integrity.py` — provenance integrity audits
- `axiom/services/api_gateway/routes/evidence_api.py` — `/evidence/*` API

## API surface

| Endpoint | Purpose |
|----------|---------|
| `POST /evidence/claims` | Register a scientific claim |
| `GET /evidence/claims` | List claims |
| `POST /evidence/claims/{id}/evidence` | Attach evidence |
| `POST /evidence/claims/{id}/status` | Update status (gated) |
| `POST /evidence/claims/{id}/labels` | Apply discovery label (gated) |
| `GET /evidence/claims/{id}/lineage` | Provenance lineage |
| `GET /evidence/dashboard` | Evidence dashboard |
| `POST /evidence/reproduction/compare` | Compare SCEP/RVP runs |
| `GET /evidence/integrity` | Integrity audit |

## Discovery gate

Major discovery labels (`NEW_DISCOVERY`, `NEW_THEOREM`, `NOVEL_RESULT`, `PROOF_OF_OPEN_PROBLEM`) require:

- `VERIFIED` or `FORMALLY_VERIFIED` status
- Successful reproduction
- Independent verification
- Human expert review
- `FORMALLY_VERIFIED` for theorem/open-problem labels

`FORMALLY_VERIFIED` requires formal proof evidence from an actual verifier — never from model-generated informal proofs alone.

## Production requirements

```bash
REQUIRE_AUTH_FOR_EVIDENCE_ROUTES=true
```

## Relationship to other loops

- **H1-OBS** — SCEP run provenance feeds reproduction comparison
- **S0-E4** — `EvidenceState` on capability snapshots
- **TSS** — optional authentication for `/evidence/*`
- **CEL** — capability engineering drives what gets registered

## Constraints

Do NOT: fabricate citations, invent experiments, hide failed attempts, or upgrade claim status without evidence. Failed research directions remain discoverable unless explicitly archived.
