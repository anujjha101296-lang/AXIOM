"""Tests for AXIOM Cognitive Architecture."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from axiom.cognitive import CognitiveArchitecture, architecture_manifest
from axiom.cognitive.models import CognitiveCycleStatus, CognitiveLayer
from axiom.cognitive.model_provider import HeuristicModelProvider, register_provider
from axiom.services.api_gateway.main import app

client = TestClient(app)


class TestACAManifest:
    def test_architecture_has_nine_layers(self):
        manifest = architecture_manifest()
        assert len(manifest["layers"]) == 9
        assert len(manifest["pillars"]) == 8

    def test_each_layer_maps_to_subsystem(self):
        manifest = architecture_manifest()
        for layer in manifest["layers"]:
            assert layer["subsystem_primary"].startswith("axiom.")


class TestACAEngine:
    def test_full_cycle_completes_all_layers(self, tmp_path):
        db = str(tmp_path / "aca.db")
        register_provider(HeuristicModelProvider())
        engine = CognitiveArchitecture(db, model_provider_id="heuristic")
        cycle = engine.create_cycle(
            objective="Determine if Goldbach's conjecture holds for even n < 10^6",
            domain="mathematics",
        )
        result = engine.run_full_cycle(cycle.cycle_id)

        assert result.status == CognitiveCycleStatus.COMPLETED
        assert len(result.layers_completed) == 9
        assert result.context.get("understanding") is not None
        assert result.context.get("reasoning") is not None
        assert result.context.get("verification") is not None
        assert result.context.get("reflection") is not None

    def test_cannot_skip_layers(self, tmp_path):
        db = str(tmp_path / "aca_skip.db")
        engine = CognitiveArchitecture(db, model_provider_id="heuristic")
        cycle = engine.create_cycle(objective="Skip test", domain="research")

        with pytest.raises(ValueError):
            engine.execute_layer(cycle.cycle_id, CognitiveLayer.REASONING)

    def test_model_provider_interchangeable(self, tmp_path):
        db = str(tmp_path / "aca_provider.db")
        register_provider(HeuristicModelProvider())
        engine = CognitiveArchitecture(db, model_provider_id="heuristic")
        cycle = engine.create_cycle(
            objective="Provider test",
            domain="research",
            model_provider="heuristic",
        )
        result = engine.run_full_cycle(cycle.cycle_id)
        assert result.model_provider == "heuristic"
        assert "heuristic" in result.context.get("execution", {}).get("model_output_preview", "")

    def test_persistence(self, tmp_path):
        db = str(tmp_path / "aca_persist.db")
        engine = CognitiveArchitecture(db, model_provider_id="heuristic")
        cycle = engine.create_cycle(objective="Persist test", domain="research")
        engine.run_full_cycle(cycle.cycle_id)

        loaded = engine.store.get(cycle.cycle_id)
        assert loaded is not None
        assert loaded.is_complete()


class TestACAAPI:
    def test_architecture_endpoint(self):
        r = client.get("/aca/architecture")
        assert r.status_code == 200
        assert r.json()["abbreviation"] == "ACA"
        assert len(r.json()["layers"]) == 9

    def test_create_and_run_cycle(self, tmp_path, monkeypatch):
        monkeypatch.setenv("DB_PATH", str(tmp_path / "api_aca.db"))
        from axiom.config import settings
        settings.__dict__["db_path"] = str(tmp_path / "api_aca.db")

        r = client.post("/aca/cycles", json={
            "objective": "Analyze prime distribution",
            "domain": "mathematics",
            "model_provider": "heuristic",
        })
        assert r.status_code == 201
        cycle_id = r.json()["cycle_id"]

        r2 = client.post(f"/aca/cycles/{cycle_id}/run")
        assert r2.status_code == 200
        body = r2.json()
        assert body["status"] == "completed"
        assert len(body["layers_completed"]) == 9

    def test_layers_endpoint(self):
        r = client.get("/aca/layers")
        assert r.status_code == 200
        assert len(r.json()) == 9

    def test_providers_endpoint(self):
        r = client.get("/aca/providers")
        assert r.status_code == 200
        assert "default" in r.json()["available"]
