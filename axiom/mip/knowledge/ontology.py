"""
Department A — Mathematical Knowledge
Mathematical ontology: object types, edge types, domain taxonomy.
"""
from __future__ import annotations

from enum import Enum


class MathObjectType(str, Enum):
    """All recognized mathematical object types in AXIOM MIP."""
    OBJECT = "object"
    AXIOM = "axiom"
    DEFINITION = "definition"
    THEOREM = "theorem"
    LEMMA = "lemma"
    PROOF = "proof"
    COROLLARY = "corollary"
    CONJECTURE = "conjecture"
    OPEN_PROBLEM = "open_problem"
    EQUIVALENT_STATEMENT = "equivalent_statement"
    COUNTEREXAMPLE = "counterexample"
    TRANSFORMATION = "transformation"
    DOMAIN = "domain"
    AXIOM_SYSTEM = "axiom_system"
    REFERENCE = "reference"


class MathEdgeType(str, Enum):
    """Logical relationship types between mathematical objects."""
    PROVES = "PROVES"
    DEPENDS_ON = "DEPENDS_ON"
    EQUIVALENT_TO = "EQUIVALENT_TO"
    GENERALIZES = "GENERALIZES"
    SPECIALIZES = "SPECIALIZES"
    CONTRADICTS = "CONTRADICTS"
    COUNTEREXAMPLE_FOR = "COUNTEREXAMPLE_FOR"
    IMPLIES = "IMPLIES"
    CITED_BY = "CITED_BY"
    DERIVED_FROM = "DERIVED_FROM"
    BELONGS_TO = "BELONGS_TO"


class MathDomain(str, Enum):
    """Mathematical domain taxonomy."""
    ALGEBRA = "algebra"
    NUMBER_THEORY = "number_theory"
    ANALYSIS = "analysis"
    TOPOLOGY = "topology"
    LOGIC = "logic"
    COMBINATORICS = "combinatorics"
    CATEGORY_THEORY = "category_theory"
    GEOMETRY = "geometry"
    PROBABILITY = "probability"
    COMPUTATIONAL = "computational"
    ALGEBRAIC_GEOMETRY = "algebraic_geometry"
    DIFFERENTIAL_GEOMETRY = "differential_geometry"
    MATHEMATICAL_PHYSICS = "mathematical_physics"
    UNKNOWN = "unknown"


class EpistemicStatus(str, Enum):
    """Epistemic status of a mathematical claim."""
    VERIFIED = "verified"
    CONJECTURED = "conjectured"
    REFUTED = "refuted"
    DISPUTED = "disputed"
    OPEN = "open"
    UNKNOWN = "unknown"


# Domain keyword mapping for auto-classification
DOMAIN_KEYWORDS: dict[MathDomain, list[str]] = {
    MathDomain.NUMBER_THEORY: [
        "prime", "zeta", "riemann", "modular", "congruence", "dirichlet",
        "euler", "arithmetic", "integer", "divisor", "gcd", "lcm",
        "fermat", "goldbach", "twin prime",
    ],
    MathDomain.ANALYSIS: [
        "continuous", "differentiable", "integral", "limit", "convergent",
        "holomorphic", "analytic", "measurable", "lebesgue", "series",
        "fourier", "banach", "hilbert",
    ],
    MathDomain.ALGEBRA: [
        "group", "ring", "field", "module", "vector space", "homomorphism",
        "isomorphism", "polynomial", "linear", "matrix", "determinant",
        "eigenvalue", "galois",
    ],
    MathDomain.TOPOLOGY: [
        "compact", "connected", "open set", "closed set", "homeomorphism",
        "homotopy", "manifold", "fiber bundle", "metric space",
    ],
    MathDomain.LOGIC: [
        "proof", "axiom", "theorem", "lemma", "conjecture", "decidable",
        "computable", "complexity", "np-hard", "p vs np",
    ],
    MathDomain.ALGEBRAIC_GEOMETRY: [
        "variety", "scheme", "elliptic curve", "hodge", "cohomology",
        "sheaf", "divisor class",
    ],
    MathDomain.MATHEMATICAL_PHYSICS: [
        "yang-mills", "navier-stokes", "gauge", "quantum field",
        "mass gap", "fluid dynamics",
    ],
}


def classify_domain(text: str) -> MathDomain:
    """Auto-classify a mathematical statement into a domain."""
    text_lower = text.lower()
    scores: dict[MathDomain, int] = {}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[domain] = score
    if not scores:
        return MathDomain.UNKNOWN
    return max(scores, key=lambda d: scores[d])
