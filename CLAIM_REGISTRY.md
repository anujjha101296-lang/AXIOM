# Claim Registry

**Last updated:** 2026-08-08  
**Loop:** E&R (Evidence & Reproducibility)

## Purpose

Structured registry of scientific claims with provenance, evidence, and verification status.

## Claim fields

| Field | Description |
|-------|-------------|
| `claim_id` | Unique identifier (`clm_*`) |
| `statement` | Claim text |
| `author` | Agent or human author |
| `status` | Epistemic status (see below) |
| `version` | Monotonic version number |
| `parent_claim_ids` | Dependency claims |
| `supporting_evidence_ids` | Evidence supporting the claim |
| `contradicting_evidence_ids` | Evidence against the claim |
| `labels` | Discovery labels (gated) |
| `reviewer` | Human reviewer when applicable |

## Status values

`UNKNOWN` → `SPECULATIVE` → `PLAUSIBLE` → `SUPPORTED` → `VERIFIED` → `FORMALLY_VERIFIED`

Terminal negative statuses: `REJECTED`, `DISPROVED`

## Storage

SQLite tables: `er_claims`, `er_claim_versions`, `er_evidence`, `er_sources`, `er_experiments`, `er_provenance_edges`

## API

- `POST /evidence/claims` — register
- `GET /evidence/claims` — list
- `GET /evidence/claims/{id}` — retrieve
- `GET /evidence/claims/{id}/lineage` — provenance chain

## Versioning

Claims are never silently overwritten. Each material change archives the prior version in `er_claim_versions`.
