# Research Integrity

**Last updated:** 2026-08-08  
**Loop:** E&R (Evidence & Reproducibility)

## Principles

AXIOM must never:

- Fabricate citations
- Invent experiments or results
- Invent evidence
- Hide failed experiments
- Delete contradictory evidence
- Convert speculation into fact
- Suppress uncertainty

Every failed research direction remains available for future analysis unless explicitly archived.

## Enforcement

| Mechanism | Location |
|-----------|----------|
| Discovery gate | `axiom/evidence/discovery_gate.py` |
| Status upgrade validation | Blocks unsupported upgrades |
| Integrity audit | `axiom/evidence/integrity.py` |
| Versioned artifacts | `er_claim_versions` table |
| Automated tests | `tests/test_evidence_registry.py` |

## Audit questions

For each major conclusion:

1. Is the question precise?
2. Are assumptions explicit?
3. Are sources reliable?
4. Is evidence sufficient?
5. Are alternative explanations considered?
6. Were competing hypotheses tested?
7. Were counterexamples attempted?
8. Was the result independently verified?
9. Can it be reproduced?
10. Are limitations documented?

## Reporting violations

Record integrity issues in this document and in `GET /evidence/integrity` findings.
