"""Tests for E&R evidence registry, discovery gate, and reproduction."""

from __future__ import annotations

import pytest

from axiom.evidence.discovery_gate import validate_discovery_label, validate_status_upgrade
from axiom.evidence.integrity import audit_registry
from axiom.evidence.models import ClaimStatus, EvidenceType, ReproductionStatus
from axiom.evidence.registry import ClaimRegistry
from axiom.evidence.reproduction import compare_provenance_runs


@pytest.fixture
def registry() -> ClaimRegistry:
    return ClaimRegistry(":memory:")


def test_register_claim_and_version_on_evidence(registry: ClaimRegistry):
    claim = registry.register_claim("Test hypothesis", author="tester")
    assert claim.status == ClaimStatus.UNKNOWN
    assert claim.version == 1

    evidence = registry.add_evidence(
        claim.claim_id,
        EvidenceType.EXPERIMENT,
        "Benchmark run completed",
    )
    updated = registry.get_claim(claim.claim_id)
    assert updated is not None
    assert evidence.evidence_id in updated.supporting_evidence_ids
    assert updated.version == 2


def test_status_upgrade_blocked_without_evidence(registry: ClaimRegistry):
    claim = registry.register_claim("Unsupported claim")
    _, gate = registry.update_status(claim.claim_id, ClaimStatus.SUPPORTED)
    assert not gate.allowed
    assert "supporting evidence" in gate.reason.lower()


def test_status_upgrade_to_verified_with_evidence(registry: ClaimRegistry):
    claim = registry.register_claim("Supported claim", status=ClaimStatus.PLAUSIBLE)
    registry.add_evidence(claim.claim_id, EvidenceType.EXPERIMENT, "Independent test passed")
    _, gate_s = registry.update_status(claim.claim_id, ClaimStatus.SUPPORTED)
    assert gate_s.allowed
    updated, gate = registry.update_status(claim.claim_id, ClaimStatus.VERIFIED)
    assert gate.allowed
    assert updated.status == ClaimStatus.VERIFIED


def test_formally_verified_requires_verifier(registry: ClaimRegistry):
    claim = registry.register_claim("Theorem claim")
    with pytest.raises(ValueError, match="verifier"):
        registry.add_evidence(
            claim.claim_id,
            EvidenceType.FORMAL_PROOF,
            "Lean proof",
            formally_verified=True,
        )


def test_formally_verified_status_gate(registry: ClaimRegistry):
    claim = registry.register_claim("Formal theorem", status=ClaimStatus.SUPPORTED)
    registry.add_evidence(
        claim.claim_id,
        EvidenceType.FORMAL_PROOF,
        "Lean 4 proof checked",
        formally_verified=True,
        verifier="lean4",
    )
    _, gate_v = registry.update_status(claim.claim_id, ClaimStatus.VERIFIED)
    assert gate_v.allowed
    updated, gate = registry.update_status(
        claim.claim_id, ClaimStatus.FORMALLY_VERIFIED, reviewer="human"
    )
    assert gate.allowed
    assert updated.status == ClaimStatus.FORMALLY_VERIFIED


def test_discovery_label_blocked_without_requirements(registry: ClaimRegistry):
    claim = registry.register_claim("Novel result candidate", status=ClaimStatus.SUPPORTED)
    registry.add_evidence(claim.claim_id, EvidenceType.EXPERIMENT, "Initial result")
    _, gate_v = registry.update_status(claim.claim_id, ClaimStatus.VERIFIED)
    assert gate_v.allowed

    _, gate = registry.add_discovery_label(claim.claim_id, "NEW_DISCOVERY")
    assert not gate.allowed
    assert "reproduction" in gate.reason.lower()


def test_discovery_label_allowed_with_requirements(registry: ClaimRegistry):
    claim = registry.register_claim("Verified theorem", status=ClaimStatus.SUPPORTED)
    registry.add_evidence(
        claim.claim_id,
        EvidenceType.FORMAL_PROOF,
        "Lean proof",
        formally_verified=True,
        verifier="lean4",
    )
    _, gate_v = registry.update_status(claim.claim_id, ClaimStatus.VERIFIED)
    assert gate_v.allowed
    _, gate_f = registry.update_status(
        claim.claim_id, ClaimStatus.FORMALLY_VERIFIED, reviewer="human"
    )
    assert gate_f.allowed

    updated, gate = registry.add_discovery_label(
        claim.claim_id,
        "NEW_THEOREM",
        reproduction_passed=True,
        independent_verification=True,
        human_review=True,
    )
    assert gate.allowed
    assert "NEW_THEOREM" in updated.labels


def test_compare_provenance_reproduced():
    original = {
        "inputs": {"benchmark_suite": "EPIC-002", "composite_score": 0.85},
        "environment": {"python_version": "3.11.0"},
    }
    reproduction = {
        "inputs": {"benchmark_suite": "EPIC-002", "composite_score": 0.85},
        "environment": {"python_version": "3.11.0"},
    }
    status, diffs = compare_provenance_runs(original, reproduction)
    assert status == ReproductionStatus.REPRODUCED
    assert not diffs


def test_compare_provenance_not_reproduced():
    original = {
        "inputs": {"benchmark_suite": "EPIC-002", "composite_score": 0.85},
        "environment": {"python_version": "3.11.0"},
    }
    reproduction = {
        "inputs": {"benchmark_suite": "OTHER", "composite_score": 0.50},
        "environment": {"python_version": "3.12.0"},
    }
    status, diffs = compare_provenance_runs(original, reproduction)
    assert status == ReproductionStatus.NOT_REPRODUCED
    assert diffs


def test_integrity_audit_detects_broken_links(registry: ClaimRegistry):
    claim = registry.register_claim("Broken link test")
    claim.supporting_evidence_ids = ["evd_missing"]
    registry._save_claim(claim)  # noqa: SLF001 — test integrity path

    report = audit_registry(registry)
    codes = {f.code for f in report.findings}
    assert "broken_evidence_link" in codes


def test_simulation_only_cannot_verify(registry: ClaimRegistry):
    claim = registry.register_claim("Simulation only", status=ClaimStatus.SUPPORTED)
    registry.add_evidence(claim.claim_id, EvidenceType.SIMULATION, "Sim result")
    _, gate = registry.update_status(claim.claim_id, ClaimStatus.VERIFIED)
    assert not gate.allowed


def test_lineage_includes_evidence(registry: ClaimRegistry):
    claim = registry.register_claim("Lineage test")
    registry.add_evidence(claim.claim_id, EvidenceType.PAPER, "Citation")
    lineage = registry.get_lineage(claim.claim_id)
    assert lineage["claim"]["claim_id"] == claim.claim_id
    assert len(lineage["evidence"]) == 1
