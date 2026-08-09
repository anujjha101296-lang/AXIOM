"""Tests for the Frontier Research Campaign Engine (FRCE)."""

from __future__ import annotations

import pytest

from axiom.campaign import (
    CampaignPhase,
    FrontierCampaignEngine,
    LadderLevel,
    can_transition,
    ladder_manifest,
    list_roles,
)
from axiom.campaign.graph import decompose_problem, find_bottleneck, graph_summary
from axiom.campaign.models import ContributionLevel, PivotDecision
from axiom.campaign.pivot import evaluate_cycle
from axiom.campaign.models import CycleRecord, _utc_now


class TestCampaignModels:
    def test_state_transitions(self):
        assert can_transition(CampaignPhase.PROPOSED, CampaignPhase.SCOPED)
        assert not can_transition(CampaignPhase.PROPOSED, CampaignPhase.RESEARCHING)
        assert can_transition(CampaignPhase.REVIEW, CampaignPhase.ABANDONED)

    def test_ladder_manifest(self):
        manifest = ladder_manifest()
        assert len(manifest["levels"]) == 10
        assert "millennium_gate" in manifest

    def test_roles_defined(self):
        roles = list_roles()
        assert len(roles) >= 10
        assert any(r["role"] == "principal_investigator" for r in roles)


class TestResearchGraph:
    def test_decompose_problem(self, tmp_path):
        engine = FrontierCampaignEngine(str(tmp_path / "graph.db"))
        campaign = engine.create_campaign(
            name="Graph Test",
            objective="Prove a theorem about primes",
            problem_definition="Consider prime gaps. Identify known bounds. Find open subproblems.",
        )
        decompose_problem(campaign)
        assert len(campaign.research_graph) >= 2
        main = campaign.research_graph[0]
        assert main.node_type.value == "main_problem"
        bottleneck = find_bottleneck(campaign)
        assert bottleneck is not None
        summary = graph_summary(campaign)
        assert summary["node_count"] >= 2


class TestCampaignEngine:
    def test_create_and_scope(self, tmp_path):
        engine = FrontierCampaignEngine(str(tmp_path / "frce.db"))
        campaign = engine.create_campaign(
            name="Tier 1 Campaign",
            objective="Verify Fermat's Little Theorem computationally",
            problem_definition="For prime p and integer a not divisible by p, a^(p-1) ≡ 1 (mod p).",
            ladder_level=LadderLevel.LEVEL_1_KNOWN_ANSWER_MATH,
        )
        assert campaign.phase == CampaignPhase.PROPOSED

        campaign = engine.scope(campaign.campaign_id)
        assert campaign.phase == CampaignPhase.SCOPED
        assert len(campaign.research_graph) >= 1
        assert len(campaign.checkpoints) == 1

    def test_plan_generates_strategies(self, tmp_path):
        engine = FrontierCampaignEngine(str(tmp_path / "plan.db"))
        campaign = engine.create_campaign(
            name="Plan Test",
            objective="Explore convergence of a series",
            problem_definition="Analyze ∑ 1/n² convergence.",
        )
        engine.scope(campaign.campaign_id)
        campaign = engine.plan(campaign.campaign_id)
        assert len(campaign.strategies) >= 1
        assert len(campaign.hypotheses) >= 1
        assert campaign.routing_plan_id is not None

    def test_run_cycle_integrates_loops(self, tmp_path):
        engine = FrontierCampaignEngine(str(tmp_path / "cycle.db"))
        campaign = engine.create_campaign(
            name="Cycle Test",
            objective="Test computational evidence collection",
            problem_definition="Run sandbox experiment.",
        )
        engine.scope(campaign.campaign_id)
        engine.plan(campaign.campaign_id)
        result = engine.run_cycle(campaign.campaign_id)

        assert result["cycle_number"] == 1
        assert "pivot_decision" in result
        assert "agent_activity" in result
        assert "what" in result["agent_activity"]
        updated = engine.get_campaign(campaign.campaign_id)
        assert updated is not None
        assert len(updated.cycles) == 1
        assert len(updated.memory) == 1

    def test_dashboard(self, tmp_path):
        engine = FrontierCampaignEngine(str(tmp_path / "dash.db"))
        campaign = engine.create_campaign(
            name="Dashboard Test",
            objective="Dashboard smoke test",
        )
        engine.scope(campaign.campaign_id)
        dash = engine.dashboard(campaign.campaign_id)
        assert dash["campaign_id"] == campaign.campaign_id
        assert "next_compute" in dash
        assert "ladder_readiness" in dash
        assert "agent_activity" in dash
        assert dash["agent_activity"]["why"] == "Dashboard smoke test"

    def test_abandon_preserves_memory(self, tmp_path):
        engine = FrontierCampaignEngine(str(tmp_path / "abandon.db"))
        campaign = engine.create_campaign(
            name="Abandon Test",
            objective="Test abandonment preserves learning",
        )
        engine.scope(campaign.campaign_id)
        engine.abandon(campaign.campaign_id, reason="Direction unlikely to succeed")
        updated = engine.get_campaign(campaign.campaign_id)
        assert updated.phase == CampaignPhase.ABANDONED
        assert len(updated.journal) >= 1

    def test_checkpoint_immutable_sequence(self, tmp_path):
        engine = FrontierCampaignEngine(str(tmp_path / "cp.db"))
        campaign = engine.create_campaign(name="CP Test", objective="Checkpoint test")
        engine.scope(campaign.campaign_id)
        engine.checkpoint(campaign.campaign_id, title="Checkpoint #002")
        updated = engine.get_campaign(campaign.campaign_id)
        assert len(updated.checkpoints) >= 2
        assert updated.checkpoints[-1].sequence == len(updated.checkpoints)


class TestPivotMechanism:
    def test_counterexample_triggers_pivot(self):
        from axiom.campaign.models import FrontierCampaign, ResourceBudget

        campaign = FrontierCampaign(
            campaign_id="test",
            name="test",
            objective="test",
        )
        cycle = CycleRecord(
            cycle_id="c1",
            cycle_number=1,
            started_at=_utc_now(),
            contribution_level=ContributionLevel.COUNTEREXAMPLE,
        )
        decision = evaluate_cycle(campaign, cycle)
        assert decision == PivotDecision.PIVOT

    def test_verified_lemma_escalates(self):
        from axiom.campaign.models import FrontierCampaign

        campaign = FrontierCampaign(
            campaign_id="test",
            name="test",
            objective="test",
        )
        cycle = CycleRecord(
            cycle_id="c1",
            cycle_number=1,
            started_at=_utc_now(),
            contribution_level=ContributionLevel.VERIFIED_LEMMA,
            learned=["New verified lemma"],
        )
        decision = evaluate_cycle(campaign, cycle)
        assert decision == PivotDecision.ESCALATE


class TestFrceAPI:
    def test_manifest_via_engine(self):
        from axiom.campaign.orchestrator import FrontierCampaignEngine

        manifest = FrontierCampaignEngine(":memory:").manifest()
        assert manifest["name"] == "AXIOM Frontier Research Campaign Engine"
        assert "E&R" in manifest["loops_integrated"]
        assert "SEC" in manifest["loops_integrated"]

    def test_create_campaign_via_engine(self, tmp_path):
        from axiom.campaign.orchestrator import FrontierCampaignEngine

        engine = FrontierCampaignEngine(str(tmp_path / "api_engine.db"))
        campaign = engine.create_campaign(
            name="API Test Campaign",
            objective="Test FRCE engine API surface",
            problem_definition="Smoke test campaign creation.",
            ladder_level=LadderLevel.LEVEL_1_KNOWN_ANSWER_MATH,
        )
        assert campaign.phase.value == "PROPOSED"
        assert campaign.campaign_id.startswith("camp_")
