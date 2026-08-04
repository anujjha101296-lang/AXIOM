"""
Self-Improvement Loop (SIL)
============================
Audits AXIOM's scientific outputs at the end of a discovery session,
identifies the weakest subsystem, and writes a prioritised roadmap.md
to the workspace root.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from axiom.evaluation.prize_readiness import PrizeReadinessScorer


# ── Subsystem audit rubrics ───────────────────────────────────────────────────

@dataclass
class SubsystemHealth:
    name: str
    score: float          # 0.0 – 1.0
    issues: List[str]
    priority: float       # computed: (1.0 - score) * impact_weight


SUBSYSTEMS = [
    ("Epistemic Ingest (EIE)",  "axiom.core.parser",         0.65),
    ("Knowledge Graph (EGS)",   "axiom.core.knowledge_graph", 0.80),
    ("SMT Verification",        "axiom.core.verification.smt_gateway", 0.55),
    ("Lean 4 Export (LRK)",     "axiom.core.verification.lean_exporter", 0.40),
    ("MCTS Proof Search",       "axiom.core.reasoning.mcts", 0.60),
    ("Hypothesis Engine (HYP)", "axiom.core.reasoning.hypothesis_engine", 0.35),
    ("Working Memory (MEM)",    "axiom.core.memory.working_memory", 0.50),
    ("Prize Readiness (PRS)",   "axiom.evaluation.prize_readiness", 0.30),
    ("API Gateway",             "axiom.services.api_gateway", 0.70),
    ("Frontend Canvas (UI)",    "ui",                         0.75),
]

# Impact weights — how critical each subsystem is for scientific discovery
IMPACT_WEIGHTS = {
    "Epistemic Ingest (EIE)":   0.80,
    "Knowledge Graph (EGS)":    0.70,
    "SMT Verification":         0.90,
    "Lean 4 Export (LRK)":      0.85,
    "MCTS Proof Search":        0.95,
    "Hypothesis Engine (HYP)":  0.95,
    "Working Memory (MEM)":     0.60,
    "Prize Readiness (PRS)":    0.50,
    "API Gateway":              0.40,
    "Frontend Canvas (UI)":     0.30,
}

IMPROVEMENT_ACTIONS = {
    "Epistemic Ingest (EIE)":   "Extend LaTeX parser to handle \\newtheorem macros and inline proofs.",
    "Knowledge Graph (EGS)":    "Add edge-weight decay for stale citations; build citation-age scoring.",
    "SMT Verification":         "Add real-arithmetic solvers (NRA) and polynomial arithmetic mode.",
    "Lean 4 Export (LRK)":      "Generate Mathlib tactic proofs (ring_nf, norm_num) for auto-provable goals.",
    "MCTS Proof Search":        "Implement UCB1 rollout policy; add learned heuristic from EGS patterns.",
    "Hypothesis Engine (HYP)":  "Add LLM-guided conjecture generation from EGS embedding clusters.",
    "Working Memory (MEM)":     "Persist working memory snapshots to SQLite for cross-session recall.",
    "Prize Readiness (PRS)":    "Connect PRS scores to live EGS metrics (graph size, proof count).",
    "API Gateway":              "Add WebSocket endpoint for real-time discovery progress streaming.",
    "Frontend Canvas (UI)":     "Add timeline slider to replay knowledge graph growth over sessions.",
}


class SelfImprovementLoop:
    """
    Audits all AXIOM subsystems, ranks by improvement priority,
    and writes a structured roadmap.md to the workspace root.
    """

    def __init__(self, workspace_root: str = "."):
        self.workspace_root = workspace_root
        self.scorer = PrizeReadinessScorer()

    def _audit_subsystems(self) -> List[SubsystemHealth]:
        """
        In a full implementation, each subsystem would be probed via
        its own health-check API. For Sprint 2 we use static baselines
        modulated by the prize readiness scores.
        """
        _, global_weak_score = self.scorer.global_weakest_dimension()

        healths: List[SubsystemHealth] = []
        for name, module_path, base_score in SUBSYSTEMS:
            impact = IMPACT_WEIGHTS.get(name, 0.5)
            # Modulate score downward if verification is globally weak
            score = base_score * (1.0 - 0.1 * (1.0 - global_weak_score))
            priority = (1.0 - score) * impact
            issues = []
            if score < 0.5:
                issues.append("Below 50% health — critical improvement needed.")
            if impact >= 0.90:
                issues.append("High-impact subsystem — directly affects discovery probability.")
            healths.append(
                SubsystemHealth(
                    name=name,
                    score=round(score, 3),
                    issues=issues,
                    priority=round(priority, 4),
                )
            )
        return sorted(healths, key=lambda h: h.priority, reverse=True)

    def run(self) -> str:
        """
        Perform a full self-audit and write roadmap.md.
        Returns the path to the generated roadmap.
        """
        healths = self._audit_subsystems()
        weak_dim, weak_score = self.scorer.global_weakest_dimension()
        weakest_prob = self.scorer.weakest_problem()

        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        roadmap_path = os.path.join(self.workspace_root, "roadmap.md")

        lines = [
            f"# AXIOM Autonomous Roadmap",
            f"",
            f"> Generated: {timestamp}",
            f"> Weakest Prize Domain: **{weakest_prob.name}**",
            f"> Weakest Capability Dimension: **{weak_dim}** (score: {weak_score:.3f})",
            f"",
            f"## Subsystem Health Audit",
            f"",
            f"| Rank | Subsystem | Health Score | Priority | Issues |",
            f"|-----:|:----------|-------------:|---------:|:-------|",
        ]
        for i, h in enumerate(healths, start=1):
            issue_str = "; ".join(h.issues) if h.issues else "Stable"
            lines.append(
                f"| {i} | {h.name} | {h.score:.3f} | {h.priority:.4f} | {issue_str} |"
            )

        lines += [
            f"",
            f"## Top 3 Priority Improvements",
            f"",
        ]
        for rank, health in enumerate(healths[:3], start=1):
            action = IMPROVEMENT_ACTIONS.get(health.name, "Investigate and refactor.")
            lines += [
                f"### Priority {rank}: {health.name}",
                f"",
                f"- **Health Score:** `{health.score:.3f}`",
                f"- **Priority Score:** `{health.priority:.4f}`",
                f"- **Action:** {action}",
                f"",
            ]

        lines += [
            f"## Prize Focus for Next Sprint",
            f"",
            f"**Problem:** {weakest_prob.name}",
            f"",
            f"> {weakest_prob.description}",
            f"",
            f"**Recommended Action:** {weakest_prob.recommended_action}",
            f"",
            f"---",
            f"*This roadmap is machine-generated by the AXIOM Self-Improvement Loop.*",
        ]

        content = "\n".join(lines)
        with open(roadmap_path, "w", encoding="utf-8") as f:
            f.write(content)

        return roadmap_path

    def report(self) -> Dict[str, Any]:
        """Return a JSON-serialisable summary of the last audit."""
        healths = self._audit_subsystems()
        weak_dim, weak_score = self.scorer.global_weakest_dimension()
        return {
            "weakest_dimension": weak_dim,
            "weakest_dimension_score": weak_score,
            "top_3_priority": [
                {
                    "name": h.name,
                    "score": h.score,
                    "priority": h.priority,
                    "action": IMPROVEMENT_ACTIONS.get(h.name, ""),
                }
                for h in healths[:3]
            ],
        }
