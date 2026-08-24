"""Regression tests for verification truthfulness (S0-E3)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from axiom.core.knowledge_graph.schema import VerificationTier
from axiom.core.verification.truthfulness import (
    EvidenceMode,
    assign_from_proof_search,
    assign_from_smt_modular,
    assert_not_false_formal_proof,
    classify_compiler_status,
    is_simulated_compiler_output,
)
from axiom.services.api_gateway.main import app

from axiom.services.api_gateway.auth import SECRET_TOKEN

client = TestClient(app)
headers = {"Authorization": f"Bearer {SECRET_TOKEN}"}


class TestTruthfulnessModule:
    def test_simulated_compiler_status_never_formal_proof(self):
        assignment = assign_from_proof_search(
            True,
            "simulated compile success (local Lean bin missing)",
        )
        assert_not_false_formal_proof(assignment)
        assert assignment.evidence_mode == EvidenceMode.SIMULATED
        assert assignment.formally_proven is False
        assert assignment.verification_tier == VerificationTier.TIER_1_SIMULATED

    def test_formal_compiler_success_is_formal_proof(self):
        assignment = assign_from_proof_search(True, "formally compiled successfully")
        assert assignment.formally_proven is True
        assert assignment.verification_tier == VerificationTier.TIER_2_PROVEN

    def test_smt_modular_never_tier_2(self):
        assignment = assign_from_smt_modular(True)
        assert_not_false_formal_proof(assignment)
        assert assignment.verification_tier == VerificationTier.TIER_1_SIMULATED
        assert assignment.evidence_mode == EvidenceMode.SMT_FINITE

    def test_compiler_error_not_formal(self):
        assignment = assign_from_proof_search(True, "compiler error: type mismatch")
        assert assignment.formally_proven is False
        assert assignment.verification_tier == VerificationTier.TIER_0_CONJECTURE

    def test_is_simulated_compiler_output(self):
        assert is_simulated_compiler_output("SIMULATION: Script appears structurally valid")
        assert not is_simulated_compiler_output("formally compiled successfully")

    def test_classify_compiler_status(self):
        assert classify_compiler_status("formally compiled successfully") == EvidenceMode.FORMAL_COMPILER
        assert classify_compiler_status("simulated compile success") == EvidenceMode.SIMULATED


class TestVerificationAPI:
    def test_conjecture_endpoint_labels_smt_finite_not_formal(self):
        payload = {
            "conjecture_name": "Truthfulness SMT check",
            "equation": "x + 0 == x",
            "modulus": 10,
            "variables": ["x"],
        }
        response = client.post("/verify/conjecture", json=payload, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is True
        assert data["formally_proven"] is False
        assert data["evidence_mode"] == EvidenceMode.SMT_FINITE.value
        assert data["verification_tier"] == VerificationTier.TIER_1_SIMULATED.value
        assert data["verification_tier"] != VerificationTier.TIER_2_PROVEN.value

    def test_proof_endpoint_simulated_compile_not_formal(self, monkeypatch):
        monkeypatch.setattr(
            "axiom.services.api_gateway.main.os.path.exists",
            lambda _path: False,
        )
        payload = {
            "theorem_name": "Truthfulness proof test",
            "start_expression": "x * 1 + 0",
            "target_expression": "x",
            "variables": {"x": "Int"},
        }
        response = client.post("/verify/proof", json=payload, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["is_proven"] is True
        assert data["formally_proven"] is False
        assert data["evidence_mode"] == EvidenceMode.SIMULATED.value
        assert data["verification_tier"] != VerificationTier.TIER_2_PROVEN.value
        assert "simulated" in data["compiler_status"].lower()

    def test_mip_formal_compile_reports_evidence_mode(self):
        script = (
            "import Mathlib\n"
            "theorem truthfulness_test : (1 : Nat) + 1 = 2 := by norm_num\n"
        )
        response = client.post(
            "/mip/formal/compile",
            params={"system": "lean4", "script": script, "timeout_seconds": 10},
        )
        assert response.status_code == 200
        data = response.json()
        assert "evidence_mode" in data
        assert "formally_verified" in data
        if data["evidence_mode"] == EvidenceMode.SIMULATED.value:
            assert data["formally_verified"] is False

    def test_mip_verify_claim_includes_formally_proven_flag(self):
        response = client.post(
            "/mip/verify/claim",
            json={"claim": "a + b = b + a", "timeout_seconds": 5},
        )
        assert response.status_code == 200
        data = response.json()
        assert "formally_proven" in data
        assert "evidence_modes" in data
        assert isinstance(data["formally_proven"], bool)
