"""Tests for H1-OBS unified run provenance records (SCEP)."""

from __future__ import annotations

import sqlite3

import pytest
from fastapi.testclient import TestClient

from axiom.evaluation.frameworks.capability import (
    CapabilityDimension,
    CapabilitySnapshot,
    EvidenceState,
    make_dimension_score_from_benchmark,
)
from axiom.observability.run_provenance import (
    ProvenanceStore,
    build_scep_provenance,
    capture_environment,
    record_scep_run,
)
from axiom.services.api_gateway.main import app

client = TestClient(app)


class TestProvenanceHelpers:
    def test_capture_environment_has_required_fields(self):
        env = capture_environment()
        assert "python_version" in env
        assert "app_version" in env
        assert "platform" in env

    def test_build_scep_provenance_includes_inputs_and_evidence(self):
        snapshot = CapabilitySnapshot(run_id="abc12345", timestamp="2026-01-01T00:00:00Z")
        snapshot.dimension_scores = [
            make_dimension_score_from_benchmark(
                CapabilityDimension.MATHEMATICAL_REASONING, 1.0, 10
            ),
            make_dimension_score_from_benchmark(
                CapabilityDimension.PROOF_VERIFICATION, 0.9, 5
            ),
        ]
        snapshot.compute_composite()

        record = build_scep_provenance(
            snapshot=snapshot,
            db_path=":memory:",
            started_at="2026-01-01T00:00:00Z",
            finished_at="2026-01-01T00:00:01Z",
            duration_ms=1000.0,
            benchmark_case_count=15,
            total_benchmark_ms=500.0,
            trigger="test",
        )
        assert record.run_type == "scep"
        assert record.inputs["benchmark_suite"] == "EPIC-002"
        assert record.inputs["benchmark_case_count"] == 15
        assert record.evidence_tier["aggregate"] == EvidenceState.SIMULATED.value
        assert record.environment["python_version"]


class TestProvenanceStore:
    def test_save_and_get_scep_record(self, tmp_path):
        db_path = str(tmp_path / "prov.db")
        store = ProvenanceStore(db_path)

        snapshot = CapabilitySnapshot(run_id="run00001", timestamp="2026-01-01T00:00:00Z")
        snapshot.dimension_scores = [
            make_dimension_score_from_benchmark(
                CapabilityDimension.PROOF_VERIFICATION, 0.9, 5
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

        snapshot = CapabilitySnapshot(run_id="scep001", timestamp="2026-01-01T00:00:00Z")
        snapshot.dimension_scores = [
            make_dimension_score_from_benchmark(
                CapabilityDimension.MATHEMATICAL_REASONING, 0.5, 3
            )
        ]
        snapshot.compute_composite()
        record_scep_run(db_path, snapshot, [], trigger="test")

        scep_runs = store.list_runs(run_type="scep")
        assert len(scep_runs) == 1
        assert scep_runs[0]["run_type"] == "scep"

    def test_provenance_table_created(self, tmp_path):
        db_path = str(tmp_path / "schema.db")
        ProvenanceStore(db_path)
        conn = sqlite3.connect(db_path)
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        conn.close()
        assert "run_provenance" in tables


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
        db_file = str(tmp_path / "eval_prov.db")
        monkeypatch.setenv("DB_PATH", db_file)
        from axiom.config import settings
        settings.__dict__["db_path"] = db_file

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
        db_file = str(tmp_path / "hist.db")
        monkeypatch.setenv("DB_PATH", db_file)
        from axiom.config import settings
        settings.__dict__["db_path"] = db_file

        client.post("/eval/run")
        history = client.get("/eval/history")
        assert history.status_code == 200
        entries = history.json()
        assert len(entries) >= 1
        assert "evidence_tier" in entries[0]
        assert "duration_ms" in entries[0]
