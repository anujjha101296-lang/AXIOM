"""Tests for the AXIOM Research Kernel."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from axiom.research_kernel import ResearchKernel, kernel_manifest, list_plugins
from axiom.research_kernel.engine import KernelStageIncompleteError
from axiom.research_kernel.models import STAGE_ORDER, KernelRunStatus, KernelStage
from axiom.research_kernel.registry import get_plugin
from axiom.services.api_gateway.main import app

client = TestClient(app)


class TestKernelEngine:
    def test_full_cycle_completes_all_stages(self, tmp_path):
        db = str(tmp_path / "kernel.db")
        engine = ResearchKernel(db)
        run = engine.create_run(
            objective="Prove sum(1..n) = n(n+1)/2",
            plugin_id="mathematics",
        )
        result = engine.run_full_cycle(run.run_id)

        assert result.status == KernelRunStatus.COMPLETED
        assert len(result.stages_completed) == 10
        assert result.report is not None
        assert len(result.benchmark_results) >= 2
        assert all(b["passed"] for b in result.benchmark_results)
        assert result.aca_cycle_id is not None
        assert result.sme_session_id is not None

    def test_cannot_skip_stages(self, tmp_path):
        db = str(tmp_path / "kernel_skip.db")
        engine = ResearchKernel(db)
        run = engine.create_run(objective="Test skip", plugin_id="mathematics")

        with pytest.raises(KernelStageIncompleteError):
            engine.execute_stage(run.run_id, KernelStage.EVIDENCE_ACQUISITION)

    def test_three_domain_plugins(self, tmp_path):
        db = str(tmp_path / "kernel_domains.db")
        engine = ResearchKernel(db)
        plugins = ["mathematics", "computer_science", "vlsi_hardware"]

        for plugin_id in plugins:
            run = engine.create_run(
                objective=f"Domain test for {plugin_id}",
                plugin_id=plugin_id,
            )
            completed = engine.run_full_cycle(run.run_id)
            assert completed.is_complete()
            assert completed.plugin_id == plugin_id
            assert completed.report is not None

    def test_persistence(self, tmp_path):
        db = str(tmp_path / "kernel_persist.db")
        engine = ResearchKernel(db)
        run = engine.create_run(objective="Persist test", plugin_id="computer_science")
        engine.run_full_cycle(run.run_id)

        loaded = engine.get_run(run.run_id)
        assert loaded is not None
        assert loaded.is_complete()
        assert loaded.report is not None


class TestKernelPlugins:
    def test_list_plugins(self):
        plugins = list_plugins()
        assert len(plugins) == 3
        ids = {p.plugin_id for p in plugins}
        assert ids == {"mathematics", "computer_science", "vlsi_hardware"}

    def test_mathematics_benchmarks(self):
        plugin = get_plugin("mathematics")
        benchmarks = plugin.benchmarks()
        assert len(benchmarks) >= 2
        for bench in benchmarks:
            result = plugin.run_benchmark(bench, {})
            assert "passed" in result
            assert "score" in result

    def test_manifest(self):
        manifest = kernel_manifest()
        assert len(manifest["stages"]) == 10
        assert len(manifest["plugins"]) == 3
        assert "aca" in manifest["integrations"]


class TestKernelAPI:
    def test_list_stages(self):
        r = client.get("/kernel/stages")
        assert r.status_code == 200
        assert len(r.json()) == 10

    def test_list_plugins(self):
        r = client.get("/kernel/plugins")
        assert r.status_code == 200
        assert r.json()["count"] == 3

    def test_create_and_run(self, tmp_path, monkeypatch):
        monkeypatch.setenv("DB_PATH", str(tmp_path / "api_kernel.db"))
        from axiom.config import settings
        settings.__dict__["db_path"] = str(tmp_path / "api_kernel.db")

        r = client.post("/kernel/runs", json={
            "objective": "Verify merge sort correctness",
            "plugin_id": "computer_science",
        })
        assert r.status_code == 201
        run_id = r.json()["run_id"]

        r = client.post(f"/kernel/runs/{run_id}/run")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "completed"
        assert len(data["stages_completed"]) == 10

        r = client.get(f"/kernel/runs/{run_id}/report")
        assert r.status_code == 200
        assert "Research Kernel Report" in r.json()["report"]

    def test_manifest_endpoint(self):
        r = client.get("/kernel/manifest")
        assert r.status_code == 200
        assert r.json()["name"] == "AXIOM Research Kernel"
