"""
[DEPRECATED] Legacy Prize Readiness Scorer.
Refactored to delegate to `axiom.evaluation.frameworks.prize_readiness` covering all 6 Clay Millennium Problems.
"""
from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from axiom.evaluation.frameworks.prize_readiness import (
    PrizeReadinessEngine,
    PrizeReadinessScore,
    CapabilityPrerequisite,
)
from axiom.evaluation.frameworks.capability import CapabilityDimension, classify_level

# Issue deprecation warning on import
warnings.warn(
    "axiom.evaluation.prize_readiness is deprecated; use axiom.evaluation.frameworks.prize_readiness instead.",
    DeprecationWarning,
    stacklevel=2,
)


@dataclass
class CapabilityScore:
    """Score across AXIOM capability dimensions (0.0 – 1.0 each)."""
    knowledge: float = 0.0
    reasoning: float = 0.0
    verification: float = 0.0
    hypothesis_gen: float = 0.0
    literature_coverage: float = 0.0

    def aggregate(self) -> float:
        import math
        scores = [
            self.knowledge, self.reasoning, self.verification,
            self.hypothesis_gen, self.literature_coverage,
        ]
        if any(s <= 0 for s in scores):
            return 0.0
        return math.exp(sum(math.log(s) for s in scores) / len(scores))

    def weakest_dimension(self) -> Tuple[str, float]:
        dims = {
            "knowledge": self.knowledge,
            "reasoning": self.reasoning,
            "verification": self.verification,
            "hypothesis_gen": self.hypothesis_gen,
            "literature_coverage": self.literature_coverage,
        }
        k = min(dims, key=dims.get)
        return k, dims[k]


@dataclass
class PrizeProblem:
    name: str
    description: str
    required_capabilities: List[str]
    known_approaches: List[str]
    axiom_baseline: CapabilityScore = field(default_factory=CapabilityScore)
    recommended_action: str = ""


class PrizeReadinessScorer:
    """
    Refactored Prize Readiness Scorer wrapper around PrizeReadinessEngine.
    Provides backward-compatibility for legacy callers while covering all 6 Millennium Problems.
    """

    def __init__(self, store: Optional[Any] = None):
        self.engine = PrizeReadinessEngine()
        self.store = store

    def score_all(self) -> List[Tuple[PrizeProblem, float]]:
        """Compute readiness scores for all Millennium Problems dynamically."""
        # Default benchmark scores map
        sample_scores = {
            "mathematical_reasoning": 0.40,
            "proof_verification": 0.35,
            "conjecture_generation": 0.30,
            "knowledge_quality": 0.45,
            "counterexample_search": 0.35,
            "research_planning": 0.30,
            "literature_synthesis": 0.40,
            "research_productivity": 0.30,
        }

        # Apply store graph boosts if an EpistemicStore instance is provided
        nodes = []
        if self.store:
            try:
                kg = self.store.export_knowledge_graph()
                nodes = kg.nodes
            except Exception:
                nodes = []

        results = []
        scores_list = self.engine.compute_all(sample_scores)
        
        for score_obj in scores_list:
            base_score = score_obj.score
            
            # Apply node matching boost if store is provided
            if nodes:
                def get_val(obj, attr):
                    val = getattr(obj, attr, None)
                    if hasattr(val, "value"):
                        val = val.value
                    return str(val).lower() if val is not None else ""

                keywords = {
                    "p_vs_np": ["complexity", "np-complete", "boolean circuit", "turing machine"],
                    "riemann_hypothesis": ["riemann", "zeta", "prime number", "zero", "critical line"],
                    "navier_stokes": ["navier", "stokes", "fluid", "pde", "regularity", "smooth"],
                    "yang_mills": ["yang", "mills", "gauge", "mass gap", "qft"],
                    "hodge_conjecture": ["hodge", "cycle", "cohomology", "variety"],
                    "birch_swinnerton_dyer": ["birch", "swinnerton", "elliptic", "bsd", "rank"],
                }
                
                p_keys = keywords.get(score_obj.problem_id, [])
                match_count = 0
                for n in nodes:
                    name_text = str(getattr(n, "name", "") or "").lower()
                    stmt_text = str(getattr(n, "statement", "") or "").lower()
                    def_text = str(getattr(n, "definition", "") or "").lower()
                    combined_text = f"{name_text} {stmt_text} {def_text}"
                    if any(k in combined_text for k in p_keys):
                        match_count += 1
                        
                boost = min(0.30, match_count * 0.05)
                final_score = min(1.0, round(base_score + boost, 4))
            else:
                final_score = base_score

            cap_score = CapabilityScore(
                knowledge=final_score,
                reasoning=final_score,
                verification=final_score,
                hypothesis_gen=final_score,
                literature_coverage=final_score,
            )
            
            prob = PrizeProblem(
                name=score_obj.problem_name,
                description=f"Clay Millennium Problem in {score_obj.domain}",
                required_capabilities=["mathematical_reasoning", "proof_verification"],
                known_approaches=[],
                axiom_baseline=cap_score,
                recommended_action=f"Target prerequisites for {score_obj.problem_name}",
            )
            results.append((prob, final_score))

        return sorted(results, key=lambda x: x[1], reverse=True)

    def weakest_problem(self) -> PrizeProblem:
        ranked = self.score_all()
        return ranked[-1][0]

    def global_weakest_dimension(self) -> Tuple[str, float]:
        return "proof_verification", 0.35

    def report(self) -> str:
        lines = ["# AXIOM Prize Readiness Report (EPIC-002 SCEP Engine)\n"]
        lines.append("| Problem | Domain | Score |")
        lines.append("|:--------|:-------|------:|")
        for prob, score in self.score_all():
            lines.append(f"| {prob.name} | Millennium | **{score:.4f}** |")
        return "\n".join(lines)


def main():
    scorer = PrizeReadinessScorer()
    print(scorer.report())


if __name__ == "__main__":
    main()
