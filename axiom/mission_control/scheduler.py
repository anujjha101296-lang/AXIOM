"""
axiom.mission_control.scheduler
===============================
Task Scheduler Module.
Schedules research tasks across specialist agent roles.
"""
from __future__ import annotations

from typing import List

from axiom.mission_control.models import MissionTask


class MissionTaskScheduler:
    """Schedules research tasks across specialist agent roles."""

    SPECIALIST_ROLES = [
        "Literature Researcher",
        "Mathematician",
        "Formalizer",
        "Proof Searcher",
        "Counterexample Researcher",
        "Experimenter",
        "Critic",
    ]

    def create_initial_task_graph(self, mission_id: str) -> List[MissionTask]:
        """Generate initial task graph for research mission."""
        return [
            MissionTask(mission_id=mission_id, name="Literature Survey & Prior Art Mapping", assigned_role="Literature Researcher", state="READY"),
            MissionTask(mission_id=mission_id, name="Problem Formalization & Claim Extraction", assigned_role="Formalizer", state="PLANNED"),
            MissionTask(mission_id=mission_id, name="Lemma Generation & Proof Strategy", assigned_role="Mathematician", state="PLANNED"),
            MissionTask(mission_id=mission_id, name="Lean 4 / SMT Formal Proof Search", assigned_role="Proof Searcher", state="PLANNED"),
            MissionTask(mission_id=mission_id, name="Finite Domain Counterexample Search", assigned_role="Counterexample Researcher", state="PLANNED"),
            MissionTask(mission_id=mission_id, name="Sandboxed Numerical Simulation", assigned_role="Experimenter", state="PLANNED"),
            MissionTask(mission_id=mission_id, name="Independent Epistemic Audit & Critique", assigned_role="Critic", state="PLANNED"),
        ]
