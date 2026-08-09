"""Problem profiling — classify research problems before routing (SIMR §4)."""

from __future__ import annotations

import re
import uuid

from axiom.evaluation.frameworks.capability import CapabilityDimension
from axiom.routing.models import (
    ProblemDifficulty,
    ProblemProfile,
    ResearchDomain,
    VerificationRequirement,
)

_DOMAIN_KEYWORDS: dict[ResearchDomain, list[str]] = {
    ResearchDomain.MATHEMATICS: [
        "theorem", "proof", "lemma", "conjecture", "prime", "algebra",
        "topology", "number theory", "riemann", "zeta",
    ],
    ResearchDomain.COMPUTER_SCIENCE: [
        "algorithm", "complexity", "code", "program", "data structure",
    ],
    ResearchDomain.PHYSICS: [
        "equation", "simulation", "quantum", "particle", "field",
    ],
    ResearchDomain.LITERATURE: [
        "paper", "literature", "survey", "review", "citation",
    ],
}


def profile_problem(
    statement: str,
    *,
    domain: ResearchDomain | None = None,
    difficulty: ProblemDifficulty | None = None,
    required_capabilities: list[str] | None = None,
    metadata: dict | None = None,
) -> ProblemProfile:
    """Classify a research problem and determine required capabilities."""
    text = statement.lower()
    inferred_domain = domain or _infer_domain(text)
    inferred_difficulty = difficulty or _infer_difficulty(text)
    caps = required_capabilities or _infer_required_capabilities(text, inferred_domain)

    requires_literature = any(
        kw in text for kw in ["literature", "paper", "cite", "prior work", "survey"]
    )
    requires_formal = any(
        kw in text for kw in ["prove", "formal", "theorem", "lean", "isabelle", "coq"]
    )
    requires_experiment = any(
        kw in text for kw in ["experiment", "simulate", "compute", "benchmark", "test"]
    )

    verification = VerificationRequirement.NONE
    if requires_formal:
        verification = VerificationRequirement.FORMAL
    elif requires_experiment:
        verification = VerificationRequirement.REPRODUCTION
    elif requires_literature:
        verification = VerificationRequirement.INDEPENDENT

    uncertainty = 0.7 if inferred_difficulty == ProblemDifficulty.FRONTIER else 0.4
    if inferred_difficulty == ProblemDifficulty.HARD:
        uncertainty = 0.55

    return ProblemProfile(
        problem_id=f"prob_{uuid.uuid4().hex[:12]}",
        statement=statement,
        domain=inferred_domain,
        difficulty=inferred_difficulty,
        required_capabilities=caps,
        verification_requirement=verification,
        requires_literature=requires_literature,
        requires_formal=requires_formal,
        requires_experiment=requires_experiment,
        expected_runtime_minutes=_estimate_runtime(inferred_difficulty),
        uncertainty=uncertainty,
        safety_risk=_assess_safety(text),
        metadata=metadata or {},
    )


def _infer_domain(text: str) -> ResearchDomain:
    scores: dict[ResearchDomain, int] = {d: 0 for d in ResearchDomain}
    for domain, keywords in _DOMAIN_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                scores[domain] += 1
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else ResearchDomain.GENERAL_SCIENCE


def _infer_difficulty(text: str) -> ProblemDifficulty:
    if any(kw in text for kw in ["millennium", "open problem", "unsolved", "conjecture"]):
        return ProblemDifficulty.FRONTIER
    if any(kw in text for kw in ["prove", "formal", "novel", "discover"]):
        return ProblemDifficulty.HARD
    if any(kw in text for kw in ["summarize", "explain", "what is"]):
        return ProblemDifficulty.TRIVIAL
    return ProblemDifficulty.MODERATE


def _infer_required_capabilities(text: str, domain: ResearchDomain) -> list[str]:
    caps: list[str] = []
    if domain == ResearchDomain.MATHEMATICS:
        caps.extend([
            CapabilityDimension.MATHEMATICAL_REASONING.value,
            CapabilityDimension.PROOF_VERIFICATION.value,
        ])
    if domain == ResearchDomain.LITERATURE:
        caps.append(CapabilityDimension.LITERATURE_SYNTHESIS.value)
    if "counterexample" in text:
        caps.append(CapabilityDimension.COUNTEREXAMPLE_SEARCH.value)
    if "hypothesis" in text or "conjecture" in text:
        caps.append(CapabilityDimension.CONJECTURE_GENERATION.value)
    if not caps:
        caps.append(CapabilityDimension.RESEARCH_PLANNING.value)
    return list(dict.fromkeys(caps))


def _estimate_runtime(difficulty: ProblemDifficulty) -> int:
    return {
        ProblemDifficulty.TRIVIAL: 5,
        ProblemDifficulty.MODERATE: 30,
        ProblemDifficulty.HARD: 120,
        ProblemDifficulty.FRONTIER: 480,
    }[difficulty]


def _assess_safety(text: str) -> str:
    if re.search(r"\b(weapon|bioweapon|exploit|jailbreak)\b", text):
        return "high"
    if re.search(r"\b(delete|drop table|rm -rf)\b", text):
        return "medium"
    return "low"
