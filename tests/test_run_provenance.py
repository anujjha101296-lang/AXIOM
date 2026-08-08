"""Tests for H1-OBS unified run provenance records."""

from __future__ import annotations

import json
import sqlite3
import time

import pytest
from fastapi.testclient import TestClient

from axiom.evaluation.frameworks.capability import CapabilitySnapshot, CapabilityDimension
from axiom.evaluation.frameworks.evidence import make_gated_dimension_score, EvidenceState
from axiom.observability.run_provenance import (
    ProvenanceStore,
    build_scep_provenance,
    capture_environment,
    record_rvp_run,
    record_scep_run,
    rollup_evidence_tier,
)
from axiom.research_validation.engine import ResearchValidationEngine
from axiom.research_validation.models import ResearchRunConfig
from axiom.services.api_gateway.main import app

client = TestClient(app)


class TestProvenanceHelpers:
    def test_capture_environment_has_required_fields(self):
        env = capture_environment()
        assert "python_version" in env
        assert "app_version" in env
        assert "platform" in env

    def test_rollup_evidence_tier_detects_simulated(self):
        tier = rollup_evidence_tier({
            "mathematical_reasoning": "measured",
            "proof_verification": "simulated",
        })
        assert tier["aggregate"] == "simulated"
        assert tier["has_simulated"] is True

    def test_rollup_evidence_tier_all_measured(self):
        tier = rollup_evidence_tier({
            "mathematical_reasoning": "measured",
            "proof_verification": "measured",
        })
        assert tier["aggregate"] == "measured"
        assert tier["has_simulated"] is False

    def test_build_scep_provenance_includes_inputs_and_evidence(self):
        snapshot = CapabilitySnapshot(run_id="abc12345", timestamp="2026-01-01T00:00:00Z")
        snapshot.dimension_scores = [
            make_gated_dimension_score(
                CapabilityDimension.MATHEMATICAL_REASONING,
                1.0,
                10,
                evidence_state=EvidenceState.MEASURED,
            )
        ]
        snapshot.compute_composite()

        record = build_scep_provenance(
            snapshot=snapshot,
            db_path=":memory:",
            started_at="2026-01-01T00:00:00Z",
            finished_at="2026-01-01T00:00:01Z",
            duration_ms=1000.0,
            benchmark_case_count=10,
            total_benchmark_ms=500.0,
            trigger="test",
        )
        assert record.run_type == "scep"
        assert record.inputs["benchmark_suite"] == "EPIC-002"
        assert record.inputs["benchmark_case_count"] == 10
        assert record.evidence_tier["aggregate"] == "measured"
        assert record.environment["python_version"]


class TestProvenanceStore:
    def test_save_and_get_scep_record(self, tmp_path):
        db_path = str(tmp_path / "prov.db")
        store = ProvenanceStore(db_path)

        snapshot = CapabilitySnapshot(run_id="run00001", timestamp="2026-01-01T00:00:00Z")
        snapshot.dimension_scores = [
            make_gated_dimension_score(
                CapabilityDimension.PROOF_VERIFICATION,
                0.9,
                5,
                evidence_state=EvidenceState.SIMULATED,
            )
        ]
        snapshot.compute_composite()

        record = record_scep_run(
            db_path,
            snapshot,
            [],
            started_at="2026-01-01T00:00:00Z",
            duration_ms=42.0,
            trigger="test",
        )
        fetched = store.get("scep", "run00001")
        assert fetched is not None
        assert fetched["run_id"] == "run00001"
        assert fetched["inputs"]["trigger"] == "test"
        assert fetched["duration_ms"] == record.duration_ms

    def test_list_runs_by_type(self, tmp_path):
        db_path = str(tmp_path / "prov2.db")
        store = ProvenanceStore(db_path)

        record_rvp_run(
            db_path,
            run_id="rvp001",
            config_hash="abc",
            config={"stage": 0},
            started_at="2026-01-01T00:00:00Z",
            finished_at="2026-01-01T00:00:01Z",
            duration_ms=10.0,
            stage=0,
            problem_id="p1",
            answer_score=1.0,
            passed=True,
        )

        rvp_runs = store.list_runs(run_type="rvp")
        assert len(rvp_runs) == 1
        assert rvp_runs[0]["run_type"] == "rvp"


class TestProvenanceAPI:
    def test_list_provenance_empty(self):
        response = client.get("/provenance/runs")
        assert response.status_code == 200
        assert "count" in response.json()
        assert "runs" in response.json()

    def test_get_provenance_not_found(self):
        response = client.get("/provenance/runs/scep/nonexistent")
        assert response.status_code == 404

    def test_eval_run_records_provenance(self, tmp_path, monkeypatch):
        monkeypatch.setenv("DB_PATH", str(tmp_path / "eval_prov.db"))
        from axiom.config import settings
        settings.__dict__["db_path"] = str(tmp_path / "eval_prov.db")

        response = client.post("/eval/run")
        assert response.status_code == 200
        run_id = response.json()["run_id"]

        prov = client.get(f"/provenance/runs/scep/{run_id}")
        assert prov.status_code == 200
        body = prov.json()
        assert body["run_type"] == "scep"
        assert body["inputs"]["benchmark_suite"] == "EPIC-002"
        assert "evidence_tier" in body
        assert body["duration_ms"] > 0

        detail = client.get(f"/eval/runs/{run_id}")
        assert detail.status_code == 200
        assert detail.json()["provenance"]["run_id"] == run_id

    def test_eval_history_includes_provenance_summary(self, tmp_path, monkeypatch):
        monkeypatch.setenv("DB_PATH", str(tmp_path / "hist.db"))
        from axiom.config import settings
        settings.__dict__["db_path"] = str(tmp_path / "hist.db")

        client.post("/eval/run")
        history = client.get("/eval/history")
        assert history.status_code == 200
        entries = history.json()
        assert len(entries) >= 1
        assert "evidence_tier" in entries[0]
        assert "duration_ms" in entries[0]


class TestRVPProvenanceIntegration:
    def test_rvp_run_creates_provenance(self, tmp_path):
        db_path = str(tmp_path / "rvp_prov.db")
        engine = ResearchValidationEngine(db_path)
        config = ResearchRunConfig(stage=0, problem_ids=["ka_infra_000"], seed=42)
        results = engine.run_validation(config)
        assert len(results) == 1

        run_id = results[0].run_id
        store = ProvenanceStore(db_path)
        prov = store.get("rvp", run_id)
        assert prov is not None
        assert prov["config_hash"] == results[0].config_hash
        assert prov["inputs"]["stage"] == 0
        assert prov["inputs"]["problem_id"] == "ka_infra_000"
        assert prov["evidence_tier"]["aggregate"] == "measured"
        assert "environment" in prov
        assert "git_sha" in prov["environment"] or "python_version" in prov["environment"]

    def test_rvp_result_embeds_provenance(self, tmp_path):
        db_path = str(tmp_path / "rvp_embed.db")
        engine = ResearchValidationEngine(db_path)
        config = ResearchRunConfig(stage=0, problem_ids=["ka_infra_001"], seed=1)
        result = engine.run_validation(config)[0]
        assert result.provenance["run_type"] == "rvp"
        assert result.provenance["inputs"]["stage"] == 0
        assert "environment" in result.provenance

    def test_provenance_table_exists_after_rvp(self, tmp_path):
        db_path = str(tmp_path / "rvp_schema.db")
        engine = ResearchValidationEngine(db_path)
        config = ResearchRunConfig(stage=0, problem_ids=["ka_infra_002"], seed=7)
        engine.run_validation(config)

        conn = sqlite3.connect(db_path)
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        conn.close()
        assert "run_provenance" in tables
