"""Formal mathematics prover registry (FMTP §1)."""

from __future__ import annotations

from axiom.formal_math.models import ProverSpec

try:
    from axiom.mip.formal.lean4 import check_lean4_available
except ImportError:
    def check_lean4_available() -> bool:
        return False


_PROVER_CATALOG: dict[str, ProverSpec] = {
    "lean4": ProverSpec(
        prover_id="lean4",
        name="Lean 4",
        version="4.x",
        language="Lean",
        libraries=["Mathlib4"],
        tactics=[
            "ring", "norm_num", "linarith", "simp", "induction",
            "contrapose", "omega", "nlinarith",
        ],
        automation=["aesop", "decide"],
        supported_domains=[
            "algebra", "analysis", "number_theory", "topology", "logic",
        ],
        installed=check_lean4_available(),
        limitations=[
            "Requires Mathlib build for full library",
            "Not installed in default dev environment",
        ],
        verification_status="primary" if check_lean4_available() else "simulation_available",
    ),
    "coq": ProverSpec(
        prover_id="coq",
        name="Coq",
        version="8.x",
        language="Gallina",
        libraries=["Coq.Init", "MathComp"],
        tactics=["auto", "omega", "lia", "induction"],
        automation=["auto", "tauto"],
        supported_domains=["logic", "algebra", "type_theory"],
        installed=False,
        limitations=["Not integrated in v1 — export stub only"],
        verification_status="planned",
    ),
    "isabelle": ProverSpec(
        prover_id="isabelle",
        name="Isabelle/HOL",
        version="2024",
        language="Isar",
        libraries=["HOL", "HOL-Analysis"],
        tactics=["simp", "auto", "blast"],
        automation=["sledgehammer"],
        supported_domains=["logic", "analysis", "algebra"],
        installed=False,
        limitations=["Not integrated in v1 — export stub only"],
        verification_status="planned",
    ),
    "smt": ProverSpec(
        prover_id="smt",
        name="SMT Solver (Z3)",
        version="4.x",
        language="SMT-LIB",
        libraries=[],
        tactics=[],
        automation=["z3"],
        supported_domains=["finite_arithmetic", "constraints"],
        installed=True,
        limitations=["Finite domains only — not general theorem proving"],
        verification_status="counterexample_and_finite_check",
    ),
    "sympy": ProverSpec(
        prover_id="sympy",
        name="SymPy",
        version="1.x",
        language="Python",
        libraries=["sympy"],
        tactics=[],
        automation=["simplify", "solve"],
        supported_domains=["symbolic_algebra", "calculus"],
        installed=True,
        limitations=["Symbolic computation — not machine-checked proof"],
        verification_status="experimental_evidence_only",
    ),
}


def list_provers() -> list[ProverSpec]:
    return list(_PROVER_CATALOG.values())


def get_prover(prover_id: str) -> ProverSpec | None:
    return _PROVER_CATALOG.get(prover_id)


def recommended_prover(domain: str) -> str:
    """Select highest-value prover for domain — Lean preferred when available."""
    if domain in ("algebra", "number_theory", "analysis", "topology"):
        return "lean4"
    if domain in ("finite_arithmetic", "constraints"):
        return "smt"
    if check_lean4_available():
        return "lean4"
    return "smt"
