"""Evidence registry integrity checks (E&R §21)."""

from __future__ import annotations

from dataclasses import dataclass, field

from axiom.evidence.models import ClaimStatus, EvidenceType
from axiom.evidence.registry import ClaimRegistry


@dataclass
class IntegrityFinding:
    code: str
    severity: str
    message: str
    claim_id: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        return {
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
            "claim_id": self.claim_id,
        }


@dataclass
class IntegrityReport:
    findings: list[IntegrityFinding] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(f.severity in ("critical", "high") for f in self.findings)

    def to_dict(self) -> dict[str, object]:
        return {
            "ok": self.ok,
            "finding_count": len(self.findings),
            "findings": [f.to_dict() for f in self.findings],
        }


def audit_registry(registry: ClaimRegistry) -> IntegrityReport:
    """Run provenance integrity checks on the claim registry."""
    report = IntegrityReport()
    claims = registry.list_claims(limit=10_000)

    for claim in claims:
        evidence = registry.get_evidence_for_claim(claim.claim_id)
        evidence_ids = {e.evidence_id for e in evidence}

        if claim.status in (
            ClaimStatus.SUPPORTED,
            ClaimStatus.VERIFIED,
            ClaimStatus.FORMALLY_VERIFIED,
        ):
            if not claim.supporting_evidence_ids:
                report.findings.append(
                    IntegrityFinding(
                        code="missing_provenance",
                        severity="high",
                        message=f"Claim {claim.status.value} without supporting evidence",
                        claim_id=claim.claim_id,
                    )
                )

        for eid in claim.supporting_evidence_ids:
            if eid not in evidence_ids:
                report.findings.append(
                    IntegrityFinding(
                        code="broken_evidence_link",
                        severity="high",
                        message=f"Supporting evidence {eid} not found",
                        claim_id=claim.claim_id,
                    )
                )

        for ev in evidence:
            if ev.evidence_type == EvidenceType.FORMAL_PROOF and ev.formally_verified:
                if not ev.verifier:
                    report.findings.append(
                        IntegrityFinding(
                            code="verification_bypass",
                            severity="critical",
                            message="Formal proof marked verified without verifier",
                            claim_id=claim.claim_id,
                        )
                    )

        if claim.status == ClaimStatus.FORMALLY_VERIFIED:
            formal = [
                e
                for e in evidence
                if e.evidence_type == EvidenceType.FORMAL_PROOF and e.formally_verified
            ]
            if not formal:
                report.findings.append(
                    IntegrityFinding(
                        code="incorrect_claim_status",
                        severity="critical",
                        message="FORMALLY_VERIFIED without formal proof evidence",
                        claim_id=claim.claim_id,
                    )
                )

        for label in claim.labels:
            if label in ("NEW_THEOREM", "PROOF_OF_OPEN_PROBLEM"):
                if claim.status != ClaimStatus.FORMALLY_VERIFIED:
                    report.findings.append(
                        IntegrityFinding(
                            code="unauthorized_status_upgrade",
                            severity="high",
                            message=f"Discovery label {label} without FORMALLY_VERIFIED",
                            claim_id=claim.claim_id,
                        )
                    )

    return report
