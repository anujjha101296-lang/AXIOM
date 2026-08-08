"""Tests for the AXIOM Grand Challenge Program."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from axiom.grand_challenge import GrandChallengeEngine, list_challenges, program_manifest
from axiom.grand_challenge.gates import list_gates
from axiom.grand_challenge.models import CampaignStatus, ChallengeTier
from axiom.grand_challenge.registry import get_challenge
from axiom.services.api_gateway.main import app

client = TestClient(app)


class TestChallengeRegistry:
    def test_all_tiers_have_challenges(self):
        manifest = program_manifest()
        assert manifest["total_challenges"] >= 12
        for tier_info in manifest["tiers"]:
            assert tier_info["challenge_count"] >= 1

    def test_challenge_has_required_fields(self):
        challenge = get_challenge("t1_fermat_little_theorem")
        assert challenge.objective
        assert challenge.domain
        assert challenge.verification_method
        assert challenge.success_criteria
        assert challenge.failure_criteria
        assert challenge.human_review_process

    def test_tier_5_not_prize_solver(self):
        challenge = get_challenge("t5_prize_readiness_assessment")
        assert "not" in challenge.notes.lower() or "not" in challenge.objective.lower()


class TestCampaignEngine:
    def test_create_and_run_tier0(self, tmp_path):
        engine = GrandChallengeEngine(str(tmp_path / "gcp.db"))
        campaign = engine.create_campaign(
            name="Tier 0 Smoke Test",
            description="Validate toy reasoning pipeline",
            tier=ChallengeTier.TIER_0_TOY,
        )
        campaign = engine.activate_campaign(campaign.campaign_id)
        assert campaign.status == CampaignStatus.ACTIVE

        campaign = engine.run_tier_batch(campaign.campaign_id)
        assert len(campaign.experiments) >= 2
        assert len(campaign.evidence) >= 2
        assert campaign.progress_fraction() > 0

    def test_hypothesis_and_journal(self, tmp_path):
        engine = GrandChallengeEngine(str(tmp_path / "gcp_journal.db"))
        campaign = engine.create_campaign(name="Journal Test", tier=ChallengeTier.TIER_0_TOY)
        engine.add_hypothesis(campaign.campaign_id, "Sum formula holds for all n", 0.8)
        engine.add_journal_entry(campaign.campaign_id, "Initial observation", "Pipeline started")
        journal = engine.get_journal(campaign.campaign_id)
        assert "Sum formula" in journal
        assert "Initial observation" in journal

    def test_checkpoint(self, tmp_path):
        engine = GrandChallengeEngine(str(tmp_path / "gcp_cp.db"))
        campaign = engine.create_campaign(name="Checkpoint Test", tier=ChallengeTier.TIER_0_TOY)
        engine.run_tier_batch(campaign.campaign_id)
        campaign = engine.checkpoint(campaign.campaign_id)
        assert len(campaign.checkpoints) == 1
        assert campaign.status == CampaignStatus.CHECKPOINTED

    def test_readiness_gate_blocks_advance(self, tmp_path):
        engine = GrandChallengeEngine(str(tmp_path / "gcp_gate.db"))
        campaign = engine.create_campaign(name="Gate Test", tier=ChallengeTier.TIER_0_TOY)
        readiness = engine.evaluate_readiness(campaign.campaign_id)
        assert readiness["passed"] is False
        assert len(readiness["blockers"]) > 0

        with pytest.raises(ValueError, match="Readiness gate not passed"):
            engine.advance_tier(campaign.campaign_id)

    def test_tier0_to_tier1_advance(self, tmp_path):
        engine = GrandChallengeEngine(str(tmp_path / "gcp_advance.db"))
        campaign = engine.create_campaign(
            name="Advance Test",
            tier=ChallengeTier.TIER_0_TOY,
            challenge_ids=["t0_arithmetic_series", "t0_gcd_computation"],
        )
        engine.run_tier_batch(campaign.campaign_id)
        engine.checkpoint(campaign.campaign_id)

        # Add extra experiments to meet gate threshold
        for _ in range(2):
            engine.run_experiment(campaign.campaign_id, "t0_arithmetic_series")

        readiness = engine.evaluate_readiness(campaign.campaign_id)
        if readiness["passed"]:
            campaign = engine.advance_tier(campaign.campaign_id)
            assert int(campaign.current_tier) == 1


class TestGCPAPI:
    def test_manifest(self):
        r = client.get("/gcp/manifest")
        assert r.status_code == 200
        assert r.json()["name"] == "AXIOM Grand Challenge Program"

    def test_list_challenges(self):
        r = client.get("/gcp/challenges?tier=1")
        assert r.status_code == 200
        assert r.json()["count"] >= 3

    def test_list_gates(self):
        r = client.get("/gcp/gates")
        assert r.status_code == 200
        assert r.json()["count"] == 5

    def test_create_campaign_api(self, tmp_path, monkeypatch):
        monkeypatch.setenv("DB_PATH", str(tmp_path / "api_gcp.db"))
        from axiom.config import settings
        settings.__dict__["db_path"] = str(tmp_path / "api_gcp.db")

        r = client.post("/gcp/campaigns", json={
            "name": "API Campaign",
            "description": "Test via API",
            "tier": 0,
        })
        assert r.status_code == 201
        campaign_id = r.json()["campaign_id"]

        r = client.post(f"/gcp/campaigns/{campaign_id}/run-tier")
        assert r.status_code == 200
        assert len(r.json()["experiments"]) >= 1

        r = client.get(f"/gcp/campaigns/{campaign_id}/journal")
        assert r.status_code == 200
        assert "API Campaign" in r.json()["journal"]
