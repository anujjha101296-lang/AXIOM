"""Tests for the Scientific Method Engine."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from axiom.scientific_method.engine import (
    SMEBypassError,
    SMEPhaseIncompleteError,
    ScientificMethodEngine,
)
from axiom.scientific_method.models import PHASE_ORDER, SMEPhase, SMESessionStatus
from axiom.services.api_gateway.main import app

client = TestClient(app)


class TestSMEEngine:
    def test_full_cycle_completes_all_phases(self, tmp_path):
        db = str(tmp_path / "sme.db")
        engine = ScientificMethodEngine(db)
        session = engine.create_session(
            objective="Does every even integer greater than 2 equal the sum of two primes?",
            domain="mathematics",
        )
        result = engine.run_full_cycle(session.session_id)

        assert result.status == SMESessionStatus.COMPLETED
        assert len(result.phases_completed) == 10
        assert len(result.hypotheses) >= 2
        assert len(result.criticisms) >= 2
        assert result.human_review is not None
        assert "Research Notebook" in result.human_review.research_notebook

    def test_cannot_skip_phases(self, tmp_path):
        db = str(tmp_path / "sme_skip.db")
        engine = ScientificMethodEngine(db)
        session = engine.create_session(objective="Test skip", domain="research")

        with pytest.raises(SMEPhaseIncompleteError):
            engine.execute_phase(session.session_id, SMEPhase.HYPOTHESIS_GENERATION)

    def test_hypothesis_minimum_enforced(self, tmp_path):
        db = str(tmp_path / "sme_hyp.db")
        engine = ScientificMethodEngine(db)
        session = engine.create_session(objective="Prime gaps", domain="math")

        for phase in PHASE_ORDER[:4]:
            session = engine.execute_phase(session.session_id, phase)

        assert len(session.hypotheses) >= 2
        for h in session.hypotheses:
            assert h.reasoning
            assert h.weaknesses
            assert 0.0 <= h.confidence <= 1.0

    def test_workflow_gate_blocks_bypass(self, tmp_path):
        db = str(tmp_path / "sme_gate.db")
        engine = ScientificMethodEngine(db)

        with pytest.raises(SMEBypassError):
            engine.validate_workflow_gate("research", None)

        session = engine.create_session(objective="Gated research", domain="research")
        with pytest.raises(SMEBypassError):
            engine.validate_workflow_gate("research", session.session_id, require_completed=True)

        engine.run_full_cycle(session.session_id)
        validated = engine.validate_workflow_gate(
            "research", session.session_id, require_completed=True
        )
        assert validated.is_complete()

    def test_memory_persisted(self, tmp_path):
        db = str(tmp_path / "sme_mem.db")
        engine = ScientificMethodEngine(db)
        session = engine.create_session(objective="Memory test", domain="research")
        engine.run_full_cycle(session.session_id)

        loaded = engine.get_session(session.session_id)
        assert loaded is not None
        assert len(loaded.memory_records) >= 1


class TestSMEAPI:
    def test_list_phases(self):
        r = client.get("/sme/phases")
        assert r.status_code == 200
        assert len(r.json()) == 10

    def test_create_and_run_session(self, tmp_path, monkeypatch):
        monkeypatch.setenv("DB_PATH", str(tmp_path / "api_sme.db"))
        from axiom.config import settings
        settings.__dict__["db_path"] = str(tmp_path / "api_sme.db")

        r = client.post("/sme/sessions", json={
            "objective": "Test the Riemann hypothesis for low zeros",
            "domain": "mathematics",
            "research_question": "Do all non-trivial zeros lie on Re(s)=1/2?",
            "success_criteria": ["At least one hypothesis verified"],
        })
        assert r.status_code == 201
        session_id = r.json()["session_id"]

        r2 = client.post(f"/sme/sessions/{session_id}/run")
        assert r2.status_code == 200
        body = r2.json()
        assert body["status"] == "completed"
        assert len(body["phases_completed"]) == 10

        r3 = client.get(f"/sme/sessions/{session_id}/notebook")
        assert r3.status_code == 200
        assert "research_notebook" in r3.json()

    def test_workflow_requires_sme(self, tmp_path, monkeypatch):
        monkeypatch.setenv("DB_PATH", str(tmp_path / "wf_sme.db"))
        from axiom.config import settings
        settings.__dict__["db_path"] = str(tmp_path / "wf_sme.db")

        r = client.post("/workflows", json={
            "objective": "Research without SME",
            "domain": "research",
            "sme_session_id": "fake",
        })
        assert r.status_code == 403

    def test_workflow_with_completed_sme(self, tmp_path, monkeypatch):
        monkeypatch.setenv("DB_PATH", str(tmp_path / "wf_ok.db"))
        from axiom.config import settings
        settings.__dict__["db_path"] = str(tmp_path / "wf_ok.db")

        r = client.post("/sme/sessions", json={
            "objective": "Workflow integration test",
            "domain": "research",
        })
        session_id = r.json()["session_id"]
        client.post(f"/sme/sessions/{session_id}/run")

        r2 = client.post("/workflows", json={
            "objective": "Workflow integration test",
            "domain": "research",
            "sme_session_id": session_id,
        })
        assert r2.status_code == 201
        assert r2.json()["id"]

    def test_validate_gate_endpoint(self, tmp_path, monkeypatch):
        monkeypatch.setenv("DB_PATH", str(tmp_path / "gate.db"))
        from axiom.config import settings
        settings.__dict__["db_path"] = str(tmp_path / "gate.db")

        r = client.post("/sme/sessions", json={"objective": "Gate test", "domain": "research"})
        session_id = r.json()["session_id"]
        client.post(f"/sme/sessions/{session_id}/run")

        r2 = client.post("/sme/validate-gate", params={
            "domain": "research",
            "sme_session_id": session_id,
            "require_completed": True,
        })
        assert r2.status_code == 200
        assert r2.json()["valid"] is True
