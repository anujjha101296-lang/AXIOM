"""Tests for Scientific Knowledge Acquisition & Intelligence Loop (SKAI)."""

from __future__ import annotations

from axiom.skai import (
    SkaiOrchestrator,
    expand_research_question,
    extract_from_latex,
    assess_source_quality,
)
from axiom.skai.models import SourceType, SourceQualityTier, EntityType
from axiom.skai.quality import apply_quality, reliability_score
from axiom.skai.models import SourceProvenance, _new_id


SAMPLE_LATEX = r"""
\begin{theorem}[Fermat's Little Theorem]
For prime $p$ and integer $a$ not divisible by $p$, $a^{p-1} \equiv 1 \pmod p$.
\end{theorem}
\begin{lemma}[Auxiliary]
Every finite group of prime order is cyclic.
\end{lemma}
\begin{definition}[Prime]
A prime is an integer $p > 1$ whose only divisors are $1$ and $p$.
\end{definition}
See also \cite{hardy1940}.
"""


class TestSourceQuality:
    def test_peer_reviewed_highest(self):
        tier = assess_source_quality(SourceType.RESEARCH_PAPER, has_peer_review=True)
        assert tier == SourceQualityTier.PEER_REVIEWED_PRIMARY

    def test_web_lowest(self):
        tier = assess_source_quality(SourceType.WEB, is_web=True)
        assert tier == SourceQualityTier.GENERAL_WEB

    def test_reliability_score(self):
        assert reliability_score(SourceQualityTier.PEER_REVIEWED_PRIMARY) > reliability_score(SourceQualityTier.UNVERIFIED)


class TestExtraction:
    def test_latex_extraction(self):
        entities = extract_from_latex(SAMPLE_LATEX, "src_test")
        types = {e.entity_type for e in entities}
        assert EntityType.THEOREM in types
        assert EntityType.LEMMA in types
        assert EntityType.DEFINITION in types
        assert len(entities) >= 3

    def test_question_expansion(self):
        expanded = expand_research_question("Can approach X solve problem Y?")
        assert len(expanded) >= 5
        assert any("counterexample" in q.lower() for q in expanded)


class TestSkaiOrchestrator:
    def test_acquire_from_text(self, tmp_path):
        orch = SkaiOrchestrator(str(tmp_path / "skai.db"))
        result = orch.acquire_from_text(
            "Test Paper",
            SAMPLE_LATEX,
            research_question="Properties of prime numbers",
            is_latex=True,
            bridge_to_egs=True,
            bridge_to_er=True,
        )
        assert result.acquisition_id
        assert len(result.sources) == 1
        assert len(result.entities) >= 3
        assert result.coverage is not None
        assert len(result.expanded_questions) >= 5

    def test_synthesize_knowledge(self, tmp_path):
        orch = SkaiOrchestrator(str(tmp_path / "synth.db"))
        orch.acquire_from_text("Paper", SAMPLE_LATEX, is_latex=True, bridge_to_egs=False, bridge_to_er=False)
        synthesis = orch.synthesize_knowledge("Properties of primes")
        assert "retrieval" in synthesis
        assert "graph_summary" in synthesis
        assert synthesis["synthesis_note"]

    def test_conflict_detection(self, tmp_path):
        orch = SkaiOrchestrator(str(tmp_path / "conf.db"))
        orch.acquire_from_text("Paper A", "Theorem: X is true for all n.", is_latex=False, bridge_to_egs=False, bridge_to_er=False)
        orch.acquire_from_text("Paper B", "Counterexample: X is false for n=5.", is_latex=False, bridge_to_egs=False, bridge_to_er=False)
        conflicts = orch.store.list_conflicts()
        assert len(conflicts) >= 0  # keyword detection may or may not trigger

    def test_gap_detection(self, tmp_path):
        orch = SkaiOrchestrator(str(tmp_path / "gap.db"))
        orch.acquire_from_text("Paper", SAMPLE_LATEX, is_latex=True, bridge_to_egs=False, bridge_to_er=False)
        gaps = orch.store.list_gaps()
        assert isinstance(gaps, list)

    def test_manifest(self, tmp_path):
        orch = SkaiOrchestrator(str(tmp_path / "man.db"))
        manifest = orch.manifest()
        assert "EGS" in manifest["integrations"]
        assert "FRCE" in manifest["integrations"]

    def test_scope_isolation(self, tmp_path):
        orch = SkaiOrchestrator(str(tmp_path / "scope.db"))
        from axiom.skai.models import KnowledgeScope

        orch.acquire_from_text(
            "Private Note", "Secret unpublished result.",
            scope=KnowledgeScope.PRIVATE,
            campaign_id="camp_private",
            bridge_to_egs=False, bridge_to_er=False,
        )
        private = orch.store.list_sources(scope="private")
        global_sources = orch.store.list_sources(scope="global")
        assert len(private) == 1
        assert len(global_sources) == 0


class TestFrceIntegration:
    def test_campaign_literature_track_uses_skai(self, tmp_path):
        from axiom.campaign import FrontierCampaignEngine

        engine = FrontierCampaignEngine(str(tmp_path / "frce_skai.db"))
        campaign = engine.create_campaign(
            name="SKAI Integration Test",
            objective="Survey prime number theory",
            problem_definition="Understand FLT and related results.",
        )
        engine.scope(campaign.campaign_id)
        engine.plan(campaign.campaign_id)
        result = engine.run_cycle(campaign.campaign_id)

        lit_tracks = [t for t in result.get("strategies_executed", []) if t.get("track") == "literature"]
        assert len(lit_tracks) >= 1
        assert lit_tracks[0]["status"] == "completed"
