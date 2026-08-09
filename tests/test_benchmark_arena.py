"""Tests for Research Benchmark Arena."""

from __future__ import annotations

from fastapi.testclient import TestClient

from axiom.evaluation.arena.runner import get_public_catalog, run_arena
from axiom.evaluation.arena.suite_v1 import build_catalog, public_catalog
from axiom.services.api_gateway.main import app


def test_catalog_has_60_cases_without_answers():
    cases = build_catalog()
    assert len(cases) == 60
    pub = public_catalog()
    assert len(pub) == 60
    for c in pub:
        assert c["ground_truth_exposed"] is False
        assert "_grader" not in c.get("inputs", {})
        blob = str(c).lower()
        assert "expected_answer" not in blob


def test_arena_baseline_run(tmp_path):
    db = str(tmp_path / "arena.db")
    out = run_arena(db, is_baseline=True, notes="unit baseline")
    run = out["run"]
    assert run["is_baseline"] is True
    assert run["summary"]["total"] == 60
    assert "scientific_honesty" in run["dimension_scores"]
    assert run["readiness"]["millennium_ready"] is False
    assert len(run["weaknesses"]) >= 1
    # Measured score only — no fabricated perfect requirement
    assert 0.0 <= run["summary"]["mean_score"] <= 1.0


def test_arena_api(tmp_path, monkeypatch):
    db = str(tmp_path / "arena_api.db")
    monkeypatch.setenv("AXIOM_DB_PATH", db)
    from axiom.config import settings

    monkeypatch.setattr(settings, "db_path", db)
    client = TestClient(app)
    cat = client.get("/arena/catalog")
    assert cat.status_code == 200
    body = cat.json()
    assert body["count"] == 60
    assert body["ground_truth_exposed"] is False

    run = client.post("/arena/run", json={"is_baseline": True, "notes": "api baseline"})
    assert run.status_code == 200, run.text
    payload = run.json()
    assert payload["run"]["summary"]["total"] == 60
    assert payload["run"]["readiness"]["millennium_ready"] is False

    ready = client.get("/arena/readiness")
    assert ready.status_code == 200
    assert ready.json()["readiness"] is not None


def test_public_catalog_helper():
    data = get_public_catalog()
    assert data["count"] == 60


def test_arena_extension_security_long_horizon(tmp_path):
    db = str(tmp_path / "arena_ext.db")
    out = run_arena(db, include_extension=True, notes="ARENA-1 extension")
    run = out["run"]
    assert run["summary"]["total"] == 73  # 60 + 13
    assert run["summary"]["failed"] == 0 or len(run["failures"]) < 5
    assert "long_horizon" in run["dimension_scores"]
    assert run["dimension_scores"]["long_horizon"] > 0
    assert run["readiness"]["millennium_ready"] is False
    # With dedicated LH evidence, Tier 8 should unlock when cases pass
    if run["summary"]["failed"] == 0:
        assert run["readiness"]["highest_unlocked_tier"] >= 8
        assert run["readiness"]["highest_unlocked_tier"] < 10
    # Catalog with extension
    cat = get_public_catalog(include_extension=True)
    assert cat["count"] == 73
    assert cat["ground_truth_exposed"] is False
    assert all("_grader" not in (c.get("inputs") or {}) for c in cat["benchmarks"])
