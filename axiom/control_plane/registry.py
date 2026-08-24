"""
axiom.control_plane.registry
============================
Unified Agent & Resource Registry.
Defines canonical specialist agent profiles and allowed tool sets.
"""
from __future__ import annotations

from typing import Dict, List

from axiom.control_plane.models import AgentProfile


class AgentRegistry:
    """Canonical registry for AXIOM specialist agent profiles."""

    def __init__(self):
        self._profiles: Dict[str, AgentProfile] = {}
        self._initialize_canonical_profiles()

    def _initialize_canonical_profiles(self) -> None:
        profiles = [
            AgentProfile(name="Research Planner", role="RESEARCH_PLANNER", allowed_tools=["create_plan", "decompose_problem"], allowed_models=["gpt-4o", "claude-3-5-sonnet"]),
            AgentProfile(name="Literature Researcher", role="LITERATURE_RESEARCHER", allowed_tools=["discover_sources", "fetch_source", "search_evidence"], allowed_models=["gpt-4o-mini", "claude-3-5-haiku"]),
            AgentProfile(name="Mathematician", role="MATHEMATICIAN", allowed_tools=["formulate_lemma", "derive_bounds"], allowed_models=["gpt-4o", "claude-3-5-sonnet"]),
            AgentProfile(name="Formalizer", role="FORMALIZER", allowed_tools=["to_lean4", "to_smt"], allowed_models=["gpt-4o"]),
            AgentProfile(name="Proof Searcher", role="PROOF_SEARCHER", allowed_tools=["verify_lean4", "solve_smt"], allowed_models=["claude-3-5-sonnet"]),
            AgentProfile(name="Counterexample Researcher", role="COUNTEREXAMPLE_RESEARCHER", allowed_tools=["search_counterexample"], allowed_models=["gpt-4o-mini"]),
            AgentProfile(name="Experimentalist", role="EXPERIMENTALIST", allowed_tools=["execute_sandbox"], allowed_models=["gpt-4o-mini"]),
            AgentProfile(name="Critic", role="CRITIC", allowed_tools=["audit_progress", "challenge_claim"], allowed_models=["gpt-4o", "claude-3-5-sonnet"]),
            AgentProfile(name="Synthesizer", role="SYNTHESIZER", allowed_tools=["compile_paper"], allowed_models=["gpt-4o"]),
        ]
        for p in profiles:
            self._profiles[p.role] = p

    def get_profile(self, role: str) -> AgentProfile:
        return self._profiles.get(role, AgentProfile(name=role, role=role))

    def list_profiles(self) -> List[AgentProfile]:
        return list(self._profiles.values())
