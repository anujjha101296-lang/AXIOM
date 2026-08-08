"""Evidence & Reproducibility Loop package."""

from axiom.evidence.discovery_gate import GateResult, validate_discovery_label, validate_status_upgrade
from axiom.evidence.models import (
    ClaimStatus,
    EvidenceType,
    ReproductionStatus,
    ScientificClaim,
)
from axiom.evidence.integrity import IntegrityReport, audit_registry
from axiom.evidence.registry import ClaimRegistry, get_claim_registry
from axiom.evidence.reproduction import compare_provenance_runs

__all__ = [
    "ClaimRegistry",
    "ClaimStatus",
    "EvidenceType",
    "GateResult",
    "IntegrityReport",
    "ReproductionStatus",
    "ScientificClaim",
    "audit_registry",
    "compare_provenance_runs",
    "get_claim_registry",
    "validate_discovery_label",
    "validate_status_upgrade",
]
