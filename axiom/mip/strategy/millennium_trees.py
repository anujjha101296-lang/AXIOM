"""
Department F — Research Planning
Hierarchical decomposition trees for all 6 Millennium Prize Problems.
Pre-built lemma DAGs with Lemma Prioritization Index P(L).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Lemma:
    """A sub-problem node in a research strategy decomposition tree."""
    id: str
    name: str
    description: str
    domain: str
    estimated_impact: float   # 0.0–1.0: how much solving this advances the parent problem
    feasibility: float        # 0.0–1.0: current estimated feasibility given AXIOM's capabilities
    estimated_cost: float     # 0.0–1.0: relative effort required
    children: list["Lemma"] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)
    status: str = "open"      # open, in_progress, solved, blocked
    notes: str = ""

    @property
    def priority_index(self) -> float:
        """P(L) = (impact × feasibility) / cost"""
        if self.estimated_cost == 0:
            return 0.0
        return round((self.estimated_impact * self.feasibility) / self.estimated_cost, 4)

    def to_dict(self, depth: int = 0) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "domain": self.domain,
            "priority_index": self.priority_index,
            "impact": self.estimated_impact,
            "feasibility": self.feasibility,
            "cost": self.estimated_cost,
            "status": self.status,
            "notes": self.notes,
            "children": [c.to_dict(depth + 1) for c in self.children] if depth < 4 else [],
        }


# ═══════════════════════════════════════════════════════
# RIEMANN HYPOTHESIS DECOMPOSITION TREE
# ═══════════════════════════════════════════════════════

RIEMANN_TREE = Lemma(
    id="riemann_hypothesis",
    name="Riemann Hypothesis",
    description="All non-trivial zeros of ζ(s) lie on Re(s) = 1/2",
    domain="number_theory",
    estimated_impact=1.0,
    feasibility=0.02,
    estimated_cost=1.0,
    children=[
        Lemma(
            id="rh_functional_equation",
            name="Functional Equation Structure",
            description="Understand the symmetry ξ(s) = ξ(1-s) and its implications for zero locations",
            domain="complex_analysis",
            estimated_impact=0.4,
            feasibility=0.6,
            estimated_cost=0.3,
            children=[
                Lemma(
                    id="rh_xi_function",
                    name="Xi Function Properties",
                    description="ξ(s) is entire of order 1, all zeros are non-trivial zeros of ζ",
                    domain="complex_analysis",
                    estimated_impact=0.3,
                    feasibility=0.75,
                    estimated_cost=0.25,
                ),
                Lemma(
                    id="rh_zeta_analytic_continuation",
                    name="Analytic Continuation of ζ",
                    description="Formal proof of ζ(s) analytic continuation to ℂ \\ {1}",
                    domain="complex_analysis",
                    estimated_impact=0.25,
                    feasibility=0.8,
                    estimated_cost=0.2,
                ),
            ],
        ),
        Lemma(
            id="rh_zero_free_region",
            name="Zero-Free Region Expansion",
            description="Extend known zero-free region toward Re(s)=1/2",
            domain="analytic_number_theory",
            estimated_impact=0.35,
            feasibility=0.35,
            estimated_cost=0.5,
            children=[
                Lemma(
                    id="rh_de_la_vallee",
                    name="de la Vallée-Poussin Type Bound",
                    description="Improve classical zero-free region bound c/log|t|",
                    domain="analytic_number_theory",
                    estimated_impact=0.2,
                    feasibility=0.4,
                    estimated_cost=0.4,
                ),
                Lemma(
                    id="rh_density_estimate",
                    name="Zero Density Estimates",
                    description="N(σ,T) ≪ T^(A(1-σ)) log^B T bounds",
                    domain="analytic_number_theory",
                    estimated_impact=0.25,
                    feasibility=0.45,
                    estimated_cost=0.45,
                ),
            ],
        ),
        Lemma(
            id="rh_explicit_formula",
            name="Explicit Formula Verification",
            description="ψ(x) = x - Σ_{ρ} x^ρ/ρ - log(2π) connection to prime distribution",
            domain="analytic_number_theory",
            estimated_impact=0.3,
            feasibility=0.55,
            estimated_cost=0.3,
            children=[
                Lemma(
                    id="rh_prime_number_theorem",
                    name="Prime Number Theorem Connection",
                    description="π(x) ~ x/log(x) and its error term implications",
                    domain="analytic_number_theory",
                    estimated_impact=0.2,
                    feasibility=0.7,
                    estimated_cost=0.2,
                ),
            ],
        ),
        Lemma(
            id="rh_spectral_approach",
            name="Spectral/Operator Theory Approach",
            description="Hilbert–Pólya conjecture: zeros as eigenvalues of a Hermitian operator",
            domain="functional_analysis",
            estimated_impact=0.4,
            feasibility=0.15,
            estimated_cost=0.8,
        ),
        Lemma(
            id="rh_computational_verification",
            name="Computational Zero Verification",
            description="Track verified zeros on critical line (currently 10^13+ zeros verified)",
            domain="computational_mathematics",
            estimated_impact=0.1,
            feasibility=0.9,
            estimated_cost=0.1,
            notes="High feasibility — AXIOM can implement zeta zero tracking via mpmath",
        ),
    ],
)


# ═══════════════════════════════════════════════════════
# P vs NP DECOMPOSITION TREE
# ═══════════════════════════════════════════════════════

P_VS_NP_TREE = Lemma(
    id="p_vs_np",
    name="P vs NP",
    description="Does P = NP? Can every NP problem be solved in polynomial time?",
    domain="computational_complexity",
    estimated_impact=1.0,
    feasibility=0.01,
    estimated_cost=1.0,
    children=[
        Lemma(
            id="pvnp_circuit_complexity",
            name="Circuit Complexity Lower Bounds",
            description="Prove super-polynomial circuit lower bounds for NP functions",
            domain="circuit_complexity",
            estimated_impact=0.5,
            feasibility=0.12,
            estimated_cost=0.7,
        ),
        Lemma(
            id="pvnp_natural_proofs",
            name="Overcoming Natural Proofs Barrier",
            description="Razborov-Rudich natural proofs barrier — any proof must avoid naturalness",
            domain="complexity_theory",
            estimated_impact=0.3,
            feasibility=0.1,
            estimated_cost=0.8,
        ),
        Lemma(
            id="pvnp_sat_lower_bound",
            name="SAT Lower Bound",
            description="Prove SAT requires super-polynomial time on any deterministic TM",
            domain="computational_complexity",
            estimated_impact=0.6,
            feasibility=0.08,
            estimated_cost=0.9,
        ),
        Lemma(
            id="pvnp_algebraization",
            name="Overcoming Algebrization Barrier",
            description="Aaronson-Wigderson algebrization barrier must be circumvented",
            domain="complexity_theory",
            estimated_impact=0.3,
            feasibility=0.1,
            estimated_cost=0.75,
        ),
    ],
)


# ═══════════════════════════════════════════════════════
# YANG-MILLS DECOMPOSITION TREE
# ═══════════════════════════════════════════════════════

YANG_MILLS_TREE = Lemma(
    id="yang_mills",
    name="Yang–Mills Mass Gap",
    description="Prove Yang–Mills quantum gauge theory exists with positive mass gap Δ > 0",
    domain="mathematical_physics",
    estimated_impact=1.0,
    feasibility=0.02,
    estimated_cost=1.0,
    children=[
        Lemma(
            id="ym_gauge_field_algebra",
            name="Gauge Field Algebraic Structures",
            description="Formalize SU(N) gauge group representations and connection algebra",
            domain="algebra",
            estimated_impact=0.3,
            feasibility=0.4,
            estimated_cost=0.4,
            notes="High priority — AXIOM can ingest Jaffe-Witten formulation papers",
        ),
        Lemma(
            id="ym_functional_integral",
            name="Functional Integral Measure",
            description="Rigorous construction of the Yang–Mills functional integral on ℝ⁴",
            domain="mathematical_physics",
            estimated_impact=0.4,
            feasibility=0.1,
            estimated_cost=0.8,
        ),
        Lemma(
            id="ym_spectral_gap",
            name="Spectral Gap of Hamiltonian",
            description="Prove H_{YM} has a spectral gap above ground state energy",
            domain="functional_analysis",
            estimated_impact=0.5,
            feasibility=0.1,
            estimated_cost=0.85,
        ),
    ],
)


# ═══════════════════════════════════════════════════════
# BSD DECOMPOSITION TREE
# ═══════════════════════════════════════════════════════

BSD_TREE = Lemma(
    id="birch_swinnerton_dyer",
    name="Birch–Swinnerton-Dyer Conjecture",
    description="Rank of elliptic curve E/ℚ equals order of zero of L(E,s) at s=1",
    domain="algebraic_geometry",
    estimated_impact=1.0,
    feasibility=0.03,
    estimated_cost=1.0,
    children=[
        Lemma(
            id="bsd_elliptic_curve_model",
            name="Elliptic Curve Models",
            description="Formalize Weierstrass models y² = x³ + ax + b over ℚ",
            domain="algebraic_geometry",
            estimated_impact=0.3,
            feasibility=0.5,
            estimated_cost=0.3,
        ),
        Lemma(
            id="bsd_l_function",
            name="L-Function Analytic Properties",
            description="Analytic continuation and functional equation for L(E,s)",
            domain="analytic_number_theory",
            estimated_impact=0.4,
            feasibility=0.3,
            estimated_cost=0.5,
        ),
        Lemma(
            id="bsd_rank_computation",
            name="Mordell–Weil Rank Computation",
            description="Compute rational points group structure and rank",
            domain="algebraic_geometry",
            estimated_impact=0.3,
            feasibility=0.45,
            estimated_cost=0.4,
        ),
    ],
)


# ═══════════════════════════════════════════════════════
# NAVIER-STOKES DECOMPOSITION TREE
# ═══════════════════════════════════════════════════════

NAVIER_STOKES_TREE = Lemma(
    id="navier_stokes",
    name="Navier–Stokes Existence and Smoothness",
    description="Global smooth solutions to 3D Navier–Stokes equations",
    domain="pde_analysis",
    estimated_impact=1.0,
    feasibility=0.02,
    estimated_cost=1.0,
    children=[
        Lemma(
            id="ns_local_existence",
            name="Local-in-Time Existence",
            description="Local smooth solutions exist for short time (classical result)",
            domain="pde_analysis",
            estimated_impact=0.2,
            feasibility=0.8,
            estimated_cost=0.2,
        ),
        Lemma(
            id="ns_energy_inequality",
            name="Energy Inequality",
            description="Leray energy inequality: ∫|u|² dx + 2ν ∫∫|∇u|² dx dt ≤ ∫|u₀|² dx",
            domain="pde_analysis",
            estimated_impact=0.35,
            feasibility=0.55,
            estimated_cost=0.35,
        ),
        Lemma(
            id="ns_regularity_criteria",
            name="Blow-up Criteria",
            description="Serrin/Prodi-Serrin regularity criteria for global regularity",
            domain="pde_analysis",
            estimated_impact=0.4,
            feasibility=0.3,
            estimated_cost=0.55,
        ),
    ],
)


# ═══════════════════════════════════════════════════════
# HODGE CONJECTURE DECOMPOSITION TREE
# ═══════════════════════════════════════════════════════

HODGE_TREE = Lemma(
    id="hodge_conjecture",
    name="Hodge Conjecture",
    description="Every Hodge class on a smooth complex projective variety is algebraic",
    domain="algebraic_geometry",
    estimated_impact=1.0,
    feasibility=0.02,
    estimated_cost=1.0,
    children=[
        Lemma(
            id="hodge_cohomology_structure",
            name="Hodge Decomposition",
            description="H^n(X,ℂ) = ⊕_{p+q=n} H^{p,q}(X) formal decomposition",
            domain="algebraic_geometry",
            estimated_impact=0.3,
            feasibility=0.55,
            estimated_cost=0.3,
        ),
        Lemma(
            id="hodge_algebraic_cycles",
            name="Algebraic Cycle Classes",
            description="Chern class map from algebraic K-theory to cohomology",
            domain="algebraic_geometry",
            estimated_impact=0.4,
            feasibility=0.35,
            estimated_cost=0.5,
        ),
    ],
)


# Registry of all 6 Millennium Problems
MILLENNIUM_TREES: dict[str, Lemma] = {
    "riemann_hypothesis": RIEMANN_TREE,
    "p_vs_np": P_VS_NP_TREE,
    "yang_mills": YANG_MILLS_TREE,
    "birch_swinnerton_dyer": BSD_TREE,
    "navier_stokes": NAVIER_STOKES_TREE,
    "hodge_conjecture": HODGE_TREE,
}


def get_prioritized_queue(problem_id: str) -> list[dict[str, Any]]:
    """Return flat prioritized list of lemmas sorted by P(L) descending."""
    tree = MILLENNIUM_TREES.get(problem_id)
    if tree is None:
        return []

    def flatten(node: Lemma, parent_id: str | None = None) -> list[dict[str, Any]]:
        result = [{"parent_id": parent_id, **node.to_dict()}]
        for child in node.children:
            result.extend(flatten(child, node.id))
        return result

    all_lemmas = flatten(tree)
    # Skip root node, sort children by priority
    return sorted(all_lemmas[1:], key=lambda x: x["priority_index"], reverse=True)
