"""
Prize Readiness Scorer (PRS)
=============================
Evaluates AXIOM's current scientific capability against officially
recognised prize-backed open problems (Clay Millennium Prizes + IMO).

Scores are produced on a 0.0–1.0 scale per dimension and per problem.
Running as __main__ prints a formatted leaderboard and identifies the
weakest capability gap with a recommended next action.
"""

from __future__ import annotations

import sys
import textwrap
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


# ── Capability Dimensions ────────────────────────────────────────────────────

@dataclass
class CapabilityScore:
    """Score across the five AXIOM capability dimensions (0.0 – 1.0 each)."""
    knowledge:          float = 0.0   # Depth of relevant knowledge in EGS
    reasoning:          float = 0.0   # Proof / deduction power (MCTS + SMT)
    verification:       float = 0.0   # Formal verification (Lean 4)
    hypothesis_gen:     float = 0.0   # Novel conjecture generation (HYP)
    literature_coverage: float = 0.0  # arXiv ingestion coverage

    def aggregate(self) -> float:
        """Geometric mean — one weak dimension drags the overall score down."""
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


# ── Problem Definitions ───────────────────────────────────────────────────────

@dataclass
class PrizeProblem:
    name: str
    description: str
    required_capabilities: List[str]      # Which AXIOM dimensions matter most
    known_approaches: List[str]           # Existing mathematical strategies
    axiom_baseline: CapabilityScore = field(default_factory=CapabilityScore)
    recommended_action: str = ""


PRIZE_PROBLEMS: List[PrizeProblem] = [
    PrizeProblem(
        name="P vs NP",
        description=(
            "Does every problem whose solution can be quickly verified by a "
            "computer also be quickly solved by a computer?"
        ),
        required_capabilities=["reasoning", "verification", "hypothesis_gen"],
        known_approaches=["Circuit complexity", "Proof complexity", "Algebrization"],
        axiom_baseline=CapabilityScore(
            knowledge=0.12, reasoning=0.08, verification=0.05,
            hypothesis_gen=0.10, literature_coverage=0.15,
        ),
        recommended_action=(
            "Expand EGS with complexity-theory papers. "
            "Build symbolic Boolean circuit reasoning module."
        ),
    ),
    PrizeProblem(
        name="Riemann Hypothesis",
        description=(
            "All non-trivial zeros of the Riemann zeta function have real part 1/2."
        ),
        required_capabilities=["knowledge", "reasoning", "verification"],
        known_approaches=[
            "Analytic number theory", "Random Matrix Theory",
            "L-functions", "Spectral theory",
        ],
        axiom_baseline=CapabilityScore(
            knowledge=0.10, reasoning=0.06, verification=0.04,
            hypothesis_gen=0.08, literature_coverage=0.12,
        ),
        recommended_action=(
            "Ingest Davenport, Edwards, and Titchmarsh into EGS. "
            "Build ζ(s) numerical evaluator and zero-tracker."
        ),
    ),
    PrizeProblem(
        name="Navier–Stokes Existence & Smoothness",
        description=(
            "Prove or provide a counterexample to whether smooth, globally "
            "defined solutions to the Navier–Stokes equations always exist in 3D."
        ),
        required_capabilities=["knowledge", "reasoning", "hypothesis_gen"],
        known_approaches=[
            "Energy methods", "Weak solutions (Leray)", "Regularity criteria",
        ],
        axiom_baseline=CapabilityScore(
            knowledge=0.08, reasoning=0.05, verification=0.03,
            hypothesis_gen=0.07, literature_coverage=0.10,
        ),
        recommended_action=(
            "Build PDE symbolic solver. "
            "Ingest Leray, Temam, and Constantin into EGS."
        ),
    ),
    PrizeProblem(
        name="Yang–Mills Existence & Mass Gap",
        description=(
            "Prove that quantum Yang–Mills theory exists and has a positive mass gap."
        ),
        required_capabilities=["knowledge", "reasoning", "verification"],
        known_approaches=[
            "Lattice gauge theory", "Constructive QFT", "Topological methods",
        ],
        axiom_baseline=CapabilityScore(
            knowledge=0.06, reasoning=0.04, verification=0.03,
            hypothesis_gen=0.05, literature_coverage=0.08,
        ),
        recommended_action=(
            "Ingest Jaffe–Witten formulation papers. "
            "Build gauge-field algebraic structures in EGS."
        ),
    ),
    PrizeProblem(
        name="Hodge Conjecture",
        description=(
            "Every Hodge class of a non-singular complex algebraic variety is "
            "a rational linear combination of cohomology classes of algebraic cycles."
        ),
        required_capabilities=["knowledge", "hypothesis_gen", "verification"],
        known_approaches=[
            "Algebraic geometry", "Transcendental methods",
            "Motivic cohomology",
        ],
        axiom_baseline=CapabilityScore(
            knowledge=0.07, reasoning=0.05, verification=0.03,
            hypothesis_gen=0.06, literature_coverage=0.09,
        ),
        recommended_action=(
            "Ingest Grothendieck and Deligne. "
            "Build cohomology class graph representation in EGS."
        ),
    ),
    PrizeProblem(
        name="Birch and Swinnerton-Dyer Conjecture",
        description=(
            "The rank of an elliptic curve equals the order of vanishing of its L-function at s=1."
        ),
        required_capabilities=["knowledge", "reasoning", "hypothesis_gen"],
        known_approaches=[
            "Elliptic curves", "L-functions", "Modular forms",
            "Iwasawa theory",
        ],
        axiom_baseline=CapabilityScore(
            knowledge=0.09, reasoning=0.07, verification=0.04,
            hypothesis_gen=0.08, literature_coverage=0.11,
        ),
        recommended_action=(
            "Build elliptic curve arithmetic module. "
            "Ingest Wiles, Taylor, and Coates into EGS."
        ),
    ),
    PrizeProblem(
        name="Poincaré Conjecture (Reference — Solved 2003)",
        description=(
            "Every simply connected, closed 3-manifold is homeomorphic to the 3-sphere. "
            "[Solved by Perelman — used as calibration baseline for AXIOM reasoning.]"
        ),
        required_capabilities=["knowledge", "reasoning", "verification"],
        known_approaches=["Ricci flow", "Surgery theory"],
        axiom_baseline=CapabilityScore(
            knowledge=0.20, reasoning=0.15, verification=0.10,
            hypothesis_gen=0.12, literature_coverage=0.22,
        ),
        recommended_action=(
            "Use Perelman's proof as a benchmark for AXIOM formal verification. "
            "Target reproducing key Ricci-flow lemmas in Lean 4."
        ),
    ),
]


# ── Scorer ───────────────────────────────────────────────────────────────────

class PrizeReadinessScorer:

    def __init__(self, problems: List[PrizeProblem] | None = None, store: Optional[Any] = None):
        self.problems = problems or PRIZE_PROBLEMS
        self.store = store

    def score_all(self) -> List[Tuple[PrizeProblem, float]]:
        """Return (problem, aggregate_score) sorted descending, dynamically adjusted if store is provided."""
        import copy
        
        nodes = []
        if self.store:
            try:
                kg = self.store.export_knowledge_graph()
                nodes = kg.nodes
            except Exception:
                nodes = []
                
        results = []
        for p in self.problems:
            # Deep copy to avoid mutating the class level constants
            b = copy.deepcopy(p.axiom_baseline)
            
            if nodes:
                # Convert string type names/status to lower for robust comparison
                def get_val(obj, attr):
                    val = getattr(obj, attr, None)
                    if hasattr(val, "value"):
                        val = val.value
                    return str(val).lower() if val is not None else ""

                num_concepts = sum(1 for n in nodes if get_val(n, "type") == "concept")
                num_papers = sum(1 for n in nodes if get_val(n, "type") == "paper")
                num_verified = sum(1 for n in nodes if get_val(n, "status") == "verified")
                num_conjectures = sum(1 for n in nodes if get_val(n, "status") == "conjectured")
                
                # Check for tier 2 proofs
                num_proofs = 0
                for n in nodes:
                    tier_val = getattr(n, "tier", None)
                    if hasattr(tier_val, "value"):
                        tier_val = tier_val.value
                    if tier_val == 2 or str(tier_val) == "2" or str(tier_val).lower() == "tier_2_proven":
                        num_proofs += 1

                global_knowledge_boost = min(0.1, (num_concepts + num_papers) / 100.0)
                global_reasoning_boost = min(0.1, num_verified / 50.0)
                global_verification_boost = min(0.1, num_proofs / 20.0)
                global_hypothesis_boost = min(0.1, num_conjectures / 50.0)
                global_coverage_boost = min(0.1, num_papers / 50.0)
                
                # Keywords to match relevant nodes for problem-specific boosts
                keywords = {
                    "P vs NP": ["complexity", "np-complete", "boolean circuit", "turing machine", "polynomial time"],
                    "Riemann Hypothesis": ["riemann", "zeta", "prime number", "zero distribution", "l-function", "critical line"],
                    "Navier–Stokes Existence & Smoothness": ["navier-stokes", "fluid dynamics", "pde", "regularity", "smooth solution", "euler equations"],
                    "Yang–Mills Existence & Mass Gap": ["yang-mills", "gauge theory", "mass gap", "quantum field", "qft", "gauge field"],
                    "Hodge Conjecture": ["hodge", "algebraic cycle", "cohomology", "complex variety", "kahler manifold"],
                    "Birch and Swinnerton-Dyer Conjecture": ["birch", "swinnerton", "elliptic curve", "bsd conjecture", "rank of elliptic", "l-series"],
                    "Poincaré Conjecture (Reference — Solved 2003)": ["poincare", "sphere", "3-manifold", "ricci flow", "homeomorphic", "perelman"],
                }
                
                p_keys = keywords.get(p.name, [])
                relevant_nodes = []
                for n in nodes:
                    name_text = str(getattr(n, "name", "") or "").lower()
                    stmt_text = str(getattr(n, "statement", "") or "").lower()
                    def_text = str(getattr(n, "definition", "") or "").lower()
                    combined_text = f"{name_text} {stmt_text} {def_text}"
                    if any(k in combined_text for k in p_keys):
                        relevant_nodes.append(n)
                        
                rel_concepts = sum(1 for n in relevant_nodes if get_val(n, "type") == "concept")
                rel_papers = sum(1 for n in relevant_nodes if get_val(n, "type") == "paper")
                rel_verified = sum(1 for n in relevant_nodes if get_val(n, "status") == "verified")
                rel_conjectures = sum(1 for n in relevant_nodes if get_val(n, "status") == "conjectured")
                
                rel_proofs = 0
                for n in relevant_nodes:
                    tier_val = getattr(n, "tier", None)
                    if hasattr(tier_val, "value"):
                        tier_val = tier_val.value
                    if tier_val == 2 or str(tier_val) == "2" or str(tier_val).lower() == "tier_2_proven":
                        rel_proofs += 1

                rel_knowledge_boost = min(0.15, (rel_concepts + rel_papers) / 10.0)
                rel_reasoning_boost = min(0.15, rel_verified / 5.0)
                rel_verification_boost = min(0.2, rel_proofs / 3.0)
                rel_hypothesis_boost = min(0.15, rel_conjectures / 10.0)
                rel_coverage_boost = min(0.15, rel_papers / 5.0)
                
                # Apply updates to baseline capabilities
                b.knowledge = min(1.0, b.knowledge + global_knowledge_boost + rel_knowledge_boost)
                b.reasoning = min(1.0, b.reasoning + global_reasoning_boost + rel_reasoning_boost)
                b.verification = min(1.0, b.verification + global_verification_boost + rel_verification_boost)
                b.hypothesis_gen = min(1.0, b.hypothesis_gen + global_hypothesis_boost + rel_hypothesis_boost)
                b.literature_coverage = min(1.0, b.literature_coverage + global_coverage_boost + rel_coverage_boost)
            
            p_adjusted = PrizeProblem(
                name=p.name,
                description=p.description,
                required_capabilities=p.required_capabilities,
                known_approaches=p.known_approaches,
                axiom_baseline=b,
                recommended_action=p.recommended_action
            )
            results.append((p_adjusted, b.aggregate()))
            
        return sorted(results, key=lambda x: x[1], reverse=True)

    def weakest_problem(self) -> PrizeProblem:
        ranked = self.score_all()
        return ranked[-1][0]   # lowest aggregate

    def global_weakest_dimension(self) -> Tuple[str, float]:
        """Average each dimension across all problems; find the lowest."""
        dim_totals: Dict[str, float] = {
            "knowledge": 0.0, "reasoning": 0.0, "verification": 0.0,
            "hypothesis_gen": 0.0, "literature_coverage": 0.0,
        }
        ranked_probs = [item[0] for item in self.score_all()]
        n = len(ranked_probs)
        for p in ranked_probs:
            b = p.axiom_baseline
            dim_totals["knowledge"]           += b.knowledge
            dim_totals["reasoning"]           += b.reasoning
            dim_totals["verification"]        += b.verification
            dim_totals["hypothesis_gen"]      += b.hypothesis_gen
            dim_totals["literature_coverage"] += b.literature_coverage
        avgs = {k: v / n for k, v in dim_totals.items()}
        weakest = min(avgs, key=avgs.get)
        return weakest, avgs[weakest]

    def report(self) -> str:
        """Return a formatted markdown report string."""
        lines = ["# AXIOM Prize Readiness Report\n"]
        lines.append(
            "| Problem | Knowledge | Reasoning | Verification | Hypothesis | Coverage | **Score** |"
        )
        lines.append(
            "|:--------|----------:|----------:|-------------:|-----------:|---------:|----------:|"
        )
        for prob, score in self.score_all():
            b = prob.axiom_baseline
            lines.append(
                f"| {prob.name} "
                f"| {b.knowledge:.2f} "
                f"| {b.reasoning:.2f} "
                f"| {b.verification:.2f} "
                f"| {b.hypothesis_gen:.2f} "
                f"| {b.literature_coverage:.2f} "
                f"| **{score:.3f}** |"
            )

        weakest_prob = self.weakest_problem()
        weak_dim, weak_score = self.global_weakest_dimension()

        lines.append(f"\n## Weakest Problem\n**{weakest_prob.name}**")
        lines.append(f"\n> Recommended next action: {weakest_prob.recommended_action}")
        lines.append(f"\n## Weakest Capability Dimension\n**{weak_dim}** (avg score: {weak_score:.3f})")
        lines.append(
            f"\n> Priority: invest Sprint resources in improving `{weak_dim}` "
            f"across all problem domains."
        )
        return "\n".join(lines)


# ── CLI entry point ───────────────────────────────────────────────────────────

def main():
    scorer = PrizeReadinessScorer()
    print(scorer.report())

    weak_dim, weak_score = scorer.global_weakest_dimension()
    weakest_prob = scorer.weakest_problem()

    print(f"\n{'='*60}")
    print(f"WEAKEST DIMENSION : {weak_dim.upper()} (score {weak_score:.3f})")
    print(f"WEAKEST PROBLEM   : {weakest_prob.name}")
    print(f"RECOMMENDED ACTION: {weakest_prob.recommended_action}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
